import logging
import json
import base64
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse
import aiohttp
from io import BytesIO
from PIL import Image

from openai_client import AsyncOpenAIClient
from schemas.product import ScraperInput, HtmlContext
from prompts.image_extraction import (
    IMAGE_EXTRACTION_SYSTEM_PROMPT,
    IMAGE_EXTRACTION_USER_PROMPT_TEMPLATE,
    IMAGE_EXTRACTABLE_PROPERTIES,
    IMAGE_FALLBACK_SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)

class ImageExtractorService:
    """
    Service that extracts schema.org properties from product images using GPT-4o vision model.
    Focus: Visual property extraction from product images.
    """
    SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    TARGET_PROPERTIES = list(IMAGE_EXTRACTABLE_PROPERTIES.keys())
    REFUSAL_KEYWORDS = [
        "can't help with that", "unable to identify or describe", "can't help with identifying",
        "sorry, i can't help with", "i'm not able to identify", "i cannot identify",
        "i'm unable to provide descriptions", "cannot analyze this image"
    ]

    def __init__(self):
        self.openai_client = AsyncOpenAIClient()

    async def extract_image_contexts(
        self, 
        scraper_input: ScraperInput,
        product_name: Optional[str] = None,
        product_url: Optional[str] = None
    ) -> Dict[str, HtmlContext]:
        try:
            logger.info(f"Starting image extraction for {len(self.TARGET_PROPERTIES)} properties")
            image_contexts = {}
            main_image_url = scraper_input.images.url_main_image
            if main_image_url:
                logger.info(f"Processing main image: {main_image_url}")
                contexts = await self._extract_from_single_image(
                    image_url=main_image_url,
                    product_name=product_name,
                    product_url=product_url
                )
                image_contexts.update(contexts)
            incomplete_properties = [
                prop for prop, context in image_contexts.items()
                if not context.relevant_html_product_context.strip()
            ]
            if incomplete_properties and scraper_input.images.other_main_images:
                logger.info(f"Processing additional images for incomplete properties: {incomplete_properties}")
                for additional_image_url in scraper_input.images.other_main_images:
                    if not incomplete_properties:
                        break
                    logger.info(f"Processing additional image: {additional_image_url}")
                    additional_contexts = await self._extract_from_single_image(
                        image_url=additional_image_url,
                        product_name=product_name,
                        product_url=product_url,
                        target_properties=incomplete_properties
                    )
                    for prop in incomplete_properties[:]:
                        if (prop in additional_contexts and 
                            additional_contexts[prop].relevant_html_product_context.strip()):
                            image_contexts[prop] = additional_contexts[prop]
                            incomplete_properties.remove(prop)
            for property_name in self.TARGET_PROPERTIES:
                if property_name not in image_contexts:
                    image_contexts[property_name] = HtmlContext(
                        relevant_html_product_context=""
                    )
            logger.info(f"Image extraction completed. Properties with data: {sum(1 for ctx in image_contexts.values() if ctx.relevant_html_product_context.strip())}")
            return image_contexts
        except Exception as e:
            logger.error(f"Critical error in image extraction: {str(e)}")
            return {
                prop: HtmlContext(relevant_html_product_context="")
                for prop in self.TARGET_PROPERTIES
            }

    async def _extract_from_single_image(
        self,
        image_url: str,
        product_name: Optional[str] = None,
        product_url: Optional[str] = None,
        target_properties: Optional[List[str]] = None
    ) -> Dict[str, HtmlContext]:
        contexts = {}
        properties_to_process = target_properties or self.TARGET_PROPERTIES
        try:
            base64_image = await self._download_and_encode_image(image_url)
            if not base64_image:
                logger.warning(f"Failed to download/encode image: {image_url}")
                return {prop: HtmlContext(relevant_html_product_context="") for prop in properties_to_process}
            for property_name in properties_to_process:
                try:
                    extracted_value = await self._extract_property_from_image(
                        property_name=property_name,
                        base64_image=base64_image,
                        image_url=image_url,
                        product_name=product_name or "Unknown Product",
                        product_url=product_url or ""
                    )
                    contexts[property_name] = HtmlContext(
                        relevant_html_product_context=extracted_value
                    )
                    logger.debug(f"Extracted {property_name} from image: {extracted_value[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to extract {property_name} from image: {str(e)}")
                    contexts[property_name] = HtmlContext(relevant_html_product_context="")
            return contexts
        except Exception as e:
            logger.error(f"Error processing image {image_url}: {str(e)}")
            return {prop: HtmlContext(relevant_html_product_context="") for prop in properties_to_process}

    async def _download_and_encode_image(self, image_url: str) -> Optional[str]:
        try:
            parsed_url = urlparse(image_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.error(f"Invalid image URL: {image_url}")
                return None
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"Image download failed: {image_url} (status: {response.status})")
                        return None
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        logger.warning(f"URL does not appear to be an image: {image_url}")
                        return None
                    image_data = await response.read()
                    base64_string = base64.b64encode(image_data).decode('utf-8')
                    logger.debug(f"Successfully encoded image: {image_url}")
                    return base64_string
        except Exception as e:
            logger.error(f"Failed to download/encode image {image_url}: {str(e)}")
            return None

    async def _extract_property_from_image(
        self,
        property_name: str,
        base64_image: str,
        image_url: str,
        product_name: str,
        product_url: str
    ) -> str:
        try:
            property_description = IMAGE_EXTRACTABLE_PROPERTIES.get(
                property_name,
                f"Information related to the {property_name} property"
            )
            user_prompt = IMAGE_EXTRACTION_USER_PROMPT_TEMPLATE.format(
                property=property_name,
                property_description=property_description,
                product_name=product_name,
                product_url=product_url
            )
            response = await self._call_vision_api(
                system_prompt=IMAGE_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                base64_image=base64_image
            )
            if not response:
                return ""
            if self._is_safety_refusal(response):
                logger.warning(f"Safety refusal detected for {property_name}, trying fallback")
                fallback_response = await self._call_vision_api(
                    system_prompt=IMAGE_FALLBACK_SYSTEM_PROMPT,
                    user_prompt=f"Extract {property_name} information from this product image.",
                    base64_image=base64_image
                )
                response = fallback_response if fallback_response and not self._is_safety_refusal(fallback_response) else ""
            try:
                parsed_response = json.loads(response)
                return parsed_response.get(property_name, "")
            except json.JSONDecodeError:
                return response.strip()
        except Exception as e:
            logger.error(f"Error extracting {property_name} from image: {str(e)}")
            return ""

    async def _call_vision_api(
        self,
        system_prompt: str,
        user_prompt: str,
        base64_image: str,
        model: str = "gpt-4o",
        max_tokens: int = 500
    ) -> Optional[str]:
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
            response = await self.openai_client.complete_vision(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=0
            )
            return response
        except Exception as e:
            logger.error(f"Vision API call failed: {str(e)}")
            return None

    def _is_safety_refusal(self, response: str) -> bool:
        if not response:
            return False
        lower_response = response.lower()
        return any(keyword in lower_response for keyword in self.REFUSAL_KEYWORDS)

    def get_target_properties(self) -> List[str]:
        return self.TARGET_PROPERTIES.copy()

    def get_property_description(self, property_name: str) -> str:
        return IMAGE_EXTRACTABLE_PROPERTIES.get(
            property_name,
            f"Information related to the {property_name} property"
        ) 