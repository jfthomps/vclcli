import os
import pyperclip
from rich.panel import Panel
from rich.syntax import Syntax
from rich.console import Group
from vcl.rpc import call, VCLRPCError
from vcl.ui import console, make_images_table, make_requests_table, show_json, show_success


def cmd_test(*, json: bool = False):
    with console.status("[bold green]Testing RPC...[/bold green]"):
        res = call("XMLRPCtest", ["hello"])
    if json:
        show_json(res, title="XMLRPCtest")
    else:
        console.print(Panel.fit(f"[green]success[/green]\n{res}", title="XMLRPCtest"))

def cmd_getIP(*, json: bool = False):
    res = call("XMLRPCgetIP", [])
    console.print(Panel.fit(f"[green]success[/green]\n{res['ip']}", title="XMLRPCgetIP"))

def cmd_images_list(*, json: bool = False):
    with console.status("[bold green]Fetching images...[/bold green]"):
        images = call("XMLRPCgetImages", [])
    if json:
        show_json(images, title="Images")
    else:
        console.print(make_images_table(images))


def cmd_request_list(*, json: bool = False):
    with console.status("[bold green]Fetching active requests...[/bold green]"):
        res = call("XMLRPCgetRequestIds", [])

    if json:
        show_json(res, title="Request IDs")
        return

    if not isinstance(res, dict) or res.get("status") != "success":
        raise VCLRPCError(f"request list failed: {res}")

    reqs = res.get("requests", [])
    console.print(make_requests_table(reqs))


def cmd_request_create(image_id: int, start: str = "now", duration: int = 60, *, json: bool = False):
    with console.status("[bold green]Creating request...[/bold green]"):
        res = call("XMLRPCaddRequest", [int(image_id), start, int(duration)])

    if json:
        show_json(res, title="Create Request")
        return

    if isinstance(res, dict) and res.get("status") == "success":
        show_success(f"Request created: requestid={res.get('requestid')}", title="request create")
    else:
        raise VCLRPCError(f"request create failed: {res}")


def cmd_request_status(request_id: int, *, json: bool = False):
    with console.status("[bold green]Fetching request status...[/bold green]"):
        res = call("XMLRPCgetRequestStatus", [int(request_id)])

    if json:
        show_json(res, title="Request Status")
        return

    # status can vary by server version; print a friendly summary if dict-like
    if isinstance(res, dict):
        console.print(Panel.fit(str(res), title="request status"))
    else:
        console.print(Panel.fit(f"{res}", title="request status"))


def cmd_request_end(request_id: int, *, json: bool = False):
    with console.status("[bold green]Ending request...[/bold green]"):
        res = call("XMLRPCendRequest", [int(request_id)])

    if json:
        show_json(res, title="End Request")
        return

    if isinstance(res, dict) and res.get("status") == "error":
        raise VCLRPCError(f"request end failed: {res}")

    show_success(f"Request ended: {request_id}", title="request end")


def cmd_request_end_all(*, json: bool = False):
    with console.status("[bold green]Fetching active requests...[/bold green]"):
        res = call("XMLRPCgetRequestIds", [])

    if not isinstance(res, dict) or res.get("status") != "success":
        raise VCLRPCError(f"request end-all failed fetching ids: {res}")

    reqs = res.get("requests", [])
    ended = []
    failed = []

    for r in reqs:
        rid = r.get("requestid")
        try:
            rc = call("XMLRPCendRequest", [int(rid)])
            if isinstance(rc, dict) and rc.get("status") == "error":
                failed.append({"requestid": rid, "error": rc})
            else:
                ended.append(rid)
        except Exception as e:
            failed.append({"requestid": rid, "error": str(e)})

    out = {"ended": ended, "failed": failed}

    if json:
        show_json(out, title="End All Requests")
    else:
        show_success(f"Ended {len(ended)} request(s); failed {len(failed)}.", title="request end-all")
        if failed:
            show_json(failed, title="Failures")


# def cmd_request_connect(request_id: int, *, client_ip: str | None = None, json: bool = False):
#     if client_ip is None:
#         client_ip = os.getenv("VCL_CLIENT_IP")

#     if not client_ip:
#         raise VCLRPCError("Missing client IP. Provide --client-ip or set VCL_CLIENT_IP.")

#     with console.status("[bold green]Fetching connect data...[/bold green]"):
#         res = call("XMLRPCgetRequestConnectData", [int(request_id), client_ip])

#     if json:
#         show_json(res, title="Connect Data")
#         return

#     # If API returns non-dict, just print it
#     if not isinstance(res, dict):
#         console.print(Panel.fit(str(res), title="Connect Data"))
#         return

#     # Common fields (names can vary slightly by VCL version)
#     server = res.get("serverIP") or res.get("serverip") or res.get("hostname") or "?"
#     user = res.get("user") or res.get("userid") or "?"
#     port = res.get("connectport") or res.get("port") or 22

