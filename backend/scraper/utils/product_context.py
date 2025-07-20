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
    5. If OpenAI fails, falls back to HTML-based extraction.
    6. Extracts product images.
    7. Parses JSON-LD for schema backup.
    8. Returns:
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
        # Allow lazy-loaded images to load
        await page.wait_for_timeout(int(delay * 1000))

        # 1) Extract full page text for OpenAI
        await page.evaluate("() => document.querySelectorAll('script, style').forEach(e => e.remove())")
        raw_page_text = await page.evaluate("() => document.body.innerText")
        raw_page_text = re.sub(r"\s+", " ", raw_page_text).strip()
        logger.debug(f"Raw page text length: {len(raw_page_text)}")

        # 2) Try OpenAI first (primary method)
        relevant_summary = None
        openai_success = False
        
        try:
            # Limit text size to avoid token limits
            MAX_CHARS = 20000  # Conservative limit
            if len(raw_page_text) > MAX_CHARS:
                logger.warning(f"Text too long ({len(raw_page_text)} chars), truncating to {MAX_CHARS}")
                truncated_text = raw_page_text[:MAX_CHARS]
                # Try to end at sentence boundary
                last_period = truncated_text.rfind('.')
                if last_period > MAX_CHARS * 0.8:
                    truncated_text = truncated_text[:last_period + 1]
                raw_page_text_for_ai = truncated_text
            else:
                raw_page_text_for_ai = raw_page_text

            client = OpenAIClient()
            system_prompt = (
                "You are an expert product summarizer. "
                "Given the text of a product page, extract the main product details "
                "(name, price, description, features, variants, availability) and return "
                "a JSON object: { name, price, description, features[], variants[], availability }. "
                "If the page does not contain specific product information (like site maps, category pages, "
                "or general content), respond with exactly: 'FALLBACK_TO_HTML_EXTRACTION'"
            )
            
            relevant_summary = await asyncio.to_thread(
                client.complete,
                system_prompt,
                raw_page_text_for_ai,
                "gpt-4",
                0,
                1024
            )
            
            # Validate OpenAI response
            if relevant_summary and len(relevant_summary.strip()) > 10:
                # Check for various failure indicators
                failure_indicators = [
                    "does not contain any product details",
                    "not a product page", 
                    "no product details",
                    "not contain.*product",
                    "appears to be.*cookies",
                    "please provide.*valid product",
                    "error",
                    "cannot.*extract",
                    "unable to.*extract",
                    "fallback_to_html_extraction"  # Our specific keyword
                ]
                
                response_lower = relevant_summary.lower()
                is_failure = any(indicator in response_lower for indicator in failure_indicators)
                
                if not is_failure:
                    openai_success = True
                    logger.debug(f"OpenAI success: {len(relevant_summary)} chars")
                else:
                    logger.warning(f"OpenAI detected non-product content: {relevant_summary[:100]}...")
            else:
                logger.warning("OpenAI returned empty or very short response")
                
        except Exception as e:
            logger.warning(f"OpenAI extraction failed: {e}")
            # Try once more with shorter text for token limit errors
            if "context_length_exceeded" in str(e) or "maximum context length" in str(e):
                try:
                    short_text = raw_page_text[:10000]
                    relevant_summary = await asyncio.to_thread(
                        client.complete,
                        system_prompt,
                        short_text,
                        "gpt-4",
                        0,
                        1024
                    )
                    if relevant_summary and len(relevant_summary.strip()) > 10:
                        # Apply same validation as above
                        failure_indicators = [
                            "does not contain any product details",
                            "not a product page", 
                            "no product details",
                            "not contain.*product",
                            "appears to be.*cookies",
                            "please provide.*valid product",
                            "error",
                            "cannot.*extract",
                            "unable to.*extract",
                            "fallback_to_html_extraction"  # Our specific keyword
                        ]
                        
                        response_lower = relevant_summary.lower()
                        is_failure = any(indicator in response_lower for indicator in failure_indicators)
                        
                        if not is_failure:
                            openai_success = True
                            logger.debug(f"OpenAI success (short): {len(relevant_summary)} chars")
                        else:
                            logger.warning(f"OpenAI short text also detected non-product content")
                except Exception as e2:
                    logger.warning(f"OpenAI short text attempt failed: {e2}")

        # 3) Fallback to HTML-based extraction if OpenAI failed
        if not openai_success:
            logger.info("Falling back to original HTML-based extraction")
            try:
                # Use the original HTML extraction approach
                extractor = ProductImageExtractor()
                data = await extractor.extract_product_images(page)
                
                # Extract schema.org Product images from JSON-LD as fallback (original logic)
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
                data['json_ld_schema'] = schema_images
                imgs = data.get('images', {})
                
                # Override main image with first schema.org image if available
                if schema_images:
                    original_main = imgs.get('url_main_image')
                    imgs['url_main_image'] = schema_images[0]
                    other_images = imgs.get('other_images') or []
                    # Preserve original scraped main as alternate
                    if original_main and original_main != schema_images[0] and original_main not in other_images:
                        other_images.insert(0, original_main)
                    # Append remaining schema images
                    for img_url in schema_images[1:]:
                        if img_url not in other_images:
                            other_images.append(img_url)
                    imgs['other_images'] = other_images
                
                await page.close()
                
                # Use the processed imgs (original approach)
                html_ctx = data.get('relevant_html_product_context', '')
                logger.debug(f"ProductContext url_main_image: {imgs.get('url_main_image')}")
                logger.debug(f"ProductContext other_images: {imgs.get('other_images')}")
                
                # Return original format
                return {
                    'relevant_html_product_context': html_ctx,
                    'images': imgs,
                    'json_ld_schema': schema_images
                }
                
            except Exception as e:
                logger.error(f"HTML fallback also failed: {e}")
                relevant_summary = "No content. All techniques failed."

        # 4) Extract images (OpenAI success path)
        extractor = ProductImageExtractor()
        data = await extractor.extract_product_images(page)
        # 5) Extract JSON-LD (using new approach)
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
            "images": data.get("images", {}),
            "json_ld_schema": schema_images
        }


# backward compatibility
async def scrape_product_context(
    url: str,
    headless: bool = True,
    delay: float = 1.0
) -> Dict[str, Any]:
    return await scrapeProductContext(url, headless, delay)