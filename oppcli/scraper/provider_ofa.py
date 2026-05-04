"""
oppcli/scraper/provider_ofa.py — Scraper for Opportunities For Africans (Async + Paginated).
"""

import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from oppcli.scraper.base import BaseScraper

class OFAScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Opportunities For Africans"

    async def scrape(self) -> List[Dict[str, Any]]:
        results = []
        # Fetch first 3 pages to get more results
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            for page_num in range(1, 4):
                url = f"https://www.opportunitiesforafricans.com/category/fellowships/page/{page_num}/"
                if page_num == 1:
                    url = "https://www.opportunitiesforafricans.com/category/fellowships/"
                    
                try:
                    response = await client.get(url)
                    if response.status_code != 200: break
                except Exception:
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                articles = soup.select("article")
                
                for art in articles:
                    title_tag = art.select_one(".entry-title a")
                    if not title_tag: continue
                    
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get("href")
                    
                    category = "Fellowship" 
                    if "Scholarship" in title: category = "Scholarship"
                    elif "Internship" in title: category = "Internship"
                    
                    results.append({
                        "title": title,
                        "org": "OFA",
                        "category": category,
                        "region": "Pan-Africa",
                        "deadline": datetime.now().strftime("%Y-12-31"),
                        "link": link,
                        "description": f"Latest {category} from Opportunities For Africans.",
                        "stipend": True,
                        "tags": ["latest", "scraped", "africa"]
                    })
            
        return results