#     # Password sometimes exists for “this reservation only”
#     password = (
#         res.get("password")
#         or res.get("passwd")
#         or res.get("reservationpassword")
#         or res.get("connectpassword")
#     )

#     # Helpful, copy-friendly commands
#     ssh_cmd = f"ssh -p {port} {user}@{server}"
#     scp_cmd = f"scp -P {port} <local_file> {user}@{server}:~/"
#     rdp_hint = "If this is a Windows/RDP image, connect using an RDP client to the same host."

#     lines = []
#     lines.append(f"[bold]Remote Computer:[/bold] {server}")
#     lines.append(f"[bold]User ID:[/bold] {user}")
#     lines.append(f"[bold]Port:[/bold] {port}")
#     lines.append("")
#     lines.append("[bold]How to connect[/bold]")
#     lines.append("1) Open a terminal.")
#     lines.append(f"2) Run: [cyan]{ssh_cmd}[/cyan]")

#     # Password guidance
#     if password:
#         lines.append(f"3) When prompted, use this reservation password: [yellow]{password}[/yellow]")
#         lines.append("[dim]Note: This password is typically for this reservation only.[/dim]")
#     else:
#         lines.append("3) When prompted for a password, use your campus password (or the reservation password if shown in the VCL web UI).")

#     lines.append("")
#     lines.append("[bold]Optional[/bold]")
#     lines.append(f"- Upload a file: [cyan]{scp_cmd}[/cyan]")
#     lines.append(f"- {rdp_hint}")
#     lines.append("")
#     lines.append("[dim]Tip: If you're connecting from a new network/location, VCL may require re-fetching connect data again.[/dim]")

#     console.print(Panel.fit("\n".join(lines), title="Connect Instructions"))

def cmd_request_connect(
    request_id: int,
    *,
    client_ip: str | None = None,
    json: bool = False,
    copy: bool = False,   # NEW: optional clipboard copy
):
    if client_ip is None:
        res = call("XMLRPCgetIP", [])
        if res['status'] == 'success':
            client_ip = res['ip']

    if not client_ip:
        raise VCLRPCError("Failed to get client IP from call to XMLRPCgetIP")

    with console.status("[bold green]Fetching connect data...[/bold green]"):
        res = call("XMLRPCgetRequestConnectData", [int(request_id), client_ip])

    if json:
        show_json(res, title="Connect Data")
        return

    # If API returns non-dict, just print it
    if not isinstance(res, dict):
        console.print(Panel.fit(str(res), title="Connect Data"))
        return

    # Common fields (names can vary slightly by VCL version)
    server = res.get("serverIP") or res.get("serverip") or res.get("hostname") or "?"
    user = res.get("user") or res.get("userid") or "?"
    port = res.get("connectport") or res.get("port") or 22

    # Password sometimes exists for “this reservation only”
    password = (
        res.get("password")
        or res.get("passwd")
        or res.get("reservationpassword")
        or res.get("connectpassword")
    )

    # Helpful, copy-friendly commands
    ssh_cmd = f"ssh -p {port} {user}@{server}"
    scp_cmd = f"scp -P {port} <local_file> {user}@{server}:~/"
    rdp_hint = "If this is a Windows/RDP image, connect using an RDP client to the same host."

    # Optional: copy SSH command to clipboard (best alternative to a clickable button)
    copy_msg = ""
    if copy:
        try:
            pyperclip.copy(ssh_cmd)
            copy_msg = "[green]✅ Copied SSH command to clipboard[/green]\n"
        except Exception as e:
            copy_msg = f"[yellow]⚠️ Clipboard copy failed:[/yellow] {e}\n"

    # Text portion (keep it almost identical to what you had)
    lines = []
    lines.append(f"[bold]Remote Computer:[/bold] {server}")
    lines.append(f"[bold]User ID:[/bold] {user}")
    lines.append(f"[bold]Port:[/bold] {port}")
    lines.append("")
    lines.append("[bold]How to connect[/bold]")
    lines.append("1) Open a terminal.")
    lines.append("2) Run the following command:")

    if password:
        lines.append("3) When prompted, use this reservation password (if provided):")
        lines.append(f"   [yellow]{password}[/yellow]")
        lines.append("[dim]Note: This password is typically for this reservation only.[/dim]")
    else:
        lines.append("3) When prompted for a password, use your campus password (or the reservation password if shown in the VCL web UI).")

    lines.append("")
    lines.append("[bold]Optional[/bold]")
    lines.append("Upload a file:")
    lines.append(f"- {rdp_hint}")
    lines.append("")
    lines.append("[dim]Tip: If you're connecting from a new network/location, VCL may require re-fetching connect data again.[/dim]")

    # Render with code blocks (Monokai) using Group
    content = Group(
        copy_msg + "\n".join(lines),
        Syntax(ssh_cmd, "bash", theme="monokai", word_wrap=True),
        Syntax(scp_cmd, "bash", theme="monokai", word_wrap=True),
    )

    console.print(Panel(content, title="Connect Instructions"))
