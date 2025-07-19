# main.py - The public interface

from typing import Any, Dict, List, Optional
import logging
from .core.browser_manager import BrowserManager
from .core.crawler import Crawler
from .utils.domain_utils import clean_domain_url
from .utils.main_product_detector import MainProductDetector
from config import CRAWLER_PRODUCT_COLLECTION_GOAL

# Set up logger
logger = logging.getLogger(__name__)

async def scrape_domain(domain_url: str, headless: bool = True, max_products: int = None, 
                       delay: float = 1.0, min_jsonld_products: int = None) -> Dict[str, Any]:
    """
    High-level function to scrape a domain using the crawler.
    
    This function uses a breadth-first crawler to discover and scrape product pages.
    The crawler includes robust retry logic, error handling, and resource management.
    
    Args:
        domain_url: The domain URL to scrape (can be a single URL, multiple URLs, or domain)
        headless: Whether to run browser in headless mode
        max_products: Maximum number of products to scrape (defaults to config)
        delay: Delay between requests
        min_jsonld_products: Minimum number of products with JSON-LD required to consider successful (defaults to data collection goal)
        
    Returns:
        Dictionary containing scraped schemas (all, product, and non-product), crawler execution summary, and detailed error information
    """
    from .utils.error_handling import ExtractionResult, aggregate_errors, ExtractionError, ExtractionErrorType
    
    # Clean and standardize the domain URL
    try:
        cleaned_domain_url = clean_domain_url(domain_url)
    except ValueError as e:
        # Return error response for invalid domain
        return {
            "product_schemas": [],
            "non_product_schemas": [],
            "all_schemas": [],
            "crawler_summary": {"error": str(e)},
            "error": str(e),
            "extraction_result": {
                "success": False,
                "products": [],
                "statistics": {"domain_url": domain_url, "error": str(e)}
            }
        }
    
    # Use configuration defaults if not provided
    max_products = max_products or CRAWLER_PRODUCT_COLLECTION_GOAL
    min_jsonld_products = min_jsonld_products or CRAWLER_PRODUCT_COLLECTION_GOAL

    # Initialize result tracking
    extraction_result = ExtractionResult(success=True, products=[], statistics={
        "domain_url": cleaned_domain_url,
        "original_domain_url": domain_url,  # Keep original for reference
        "max_products": max_products,
        "min_jsonld_products": min_jsonld_products,
        "crawler_used": "breadth_first_crawler"
    })

    async with BrowserManager(headless=headless) as browser_manager:
        # Create crawler with robust configuration
        crawler = Crawler(browser_manager, delay=delay, timeout=10000)
        
        # Discover product pages using crawler with cleaned domain URL
        crawler_result = await crawler.scrapeStructuredDataFromDomain(
            cleaned_domain_url, max_products, min_jsonld_products
        )
        
        # Update statistics
        if crawler_result.success:
            extraction_result.products = crawler_result.product_schemas
            extraction_result.statistics["product_schemas_scraped"] = len(crawler_result.product_schemas)
            extraction_result.statistics["non_product_schemas_scraped"] = len(crawler_result.non_product_schemas)
            extraction_result.statistics["all_schemas_scraped"] = len(crawler_result.jsonld_schemas)
            extraction_result.statistics.update(crawler_result.statistics)
        else:
            # Add crawler failure error
            crawler_error = ExtractionError(
                ExtractionErrorType.UNKNOWN_ERROR,
                crawler_result.error or "Crawler failed",
                cleaned_domain_url,
                {
                    "domain_url": cleaned_domain_url,
                    "original_domain_url": domain_url,
                    "max_products": max_products,
                    "min_jsonld_products": min_jsonld_products,
                    "crawler_statistics": crawler_result.statistics
                }
            )
            extraction_result.add_error(crawler_error)
        
        # Prepare response
        response = {
            "product_schemas": crawler_result.product_schemas,
            "non_product_schemas": crawler_result.non_product_schemas,
            "all_schemas": crawler_result.jsonld_schemas,
            "crawler_summary": crawler_result.statistics,
            "extraction_result": extraction_result.to_dict()
        }
        
        # Add error aggregation if there are errors
        if extraction_result.errors:
            response["error_aggregation"] = aggregate_errors(extraction_result.errors)
            response["error"] = crawler_result.error  # Keep backward compatibility
        
        return response


