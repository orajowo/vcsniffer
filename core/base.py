# core/base.py
import asyncio
import logging
import time
import os
from abc import ABC, abstractmethod
from typing import Dict, Any

from playwright.async_api import Page
from core.browser_manager import get_browser

log = logging.getLogger(__name__)

try:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(project_root, 'core', 'stealth.js'), 'r') as f:
        STEALTH_SCRIPT = f.read()
    log.info("✅ Skrip stealth.js berhasil dimuat.")
except FileNotFoundError:
    log.warning("⚠️ Skrip stealth.js tidak ditemukan. Menjalankan tanpa mode stealth.")
    STEALTH_SCRIPT = None

class StealthBrowser:
    """An async context manager for a browser page with stealth capabilities."""
    def __init__(self):
        self.context = None
        self.page = None

    async def __aenter__(self):
        try:
            browser = await get_browser()
            self.context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                java_script_enabled=True,
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
            )
            self.page = await self.context.new_page()

            if STEALTH_SCRIPT:
                await self.page.add_init_script(STEALTH_SCRIPT)

            return self
        except asyncio.CancelledError:
            await self.close_all()
            raise
        
    async def __aexit__(self, exc_type, exc, tb):
        await self.close_all()

    async def close_all(self):
        if self.page:
            try:
                await self.page.close()
            except Exception as e:
                log.debug(f"Ignoring error while closing page: {e}")
        
        if self.context:
            try:
                await self.context.close()
            except Exception as e:
                log.debug(f"Ignoring error while closing context: {e}")


class BaseScraperService(ABC):
    """
    Abstract base class for stream scraper services.
    Handles the boilerplate logic for Browse and finding M3U8 requests.
    """
    def __init__(self, request_timeout: int = 30):
        self.log = logging.getLogger(self.__class__.__name__)
        self.request_timeout = request_timeout

    @abstractmethod
    def _is_target_request(self, url: str) -> bool:
        """
        Abstract method to be implemented by subclasses.
        Return True if the request URL is the desired stream URL.
        """
        raise NotImplementedError

    async def _after_navigation(self, page: Page):
        """
        Ini adalah hook untuk melakukan aksi setelah halaman dimuat.
        """
        pass

    async def get_stream(self, target_url: str) -> Dict[str, Any]:
        start_time = time.time()
        self.log.info(f"Starting process for: {target_url}")

        final_url: str | None = None
        m3u8_found = asyncio.Event()

        try:
            # [FIX] Mengembalikan ke pola `async with` yang lebih aman dan standar.
            # __aexit__ akan dipanggil secara otomatis, bahkan jika ada error.
            async with StealthBrowser() as sb:
                page = sb.page

                async def handle_request(request):
                    nonlocal final_url
                    if self._is_target_request(request.url):
                        if not m3u8_found.is_set():
                            self.log.info(f"✅ Target request found: {request.url}")
                            final_url = request.url
                            m3u8_found.set()
                
                page.on("request", handle_request)
                await page.goto(target_url, wait_until="domcontentloaded", timeout=self.request_timeout * 1000)
                await self._after_navigation(page)

                await asyncio.wait_for(m3u8_found.wait(), timeout=self.request_timeout)

        except Exception as e:
            self.log.error(f"❌ Scraping error: {e}", exc_info=True)
            # Tidak perlu blok `finally` untuk menutup sb, `async with` menanganinya.
        
        elapsed = time.time() - start_time
        self.log.info(f"Process finished in {elapsed:.2f} seconds.")

        return {"success": bool(final_url), "url": final_url}