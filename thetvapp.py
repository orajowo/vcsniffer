# service/thetvapp.py
from playwright.async_api import Page
from core.base import BaseScraperService

class ThetvappService(BaseScraperService):
    """Scraper service for thetvapp."""
    def __init__(self):
        super().__init__(request_timeout=25)

    def _is_target_request(self, url: str) -> bool:
        """Identifies the specific M3U8 stream URL with tokens."""
        is_m3u8 = ".m3u8" in url
        has_token = "token=" in url and "expires=" in url
        has_specific_path = "tracks-v1a1/mono.m3u8" in url
        return is_m3u8 and (has_token or has_specific_path)

    async def _after_navigation(self, page: Page):
        """Tries to click stream load buttons after page navigation."""
        buttons_to_try = ["text=Load HD Stream", "text=Load SD Stream"]
        for selector in buttons_to_try:
            try:
                self.log.info(f"Attempting to click '{selector}'...")
                await page.click(selector, timeout=5000)
                self.log.info(f"Successfully clicked '{selector}'.")
                break 
            except Exception:
                self.log.warning(f"Could not find or click '{selector}'.")