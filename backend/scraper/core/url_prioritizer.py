"""
URL Prioritization System for E-commerce Product Discovery

This module provides intelligent URL scoring and prioritization for e-commerce websites.
It assigns numerical scores to URLs based on their likelihood of being product pages,
with higher scores indicating higher priority for product discovery.
"""

import json
import re
import os
from typing import Dict, Any, List, Tuple, Set
from urllib.parse import urlparse


class UrlPrioritizer:
    """Intelligent URL prioritizer for e-commerce websites using a scoring system."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the URL prioritizer with configuration from JSON file.
        
        Args:
            config_path: Path to the JSON configuration file. If None, uses default path.
        """
        if config_path is None:
            # Default to the config file in the same directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'url_prioritizer_config.json')
        
        self.config = self._load_config(config_path)
        self.url_patterns = self._parse_url_patterns()
        self.html_context_patterns = self.config.get('html_context_patterns', {})
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to the JSON configuration file
            
        Returns:
            Dictionary containing the configuration
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in configuration file {config_path}: {e}", e.doc, e.pos)
    
    def _parse_url_patterns(self) -> List[Tuple[str, float]]:
        """
        Parse URL patterns from the configuration into the format expected by the scoring logic.
        
        Returns:
            List of tuples (pattern, score) for URL pattern matching
        """
        patterns = []
        for pattern_data in self.config.get('url_patterns', []):
            pattern = pattern_data.get('pattern')
            score = pattern_data.get('score')
            if pattern is not None and score is not None:
                patterns.append((pattern, float(score)))
        return patterns
        # URL scoring patterns with their respective scores
        
    
    def prioritize_urls(self, links_with_context: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """
        Score and prioritize a list of links with their HTML context.
        
        Args:
            links_with_context: List of dictionaries, each containing:
                - 'url': The URL string
                - 'context': Dictionary with HTML context (text, className, id, etc.)
            
        Returns:
            List of tuples (url, score) sorted by score in descending order
        """
        scored_links = []
        
        for link_data in links_with_context:
            url = link_data['url']
            context = link_data.get('context', {})
            
            # Score the URL
            url_score = self._calculate_url_score(url)
            
            # Score the context
            context_score = self._calculate_context_score(context)
            
            # Add scores together
            total_score = url_score + context_score
            
            scored_links.append((url, total_score))
        
        # Sort by score in descending order
        scored_links.sort(key=lambda x: x[1], reverse=True)
        
        return scored_links
    
    def _calculate_url_score(self, url: str) -> float:
        """
        Calculate a score for a URL based on its pattern.
        
        Args:
            url: The URL to score
            
        Returns:
            float: URL score (can be negative for file extensions, 0-100 for content pages)
        """
        # Check URL patterns (return immediately when first match is found)
        for pattern, score in self.url_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return float(score)
        
        # Additional scoring for URLs ending in .html
        if url.endswith('.html'):
            # Check if it contains product-related words
            product_words = ['product', 'item', 'buy', 'detail', 'view', 'pdp']
            if any(word in url.lower() for word in product_words):
                return 85.0  # High score for product-like .html URLs
            else:
                return 40.0  # Medium score for other .html URLs
        
        # Additional scoring for URLs with common e-commerce patterns
        parsed_url = urlparse(url)
        if parsed_url.path and parsed_url.path != '/':
            # Check for shop/store/catalog patterns
            shop_words = ['shop', 'store', 'catalog', 'browse']
            if any(word in url.lower() for word in shop_words):
                return 50.0  # Medium score for shop-like URLs
        
        # Default score for unrecognized patterns
        return 20.0
    
    def _calculate_context_score(self, context: Dict[str, Any]) -> float:
        """
        Calculate a score for HTML context based on patterns found in class names, IDs, text, etc.
        
        Args:
            context: Dictionary containing HTML context information
            
        Returns:
            float: Context score (can be positive or negative)
        """
        # Check each category of patterns (return immediately when first match is found)
        for category, config in self.html_context_patterns.items():
            patterns = config['patterns']
            pattern_score = config['score']
            
            for pattern in patterns:
                if self._context_contains_pattern(context, pattern):
                    return pattern_score  # Return immediately on first match
        
        return 0.0
    
    def _context_contains_pattern(self, context: Dict[str, Any], pattern: str) -> bool:
        """
        Check if the HTML context contains a specific pattern, including parent, sibling, children, and grandchildren text fields.
        
        Args:
            context: Dictionary containing HTML context information
            pattern: Pattern to search for
        
        Returns:
            bool: True if pattern is found in context
        """
        pattern_lower = pattern.lower()
        # Use simple substring matching to be very broad
        # This allows "product" to match anywhere in the string, even embedded in random text
        regex_pattern = re.compile(rf'{re.escape(pattern_lower)}', re.IGNORECASE)

        def check_element_attributes(element_data: Dict[str, Any]) -> bool:
            if not element_data:
                return False
            for field in ['text', 'title', 'class', 'id']:
                val = element_data.get(field, '')
                if regex_pattern.search(val):
                    return True
            for attr_name, attr_value in element_data.get('data-*', {}).items():
                if regex_pattern.search(attr_name) or regex_pattern.search(attr_value):
                    return True
            return False

        # Check the link element itself
        if check_element_attributes(context):
            return True

        # Check parentText
        parent_text = context.get('parentText', '')
        if isinstance(parent_text, str) and regex_pattern.search(parent_text):
            return True

        # Check childrenTexts and grandchildrenTexts of anchor
        for field in ['childrenTexts', 'grandchildrenTexts']:
            texts = context.get(field, [])
            for t in texts:
                if isinstance(t, str) and regex_pattern.search(t):
                    return True

        # Check siblingTexts (array of dicts with text, childrenTexts, grandchildrenTexts)
        for sibling in context.get('siblingTexts', []):
            if isinstance(sibling, dict):
                if regex_pattern.search(sibling.get('text', '')):
                    return True
                for t in sibling.get('childrenTexts', []):
                    if isinstance(t, str) and regex_pattern.search(t):
                        return True
                for t in sibling.get('grandchildrenTexts', []):
                    if isinstance(t, str) and regex_pattern.search(t):
                        return True

        # Check parentChildrenTexts (array of dicts with text, childrenTexts, grandchildrenTexts)
        for child in context.get('parentChildrenTexts', []):
            if isinstance(child, dict):
                if regex_pattern.search(child.get('text', '')):
                    return True
                for t in child.get('childrenTexts', []):
                    if isinstance(t, str) and regex_pattern.search(t):
                        return True
                for t in child.get('grandchildrenTexts', []):
                    if isinstance(t, str) and regex_pattern.search(t):
                        return True

        # Check ancestor (only 1 layer up, legacy)
        parent = context.get('parent', {})
        if parent and check_element_attributes(parent):
            return True

        # Check children of the link element and its parent (legacy recursive)
        checked_elements = set()
        def check_children_recursive(element_data: Dict[str, Any], depth: int = 0) -> bool:
            if depth > 3 or not element_data:
                return False
            element_id = id(element_data)
            if element_id in checked_elements:
                return False
            checked_elements.add(element_id)
            children = element_data.get('children', [])
            for child in children:
                if check_element_attributes(child):
                    return True
                if depth < 3 and check_children_recursive(child, depth + 1):
                    return True
            return False
        if check_children_recursive(context):
            return True
        if parent:
            if check_children_recursive(parent):
                return True
        return False
    
 