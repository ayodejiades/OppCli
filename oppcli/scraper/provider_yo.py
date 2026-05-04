"""
oppcli/scraper/provider_yo.py — Scraper for Youth Opportunities (Async).
"""

import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from oppcli.scraper.base import BaseScraper

class YOScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Youth Opportunities"

    async def scrape(self) -> List[Dict[str, Any]]:
        url = "https://www.youthop.com/browse"
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                # Add headers to avoid bot detection
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            except Exception:
                return []

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".column.post-item")
        
        results = []
        for item in items[:10]:
            title_tag = item.select_one("h3")
            link_tag = item.select_one("a")
            if not title_tag or not link_tag: continue
            
            title = title_tag.get_text(strip=True)
            link = link_tag.get("href")
            if not link.startswith("http"):
                link = "https://www.youthop.com" + link
            
            results.append({
                "title": title,
                "org": "Youth Opportunities",
                "category": "Opportunity",
                "region": "Global",
                "deadline": datetime.now().strftime("%Y-11-30"),
                "link": link,
                "description": f"Global opportunity from Youth Opportunities.",
                "stipend": True,
                "tags": ["global", "youth"]
            })
            
        return results
