"""
Environment initialization module

This module handles environment setup and should be imported before any other modules
to ensure proper configuration loading.
"""

from scraper.utils.env_loader import setup_environment

def initialize_environment():
    """Initialize the environment by loading the appropriate configuration file."""
    setup_environment()

# Initialize environment when this module is imported
initialize_environment() 