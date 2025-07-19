"""
Breadth-first web crawler for product page discovery.

This crawler discovers product pages by crawling websites in a breadth-first manner,
extracting JSON-LD product data and intelligently prioritizing URLs for optimal discovery.
"""

import asyncio
from typing import List, Dict, Any, Optional, Set
from collections import deque
from urllib.parse import urljoin

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from .browser_manager import BrowserManager
from ..utils.utils import logger
from .url_prioritizer import UrlPrioritizer
from .crawl_queue_manager import CrawlQueueManager
from ..utils.domain_utils import is_same_domain
try:
    from config import (
        CRAWLER_MAX_PAGES_TO_CRAWL,
        CRAWLER_PRODUCT_COLLECTION_GOAL,
        PAGE_NAVIGATION_TIMEOUT,
        NETWORK_IDLE_TIMEOUT
    )
except ImportError:
    # Fallback for when running from tests directory
    import sys
    import os
    # Add the backend directory to the path
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from config import (
        CRAWLER_MAX_PAGES_TO_CRAWL,
        CRAWLER_PRODUCT_COLLECTION_GOAL,
        PAGE_NAVIGATION_TIMEOUT,
        NETWORK_IDLE_TIMEOUT
    )


class CrawlerResult:
    """Result of a crawler execution."""
    
    def __init__(self, success: bool, jsonld_schemas: List[Dict[str, Any]] = None, 
                 error: str = None, statistics: Dict[str, Any] = None, product_schemas: List[Dict[str, Any]] = None, non_product_schemas: List[Dict[str, Any]] = None):
        self.success = success
        self.jsonld_schemas = jsonld_schemas or []
        self.error = error
        self.statistics = statistics or {}
        self.product_schemas = product_schemas or []
        self.non_product_schemas = non_product_schemas or []
    
    def __str__(self):
        if self.success:
            stats_str = ""
            if self.statistics:
                stats_str = f", stats={self.statistics}"
            return f"CrawlerResult(success=True, jsonld_schemas={len(self.jsonld_schemas)}, product_schemas={len(self.product_schemas)}, non_product_schemas={len(self.non_product_schemas)}{stats_str})"
        else:
            return f"CrawlerResult(success=False, error='{self.error}')"