class MainProductScraper:
    """Focused scraper for extracting and identifying main products from single pages."""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.detector = MainProductDetector()
    
    async def _extract_and_process_products(self, jsonld_scripts: List[str]) -> List[Dict[str, Any]]:
        """Extract and process products from JSON-LD scripts."""
        from .core.jsonld_parser import parse_json_ld_scripts, _is_product_schema, deduplicate_and_select_best_schemas, _flatten_nested_structures
        
        if not jsonld_scripts:
            return []
        
        try:
            # Parse all JSON-LD scripts
            parsed_objects = parse_json_ld_scripts(jsonld_scripts)
            logger.debug(f"Parsed {len(parsed_objects)} total objects")
            
            # Flatten nested structures
            flattened_objects = _flatten_nested_structures(parsed_objects)
            logger.debug(f"Flattened to {len(flattened_objects)} objects")
            
            # Filter for products only
            product_objects = [obj for obj in flattened_objects if _is_product_schema(obj)]
            logger.debug(f"Found {len(product_objects)} product schemas")
            
            # Deduplicate products
            if product_objects:
                all_schemas_deduplicated = deduplicate_and_select_best_schemas(product_objects)
                # Filter back to products only since the function returns all schemas
                unique_products = [obj for obj in all_schemas_deduplicated if _is_product_schema(obj)]
                return unique_products
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to extract products from JSON-LD scripts: {e}")
            return []
    
    async def scrape_main_product(self, domain_url: str, headless: bool = True) -> Dict[str, Any]:
        """
        Extract and identify the main product from a single product page.
        
        Args:
            domain_url: The product page URL to scrape
            headless: Whether to run browser in headless mode
            
        Returns:
            Dictionary containing the main product and analysis details
        """
        from .utils.error_handling import ExtractionResult, ExtractionError, ExtractionErrorType
        from .utils.domain_utils import clean_domain_url
        
        # Clean and standardize the URL
        try:
            cleaned_url = clean_domain_url(domain_url)
        except ValueError as e:
            return self._create_error_response(domain_url, str(e))
        
        async with BrowserManager(headless=headless) as browser_manager:
            try:
                # Create a single page for focused extraction
                page = await browser_manager.new_page()
                
                # Navigate to the product page
                await page.goto(cleaned_url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(int(self.delay * 1000))
                
                # Extract JSON-LD schemas from the page
                from .utils.json_ld_extraction_utils import JSONLDExtractor
                extractor = JSONLDExtractor(delay=self.delay)
                jsonld_scripts = await extractor.extract_jsonld_from_page(page)
                
                logger.debug(f"Found {len(jsonld_scripts)} JSON-LD scripts")
                
                # Parse and extract product schemas
                all_products = await self._extract_and_process_products(jsonld_scripts)
                logger.info(f"Extracted {len(all_products)} unique product schemas")
                
                # Identify the main product
                main_product = await self.detector.identify_main_product(page, all_products, cleaned_url)
                
                # Generate analysis summary
                analysis = self._create_analysis_summary(
                    cleaned_url, domain_url, all_products, main_product
                )
                
                await page.close()
                
                return {
                    "main_product": main_product,
                    "all_products_found": all_products,
                    "analysis": analysis
                }
                
            except Exception as e:
                logger.error(f"Main product scraping failed: {e}")
                return self._create_error_response(domain_url, str(e), cleaned_url)
    
    def _create_analysis_summary(self, cleaned_url: str, original_url: str, 
                                all_products: List[Dict[str, Any]], 
                                main_product: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create analysis summary for the scraping results."""
        confidence = "high" if len(all_products) == 1 else ("medium" if main_product else "low")
        
        analysis = {
            "url_analyzed": cleaned_url,
            "original_url": original_url,
            "products_found": len(all_products),
            "products_analyzed": len(all_products),
            "main_product_detected": main_product is not None,
            "main_product_confidence": confidence,
            "detection_method": "url_aware_main_product_detector"
        }
        
        # Add main product summary if found
        if main_product:
            analysis["main_product_summary"] = self.detector.get_main_product_summary(main_product)
        
        return analysis
    
    def _create_error_response(self, original_url: str, error_msg: str, 
                              cleaned_url: str = None) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "main_product": None,
            "all_products_found": [],
            "analysis": {
                "error": error_msg,
                "url_analyzed": cleaned_url or original_url,
                "original_url": original_url,
                "products_analyzed": 0,
                "main_product_confidence": "low"
            }
        }


async def scrape_main_product(domain_url: str, headless: bool = True, delay: float = 1.0) -> Dict[str, Any]:
    """
    Public API function for main product scraping.
    
    Args:
        domain_url: The product page URL to scrape
        headless: Whether to run browser in headless mode
        delay: Delay between requests
        
    Returns:
        Dictionary containing the main product and analysis details
    """
    scraper = MainProductScraper(delay=delay)
    return await scraper.scrape_main_product(domain_url, headless)