"""
oppcli/scraper/base.py — Base class for all opportunity scrapers.
"""

from typing import List, Dict, Any
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The display name of the scraper/provider."""
        pass

    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Runs the scraper asynchronously and returns a list of opportunity dictionaries.
        """
        pass
