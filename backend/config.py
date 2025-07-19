"""
Configuration settings for the Agent Readiness Evaluator API
"""

import os
from typing import Optional

# Environment Detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# Server Configuration
DEFAULT_PORT = 9991
DEFAULT_HOST = "127.0.0.1"

# Get configuration from environment variables with defaults
PORT = int(os.getenv("PORT", DEFAULT_PORT))
HOST = os.getenv("HOST", DEFAULT_HOST)

# Return Saved Response Immediately Mode
RETURN_SAVED_RESPONSE_IMMEDIATELY = os.getenv("RETURN_SAVED_RESPONSE_IMMEDIATELY", "false").lower() == "true"

# API Configuration
MAX_PRODUCTS = int(os.getenv("MAX_PRODUCTS", "20"))

# Scraper Configuration
# Note: Use CRAWLER_MAX_PAGES_TO_CRAWL and CRAWLER_PRODUCT_COLLECTION_GOAL instead

# Environment-specific default values for Crawler Configuration
def get_crawler_config():
    """Get environment-specific crawler configuration"""
    if ENVIRONMENT == "production":
        return {
            "max_pages_to_crawl": int(os.getenv("DEFAULT_CRAWLER_MAX_PAGES_TO_CRAWL", "200")),
            "data_collection_goal": int(os.getenv("CRAWLER_PRODUCT_COLLECTION_GOAL", "100"))
        }
    elif ENVIRONMENT == "test":
        return {
            "max_pages_to_crawl": int(os.getenv("DEFAULT_CRAWLER_MAX_PAGES_TO_CRAWL", "10")),
            "data_collection_goal": int(os.getenv("CRAWLER_PRODUCT_COLLECTION_GOAL", "5"))
        }
    else:  # development
        return {
            "max_pages_to_crawl": int(os.getenv("DEFAULT_CRAWLER_MAX_PAGES_TO_CRAWL", "50")),
            "data_collection_goal": int(os.getenv("CRAWLER_PRODUCT_COLLECTION_GOAL", "5"))
        }

# Crawler Configuration
crawler_config = get_crawler_config()
CRAWLER_MAX_PAGES_TO_CRAWL = crawler_config["max_pages_to_crawl"]
CRAWLER_PRODUCT_COLLECTION_GOAL = crawler_config["data_collection_goal"]

# Timeout Configuration
PAGE_NAVIGATION_TIMEOUT = int(os.getenv("PAGE_NAVIGATION_TIMEOUT", "30000"))  # 30 seconds
NETWORK_IDLE_TIMEOUT = int(os.getenv("NETWORK_IDLE_TIMEOUT", "15000"))  # 15 seconds

# Product patterns
DEFAULT_PRODUCT_PATTERNS = ['/product', '/products', '/shop', '/item', '/p/']

def print_config():
    """Print current configuration"""
    print(f"Server Configuration:")
    print(f"  Host: {HOST}")
    print(f"  Port: {PORT}")
    print(f"  Return Saved Response Immediately: {RETURN_SAVED_RESPONSE_IMMEDIATELY}")
    print(f"  Environment: {ENVIRONMENT}")
    print(f"  Max Products: {MAX_PRODUCTS}")
    print(f"Scraper Configuration:")
    print(f"  Using CRAWLER_MAX_PAGES_TO_CRAWL and CRAWLER_PRODUCT_COLLECTION_GOAL")
    print(f"Crawler Configuration:")
    print(f"  Max Pages to Crawl: {CRAWLER_MAX_PAGES_TO_CRAWL}")
    print(f"  Data Collection Goal: {CRAWLER_PRODUCT_COLLECTION_GOAL}")
    print(f"Timeout Configuration:")
    print(f"  Page Navigation Timeout: {PAGE_NAVIGATION_TIMEOUT}ms")
    print(f"  Network Idle Timeout: {NETWORK_IDLE_TIMEOUT}ms") 