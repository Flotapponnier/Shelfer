"""
Extractor Service

Orchestrates the complete product data extraction pipeline:
scraper → HTML extractor → image extractor → combined output

This service layer provides clean separation of concerns and makes the 
controller lightweight while handling the complex workflow.
"""

import logging
from typing import Dict, Any, Optional
from schemas.product import ScraperInput, ProductImages, ExtractorOutput, HtmlContext
from services.html_extractor import HtmlExtractorService
from services.image_extractor import ImageExtractorService

logger = logging.getLogger(__name__)

class ExtractorService:
    """
    Service that orchestrates the complete product data extraction pipeline.
    
    Workflow:
    1. Receives scraped product data
    2. Runs HTML extractor (22 properties)
    3. Runs image extractor (10 properties) 
    4. Combines results into unified output
    5. Returns enriched data ready for further processing
    """
    
    def __init__(self):
        self.html_extractor = HtmlExtractorService()
        self.image_extractor = ImageExtractorService()
    
    async def extract_product_data(
        self,
        scraped_data: Dict[str, Any],
        product_name: Optional[str] = None,
        product_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main method to extract product data through both extractors.
        
        Args:
            scraped_data: Raw data from scraper in format:
                {
                    "product_html": str,
                    "images": {
                        "url_main_image": str,
                        "other_images": List[str]
                    },
                    "json_ld_schema": dict (optional)
                }
            product_name: Optional product name for context
            product_url: Optional product URL for context
            
        Returns:
            Dict containing combined extraction results ready for enricher
        """
        try:
            logger.info("Starting product data extraction pipeline")
            
            # Log the scraped data for debugging
            html_length = len(scraped_data.get("product_html", ""))
            images_data = scraped_data.get("images", {})
            main_image = images_data.get("url_main_image", "")
            other_images = images_data.get("other_images", [])
            
            logger.info(f"📊 Scraped data summary:")
            logger.info(f"   - HTML length: {html_length} characters")
            logger.info(f"   - Main image: {'✅' if main_image else '❌'} {main_image[:100] if main_image else 'None'}")
            logger.info(f"   - Other images: {len(other_images)} found")
            
            if html_length == 0:
                logger.warning("🚨 WARNING: Empty product HTML detected - this will cause LLM hallucination!")
            
            # Convert scraped data to internal format
            scraper_input = self._convert_scraped_data(scraped_data)
            
            # Step 1: Extract HTML contexts (22 properties)
            logger.info("Running HTML extraction...")
            html_result = await self.html_extractor.extract_html_contexts(scraper_input)
            
            # Step 2: Extract image contexts (10 properties)
            logger.info("Running image extraction...")
            image_contexts = await self.image_extractor.extract_image_contexts(
                scraper_input, 
                product_name=product_name,
                product_url=product_url
            )
            
            # Step 3: Combine results
            logger.info("Combining extraction results...")
            combined_result = self._combine_extraction_results(
                html_result=html_result,
                image_contexts=image_contexts
            )
            
            # Step 4: Add processing metadata
            combined_result["processing_metadata"] = self._generate_processing_metadata(
                html_result, image_contexts
            )
            
            logger.info("Product data extraction pipeline completed successfully")
            return combined_result
            
        except Exception as e:
            logger.error(f"Error in product data extraction pipeline: {str(e)}")
            # Return error structure that enricher can handle
            return {
                "json_ld_schema": scraped_data.get("json_ld_schema"),
                "html_contexts": {},
                "error": str(e),
                "processing_metadata": {
                    "success": False,
                    "html_properties_extracted": 0,
                    "image_properties_extracted": 0,
                    "total_properties": 32
                }
            }
    
    def _convert_scraped_data(self, scraped_data: Dict[str, Any]) -> ScraperInput:
        """
        Convert raw scraped data to ScraperInput format.
        
        Handles both camelCase (external) and snake_case (internal) formats.
        """
        try:
            # Extract data using consistent snake_case field names
            product_html = scraped_data.get("product_html", "")
            images_data = scraped_data.get("images", {})
            url_main_image = images_data.get("url_main_image", "")
            other_images = images_data.get("other_images", [])
            
            # Debug: Log what we actually received
            logger.debug(f"🔍 ExtractorService received data keys: {list(scraped_data.keys())}")
            logger.debug(f"🔍 ExtractorService product_html length: {len(product_html)} chars")
            logger.debug(f"🔍 ExtractorService product_html preview: {product_html[:200] if product_html else 'EMPTY!'}")
            
            # Handle json_ld_schema: support both dict and list formats
            raw_json_ld = scraped_data.get("json_ld_schema")
            if isinstance(raw_json_ld, list) and len(raw_json_ld) == 0:
                json_ld_schema = None
            elif isinstance(raw_json_ld, list) and len(raw_json_ld) > 0:
                json_ld_schema = raw_json_ld  # Keep the list of schemas
            elif isinstance(raw_json_ld, dict):
                json_ld_schema = raw_json_ld
            else:
                json_ld_schema = None
            
            return ScraperInput(
                product_html=product_html,
                images=ProductImages(
                    url_main_image=url_main_image,
                    other_main_images=other_images
                ),
                json_ld_schema=json_ld_schema
            )
            
        except Exception as e:
            logger.error(f"Error converting scraped data: {str(e)}")
            # Return minimal valid input
            return ScraperInput(
                product_html="",
                images=ProductImages(url_main_image="", other_main_images=[]),
                json_ld_schema=None
            )
    
    def _combine_extraction_results(
        self,
        html_result: ExtractorOutput,
        image_contexts: Dict[str, HtmlContext]
    ) -> Dict[str, Any]:
        """
        Combine HTML and image extraction results into unified format.
        
        Returns format expected by enricher:
        {
            "json_ld_schema": {...},
            "html_contexts": {
                "property_name": {
                    "relevant_html_product_context": "..."
                }
            }
        }
        """
        # Start with HTML contexts
        combined_contexts = html_result.html_contexts.copy()
        
        # Add image contexts (they use the same HtmlContext structure)
        combined_contexts.update(image_contexts)
        
        # Convert to dictionary format for API response
        html_contexts_dict = {
            property_name: {
                "relevant_html_product_context": context.relevant_html_product_context
            }
            for property_name, context in combined_contexts.items()
        }
        
        return {
            "json_ld_schema": html_result.json_ld_schema,
            "html_contexts": html_contexts_dict
        }
    
    def _generate_processing_metadata(
        self,
        html_result: ExtractorOutput,
        image_contexts: Dict[str, HtmlContext]
    ) -> Dict[str, Any]:
        """
        Generate metadata about the processing results.
        """
        # Count successful extractions
        html_success_count = sum(
            1 for context in html_result.html_contexts.values()
            if context.relevant_html_product_context.strip()
        )
        
        image_success_count = sum(
            1 for context in image_contexts.values()
            if context.relevant_html_product_context.strip()
        )
        
        total_html_properties = len(html_result.html_contexts)
        total_image_properties = len(image_contexts)
        
        return {
            "success": True,
            "html_properties_extracted": html_success_count,
            "html_properties_total": total_html_properties,
            "html_success_rate": html_success_count / total_html_properties if total_html_properties > 0 else 0,
            "image_properties_extracted": image_success_count,
            "image_properties_total": total_image_properties,
            "image_success_rate": image_success_count / total_image_properties if total_image_properties > 0 else 0,
            "total_properties_extracted": html_success_count + image_success_count,
            "total_properties": total_html_properties + total_image_properties,
            "overall_success_rate": (html_success_count + image_success_count) / (total_html_properties + total_image_properties)
        }
    
    def get_supported_properties(self) -> Dict[str, Any]:
        """
        Get information about all supported properties.
        
        Returns:
            Dictionary with HTML and image properties info
        """
        return {
            "html_properties": {
                "count": len(self.html_extractor.get_target_properties()),
                "properties": self.html_extractor.get_target_properties()
            },
            "image_properties": {
                "count": len(self.image_extractor.get_target_properties()),
                "properties": self.image_extractor.get_target_properties()
            },
            "total_properties": len(self.html_extractor.get_target_properties()) + len(self.image_extractor.get_target_properties())
        } 