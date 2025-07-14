# service/beesports.py
from core.base import BaseScraperService

class BeesportsService(BaseScraperService):
    """Scraper service for beesports.net"""
    def __init__(self):
        super().__init__(request_timeout=15)

    def _is_target_request(self, url: str) -> bool:
        """Identifies the M3U8 stream URL."""
        return ".m3u8" in url