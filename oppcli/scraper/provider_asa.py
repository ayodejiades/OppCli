"""
oppcli/scraper/provider_asa.py — Scraper for After School Africa (Async + Paginated).
"""

import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from oppcli.scraper.base import BaseScraper

class ASAScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "After School Africa"

    async def scrape(self) -> List[Dict[str, Any]]:
        results = []
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            
            for page_num in range(1, 4):
                url = f"https://www.afterschoolafrica.com/category/scholarship/page/{page_num}/"
                if page_num == 1:
                    url = "https://www.afterschoolafrica.com/category/scholarship/"
                    
                try:
                    response = await client.get(url, headers=headers)
                    if response.status_code != 200: break
                except Exception:
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                items = soup.select(".gb-query-loop-item")
                
                for item in items:
                    title_tag = item.select_one(".gb-headline a")
                    if not title_tag: continue
                    
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get("href")
                    
                    results.append({
                        "title": title,
                        "org": "After School Africa",
                        "category": "Scholarship",
                        "region": "Pan-Africa",
                        "deadline": datetime.now().strftime("%Y-10-15"),
                        "link": link,
                        "description": f"Educational opportunity from After School Africa.",
                        "stipend": True,
                        "tags": ["scholarship", "africa", "education"]
                    })
            
        return results
