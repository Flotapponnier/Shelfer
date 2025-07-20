"""
Product Context Extraction Utility

Fetches page text and uses OpenAI to summarize the main product.
"""
import logging
import re
import asyncio
from typing import Dict, Any, List

from ..core.browser_manager import BrowserManager
from .image_extractor import ProductImageExtractor
from .json_ld_extraction_utils import JSONLDExtractor
from openai_client import OpenAIClient

logger = logging.getLogger(__name__)

async def scrapeProductContext(url: str, headless: bool = True, delay: float = 1.0) -> Dict[str, Any]:
    """
    Scrape a product page, get its text, and use an LLM to summarize the main product info.
    Returns the raw text, LLM summary, images, and JSON-LD schema.
    """
    async with BrowserManager(headless=headless) as browser_manager:
        page = await browser_manager.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(int(delay * 1000))

        # Remove scripts/styles and get full page text
        raw_page_text = await page.evaluate(
            """() => { document.querySelectorAll('script, style').forEach(e => e.remove()); return document.body.innerText; }"""
        )
        # Collapse whitespace
        raw_page_text = re.sub(r"\s+", " ", raw_page_text).strip()
        logger.debug(f"Raw page text length: {len(raw_page_text)}")
        logger.debug(f"Raw page text snippet: {raw_page_text[:300]}")

        # Call LLM to summarize product
        client = OpenAIClient()
        system_prompt = (
            "You are an expert product summarizer. You receive the full text of a webpage. "
            "Extract and summarize the main product details: name, price, description, features, variants, availability. "
            "Return as a JSON object with keys: name, price, description, features (array of strings), variants (array), availability."
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

        # Extract images and JSON-LD data
        image_extractor = ProductImageExtractor()
        images_data = await image_extractor.extract_product_images(page)
        schema_data = []
        try:
            jsonld_scripts = await JSONLDExtractor().extract_jsonld_from_page(page)
            from ..core.jsonld_parser import parse_json_ld_scripts
            parsed = parse_json_ld_scripts(jsonld_scripts)
            schema_data = [o for o in parsed if '@type' in o]
        except Exception as e:
            logger.warning(f"JSON-LD parse failed: {e}")

        await page.close()
        return {
            'raw_page_text': raw_page_text,
            'relevant_html_product_context': relevant_summary,
            'images': images_data.get('images', {}),
            'json_ld_schema': schema_data
        }

# Backward compatibility
async def scrape_product_context(url: str, headless: bool = True, delay: float = 1.0) -> Dict[str, Any]:
    return await scrapeProductContext(url, headless, delay)