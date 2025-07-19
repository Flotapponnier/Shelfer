"""
Error handling utilities for JSON-LD extraction.

This module provides structured error handling and categorization for different types
of JSON-LD extraction failures.
"""

import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from .utils import logger


class ExtractionErrorType(Enum):
    """Enumeration of different types of JSON-LD extraction errors."""
    
    # Page loading errors
    NAVIGATION_TIMEOUT = "navigation_timeout"
    NETWORK_ERROR = "network_error"
    DNS_ERROR = "dns_error"
    SSL_ERROR = "ssl_error"
    HTTP_ERROR = "http_error"
    
    # Content access errors
    CONTENT_NOT_ACCESSIBLE = "content_not_accessible"
    JAVASCRIPT_ERROR = "javascript_error"
    DOM_ACCESS_ERROR = "dom_access_error"
    
    # JSON-LD specific errors
    NO_JSONLD_SCRIPTS = "no_jsonld_scripts"
    JSONLD_PARSE_ERROR = "jsonld_parse_error"
    NO_PRODUCT_SCHEMAS = "no_product_schemas"
    INVALID_JSONLD_STRUCTURE = "invalid_jsonld_structure"
    

    
    # Browser/technical errors
    BROWSER_ERROR = "browser_error"
    RESOURCE_LIMIT = "resource_limit"
    UNKNOWN_ERROR = "unknown_error"


class ExtractionError:
    """Structured error information for JSON-LD extraction failures."""
    
    def __init__(self, 
                 error_type: ExtractionErrorType,
                 message: str,
                 url: str,
                 details: Optional[Dict[str, Any]] = None,
                 timestamp: Optional[datetime] = None):
        self.error_type = error_type
        self.message = message
        self.url = url
        self.details = details or {}
        self.timestamp = timestamp or datetime.now()
        self.traceback = None
    
    def add_traceback(self, tb: str):
        """Add traceback information to the error."""
        self.traceback = tb
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response."""
        result = {
            "error_type": self.error_type.value,
            "message": self.message,
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }
        if self.traceback:
            result["traceback"] = self.traceback
        return result
    
    def __str__(self) -> str:
        return f"{self.error_type.value}: {self.message} (URL: {self.url})"


class ExtractionResult:
    """Result of JSON-LD extraction with detailed error information."""
    
    def __init__(self, 
                 success: bool,
                 products: List[Dict[str, Any]] = None,
                 errors: List[ExtractionError] = None,
                 statistics: Dict[str, Any] = None):
        self.success = success
        self.products = products or []
        self.errors = errors or []
        self.statistics = statistics or {}
    
    def add_error(self, error: ExtractionError):
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for API response."""
        return {
            "success": self.success,
            "products": self.products,
            "errors": [error.to_dict() for error in self.errors],
            "statistics": self.statistics
        }


def categorize_error(exception: Exception, url: str, context: Dict[str, Any] = None) -> ExtractionError:
    """
    Categorize an exception into a specific error type with detailed information.
    
    Args:
        exception: The exception that occurred
        url: The URL being processed when the error occurred
        context: Additional context about the operation
        
    Returns:
        ExtractionError with categorized error information
    """
    context = context or {}
    error_message = str(exception)
    exception_type = type(exception).__name__
    
    # Categorize based on exception type and message
    if "timeout" in error_message.lower() or "TimeoutError" in exception_type:
        error_type = ExtractionErrorType.NAVIGATION_TIMEOUT
        message = f"Page navigation timed out: {error_message}"
    
    elif "network" in error_message.lower() or "ConnectionError" in exception_type:
        error_type = ExtractionErrorType.NETWORK_ERROR
        message = f"Network connection error: {error_message}"
    
    elif "dns" in error_message.lower() or "NameResolutionError" in exception_type:
        error_type = ExtractionErrorType.DNS_ERROR
        message = f"DNS resolution failed: {error_message}"
    
    elif "ssl" in error_message.lower() or "SSLError" in exception_type:
        error_type = ExtractionErrorType.SSL_ERROR
        message = f"SSL/TLS error: {error_message}"
    
    elif "404" in error_message or "not found" in error_message.lower():
        error_type = ExtractionErrorType.HTTP_ERROR
        message = f"HTTP error (404): Page not found"
    
    elif "403" in error_message or "forbidden" in error_message.lower():
        error_type = ExtractionErrorType.HTTP_ERROR
        message = f"HTTP error (403): Access forbidden"
    
    elif "500" in error_message or "server error" in error_message.lower():
        error_type = ExtractionErrorType.HTTP_ERROR
        message = f"HTTP error (500): Server error"
    
    elif "JSONDecodeError" in exception_type or ("json" in error_message.lower() and "decode" in error_message.lower()):
        error_type = ExtractionErrorType.JSONLD_PARSE_ERROR
        message = f"JSON parsing error: {error_message}"
    
    elif "javascript" in error_message.lower() or "js" in error_message.lower():
        error_type = ExtractionErrorType.JAVASCRIPT_ERROR
        message = f"JavaScript execution error: {error_message}"
    
    elif "dom" in error_message.lower() and "element" in error_message.lower():
        error_type = ExtractionErrorType.DOM_ACCESS_ERROR
        message = f"DOM access error: {error_message}"
    
    elif "browser" in error_message.lower() or "playwright" in error_message.lower():
        error_type = ExtractionErrorType.BROWSER_ERROR
        message = f"Browser error: {error_message}"
    
    else:
        error_type = ExtractionErrorType.UNKNOWN_ERROR
        message = f"Unknown error ({exception_type}): {error_message}"
    
    # Create error with context
    error = ExtractionError(error_type, message, url, context)
    error.add_traceback(traceback.format_exc())
    
    return error


def create_no_jsonld_error(url: str, script_count: int = 0, context: Dict[str, Any] = None) -> ExtractionError:
    """Create a specific error for when no JSON-LD scripts are found."""
    context = context or {}
    context["jsonld_scripts_found"] = script_count
    
    if script_count == 0:
        message = "No JSON-LD script tags found on the page"
        error_type = ExtractionErrorType.NO_JSONLD_SCRIPTS
    else:
        message = f"Found {script_count} JSON-LD script tags but no valid product schemas"
        error_type = ExtractionErrorType.NO_PRODUCT_SCHEMAS
    
    return ExtractionError(error_type, message, url, context)








def aggregate_errors(errors: List[ExtractionError]) -> Dict[str, Any]:
    """
    Aggregate errors by type for summary reporting.
    
    Args:
        errors: List of extraction errors
        
    Returns:
        Dictionary with error counts and summaries
    """
    error_counts = {}
    error_summaries = {}
    
    for error in errors:
        error_type = error.error_type.value
        if error_type not in error_counts:
            error_counts[error_type] = 0
            error_summaries[error_type] = []
        
        error_counts[error_type] += 1
        error_summaries[error_type].append({
            "url": error.url,
            "message": error.message,
            "timestamp": error.timestamp.isoformat()
        })
    
    return {
        "total_errors": len(errors),
        "error_counts": error_counts,
        "error_summaries": error_summaries,
        "most_common_error": max(error_counts.items(), key=lambda x: x[1])[0] if error_counts else None
    } 