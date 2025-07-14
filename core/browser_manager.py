# core/browser_manager.py
import logging
from playwright.async_api import Browser, Playwright
from playwright_on_lambda import PlaywrightOnLambda # <-- [UBAH] Impor baru

log = logging.getLogger(__name__)

_browser: Browser | None = None
_playwright_context: PlaywrightOnLambda | None = None

async def init_browser():
    """
    Initializes a browser instance in a serverless context.
    """
    global _browser, _playwright_context
    if _browser is None:
        log.info("Initializing Playwright for serverless environment...")
        
        # [UBAH] Gunakan launcher dari playwright-on-lambda
        _playwright_context = PlaywrightOnLambda()
        await _playwright_context.install() # Ini akan men-download browser jika perlu
        
        _browser = await _playwright_context.launch()
        log.info("🌐 Serverless browser initialized.")

async def get_browser() -> Browser:
    """Gets the initialized browser instance."""
    if _browser is None:
        raise RuntimeError("Browser not initialized.")
    return _browser

async def close_browser():
    """Closes the browser and cleans up resources."""
    global _browser, _playwright_context
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright_context:
        await _playwright_context.close()
        _playwright_context = None
    log.info("Browser resources released.")