class Crawler:
    """Breadth-first web crawler for discovering product pages."""
    
    def __init__(self, browser_manager: BrowserManager, delay: float = 1.0, timeout: int = 10000):
        self.browser_manager = browser_manager
        self.delay = delay
        self.timeout = timeout
        
        # Initialize the URL prioritizer
        self.url_prioritizer = UrlPrioritizer()
        
        # Initialize robust utilities
        from ..utils.json_ld_extraction_utils import JSONLDExtractor
        self.jsonld_extractor = JSONLDExtractor(delay, 0, timeout)
    
    async def scrapeStructuredDataFromDomain(self, domain_url: str, max_products: int = None, min_jsonld_products: int = None) -> CrawlerResult:
        """
        Discover product pages and collect JSON-LD products by crawling websites in breadth-first order.
        
        Args:
            domain_url: The domain URL to search
            max_products: Maximum number of product URLs to find (defaults to config)
            min_jsonld_products: Minimum number of JSON-LD products required (defaults to config)
            
        Returns:
            CrawlerResult: URLs found and JSON-LD products collected
        """
        # Use configuration defaults if not provided
        max_products = max_products or CRAWLER_PRODUCT_COLLECTION_GOAL
        min_jsonld_products = min_jsonld_products or CRAWLER_PRODUCT_COLLECTION_GOAL
        
        # Initialize statistics tracking
        statistics = {
            "pages_visited": 0,
            "links_processed": 0,
            "jsonld_extraction_attempts": 0,
            "jsonld_extraction_successes": 0
        }
        
        try:
            logger.info(f"Starting Crawler for domain: {domain_url}")
            logger.info(f"Configuration: max_products={max_products}, min_jsonld_products={min_jsonld_products}")
            
            # Initialize the crawl queue manager
            queue_manager = CrawlQueueManager(domain_url, self.url_prioritizer)
            queue_manager.add_initial_url(domain_url, 0.0)
            
            jsonld_schemas = []
            
            # Process the queue until we have enough JSON-LD schemas or reach limits
            jsonld_schemas, discovery_stats = await self._crawl_with_jsonld_extraction(
                domain_url, queue_manager, max_products, min_jsonld_products
            )
            
            # Update statistics from the discovery process
            statistics.update(discovery_stats)
            
            # Get queue manager statistics
            queue_stats = queue_manager.get_statistics()
            statistics.update(queue_stats)
            
            logger.info(f"Crawling completed. Found {len(jsonld_schemas)} raw JSON-LD objects")
            
            # Final deduplication step - consistent with batch processing approach
            if jsonld_schemas:
                from .jsonld_parser import deduplicate_and_select_best_schemas, _is_product_schema
                original_count = len(jsonld_schemas)
                jsonld_schemas = deduplicate_and_select_best_schemas(jsonld_schemas)
                logger.info(f"Final deduplication: {original_count} raw objects → {len(jsonld_schemas)} unique schemas")
                statistics["raw_objects_found"] = original_count
                statistics["unique_schemas_found"] = len(jsonld_schemas)

                # Split into product and non-product schemas
                product_schemas = [s for s in jsonld_schemas if _is_product_schema(s)]
                non_product_schemas = [s for s in jsonld_schemas if not _is_product_schema(s)]
                statistics["product_schemas_found"] = len(product_schemas)
                statistics["non_product_schemas_found"] = len(non_product_schemas)
            else:
                product_schemas = []
                non_product_schemas = []

            # Check if we have enough Product schemas
            if len(product_schemas) >= min_jsonld_products:
                logger.info(f"Crawler found sufficient Product schemas: {len(product_schemas)}")
                return CrawlerResult(
                    success=True,
                    jsonld_schemas=jsonld_schemas,
                    product_schemas=product_schemas,
                    non_product_schemas=non_product_schemas,
                    statistics=statistics
                )
            else:
                logger.warning(f"Crawler found only {len(product_schemas)} Product schemas (minimum: {min_jsonld_products})")
                return CrawlerResult(
                    success=False,
                    error=f"Found only {len(product_schemas)} Product schemas (minimum: {min_jsonld_products})",
                    jsonld_schemas=jsonld_schemas,
                    product_schemas=product_schemas,
                    non_product_schemas=non_product_schemas,
                    statistics=statistics
                )
                
        except Exception as e:
            logger.error(f"Crawler failed: {e}")
            return CrawlerResult(
                success=False,
                error=f"Crawler error: {str(e)}",
                jsonld_schemas=[],
                product_schemas=[],
                non_product_schemas=[],
                statistics=statistics
            )
    
    async def _crawl_with_jsonld_extraction(self, domain_url: str, queue_manager: CrawlQueueManager, 
                                           max_products: int, min_jsonld_products: int) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Crawl the URL queue by processing batches of URLs in parallel, extracting JSON-LD, and updating the queue.
        
        For each batch:
        1. Take up to 5 URLs from the queue (or all available if less than 5)
        2. Process all URLs in the batch in parallel
        3. For each page:
           - Navigate to the page
           - Extract JSON-LD immediately
           - Extract all URLs from the page
        4. Merge all discovered URLs and run through URL prioritizer
        5. Update queue with new prioritized queue
        6. Continue to next batch
        
        Returns:
            tuple: (jsonld_schemas, statistics)
        """
        jsonld_schemas: List[Dict[str, Any]] = []
        max_pages_to_crawl = CRAWLER_MAX_PAGES_TO_CRAWL
        batch_size = 5  # Process 5 URLs in parallel
        
        # Statistics tracking
        total_links_processed = 0
        total_jsonld_extraction_attempts = 0
        total_jsonld_extraction_successes = 0
        
        logger.info(f"Starting parallel crawling. Queue size: {queue_manager.get_queue_size()}, batch size: {batch_size}")
        
        try:
            # Process batches until queue is empty or we've met our goals
            while not queue_manager.is_queue_empty() and len(queue_manager.get_visited_urls()) < max_pages_to_crawl:
                # Get next batch of URLs from the queue manager
                batch_urls = queue_manager.get_next_batch(batch_size)
                
                if not batch_urls:
                    break
                
                logger.info(f"🔄 Processing batch of {len(batch_urls)} URLs in parallel")
                
                # Mark URLs as visited before processing
                queue_manager.mark_urls_visited(batch_urls)
                
                # Process the batch in parallel
                batch_results = await self._process_url_batch(batch_urls)
                
                # Merge results from the batch
                batch_jsonld, batch_links_with_context, batch_stats = batch_results
                
                # Update our tracking
                jsonld_schemas.extend(batch_jsonld)
                total_links_processed += batch_stats['links_processed']
                total_jsonld_extraction_attempts += batch_stats['jsonld_attempts']
                total_jsonld_extraction_successes += batch_stats['jsonld_successes']
                
                # Check if we've met our JSON-LD goal by using the parser's categorization
                from .jsonld_parser import deduplicate_and_select_best_schemas, _is_product_schema
                
                # Do a quick categorization of current schemas to check Product count
                if jsonld_schemas:
                    product_schemas_count = sum(1 for schema in jsonld_schemas if _is_product_schema(schema))
                    if product_schemas_count >= min_jsonld_products:
                        logger.info(f"🎯 Met JSON-LD collection goal: {product_schemas_count} Product schemas found (total: {len(jsonld_schemas)} schemas)")
                        break
                
                # Merge all discovered links using the queue manager
                if batch_links_with_context:
                    # batch_links_with_context contains full links_with_context (URL + context)
                    # Merge new links into the queue
                    queue_manager.merge_new_links(batch_links_with_context)
                    
                    logger.info(f"🔄 Updated queue with fresh prioritized links. New queue size: {queue_manager.get_queue_size()}")

                    # Log top 10 queue URLs after merging new links
                    top_queue = queue_manager.get_top_queue_urls(10)
                    logger.info(f"🔝 Top 10 queue URLs after batch:")
                    for i, (url, score) in enumerate(top_queue, 1):
                        logger.info(f"   {i}. {url} (score: {score})")
                
                # Log status periodically
                if len(queue_manager.get_visited_urls()) % 10 == 0:  # Log every 10 pages
                    status = self._get_crawling_status(queue_manager, jsonld_schemas)
                    logger.info(f"📈 Crawling status: {status}")
            
            # Log final statistics
            logger.info(f"Parallel crawling completed. Visited {len(queue_manager.get_visited_urls())} pages, found {len(jsonld_schemas)} JSON-LD schemas")
            
            # Log detailed statistics
            logger.info(f"📊 DETAILED STATISTICS:")
            logger.info(f"   Pages visited: {len(queue_manager.get_visited_urls())}")
            logger.info(f"   Total links processed: {total_links_processed}")
            logger.info(f"   JSON-LD extraction attempts: {total_jsonld_extraction_attempts}")
            logger.info(f"   JSON-LD extraction successes: {total_jsonld_extraction_successes}")
                    
        except Exception as e:
            logger.error(f"Error in parallel crawling: {e}")
        
        # Prepare statistics dictionary
        statistics = {
            "pages_visited": len(queue_manager.get_visited_urls()),
            "links_processed": total_links_processed,
            "jsonld_extraction_attempts": total_jsonld_extraction_attempts,
            "jsonld_extraction_successes": total_jsonld_extraction_successes,
        }
        
        return jsonld_schemas, statistics
    
    async def _process_url_batch(self, batch_urls: List[str]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Process a batch of URLs in parallel.
        
        Args:
            batch_urls: List of URLs to process in parallel
            
        Returns:
            tuple: (jsonld_schemas, discovered_links_with_context, statistics)
        """
        # Create tasks for parallel processing
        tasks = []
        for url in batch_urls:
            tasks.append(self._process_single_url(url))
        
        if not tasks:
            return [], [], [], {"links_processed": 0, "jsonld_attempts": 0, "jsonld_successes": 0}
        
        # Execute all tasks in parallel
        logger.debug(f"🚀 Starting parallel processing of {len(tasks)} URLs")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_jsonld = []
        all_discovered_links_with_context = []
        total_links_processed = 0
        total_jsonld_attempts = 0
        total_jsonld_successes = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"❌ Error processing {batch_urls[i]}: {result}")
                continue
            
            jsonld, discovered_links_with_context, stats = result
            all_jsonld.extend(jsonld)
            all_discovered_links_with_context.extend(discovered_links_with_context)
            total_links_processed += stats['links_processed']
            total_jsonld_attempts += stats['jsonld_attempts']
            total_jsonld_successes += stats['jsonld_successes']
        
        logger.info(f"✅ Batch completed. Found {len(all_jsonld)} JSON-LD schemas, {len(all_discovered_links_with_context)} new links")
        
        batch_stats = {
            "links_processed": total_links_processed,
            "jsonld_attempts": total_jsonld_attempts,
            "jsonld_successes": total_jsonld_successes
        }
        
        return all_jsonld, all_discovered_links_with_context, batch_stats
    
    async def _process_single_url(self, url: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Process a single URL: navigate, extract JSON-LD, and discover links.
        
        Args:
            url: The URL to process
            
        Returns:
            tuple: (jsonld_schemas, discovered_links_with_context, statistics)
        """
        page = None
        try:
            logger.debug(f"🔍 Processing single URL: {url}")
            
            page = await self.browser_manager.new_page()
            
            # Navigate to the page
            await page.goto(url, timeout=PAGE_NAVIGATION_TIMEOUT, wait_until='domcontentloaded')
            
            # Wait for network idle, but continue even if it times out
            try:
                await page.wait_for_load_state('networkidle', timeout=NETWORK_IDLE_TIMEOUT)
                logger.debug(f"✅ Network is idle for: {url}")
            except PlaywrightTimeoutError:
                logger.warning(f"⚠️ Network idle timeout for: {url}, continuing with JSON-LD extraction anyway")
            
            # Extract JSON-LD
            logger.debug(f"🔍 Extracting JSON-LD from: {url}")
            extracted_jsonld = await self._extract_jsonld_from_page(page)
            
            # Extract links
            logger.debug(f"🔗 Extracting links from: {url}")
            from ..utils.utils import extract_links_with_context_js
            links_with_context = await page.evaluate(extract_links_with_context_js())
            
            # Debug: Check the structure of links_with_context
            logger.debug(f"🔍 Links with context type: {type(links_with_context)}")
            logger.debug(f"🔍 Links with context length: {len(links_with_context) if isinstance(links_with_context, list) else 'not a list'}")
            
            # Keep the full links_with_context for proper scoring
            discovered_links_with_context = []
            if isinstance(links_with_context, list):
                discovered_links_with_context = links_with_context  # Keep full context for proper scoring
            else:
                logger.warning(f"❌ Unexpected links_with_context type: {type(links_with_context)}")
                discovered_links_with_context = []
            
            stats = {
                "links_processed": len(discovered_links_with_context),
                "jsonld_attempts": 1,
                "jsonld_successes": 1 if extracted_jsonld else 0
            }
            
            logger.debug(f"✅ Completed processing {url}: {len(extracted_jsonld)} JSON-LD, {len(discovered_links_with_context)} links")
            return extracted_jsonld, discovered_links_with_context, stats
            
        except Exception as e:
            logger.warning(f"❌ Error processing {url}: {e}")
            return [], [], {"links_processed": 0, "jsonld_attempts": 1, "jsonld_successes": 0}
        finally:
            if page:
                await page.close()
    
    async def _extract_jsonld_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract JSON-LD data from the current page using json-ld-extraction-utils.
        
        Args:
            page: The Playwright page object
            
        Returns:
            List of JSON-LD schemas found on the page (raw, not deduplicated)
        """
        logger.debug(f"🔍 Extracting JSON-LD scripts from current page...")
        
        try:
            # Wait for JSON-LD scripts to load
            await page.wait_for_timeout(2000)
            
            # Use the robust JSON-LD extractor
            from ..utils.json_ld_extraction_utils import JSONLDExtractor
            extractor = JSONLDExtractor()
            
            # Extract JSON-LD scripts
            script_contents = await extractor.extract_jsonld_from_page(page)
            
            logger.debug(f"📄 Found {len(script_contents)} JSON-LD script tags")
            
            # Parse JSON-LD scripts (no deduplication at this stage)
            from .jsonld_parser import parse_json_ld_scripts
            logger.debug(f"🔍 Parsing JSON-LD scripts...")
            raw_extracted_data = parse_json_ld_scripts(script_contents)
            
            if raw_extracted_data:
                logger.info(f"✅ Successfully extracted {len(raw_extracted_data)} JSON-LD objects")
                # Log details about each extracted object
                for i, obj in enumerate(raw_extracted_data):
                    obj_type = obj.get('@type', 'Unknown')
                    obj_name = obj.get('name', 'Unknown')
                    logger.debug(f"📋 Object {i+1}: Type={obj_type}, Name={obj_name}")
                return raw_extracted_data
            else:
                logger.debug(f"⚠️ No JSON-LD data found on current page")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to extract JSON-LD from current page: {e}")
            return []
    
    def _get_crawling_status(self, queue_manager: CrawlQueueManager, jsonld_schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get current status of the crawling process."""
        queue_status = queue_manager.get_queue_status()
        return {
            "queue_size": queue_status["queue_size"],
            "visited_count": queue_status["visited_count"],
            "jsonld_schemas_found": len(jsonld_schemas),
            "next_url": queue_status["next_url"]
        } 