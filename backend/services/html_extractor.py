import logging
from typing import Dict, List
from openai_client import AsyncOpenAIClient
from schemas.product import ScraperInput, ExtractorOutput, HtmlContext
from prompts.html_extraction import (
    HTML_EXTRACTION_SYSTEM_PROMPT,
    HTML_EXTRACTION_USER_PROMPT_TEMPLATE,
    PROPERTY_DESCRIPTIONS
)
import asyncio

logger = logging.getLogger(__name__)

class HtmlExtractorService:
    """
    Service that extracts relevant HTML contexts for schema.org properties
    from scraped product HTML using OpenAI.
    
    Focus: HTML-only extraction. Image analysis is handled separately.
    """
    
    # Target schema.org properties for HTML extraction
    # Note: "image" property is handled separately by image analysis service
    TARGET_PROPERTIES = [
        # we'll comment out some properties for making it work for now
        # "offers.price",
        # "offers.priceCurrency",
        # "offers.availability",
        # "offers.itemCondition",
        "description",
        "brand",
        "color",
        "material",
        # "aggregateRating",
        # "review",
        "category",
        "keywords",
        # "manufacturer",
        "size",
        "audience",
        # "additionalType",
        # "hasMerchantReturnPolicy",
        # "negativeNotes",
        # "positiveNotes",
        # "nsn",
        # "countryOfLastProcessing",
        # "isFamilyFriendly"
    ]
    
    def __init__(self):
        self.openai_client = AsyncOpenAIClient()
    
    async def extract_html_contexts(self, scraper_input: ScraperInput) -> ExtractorOutput:
        """
        Main method to extract relevant HTML contexts for each target property from HTML only.
        
        Args:
            scraper_input: Input from the scraper containing product_html, images (not processed yet), 
                          and optional json_ld_schema
            
        Returns:
            ExtractorOutput: Formatted output containing json_ld_schema and html_contexts for each property.
                           Note: Images are not processed in this service - handled separately.
        """
        try:
            logger.info(f"Starting HTML extraction for {len(self.TARGET_PROPERTIES)} properties")
            html_contexts = {}

            async def extract_for_property(property_name):
                try:
                    relevant_html = await self._extract_property_html(
                        property_name=property_name,
                        product_html=scraper_input.product_html
                    )
                    html_contexts[property_name] = HtmlContext(
                        relevant_html_product_context=relevant_html
                    )
                    logger.debug(f"Successfully extracted HTML for property: {property_name}")
                except Exception as e:
                    logger.error(f"Failed to extract HTML for property {property_name}: {str(e)}")
                    html_contexts[property_name] = HtmlContext(
                        relevant_html_product_context=""
                    )

            # Run all property extractions in parallel
            tasks = [extract_for_property(property_name) for property_name in self.TARGET_PROPERTIES]
            await asyncio.gather(*tasks)

            # Create and return the output
            result = ExtractorOutput(
                json_ld_schema=scraper_input.json_ld_schema,
                html_contexts=html_contexts
            )
            logger.info("HTML extraction completed successfully")
            return result
        except Exception as e:
            logger.error(f"Critical error in HTML extraction: {str(e)}")
            raise
    
    async def _extract_property_html(self, property_name: str, product_html: str) -> str:
        """
        Extract relevant HTML chunks for a specific schema.org property using OpenAI.
        
        Args:
            property_name: The schema.org property name (e.g., "offers.price")
            product_html: The full product HTML from scraper
            
        Returns:
            str: Relevant HTML chunks for the property
        """
        try:
            # Check if product_html is empty - return empty result to prevent hallucination
            if not product_html or not product_html.strip():
                logger.warning(f"Empty product HTML provided for property {property_name} - skipping extraction to prevent hallucination")
                return ""
            # Get property description for context
            property_description = PROPERTY_DESCRIPTIONS.get(
                property_name, 
                f"Information related to the {property_name} property"
            )
            # Format the user prompt
            user_prompt = HTML_EXTRACTION_USER_PROMPT_TEMPLATE.format(
                property=property_name,
                property_description=property_description,
                product_html=product_html
            )
            # Call OpenAI to extract relevant HTML
            response = await self.openai_client.complete(
                system_prompt=HTML_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=2000  # Increased for HTML content
            )
            # Clean and return the response
            if response and not response.startswith("{'error':"):
                return response.strip()
            else:
                logger.warning(f"OpenAI returned error for property {property_name}: {response}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting HTML for property {property_name}: {str(e)}")
            return ""
    
    def get_target_properties(self) -> List[str]:
        """
        Get the list of target schema.org properties.
        
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
        return PROPERTY_DESCRIPTIONS.get(
            property_name, 
            f"Information related to the {property_name} property"
        ) 