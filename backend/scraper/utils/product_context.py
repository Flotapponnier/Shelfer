"""
Product Context Extraction Utility

Provides a function to scrape the main product image context from a product page,
returning HTML snippet and image URLs in a simplified format.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def scrape_product_context(url: str, headless: bool = True, delay: float = 1.0) -> Dict[str, Any]:
    """
    Scrape a product page and return its image URLs based on URL slug matching.
    """
    # Lazy import browser and extractor
    from ..core.browser_manager import BrowserManager
    from .image_extractor import ProductImageExtractor
    async with BrowserManager(headless=headless) as browser_manager:
        page = await browser_manager.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        # Allow lazy-loaded images to load
        await page.wait_for_timeout(int(delay * 1000))
        extractor = ProductImageExtractor()
        data = await extractor.extract_product_images(page)
        await page.close()
        imgs = data.get('images', {})
        html_ctx = data.get('relevantHtmlProductContext', '')
        # Log for backend visibility
        print(f"[ProductContext] urlMainimage: {imgs.get('urlMainimage')}")
        print(f"[ProductContext] otherMainImages: {imgs.get('otherMainImages')}")
        # Return scraped product context
        return {
            'relevantHtmlProductContext': html_ctx,
            'images': imgs,
            'schema.org': None
        }