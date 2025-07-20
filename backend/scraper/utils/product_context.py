"""
Product Context Extraction Utility

Fetches page text and uses OpenAI to summarize the main product info,
returning the raw text, a JSON summary, images, and JSON-LD schemas.
"""
import logging
import json
import asyncio
import re
from typing import Dict, Any, List

from ..core.browser_manager import BrowserManager
from .image_extractor import ProductImageExtractor
from .json_ld_extraction_utils import JSONLDExtractor
from ..core.jsonld_parser import parse_json_ld_scripts, _is_product_schema
from openai_client import OpenAIClient

logger = logging.getLogger(__name__)

async def scrapeProductContext(
    url: str,
    headless: bool = True,
    delay: float = 1.0
) -> Dict[str, Any]:
    """
    1. Loads the page (Playwright).
    2. Strips <script>/<style> and captures body text.
    3. Collapses whitespace.
    4. Sends to OpenAI (gpt-4) to extract a JSON summary:
       { name, price, description, features[], variants[], availability }
    5. Extracts product images.
    6. Parses JSON-LD for schema backup.
    7. Returns:
       {
         "raw_page_text":   str,
         "relevant_html_product_context":   str (JSON summary),
         "images":         { url_main_image, other_images[] },
         "json_ld_schema": [ parsed JSON-LD objects ]
       }
    """
    async with BrowserManager(headless=headless) as browser_manager:
        page = await browser_manager.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(int(delay * 1000))

        # 1) Extract full page text
        await page.evaluate("() => document.querySelectorAll('script, style').forEach(e => e.remove())")
        raw_page_text = await page.evaluate("() => document.body.innerText")
        raw_page_text = re.sub(r"\s+", " ", raw_page_text).strip()
        logger.debug(f"Raw page text length: {len(raw_page_text)}")
        logger.debug(f"Raw page text snippet: {raw_page_text[:300]}")

        # 2) Call OpenAI to summarize main product
        client = OpenAIClient()
        system_prompt = (
            "You are an expert product summarizer. "
            "Given the full text of a product page, extract the main product details "
            "(name, price, description, features, variants, availability) and return "
            "a JSON object: { name, price, description, features[], variants[], availability }."
        )
        relevant_summary = await asyncio.to_thread(
            client.complete,
            system_prompt,
            raw_page_text,
            "gpt-4",
            0,
            1024
        )
        logger.debug(f"LLM summary length: {len(relevant_summary)}")

        # 3) Extract images
        images_data = await ProductImageExtractor().extract_product_images(page)

        # 4) Extract JSON-LD
        schema_images = []
        try:
            jsonld_scripts = await JSONLDExtractor().extract_jsonld_from_page(page)
            parsed = parse_json_ld_scripts(jsonld_scripts)
            schema_images = [o for o in parsed if _is_product_schema(o)]
        except Exception as e:
            logger.warning(f"JSON-LD parse failed: {e}")

        await page.close()

        return {
            "raw_page_text": raw_page_text,
            "relevant_html_product_context": relevant_summary,
            "images": images_data.get("images", {}),
            "json_ld_schema": schema_images
        }

# backward compatibility
async def scrape_product_context(
    url: str,
    headless: bool = True,
    delay: float = 1.0
) -> Dict[str, Any]:
    return await scrapeProductContext(url, headless, delay)