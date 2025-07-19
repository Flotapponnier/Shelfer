"""
Domain utility functions for URL and domain validation.
"""

from urllib.parse import urlparse, urljoin
from typing import Optional


def clean_domain_url(domain_url: str) -> str:
    """
    Clean and standardize a domain URL.
    
    Args:
        domain_url: The raw domain URL from frontend
        
    Returns:
        Cleaned and standardized domain URL
        
    Examples:
        >>> clean_domain_url("example.com")
        "https://example.com"
        >>> clean_domain_url("https://example.com/")
        "https://example.com"
        >>> clean_domain_url("  https://example.com?param=value#fragment  ")
        "https://example.com"
    """
    if not domain_url or not domain_url.strip():
        raise ValueError("Domain URL cannot be empty")
    
    # Remove leading/trailing whitespace
    domain_url = domain_url.strip()
    
    # Add protocol if missing
    if not domain_url.startswith(('http://', 'https://')):
        domain_url = 'https://' + domain_url
    
    # Parse the URL to extract just the domain
    try:
        parsed = urlparse(domain_url)
        
        # Validate that we have a proper domain
        if not parsed.netloc or parsed.netloc == '':
            raise ValueError(f"Invalid domain URL format: {domain_url}")
        
        # Reconstruct with just scheme, netloc (domain), and path (but remove trailing slash)
        clean_url = f"{parsed.scheme}://{parsed.netloc}"
        if parsed.path and parsed.path != '/':
            clean_url += parsed.path.rstrip('/')
        return clean_url
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Invalid domain URL format: {domain_url}") from e


def is_same_domain(url: str, domain_url: str) -> bool:
    """
    Check if a URL is from the same domain, handling subdomains and relative URLs properly.
    
    Args:
        url: The URL to check (can be relative or absolute)
        domain_url: The base domain URL to compare against
        
    Returns:
        bool: True if the URL is from the same domain or a subdomain
        
    Examples:
        >>> is_same_domain("https://www.example.com/product", "https://example.com")
        True
        >>> is_same_domain("https://shop.example.com/item", "https://example.com")
        True
        >>> is_same_domain("product/123", "https://example.com")
        True
        >>> is_same_domain("/product/123", "https://example.com")
        True
        >>> is_same_domain("https://othersite.com/product", "https://example.com")
        False
    """
    try:
        # Return False if url is empty or only whitespace
        if not url or not url.strip():
            return False
        # If the URL is relative, resolve it against the domain URL
        if not url.startswith(('http://', 'https://')):
            url = urljoin(domain_url, url)
        
        # Parse both URLs
        url_parsed = urlparse(url)
        domain_parsed = urlparse(domain_url)
        
        # Check if we have valid netlocs
        if not url_parsed.netloc or not domain_parsed.netloc:
            return False
        
        url_domain = url_parsed.netloc
        domain_domain = domain_parsed.netloc
        
        # Handle exact match
        if url_domain == domain_domain:
            return True
        
        # Handle subdomain cases
        # If domain_url is example.com, accept www.example.com, sub.example.com, etc.
        if domain_domain.startswith('www.'):
            base_domain = domain_domain[4:]  # Remove www.
        else:
            base_domain = domain_domain
        
        # Check if url_domain is a subdomain of base_domain
        if url_domain == base_domain or url_domain.endswith('.' + base_domain):
            return True
        
        return False
    except:
        return False 