import logging
import json
import base64
import mimetypes
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse
import requests
from io import BytesIO
from PIL import Image

from openai_client import OpenAIClient
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
    
    # Supported image formats
    SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    # Properties that can be extracted from images
    TARGET_PROPERTIES = list(IMAGE_EXTRACTABLE_PROPERTIES.keys())
    
    # Safety refusal detection keywords
    REFUSAL_KEYWORDS = [
        "can't help with that",
        "unable to identify or describe",
        "can't help with identifying",
        "sorry, i can't help with",
        "i'm not able to identify",
        "i cannot identify",
        "i'm unable to provide descriptions",
        "cannot analyze this image"
    ]
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    def extract_image_contexts(
        self, 
        scraper_input: ScraperInput,
        product_name: Optional[str] = None,
        product_url: Optional[str] = None
    ) -> Dict[str, HtmlContext]:
        """
        Main method to extract relevant contexts for schema.org properties from product images.
        
        Args:
            scraper_input: Input containing image URLs
            product_name: Optional product name for context
            product_url: Optional product URL for context
            
        Returns:
            Dict[str, HtmlContext]: Dictionary mapping property names to extracted contexts
        """
        try:
            logger.info(f"Starting image extraction for {len(self.TARGET_PROPERTIES)} properties")
            
            image_contexts = {}
            
            # Process main image first
            main_image_url = scraper_input.images.url_main_image
            if main_image_url:
                logger.info(f"Processing main image: {main_image_url}")
                contexts = self._extract_from_single_image(
                    image_url=main_image_url,
                    product_name=product_name,
                    product_url=product_url
                )
                image_contexts.update(contexts)
            
            # Process additional images if main image extraction was incomplete
            incomplete_properties = [
                prop for prop, context in image_contexts.items()
                if not context.relevant_html_product_context.strip()
            ]
            
            if incomplete_properties and scraper_input.images.other_main_images:
                logger.info(f"Processing additional images for incomplete properties: {incomplete_properties}")
                
                for additional_image_url in scraper_input.images.other_main_images:
                    if not incomplete_properties:  # All properties completed
                        break
                        
                    logger.info(f"Processing additional image: {additional_image_url}")
                    additional_contexts = self._extract_from_single_image(
                        image_url=additional_image_url,
                        product_name=product_name,
                        product_url=product_url,
                        target_properties=incomplete_properties
                    )
                    
                    # Update only incomplete properties
                    for prop in incomplete_properties[:]:  # Copy list for safe iteration
                        if (prop in additional_contexts and 
                            additional_contexts[prop].relevant_html_product_context.strip()):
                            image_contexts[prop] = additional_contexts[prop]
                            incomplete_properties.remove(prop)
            
            # Ensure all target properties have contexts (empty if not found)
            for property_name in self.TARGET_PROPERTIES:
                if property_name not in image_contexts:
                    image_contexts[property_name] = HtmlContext(
                        relevant_html_product_context=""
                    )
            
            logger.info(f"Image extraction completed. Properties with data: {sum(1 for ctx in image_contexts.values() if ctx.relevant_html_product_context.strip())}")
            return image_contexts
            
        except Exception as e:
            logger.error(f"Critical error in image extraction: {str(e)}")
            # Return empty contexts for all properties
            return {
                prop: HtmlContext(relevant_html_product_context="")
                for prop in self.TARGET_PROPERTIES
            }
    
    def _extract_from_single_image(
        self,
        image_url: str,
        product_name: Optional[str] = None,
        product_url: Optional[str] = None,
        target_properties: Optional[List[str]] = None
    ) -> Dict[str, HtmlContext]:
        """
        Extract properties from a single image.
        
        Args:
            image_url: URL of the image to process
            product_name: Optional product name for context
            product_url: Optional product URL for context
            target_properties: Optional list of specific properties to extract
            
        Returns:
            Dict[str, HtmlContext]: Extracted contexts for properties
        """
        contexts = {}
        properties_to_process = target_properties or self.TARGET_PROPERTIES
        
        try:
            # Download and encode image
            base64_image = self._download_and_encode_image(image_url)
            if not base64_image:
                logger.warning(f"Failed to download/encode image: {image_url}")
                return {prop: HtmlContext(relevant_html_product_context="") for prop in properties_to_process}
            
            # Extract each property
            for property_name in properties_to_process:
                try:
                    extracted_value = self._extract_property_from_image(
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
    
    def _download_and_encode_image(self, image_url: str) -> Optional[str]:
        """
        Download image from URL and convert to base64.
        
        Args:
            image_url: URL of the image to download
            
        Returns:
            Base64 encoded image string or None if failed
        """
        try:
            # Validate URL
            parsed_url = urlparse(image_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.error(f"Invalid image URL: {image_url}")
                return None
            
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Validate it's an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL does not appear to be an image: {image_url}")
                return None
            
            # Convert to base64
            image_data = response.content
            base64_string = base64.b64encode(image_data).decode('utf-8')
            
            logger.debug(f"Successfully encoded image: {image_url}")
            return base64_string
            
        except Exception as e:
            logger.error(f"Failed to download/encode image {image_url}: {str(e)}")
            return None
    
    def _extract_property_from_image(
        self,
        property_name: str,
        base64_image: str,
        image_url: str,
        product_name: str,
        product_url: str
    ) -> str:
        """
        Extract a specific property from an image using GPT-4o vision.
        
        Args:
            property_name: Schema.org property name
            base64_image: Base64 encoded image
            image_url: Original image URL
            product_name: Product name for context
            product_url: Product URL for context
            
        Returns:
            Extracted property value as string
        """
        try:
            # Get property description
            property_description = IMAGE_EXTRACTABLE_PROPERTIES.get(
                property_name,
                f"Information related to the {property_name} property"
            )
            
            # Format the user prompt
            user_prompt = IMAGE_EXTRACTION_USER_PROMPT_TEMPLATE.format(
                property=property_name,
                property_description=property_description,
                product_name=product_name,
                product_url=product_url
            )
            
            # Call OpenAI Vision API
            response = self._call_vision_api(
                system_prompt=IMAGE_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                base64_image=base64_image
            )
            
            if not response:
                return ""
            
            # Check for safety refusal and retry with fallback if needed
            if self._is_safety_refusal(response):
                logger.warning(f"Safety refusal detected for {property_name}, trying fallback")
                fallback_response = self._call_vision_api(
                    system_prompt=IMAGE_FALLBACK_SYSTEM_PROMPT,
                    user_prompt=f"Extract {property_name} information from this product image.",
                    base64_image=base64_image
                )
                response = fallback_response if fallback_response and not self._is_safety_refusal(fallback_response) else ""
            
            # Parse JSON response
            try:
                parsed_response = json.loads(response)
                return parsed_response.get(property_name, "")
            except json.JSONDecodeError:
                # If not JSON, return the raw response
                return response.strip()
                
        except Exception as e:
            logger.error(f"Error extracting {property_name} from image: {str(e)}")
            return ""
    
    def _call_vision_api(
        self,
        system_prompt: str,
        user_prompt: str,
        base64_image: str,
        model: str = "gpt-4o",
        max_tokens: int = 500
    ) -> Optional[str]:
        """
        Call OpenAI Vision API with image and prompt.
        
        Args:
            system_prompt: System prompt for the model
            user_prompt: User prompt
            base64_image: Base64 encoded image
            model: Model name (should be vision-capable)
            max_tokens: Maximum tokens in response
            
        Returns:
            Model response or None if failed
        """
        try:
            # Note: We need to modify the OpenAIClient to support vision
            # For now, we'll use a direct call format
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # We need to extend the OpenAI client to support vision
            # For now, return a placeholder that indicates vision support needed
            response = self._call_openai_vision_direct(messages, model, max_tokens)
            return response
            
        except Exception as e:
            logger.error(f"Vision API call failed: {str(e)}")
            return None
    
    def _call_openai_vision_direct(self, messages: List[Dict], model: str, max_tokens: int) -> Optional[str]:
        """
        Direct call to OpenAI vision API (temporary implementation).
        TODO: Extend OpenAIClient to support vision models properly.
        """
        try:
            import openai
            import os
            
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0
            )
            
            return response.choices[0].message.content.strip() if response.choices else None
            
        except Exception as e:
            logger.error(f"Direct OpenAI vision call failed: {str(e)}")
            return None
    
    def _is_safety_refusal(self, response: str) -> bool:
        """
        Check if the response contains safety refusal keywords.
        
        Args:
            response: Model response to check
            
        Returns:
            True if response appears to be a safety refusal
        """
        if not response:
            return False
            
        lower_response = response.lower()
        return any(keyword in lower_response for keyword in self.REFUSAL_KEYWORDS)
    
    def get_target_properties(self) -> List[str]:
        """
        Get the list of target schema.org properties that can be extracted from images.
        
        Returns:
            List[str]: List of property names
        """
        return self.TARGET_PROPERTIES.copy()
    
    def get_property_description(self, property_name: str) -> str:
        """
        Get the description for a specific property.
        
        Args:
            property_name: The schema.org property name
            
        Returns:
            str: Property description
        """
        return IMAGE_EXTRACTABLE_PROPERTIES.get(
            property_name,
            f"Information related to the {property_name} property"
        ) 