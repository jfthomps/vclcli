from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.json import JSON

console = Console()


def ts(u) -> str:
    try:
        return datetime.fromtimestamp(int(u)).strftime("%Y-%m-%d %H:%M:%S") if u else "?"
    except Exception:
        return str(u)


def show_help_panel(text: str, title: str = "Help"):
    console.print(Panel.fit(text, title=title))


def show_error(msg: str, title: str = "Error"):
    console.print(Panel.fit(f"[red]{msg}[/red]", title=title))


def show_success(msg: str, title: str = "Success"):
    console.print(Panel.fit(f"[green]{msg}[/green]", title=title))


def show_json(data, title: str = "JSON"):
    console.print(Panel.fit(JSON.from_data(data), title=title))


def make_images_table(images) -> Table:
    table = Table(title="Available Images")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    for img in images:
        table.add_row(str(img.get("id", "")), str(img.get("name", "")))
    return table


def make_requests_table(reqs) -> Table:
    table = Table(title=f"Active Requests ({len(reqs)})")
    table.add_column("Request ID", style="cyan", no_wrap=True)
    table.add_column("Image", style="green")
    table.add_column("State", style="magenta")
    table.add_column("Start")
    table.add_column("End")
    table.add_column("OS", style="yellow")

    for r in reqs:
        table.add_row(
            str(r.get("requestid", "")),
            str(r.get("imagename", "")),
            str(r.get("state", "")),
            ts(r.get("start")),
            ts(r.get("end")),
            str(r.get("OS", "")),
        )
    return table
