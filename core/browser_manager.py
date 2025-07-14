import logging
from playwright.async_api import async_playwright, Browser, Playwright

log = logging.getLogger(__name__)

# Variabel ini akan dikelola per pemanggilan fungsi di lingkungan serverless
_pw: Playwright | None = None
_browser: Browser | None = None

async def init_browser():
    """
    Menginisialisasi browser Playwright standar di lingkungan Vercel.
    """
    global _browser, _pw
    if _browser is None:
        log.info("Initializing Playwright browser in Vercel environment...")
        
        # Mulai instance Playwright standar
        _pw = await async_playwright().start()
        
        # Luncurkan Chromium. Vercel sangat mengoptimalkan lingkungannya untuk ini.
        # Tidak perlu argumen khusus karena Vercel sudah menyiapkannya.
        _browser = await _pw.chromium.launch()
        
        log.info("🌐 Vercel Playwright browser initialized.")

async def get_browser() -> Browser:
    """Mengambil instance browser yang sudah diinisialisasi."""
    if _browser is None:
        raise RuntimeError("Browser not initialized.")
    return _browser

async def close_browser():
    """Menutup browser dan menghentikan Playwright dengan aman."""
    global _browser, _pw
    if _browser:
        await _browser.close()
        _browser = None
    if _pw:
        await _pw.stop()
        _pw = None
    log.info("Browser resources released.")
