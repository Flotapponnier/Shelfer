"""
Configuration management for main product detection.

This module provides centralized configuration for the main product detection algorithm,
allowing for easy tuning and customization without code changes.
"""

from typing import Dict, Any, List
import os
import json
from pathlib import Path


class DetectionConfig:
    """Manages configuration for main product detection algorithm."""
    
    def __init__(self, config_file: str = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to custom config file
        """
        self.config = self._load_config(config_file)
        self._validate_config()
    
    def _load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    custom_config = json.load(f)
                # Merge with defaults
                config = self._get_default_config()
                config.update(custom_config)
                return config
            except Exception as e:
                print(f"Warning: Failed to load config file {config_file}: {e}")
                return self._get_default_config()
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            # URL patterns that indicate main product pages
            'main_product_url_patterns': [
                r'/products?/([^/]+)/?$',           # /product/name or /products/name
                r'/liquids/([^/]+)/?$',            # /liquids/name (for e-liquid sites)
                r'/item/([^/]+)/?$',               # /item/name
                r'/p/([^/]+)/?$',                  # /p/name
                r'/buy/([^/]+)/?$',                # /buy/name
                r'/detail/([^/]+)/?$',             # /detail/name
                r'/shop/([^/]+)/?$',               # /shop/name (when single product)
                r'/([^/]+)\.html?$',               # product-name.html
                r'/([^/]+)\.html?[#?]',            # product-name.html with params/hash
            ],
            
            # Keywords that indicate suggestions/recommendations (negative signals)
            'suggestion_indicators': [
                'related', 'recommended', 'suggestion', 'similar', 'other',
                'you-might', 'also-like', 'customers-also', 'more-from',
                'recently-viewed', 'trending', 'popular', 'bestseller',
                'bundle', 'addon', 'accessory', 'complement'
            ],
            
            # CSS class/ID patterns for main product areas (positive signals)
            'main_product_indicators': [
                'product-main', 'product-detail', 'product-info', 'product-page',
                'main-product', 'primary-product', 'product-hero', 'product-focus',
                'pdp-main', 'item-detail', 'product-container', 'product-wrapper'
            ],
            
            # Scoring thresholds
            'scoring_thresholds': {
                'url_match_strong': 70,        # Strong URL match threshold
                'score_difference_clear': 15,  # Clear winner margin
                'high_confidence_minimum': 40  # Minimum for high confidence
            },
            
            # Scoring weights - these can be tuned for better performance
            'scoring_weights': {
                'url_pattern_match': 25,
                'word_match_per_word': 20,
                'high_ratio_bonus': 30,
                'exact_substring_match': 50,
                'schema_essential_field': 5,
                'schema_detailed_field': 2,
                'offer_price': 8,
                'html_main_indicator': 15,
                'html_position_above_fold': 10
            },
            
            # Algorithm settings
            'algorithm_settings': {
                'min_word_length': 3,          # Minimum word length for matching
                'max_html_search_elements': 50, # Limit HTML search for performance
                'url_match_ratio_thresholds': {
                    'excellent': 0.8,  # 80%+ word match
                    'good': 0.6,       # 60%+ word match
                    'fair': 0.4        # 40%+ word match
                }
            }
        }
    
    def _validate_config(self):
        """Validate configuration values."""
        required_keys = [
            'main_product_url_patterns',
            'suggestion_indicators', 
            'main_product_indicators',
            'scoring_thresholds',
            'scoring_weights'
        ]
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        # Validate scoring thresholds are positive
        thresholds = self.config['scoring_thresholds']
        for threshold_name, value in thresholds.items():
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"Invalid threshold {threshold_name}: must be positive number")
        
        # Validate scoring weights are positive
        weights = self.config['scoring_weights']
        for weight_name, value in weights.items():
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"Invalid weight {weight_name}: must be positive number")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def update(self, updates: Dict[str, Any]):
        """Update configuration with new values."""
        self.config.update(updates)
        self._validate_config()
    
    def save_to_file(self, file_path: str):
        """Save current configuration to file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(self.config, f, indent=2)


# Global config instance
_config_instance = None

def get_detection_config() -> DetectionConfig:
    """Get the global detection configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = DetectionConfig()
    return _config_instance

def reload_config(config_file: str = None):
    """Reload configuration from file."""
    global _config_instance
    _config_instance = DetectionConfig(config_file)