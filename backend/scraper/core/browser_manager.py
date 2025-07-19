import os
import random
import shutil
import tempfile
from typing import List, Optional
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
from ..utils.utils import take_error_screenshot
import logging

logger = logging.getLogger(__name__)

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
]


class ScreenshotPage:
    """Wrapper around Playwright Page that automatically takes screenshots on errors."""
    
    def __init__(self, page: Page, browser_manager: 'BrowserManager'):
        self._page = page
        self._browser_manager = browser_manager
        self._current_url = None
        self._screenshot_taken = False
    
    def __getattr__(self, name):
        """Delegate all other attributes to the underlying page."""
        return getattr(self._page, name)
    
    async def goto(self, url: str, **kwargs):
        """Override goto to track the current URL for screenshot purposes."""
        self._current_url = url
        try:
            return await self._page.goto(url, **kwargs)
        except Exception as e:
            await self._take_screenshot_if_needed("navigation_error")
            raise
    
    async def close(self):
        """Override close to take screenshot if page is being closed due to an error."""
        try:
            if not self._screenshot_taken and self._current_url:
                await self._take_screenshot_if_needed("page_closed")
            await self._page.close()
        except Exception as e:
            # If we can't close normally, still try to take a screenshot
            if not self._screenshot_taken and self._current_url:
                await self._take_screenshot_if_needed("page_close_error")
            raise
    
    async def _take_screenshot_if_needed(self, error_type: str):
        """Take a screenshot if not already taken and screenshot is enabled."""
        if not self._screenshot_taken and self._current_url:
            try:
                await take_error_screenshot(self._page, self._current_url, error_type)
                self._screenshot_taken = True
            except Exception as e:
                logger.debug(f"Failed to take screenshot: {e}")


class BrowserManager:
    """Manages the Playwright browser lifecycle, including setup, configuration, and cleanup."""

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.user_data_dir = tempfile.mkdtemp(prefix="playwright_")

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._active_pages: List[ScreenshotPage] = []

    async def __aenter__(self):
        """Initializes the browser context using the async context manager."""
        self.playwright = await async_playwright().start()
        await self._launch_context()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleans up all browser resources with screenshot capture on errors."""
        # Take screenshots of all active pages if there was an exception
        if exc_type is not None:
            logger.info(f"Browser manager exiting due to exception: {exc_type.__name__}: {exc_val}")
            await self._take_screenshots_of_all_pages("browser_manager_exit")
        
        try:
            if self.context:
                await self.context.close()
        except Exception as e:
            logger.warning(f"Error closing context: {e}")
            await self._take_screenshots_of_all_pages("context_close_error")
        
        try:
            if self.browser and self.browser.is_connected():
                await self.browser.close()
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
        
        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error stopping playwright: {e}")
        
        if os.path.exists(self.user_data_dir):
            try:
                shutil.rmtree(self.user_data_dir)
                logger.info(f"Cleaned up temporary user data directory: {self.user_data_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up user data directory {self.user_data_dir}: {e}")

    async def _take_screenshots_of_all_pages(self, error_type: str):
        """Take screenshots of all active pages when an error occurs."""
        for screenshot_page in self._active_pages[:]:  # Copy list to avoid modification during iteration
            try:
                if screenshot_page._current_url and not screenshot_page._screenshot_taken:
                    await take_error_screenshot(screenshot_page._page, screenshot_page._current_url, error_type)
                    screenshot_page._screenshot_taken = True
            except Exception as e:
                logger.debug(f"Failed to take screenshot of page {screenshot_page._current_url}: {e}")

    async def _launch_context(self):
        """Launches the browser context with appropriate arguments and fallbacks."""
        launch_args = self._get_browser_launch_args()

        try:
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                args=launch_args,
                timeout=self.timeout
            )
            logger.info("Launched persistent browser context.")
        except Exception as e:
            logger.warning(f"Failed to launch with persistent context: {e}. Falling back to regular browser launch.")
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=launch_args,
                timeout=self.timeout
            )
            self.context = await self.browser.new_context()

    def _get_browser_launch_args(self) -> List[str]:
        """Returns a list of arguments for launching the browser."""
        args = [
            '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
            '--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding', '--disable-features=TranslateUI,BlinkGenPropertyTrees',
            '--disable-ipc-flooding-protection', '--disable-hang-monitor',
            '--disable-prompt-on-repost', '--disable-background-networking', '--disable-sync',
            '--disable-default-apps', '--no-first-run', '--no-default-browser-check',
            '--disable-component-update', '--disable-breakpad', '--disable-client-side-phishing-detection',
            '--disable-field-trial-config', '--enable-features=NetworkService,NetworkServiceInProcess',
            '--force-color-profile=srgb', '--metrics-recording-only', '--enable-automation',
            '--password-store=basic', '--use-mock-keychain', '--no-service-autorun',
            '--export-tagged-pdf', '--disable-search-engine-choice-screen',
            '--enable-use-zoom-for-dsf=false'
        ]
        return args
    
    async def new_page(self) -> ScreenshotPage:
        """Creates and returns a new page with screenshot capabilities and a random user agent."""
        try:
            page = await self.context.new_page()
            user_agent = random.choice(USER_AGENTS)
            await page.set_extra_http_headers({'User-Agent': user_agent})
            
            # Wrap the page with screenshot capabilities
            screenshot_page = ScreenshotPage(page, self)
            self._active_pages.append(screenshot_page)
            return screenshot_page
            
        except Exception as e:
            logger.error(f"Failed to create new page: {e}")
            # Take screenshots of existing pages if context is closed
            await self._take_screenshots_of_all_pages("new_page_error")
            raise

