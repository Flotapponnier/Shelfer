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
    
    # Helper function for detailed JSON-LD debugging
    async def debug_jsonld_extraction(page, path_name: str):
        """Debug JSON-LD extraction step by step with enhanced timing for dynamic content."""
        logger.info(f"🔍 DEBUG: Starting JSON-LD extraction for {path_name}")
        
        # Step 0: Enhanced waiting for dynamic content
        logger.info(f"⏳ DEBUG: Waiting for dynamic content to load...")
        
        # Wait for network to be idle (important for dynamic content)
        try:
            await page.wait_for_load_state('networkidle', timeout=10000)
            logger.info(f"✅ DEBUG: Network is idle")
        except Exception as e:
            logger.warning(f"⚠️ DEBUG: Network idle timeout: {e}")
        
        # Additional wait for JavaScript to execute
        await page.wait_for_timeout(3000)  # 3 seconds for JS execution
        
        # Try to wait specifically for JSON-LD scripts to appear (without visibility requirement)
        try:
            await page.wait_for_selector('script[type="application/ld+json"]', state='attached', timeout=5000)
            logger.info(f"✅ DEBUG: JSON-LD script tag appeared!")
        except Exception as e:
            logger.warning(f"⚠️ DEBUG: No JSON-LD script tag appeared within 5s: {e}")
        
        # Step 1: Extract raw scripts
        try:
            jsonld_extractor = JSONLDExtractor(delay=delay)
            jsonld_scripts = await jsonld_extractor.extract_jsonld_from_page(page)
            logger.info(f"📄 DEBUG Step 1 ({path_name}): Found {len(jsonld_scripts)} JSON-LD script tags")
            
            # Log each script
            for i, script in enumerate(jsonld_scripts):
                script_preview = script[:200] if script else "EMPTY"
                logger.info(f"   Script {i+1}: {len(script)} chars - {script_preview}...")
            
            if not jsonld_scripts:
                logger.warning(f"🚨 DEBUG: No JSON-LD scripts found on page")
                # Try one more time with longer wait
                logger.info(f"🔄 DEBUG: Trying one more time with longer wait...")
                await page.wait_for_timeout(5000)  # Wait 5 more seconds
                jsonld_scripts = await jsonld_extractor.extract_jsonld_from_page(page)
                logger.info(f"📄 DEBUG Step 1 RETRY ({path_name}): Found {len(jsonld_scripts)} JSON-LD script tags")
                
                if not jsonld_scripts:
                    return []
            
        except Exception as e:
            logger.error(f"❌ DEBUG Step 1 ({path_name}): Script extraction failed: {e}")
            return []
        
        # Step 2: Parse scripts
        try:
            parsed = parse_json_ld_scripts(jsonld_scripts)
            logger.info(f"🔧 DEBUG Step 2 ({path_name}): Parsed {len(parsed)} JSON-LD objects")
            
            # Log each parsed object
            for i, obj in enumerate(parsed):
                obj_type = obj.get('@type', 'NO_TYPE')
                obj_keys = list(obj.keys())[:5]  # First 5 keys
                logger.info(f"   Object {i+1}: @type='{obj_type}', keys={obj_keys}")
            
            if not parsed:
                logger.warning(f"🚨 DEBUG: Scripts found but parsing returned no objects")
                return []
                
        except Exception as e:
            logger.error(f"❌ DEBUG Step 2 ({path_name}): JSON parsing failed: {e}")
            return []
        
        # Step 3: Filter for products
        try:
            schema_objects = [o for o in parsed if _is_product_schema(o)]
            logger.info(f"🎯 DEBUG Step 3 ({path_name}): Found {len(schema_objects)} product schemas")
            
            # Log filtering results
            for i, obj in enumerate(parsed):
                obj_type = obj.get('@type', 'NO_TYPE')
                is_product = _is_product_schema(obj)
                has_offers = 'offers' in obj
                has_sku = 'sku' in obj
                has_name = 'name' in obj
                logger.info(f"   Object {i+1}: @type='{obj_type}', is_product={is_product}, offers={has_offers}, sku={has_sku}, name={has_name}")
            
            if not schema_objects and parsed:
                logger.warning(f"🚨 DEBUG: Objects found but none matched product schema criteria")
                logger.info(f"   Available @types: {[obj.get('@type', 'NO_TYPE') for obj in parsed]}")
            
            return schema_objects
            
        except Exception as e:
            logger.error(f"❌ DEBUG Step 3 ({path_name}): Product filtering failed: {e}")
            return []
    
    async with BrowserManager(headless=headless) as browser_manager:
        page = await browser_manager.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        # Allow lazy-loaded images to load
        await page.wait_for_timeout(int(delay * 1000))

        # 1) Extract full page text for OpenAI (preserve JSON-LD scripts)
        await page.evaluate("""() => {
            // Remove all scripts EXCEPT JSON-LD scripts
            document.querySelectorAll('script:not([type="application/ld+json"])').forEach(e => e.remove());
            // Remove style tags
            document.querySelectorAll('style').forEach(e => e.remove());
        }""")
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
                
                # Extract JSON-LD schemas (using robust debugging)
                schema_objects = await debug_jsonld_extraction(page, "HTML_FALLBACK")
                
                # Extract image URLs from schema objects for image processing
                schema_images = []
                for obj in schema_objects:
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
                
                # Deduplicate schema images
                schema_images = list(dict.fromkeys(schema_images))
                
                # Store full schema objects (consistent with OpenAI path)
                data['json_ld_schema'] = schema_objects
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
                
                # Return format consistent with OpenAI path
                return {
                    'relevant_html_product_context': html_ctx,
                    'images': imgs,
                    'json_ld_schema': schema_objects
                }
                
            except Exception as e:
                logger.error(f"HTML fallback also failed: {e}")
                relevant_summary = "No content. All techniques failed."

        # 4) Extract images (OpenAI success path)
        extractor = ProductImageExtractor()
        data = await extractor.extract_product_images(page)
        # 5) Extract JSON-LD (using robust debugging)
        schema_objects = await debug_jsonld_extraction(page, "OPENAI_SUCCESS")

        await page.close()

        return {
            "raw_page_text": raw_page_text,
            "relevant_html_product_context": relevant_summary,
            "images": data.get("images", {}),
            "json_ld_schema": schema_objects
        }


# backward compatibility
async def scrape_product_context(
    url: str,
    headless: bool = True,
    delay: float = 1.0
) -> Dict[str, Any]:
    return await scrapeProductContext(url, headless, delay)