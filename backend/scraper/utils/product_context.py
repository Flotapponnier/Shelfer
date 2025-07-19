"""
Product Context Extraction Utility

Provides a function to scrape the main product image context from a product page,
returning HTML snippet and image URLs in a simplified format.
"""
import logging
import json
from .json_ld_extraction_utils import JSONLDExtractor
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
        # Extract schema.org Product images from JSON-LD as fallback
        schema_images = []
        try:
            jsonld_extractor = JSONLDExtractor(delay=delay)
            jsonld_scripts = await jsonld_extractor.extract_jsonld_from_page(page)
            for text in jsonld_scripts:
                if not text:
                    continue
                try:
                    parsed = json.loads(text)
                except Exception:
                    continue
                json_objs = parsed if isinstance(parsed, list) else [parsed]
                # Flatten @graph entries
                for obj in list(json_objs):
                    if isinstance(obj, dict) and '@graph' in obj and isinstance(obj['@graph'], list):
                        json_objs.extend(obj['@graph'])
                for obj in json_objs:
                    if not isinstance(obj, dict):
                        continue
                    types = obj.get('@type') or obj.get('type')
                    types_list = [types] if isinstance(types, str) else types if isinstance(types, list) else []
                    if any(isinstance(t, str) and t.lower() == 'product' for t in types_list):
                        image_prop = obj.get('image')
                        if isinstance(image_prop, str):
                            schema_images.append(image_prop)
                        elif isinstance(image_prop, list):
                            for item in image_prop:
                                if isinstance(item, str):
                                    schema_images.append(item)
                                elif isinstance(item, dict) and isinstance(item.get('url'), str):
                                    schema_images.append(item['url'])
                        elif isinstance(image_prop, dict) and isinstance(image_prop.get('url'), str):
                            schema_images.append(image_prop['url'])
        except Exception:
            schema_images = []
        # Deduplicate schema images
        schema_images = list(dict.fromkeys(schema_images))
        data['schema.org'] = schema_images
        imgs = data.get('images', {})
        # Override main image with first schema.org image if available
        if schema_images:
            original_main = imgs.get('urlMainimage')
            imgs['urlMainimage'] = schema_images[0]
            other_images = imgs.get('otherMainImages') or []
            # Preserve original scraped main as alternate
            if original_main and original_main != schema_images[0] and original_main not in other_images:
                other_images.insert(0, original_main)
            # Append remaining schema images
            for img_url in schema_images[1:]:
                if img_url not in other_images:
                    other_images.append(img_url)
            imgs['otherMainImages'] = other_images
        await page.close()
        imgs = data.get('images', {})
        html_ctx = data.get('relevantHtmlProductContext', '')
        # Log for backend visibility
        logger.debug(f"ProductContext urlMainimage: {imgs.get('urlMainimage')}")
        logger.debug(f"ProductContext otherMainImages: {imgs.get('otherMainImages')}")
        # Return scraped product context
        return {
            'relevantHtmlProductContext': html_ctx,
            'images': imgs,
            'schema.org': schema_images
        }