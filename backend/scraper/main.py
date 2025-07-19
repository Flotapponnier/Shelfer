# main.py - The public interface

from typing import Any, Dict, List, Optional
from .core.browser_manager import BrowserManager
from .core.crawler import Crawler
from .utils.domain_utils import clean_domain_url
from config import CRAWLER_PRODUCT_COLLECTION_GOAL

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