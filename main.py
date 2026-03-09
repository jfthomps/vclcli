import shlex
import os

from vcl.rpc import VCLRPCError
from vcl.ui import console, show_help_panel, show_error
from vcl.banner import show_startup_banner

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion

from vcl.commands import (
    cmd_test,
    cmd_getIP,
    cmd_images_list,
    cmd_request_list,
    cmd_request_connect,
    cmd_request_create,
    cmd_request_status,
    cmd_request_end,
    cmd_request_end_all,
)

HELP_TEXT = """[bold]Commands[/bold]

  [cyan]help[/cyan]
  [cyan]test[/cyan]
  [cyan]getIP[/cyan]
  [cyan]images list[/cyan]
  [cyan]request list[/cyan]
  [cyan]request create --image-id <id> [--duration <min>] [--start now][/cyan]
  [cyan]request status --id <request_id>[/cyan]
  [cyan]request connect --id <request_id>[/cyan]
  [cyan]request end --id <request_id>[/cyan]
  [cyan]request end-all[/cyan]
  [cyan]exit[/cyan] | [cyan]quit[/cyan]

Env:
  VCL_TOKEN (required)
  VCL_URL (optional)
  VCL_VERIFY_SSL (optional, default true)
"""


def _get_opt(tokens, name, default=None):
    if name not in tokens:
        return default
    i = tokens.index(name)
    return tokens[i + 1] if i + 1 < len(tokens) else default


def dispatch(line: str):
    tokens = shlex.split(line)
    if not tokens:
        return

    if tokens[0] in ("exit", "quit"):
        raise SystemExit(0)

    if tokens[0] == "help":
        show_help_panel(HELP_TEXT, title="vclctl Help")
        return

    if tokens[0] == "test":
        cmd_test()
        return

    if tokens[0] == "getIP":
        cmd_getIP()
        return

    if tokens[0] == "images" and len(tokens) >= 2 and tokens[1] == "list":
        cmd_images_list()
        return

    if tokens[0] == "request":
        if len(tokens) < 2:
            raise VCLRPCError("Usage: request <list|create|status|connect|end|end-all>")

        sub = tokens[1]
        rest = tokens[2:]

        if sub == "list":
            cmd_request_list()
            return

        if sub == "create":
            image_id = _get_opt(rest, "--image-id")
            duration = _get_opt(rest, "--duration", "60")
            start = _get_opt(rest, "--start", "now")
            if not image_id:
                raise VCLRPCError("Usage: request create --image-id <id> [--duration <min>] [--start now]")
            cmd_request_create(int(image_id), start=start, duration=int(duration))
            return

        if sub == "status":
            rid = _get_opt(rest, "--id")
            if not rid:
                raise VCLRPCError("Usage: request status --id <request_id>")
            cmd_request_status(int(rid))
            return

        if sub == "connect":
            rid = _get_opt(rest, "--id")
            if not rid:
                raise VCLRPCError("Usage: request connect --id <request_id> [--copy]")

            copy_flag = "--copy" in rest
            cmd_request_connect(int(rid), copy=copy_flag)
            return

        if sub == "end":
            rid = _get_opt(rest, "--id")
            if not rid:
                raise VCLRPCError("Usage: request end --id <request_id>")
            cmd_request_end(int(rid))
            return

        if sub == "end-all":
            cmd_request_end_all()
            return

    raise VCLRPCError("Unknown command. Type 'help'.")


class VCLCompleter(Completer):
    """
    Minimal 'single-match' tab completion:
    - If exactly 1 match exists, tab completes it.
    - If 0 or multiple matches exist, no completion is shown (no suggestion menu).
    """

    TOP = ["help", "test", "getIP", "images", "request", "exit", "quit"]
    IMAGES_SUB = ["list"]
    REQUEST_SUB = ["list", "create", "status", "connect", "end", "end-all"]

    FLAGS_BY_SUB = {
        "create": ["--image-id", "--duration", "--start"],
        "status": ["--id"],
        "connect": ["--id"],
        "end": ["--id"],
    }

    def _single_match(self, candidates, prefix: str):
        matches = [c for c in candidates if c.startswith(prefix)]
        return matches[0] if len(matches) == 1 else None

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        stripped = text.lstrip()
        if not stripped:
            return

        parts = stripped.split()
        ends_with_space = text.endswith(" ")

        # Determine which token we're completing and its prefix
        if ends_with_space:
            # completing a new token
            prefix = ""
        else:
            prefix = parts[-1]

        # --- complete top-level command ---
        if len(parts) == 1 and not ends_with_space:
            m = self._single_match(self.TOP, prefix)
            if m:
                yield Completion(m, start_position=-len(prefix))
            return

        cmd = parts[0]

        # --- complete subcommands ---
        if cmd == "images":
            # completing subcommand
            if (len(parts) == 1 and ends_with_space) or (len(parts) == 2 and not ends_with_space):
                sub_prefix = "" if ends_with_space else prefix
                m = self._single_match(self.IMAGES_SUB, sub_prefix)
                if m:
                    yield Completion(m, start_position=-len(sub_prefix))
            return

        if cmd == "request":
            # completing request subcommand
            if (len(parts) == 1 and ends_with_space) or (len(parts) == 2 and not ends_with_space):
                sub_prefix = "" if ends_with_space else prefix
                m = self._single_match(self.REQUEST_SUB, sub_prefix)
                if m:
                    yield Completion(m, start_position=-len(sub_prefix))
                return

            # completing flags for request subcommands
            if len(parts) >= 2:
                sub = parts[1]
                flags = self.FLAGS_BY_SUB.get(sub, [])
                # If we are starting a new token, only autocomplete when user begins typing '-' (so no random popups)
                if ends_with_space:
                    return
                if prefix.startswith("-"):
                    m = self._single_match(flags, prefix)
                    if m:
                        yield Completion(m, start_position=-len(prefix))
            return



def main():
    # show_help_panel("[bold]vclctl[/bold]\nType 'help' for commands.", title="vclctl")
    show_startup_banner(username=os.getenv("USER"))

    session = PromptSession(
        history=FileHistory(".vcl_history"),
        auto_suggest=None,
        completer=VCLCompleter(),
    )

    while True:
        try:
            line = session.prompt("vclctl> ").strip()
            dispatch(line)
        except SystemExit:
            console.print("[bold]bye![/bold]")
            return
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold]bye![/bold]")
            return
        except VCLRPCError as e:
            show_error(str(e))
        except Exception as e:
            show_error(f"Unexpected error: {e}")




if __name__ == "__main__":
    main()
