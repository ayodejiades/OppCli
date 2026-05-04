"""
oppcli/ui.py — Terminal rendering using Rich.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich import box

# Custom theme for OppCli
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "dim": "grey50",
    "category.Fellowship": "blue",
    "category.Scholarship": "green",
    "category.Hackathon": "orange3",
    "category.Grant": "purple",
    "category.Internship": "yellow",
    "category.Conference": "cyan",
    "urgency.urgent": "bold red",
    "urgency.soon": "orange3",
    "urgency.safe": "grey50",
})

console = Console(theme=custom_theme)

BANNER = r"""
   ___  ____  ____   ___  __    ____
  / _ \|  _ \|  _ \ / __||  |  |_  /
 | | | | |_) | |_) | |   | |   / /
 | |_| |  __/|  __/| |__ | |__/ /__
  \___/|_|   |_|    \___||____/____|
"""

def print_banner():
    console.print(Panel(
        Text(BANNER, style="info", justify="center"),
        subtitle="[dim]Opportunity finder for African students[/dim]",
        box=box.MINIMAL,
        padding=(0, 2)
    ))

def get_deadline_style(days_left: Optional[int]) -> str:
    if days_left is None:
        return "urgency.safe"
    if days_left <= 7:
        return "urgency.urgent"
    if days_left <= 30:
        return "urgency.soon"
    return "urgency.safe"

def get_deadline_text(opp: Dict[str, Any]) -> Text:
    days = opp.get("days_left")
    if opp.get("expired"):
        return Text("Expired", style="error")
    if days is None:
        return Text(opp["deadline"], style="dim")
    
    style = get_deadline_style(days)
    if days == 0:
        return Text("TODAY", style="urgency.urgent")
    if days == 1:
        return Text("1 day left", style=style)
    return Text(f"{days}d left", style=style)

def print_stats(opps: List[Dict[str, Any]]):
    total = len(opps)
    funded = sum(1 for o in opps if o["stipend"])
    urgent = sum(1 for o in opps if o.get("days_left") is not None and 0 <= o["days_left"] <= 7)
    
    stats = Text()
    stats.append(f" {total} results ", style="bold white")
    stats.append(" · ", style="dim")
    stats.append(f" {funded} funded ", style="success")
    
    if urgent:
        stats.append(" · ", style="dim")
        stats.append(f" {urgent} closing this week ", style="urgency.urgent")
        
    console.print(stats)
    console.print()

def print_table(opps: List[Dict[str, Any]]):
    if not opps:
        console.print("[dim]No opportunities found. Try different filters.[/dim]")
        return

    table = Table(box=box.SIMPLE, header_style="dim", border_style="dim", pad_edge=False)
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("Title", ratio=3)
    table.add_column("Category", ratio=1)
    table.add_column("Org", ratio=2, style="dim")
    table.add_column("Deadline", justify="right")

    for o in opps:
        title_text = Text(o["title"])
        if o["stipend"]:
            title_text.append(" *", style="success")
            
        cat_style = f"category.{o['category']}"
        
        table.add_row(
            str(o["id"]),
            title_text,
            Text(o["category"], style=cat_style),
            o["org"],
            get_deadline_text(o)
        )

    console.print(table)
    console.print("[dim]* = includes stipend / funding[/dim]")
    console.print()

def print_detail(o: Dict[str, Any]):
    # Header
    cat_style = f"category.{o['category']}"
    header = Text()
    header.append(o['title'], style="bold white")
    header.append("\n")
    header.append(f"{o['org']} ", style="dim")
    header.append("· ", style="dim")
    header.append(o['category'], style=cat_style)
    header.append(" · ", style="dim")
    header.append(o['region'], style="info")
    
    console.print(Panel(header, box=box.HORIZONTALS))
    
    # Description
    console.print(f"\n{o['description']}\n")
    
    # Metadata
    table = Table.grid(padding=(0, 2))
    table.add_column(style="dim", justify="right")
    table.add_column()
    
    funded_str = "[success]Yes ✓[/success]" if o["stipend"] else "[dim]No[/dim]"
    table.add_row("Funded:", funded_str)
    table.add_row("Deadline:", get_deadline_text(o))
    
    tags = ", ".join(f"#{t}" for t in o["tags"])
    table.add_row("Tags:", f"[info]{tags}[/info]")
    table.add_row("Apply:", f"[link={o['link']}][blue]{o['link']}[/blue][/link]")
    
    console.print(table)
    console.print()

def print_header(text: str):
    console.rule(f"[bold white]{text}[/bold white]", align="left", style="dim")
    console.print()

def print_error(msg: str):
    console.print(f"\n [error]✗ {msg}[/error]\n")

def print_tip(msg: str):
    console.print(f" [dim]→ {msg}[/dim]")

def print_export_success(path: str, count: int):
    console.print(f"\n [success]✓ Exported {count} opportunit{'y' if count == 1 else 'ies'} → {path}[/success]\n")
