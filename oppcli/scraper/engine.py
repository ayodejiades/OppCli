"""
oppcli/scraper/engine.py — Async coordinator with Incremental Refresh support.
"""

import asyncio
from typing import List, Dict, Any, Tuple
from rich.progress import Progress, SpinnerColumn, TextColumn

from oppcli.scraper.base import BaseScraper
from oppcli.scraper.provider_ofa import OFAScraper
from oppcli.scraper.provider_yo import YOScraper
from oppcli.scraper.provider_asa import ASAScraper
from oppcli import data_manager as db

class ScraperEngine:
    def __init__(self):
        self.scrapers: List[BaseScraper] = [
            OFAScraper(),
            YOScraper(),
            ASAScraper(),
        ]

    async def run_all(self) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Runs all scrapers and merges results with existing data incrementally.
        Returns (all_opportunities, stats).
        """
        scraped_opps = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            tasks = []
            for scraper in self.scrapers:
                task_id = progress.add_task(description=f"Scraping {scraper.name}...", total=None)
                tasks.append(self._run_scraper(scraper, progress, task_id))
            
            results_lists = await asyncio.gather(*tasks)
            for r_list in results_lists:
                scraped_opps.extend(r_list)

        # Incremental Merge Logic
        existing_opps = db.get_all()
        existing_map = {o.get("fingerprint") or db.calculate_fingerprint(o): o for o in existing_opps}
        
        final_list = []
        new_count = 0
        updated_count = 0
        unchanged_count = 0
        
        for opp in scraped_opps:
            fp = db.calculate_fingerprint(opp)
            opp["fingerprint"] = fp
            
            if fp in existing_map:
                unchanged_count += 1
            else:
                new_count += 1
            
            final_list.append(opp)

        # Sort by deadline urgency before assigning IDs for a cleaner list view
        from oppcli.data_manager import _enrich
        enriched = [_enrich(o) for o in final_list]
        enriched.sort(key=lambda o: o["days_left"] if o["days_left"] is not None else 9999)

        # Assign sequential IDs based on the sorted order
        for i, opp in enumerate(enriched, 1):
            opp["id"] = i

        stats = {
            "new": new_count,
            "unchanged": unchanged_count,
            "total": len(enriched)
        }
        
        return enriched, stats

    async def _run_scraper(self, scraper: BaseScraper, progress: Progress, task_id: int) -> List[Dict[str, Any]]:
        try:
            results = await scraper.scrape()
            progress.update(task_id, description=f"[green]✓ Finished {scraper.name}[/green]")
            return results
        except Exception as e:
            progress.update(task_id, description=f"[red]✗ Failed {scraper.name}: {str(e)}[/red]")
            return []
