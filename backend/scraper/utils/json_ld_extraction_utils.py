"""
Utilities for web scraping operations.

This module provides robust, reusable functions for web scraping with retry logic,
error handling, resource management, and failure detection.
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable, Awaitable
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlparse
from .utils import logger, take_error_screenshot
from .domain_utils import is_same_domain

class JSONLDExtractor:
    """JSON-LD extraction utilities."""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 1, timeout: int = 10000):
        self.retry_handler = _RetryHandler(delay, max_retries, timeout)
    
    async def extract_jsonld_from_page(self, page: Page) -> List[str]:
        """Extract JSON-LD scripts from a page."""
        return await page.evaluate(
            """() => Array.from(
                document.querySelectorAll('script[type="application/ld+json"]')
            ).map(script => script.textContent || '')"""
        ) 

class _RetryHandler:
    """Retry handler utilities with retry logic and error handling."""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 1, timeout: int = 10000):
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout
    
    async def execute_with_retry(self, operation_name: str, operation_func: Callable[..., Awaitable[Any]], 
                               *args, **kwargs) -> Any:
        """
        Execute an operation with retry logic and proper error handling.
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: Async function to execute
            *args, **kwargs: Arguments to pass to the operation
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Executing {operation_name} (attempt {attempt + 1}/{self.max_retries + 1})")
                result = await operation_func(*args, **kwargs)
                return result
                
            except PlaywrightTimeoutError as e:
                logger.warning(f"Timeout error in {operation_name} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(self.delay)
                else:
                    raise
            except Exception as e:
                logger.error(f"Error in {operation_name} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(self.delay)
                else:
                    raise
        
        raise Exception(f"Failed to execute {operation_name} after {self.max_retries + 1} attempts")
    
    async def safe_page_operation(self, browser_manager, operation_func: Callable[[Page, ...], Awaitable[Any]], 
                                *args, **kwargs) -> Any:
        """
        Execute a page operation with proper resource management.
        
        Args:
            browser_manager: Browser manager instance
            operation_func: Async function that takes a page as first argument
            *args, **kwargs: Additional arguments for the operation
            
        Returns:
            Result of the operation
        """
        page = None
        try:
            page = await browser_manager.new_page()
            return await operation_func(page, *args, **kwargs)
        finally:
            if page:
                await page.close()


