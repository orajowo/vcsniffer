# service/fstv.py
from playwright.async_api import Page
from core.base import BaseScraperService

class FstvService(BaseScraperService):
    """Scraper service for fstv.lol."""
    def __init__(self):
        super().__init__(request_timeout=15)

    def _is_target_request(self, url: str) -> bool:
        """Identifies the M3U8 stream URL."""
        return ".m3u8" in url

    # [TAMBAHAN] Override metode _after_navigation untuk menekan tombol keyboard.
    async def _after_navigation(self, page: Page):
        """
        Setelah navigasi selesai, coba tekan tombol 'Spasi' untuk
        memicu pemutaran video jika tidak dimulai secara otomatis.
        """
        self.log.info("Mencoba menekan 'Space' untuk memulai pemutaran video...")
        try:
            # Beri jeda sesaat agar semua elemen halaman siap
            #await page.wait_for_timeout(2000)
            
            # Fokus pada elemen body untuk memastikan halaman menerima input keyboard
            await page.locator('body').focus()
            
            # Tekan tombol Spasi
            await page.keyboard.press('Space')
            
            self.log.info("✅ Berhasil menekan 'Space'.")
        except Exception as e:
            self.log.warning(f"⚠️ Gagal menekan 'Space': {e}")