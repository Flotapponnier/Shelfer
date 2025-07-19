"""
JSON-LD Web Scraper

A robust Python library for extracting JSON-LD structured data from web pages.
"""

from .main import scrape_domain
from .utils.utils import (
    logger,
    USER_AGENTS,
)

__version__ = "1.0.0"
__author__ = "JSON-LD Scraper Team"

__all__ = [
    # Main function
    "scrape_domain",
    
    # Utility functions
    "logger",
    "USER_AGENTS",
] 