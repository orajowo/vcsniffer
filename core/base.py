import asyncio
import logging
import time
import os
from abc import ABC, abstractmethod
from typing import Dict, Any

from playwright.async_api import Page
from .browser_manager import get_browser

log = logging.getLogger(__name__)

try:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(project_root, 'stealth.js'), 'r', encoding='utf-8') as f:
        STEALTH_SCRIPT = f.read()
except FileNotFoundError:
    log.warning("⚠️ Skrip stealth.js tidak ditemukan.")
    STEALTH_SCRIPT = None

class StealthBrowser:
    def __init__(self):
        self.context = None
        self.page = None

    async def __aenter__(self):
        browser = await get_browser()
        self.context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()
        if STEALTH_SCRIPT:
            await self.page.add_init_script(STEALTH_SCRIPT)
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        if self.page:
            try: await self.page.close()
            except Exception: pass
        if self.context:
            try: await self.context.close()
            except Exception: pass

class BaseScraperService(ABC):
    def __init__(self, request_timeout: int = 45):
        self.log = logging.getLogger(self.__class__.__name__)
        self.request_timeout = request_timeout

    @abstractmethod
    def _is_target_request(self, url: str) -> bool:
        raise NotImplementedError

    async def _after_navigation(self, page: Page):
        pass

    async def get_stream(self, target_url: str) -> Dict[str, Any]:
        final_url: str | None = None
        m3u8_found = asyncio.Event()

        try:
            async with StealthBrowser() as sb:
                page = sb.page
                async def handle_request(request):
                    nonlocal final_url
                    if self._is_target_request(request.url) and not m3u8_found.is_set():
                        final_url = request.url
                        m3u8_found.set()
                
                page.on("request", handle_request)
                await page.goto(target_url, wait_until="domcontentloaded", timeout=self.request_timeout * 1000)
                await self._after_navigation(page)
                await asyncio.wait_for(m3u8_found.wait(), timeout=self.request_timeout)
        except Exception as e:
            log.error(f"❌ Scraping error: {e}", exc_info=True)
        
        return {"success": bool(final_url), "url": final_url}
