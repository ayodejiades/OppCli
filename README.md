# OppCli

> A premium command-line opportunity finder for African students — scholarships, fellowships, hackathons, and grants, all accessible directly from your terminal.

## The Problem

Thousands of funding opportunities exist for African students, but they are scattered across hundreds of websites. Students often miss deadlines and life-changing chances simply because the information is fragmented.

`OppCli` centralizes these opportunities into a single, high-fidelity terminal interface, allowing you to search, filter, and export results with ease. Now featuring **v2 improvements** like Incremental Refresh and Headless Scraping.

## v2 Features 🚀
- 🚀 **Incremental Refresh**: Blazing fast updates using SHA-256 fingerprinting to only process new content.
- 🌐 **Headless Scraping**: Powered by **Playwright** to extract data from complex, JavaScript-heavy websites.
- 🧵 **Parallel Execution**: All scrapers run concurrently using `asyncio` for maximum speed.

`OppCli` now features a modern, professional terminal UI powered by `Rich` and `Typer`, providing:
- **Vibrant, themed output** for better readability.
- **Responsive tables** that adapt to your terminal size.
- **Lightning-fast subcommands** and auto-generated help.
- **Standardized installation** as a global tool.

## Installation

`OppCli` is now a standard Python package.

```bash
# Clone the repository
git clone https://github.com/yourusername/oppcli
cd OppCli

# Install the package and dependencies
pip install .
```

After installation, you can run the tool simply by typing `oppcli` in your terminal.

## Usage

### Commands

| Command | Description |
|---|---|
| `oppcli list` | List all active opportunities, sorted by deadline |
| `oppcli search <keyword>` | Full-text search across title, description, org, and tags |
| `oppcli filter` | Filter by category, region, or funding |
| `oppcli show <ID>` | Full detail view for a single opportunity |
| `oppcli refresh` | Fetch latest opportunities (incremental) |
| `oppcli install-browsers` | Setup headless scraping binaries |
| `oppcli export` | Export current results to CSV or JSON |
| `oppcli categories` | List all available categories |
| `oppcli regions` | List all available regions |

### Examples

```bash
# List everything active
oppcli list

# Refresh with live data
oppcli refresh

# Include expired opportunities
oppcli list --all

# Search by keyword
oppcli search "AI"

# Filter funded fellowships only
oppcli filter -c Fellowship -f

# Filter by region
oppcli filter -r "West Africa"

# View full detail on opportunity #3
oppcli show 3

# Export to CSV
oppcli export --format csv

# Export filtered results to a specific path
oppcli export --format json -c Fellowship --output ~/fellowships.json
```

## Why This Exists

Built for African students to ensure no one misses a life-changing opportunity because information was buried.

---

MIT License