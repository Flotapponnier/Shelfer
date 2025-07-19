"""Configuration package for the scraper."""

from .detection_config import DetectionConfig, get_detection_config, reload_config

__all__ = ['DetectionConfig', 'get_detection_config', 'reload_config']