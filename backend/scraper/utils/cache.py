"""
Simple caching utilities for scraper performance optimization.
"""

import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
import hashlib
import json


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        """
        Initialize cache.
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry['expires']:
            del self._cache[key]
            return None
        
        entry['last_accessed'] = time.time()
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl,
            'last_accessed': time.time()
        }
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        """Get number of cached entries."""
        return len(self._cache)


def cache_key_from_args(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    # Create a stable string representation
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, cache_instance: SimpleCache = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds
        cache_instance: Optional cache instance, creates new one if None
    """
    if cache_instance is None:
        cache_instance = SimpleCache(ttl)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{cache_key_from_args(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Compute result and cache it
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl)
            return result
        
        # Add cache management methods to function
        wrapper.cache_clear = cache_instance.clear
        wrapper.cache_delete = lambda key: cache_instance.delete(f"{func.__name__}:{key}")
        wrapper.cache_size = cache_instance.size
        
        return wrapper
    
    return decorator


# Global cache instances for different purposes
url_analysis_cache = SimpleCache(ttl=600)  # 10 minutes for URL analysis
product_score_cache = SimpleCache(ttl=300)  # 5 minutes for product scoring