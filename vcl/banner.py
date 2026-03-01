"""
vclctl — Startup Banner
"""

from __future__ import annotations

import os
from urllib.parse import urlparse
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.rule import Rule
from rich.console import Group

# Reuse the project's shared console for consistent styling
from vcl.ui import console

# ── Block-pixel font for "VCL" (each char is 6 rows tall) ─────────────────────
VCL_ART = """\
██╗   ██╗ ██████╗██╗     
██║   ██║██╔════╝██║     
██║   ██║██║     ██║     
╚██╗ ██╔╝██║     ██║     
 ╚████╔╝ ╚██████╗███████╗
  ╚═══╝   ╚═════╝╚══════╝
"""

APP_LABEL = "vclctl"
VERSION = "v1.0.0"


def _endpoint_label() -> str:
    """
    Extract a friendly endpoint label from VCL_URL env.
    Falls back to hostname or 'VCL endpoint'.
    """
    url = os.getenv("VCL_URL", "")
    if not url:
        return "VCL endpoint"
    try:
        p = urlparse(url)
        # show just host if present
        if p.hostname:
            return p.hostname
        return url
    except Exception:
        return url


def _left_panel(username: str | None = None) -> Panel:
    """Left panel: logo + identity block (Claude-like left column)."""
    ACCENT = "bold bright_red"
    DIMACC = "dim bright_red"

    logo = Text(VCL_ART, style=ACCENT, justify="center")
    rule = Rule(style=DIMACC)

    id_table = Table.grid(padding=(0, 1))
    id_table.add_column(style="dim", no_wrap=True)
    id_table.add_column()

    display_name = username or os.getenv("USER") or "user"

    # These are intentionally generic; tweak if you want to show more details later.
    id_table.add_row("Welcome,", f"[bold white]{display_name}[/bold white]")
    id_table.add_row("", "")
    id_table.add_row("Model", "XML-RPC 2.0")
    id_table.add_row("Auth", "Bearer token")
    id_table.add_row("Endpoint", _endpoint_label())

    layout = Table.grid()
    layout.add_column()
    layout.add_row(logo)
    layout.add_row("")
    layout.add_row(rule)
    layout.add_row("")
    layout.add_row(id_table)

    return Panel(
        layout,
        title=f"[bold bright_red]{APP_LABEL}[/bold bright_red]",
        title_align="left",
        subtitle=f"[dim]{VERSION}[/dim]",
        subtitle_align="right",
        border_style="bright_red",
        padding=(1, 2),
    )


def _right_panel(recent_activity: list[dict] | None = None) -> Panel:
    """Right panel: recent activity + quick commands (Claude-like right column)."""
    DIMACC = "dim bright_red"

    # Recent activity
    activity_title = Text("Recent activity", style="bold white")

    activity = Table.grid(padding=(0, 1))
    activity.add_column(style="dim", min_width=7, no_wrap=True)
    activity.add_column()

    sample = recent_activity or [
        {"ago": "just now", "desc": "CLI started"},
        {"ago": "—", "desc": "Type 'help' to see commands"},
        {"ago": "—", "desc": "Use 'request list' to see active reservations"},
        {"ago": "—", "desc": "Use 'request connect --id <id>' for SSH details"},
    ]

    for item in sample[:4]:
        activity.add_row(item.get("ago", "—"), f"[white]{item.get('desc','')}[/white]")
    activity.add_row("", "[dim]… history available via your shell / prompt history[/dim]")

    # Quick commands (match your current CLI verbs)
    cmds_title = Text("\nQuick commands", style="bold white")

    cmds = Table.grid(padding=(0, 1))
    cmds.add_column(style="bold cyan", min_width=28, no_wrap=True)
    cmds.add_column(style="dim")

    quick_cmds = [
        ("vclctl> images list", "list available images"),
        ("vclctl> request list", "show active reservations"),
        ("vclctl> request connect --id <id>", "get SSH/RDP connection info"),
        ("vclctl> request create --image-id <id>", "create a new reservation"),
    ]
    for cmd, desc in quick_cmds:
        cmds.add_row(cmd, desc)

    cmds.add_row("", "")
    cmds.add_row("[dim]… type 'help' for full list[/dim]", "")

    layout = Table.grid()
    layout.add_column()
    layout.add_row(activity_title)
    layout.add_row(activity)
    layout.add_row(cmds_title)
    layout.add_row(cmds)

    return Panel(
        layout,
        border_style=DIMACC,
        padding=(1, 2),
    )


def show_startup_banner(
    username: str | None = None,
    recent_activity: list[dict] | None = None,
) -> None:
    """
    Render the VCL startup banner.

    Args:
        username: Override the display name (defaults to $USER env var).
        recent_activity: List of dicts with keys: 'ago', 'desc'.
    """
    console.print()
    console.print(
        Columns(
            [_left_panel(username), _right_panel(recent_activity)],
            equal=False,
            expand=True,
        )
    )
    console.print()

    console.print(
        "  [dim]✦  Ready. Type [bold white]help[/bold white] to begin, "
        "[bold white]exit[/bold white] to quit.[/dim]\n"
    )
