"""
oppcli/scraper/headless.py — Base class for scrapers that require a browser.
"""

from typing import List, Dict, Any
from abc import abstractmethod
from playwright.async_api import async_playwright
from oppcli.scraper.base import BaseScraper

class HeadlessScraper(BaseScraper):
    @abstractmethod
    async def scrape_with_page(self, page) -> List[Dict[str, Any]]:
        """Implementation that uses the provided Playwright page object."""
        pass

    async def scrape(self) -> List[Dict[str, Any]]:
        """Standard entry point that manages the Playwright lifecycle."""
        async with async_playwright() as p:
            # We use chromium by default as it's the fastest
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                results = await self.scrape_with_page(page)
                return results
            finally:
                await browser.close()
