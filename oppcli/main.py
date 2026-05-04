"""
oppcli/main.py — Main entry point using Typer.
"""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated

from oppcli import data_manager as db
from oppcli import ui
from oppcli import export as ex
from oppcli.scraper.engine import ScraperEngine

app = typer.Typer(
    help="OpportunityCLI — find scholarships, fellowships & hackathons for African students.",
    add_completion=False,
    rich_markup_mode="rich"
)

def _get_filtered_opps(category, region, funded, all_expired, query=None):
    return db.get_filtered(
        category=category,
        region=region,
        stipend_only=funded,
        hide_expired=not all_expired,
        query=query
    )

@app.command()
def list(
    all: Annotated[bool, typer.Option("--all", help="Include expired opportunities")] = False
):
    """List all active opportunities."""
    ui.print_banner()
    opps = db.get_filtered(hide_expired=not all)
    ui.print_stats(opps)
    ui.print_table(opps)
    ui.print_tip("Run `oppcli show <ID>` to see full details for any opportunity.")

@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search keyword")],
    category: Annotated[Optional[str], typer.Option("--category", "-c", help="Filter by category")] = None,
    region: Annotated[Optional[str], typer.Option("--region", "-r", help="Filter by region")] = None,
    funded: Annotated[bool, typer.Option("--funded", "-f", help="Show only funded items")] = False,
    all: Annotated[bool, typer.Option("--all", help="Include expired")] = False
):
    """Search opportunities by keyword."""
    ui.print_banner()
    opps = _get_filtered_opps(category, region, funded, all, query)
    ui.print_header(f'Search results for "{query}"')
    ui.print_stats(opps)
    ui.print_table(opps)

@app.command()
def filter(
    category: Annotated[Optional[str], typer.Option("--category", "-c", help="Filter by category")] = None,
    region: Annotated[Optional[str], typer.Option("--region", "-r", help="Filter by region")] = None,
    funded: Annotated[bool, typer.Option("--funded", "-f", help="Show only funded items")] = False,
    all: Annotated[bool, typer.Option("--all", help="Include expired")] = False
):
    """Filter by category, region, or funding."""
    ui.print_banner()
    opps = _get_filtered_opps(category, region, funded, all)
    
    parts = []
    if category: parts.append(f"category={category}")
    if region: parts.append(f"region={region}")
    if funded: parts.append("funded only")
    
    label = ", ".join(parts) if parts else "no filters (showing all active)"
    ui.print_header(f"Filtered: {label}")
    ui.print_stats(opps)
    ui.print_table(opps)
    
    if not any([category, region, funded]):
        ui.print_tip("Use -c, -r, or -f to narrow results.")

@app.command()
def show(
    id: Annotated[int, typer.Argument(help="Opportunity ID (from list)")]
):
    """Show full details for one opportunity."""
    ui.print_banner()
    opp = db.get_by_id(id)
    if opp is None:
        ui.print_error(f"No opportunity found with ID {id}.")
        ui.print_tip("Run `oppcli list` to see valid IDs.")
        raise typer.Exit(code=1)
    ui.print_detail(opp)

@app.command()
def export(
    format: Annotated[str, typer.Option("--format", help="Output format (csv or json)")] = "csv",
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output file path")] = None,
    category: Annotated[Optional[str], typer.Option("--category", "-c")] = None,
    region: Annotated[Optional[str], typer.Option("--region", "-r")] = None,
    funded: Annotated[bool, typer.Option("--funded", "-f")] = False,
    query: Annotated[Optional[str], typer.Option("--query", "-q")] = None,
    all: Annotated[bool, typer.Option("--all")] = False
):
    """Export results to CSV or JSON."""
    ui.print_banner()
    opps = _get_filtered_opps(category, region, funded, all, query)
    
    if not opps:
        ui.print_error("No opportunities to export with current filters.")
        raise typer.Exit(code=1)
        
    fmt = format.lower()
    if fmt == "csv":
        path = ex.export_csv(opps, output)
    elif fmt == "json":
        path = ex.export_json(opps, output)
    else:
        ui.print_error(f"Unknown format '{fmt}'. Use csv or json.")
        raise typer.Exit(code=1)
        
    ui.print_export_success(path, len(opps))

@app.command()
def install_browsers():
    """Download the required browser binaries for headless scraping."""
    ui.print_banner()
    ui.print_header("Installing browser binaries")
    ui.print_tip("This may take a few minutes and requires ~200MB of space.")
    
    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        ui.console.print("\n [success]✓ Browser binaries installed successfully.[/success]\n")
    except subprocess.CalledProcessError:
        ui.print_error("Failed to install browsers. Try running 'pip install playwright' first.")

@app.command()
def refresh():
    """Fetch the latest opportunities from live websites."""
    ui.print_banner()
    ui.print_header("Refreshing live opportunities")
    
    import asyncio
    engine = ScraperEngine()
    new_opps, stats = asyncio.run(engine.run_all())
    
    if not new_opps:
        ui.print_error("Failed to fetch any new opportunities. Check your internet connection.")
        raise typer.Exit(1)
        
    db.save_all(new_opps)
    
    # Show incremental stats
    stats_msg = f"\n [success]✓ Updated database: {stats['new']} new, {stats['unchanged']} unchanged.[/success]\n"
    ui.console.print(stats_msg)
    ui.print_tip("Run `oppcli list` to see the results.")

@app.command()
def categories():
    """List available categories."""
    ui.print_banner()
    ui.print_header("Available categories")
    for cat in db.CATEGORIES:
        style = f"category.{cat}"
        ui.console.print(f"  [{style}]{cat}[/{style}]")
    ui.console.print()

@app.command()
def regions():
    """List available regions."""
    ui.print_banner()
    ui.print_header("Available regions")
    for r in db.REGIONS:
        ui.console.print(f"  [info]{r}[/info]")
    ui.console.print()

if __name__ == "__main__":
    app()
