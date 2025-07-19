"""
Environment configuration loader utility
"""

import os
from pathlib import Path
from typing import Optional


def load_env_file(env_name: str) -> None:
    """
    Load environment variables from a specific environment file.
    
    Args:
        env_name: The environment name (development, test, production)
    """
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / f"{env_name}.env"
    
    if not env_file.exists():
        print(f"Warning: Environment file {env_file} not found")
        return
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Only set if not already set in environment
                if key not in os.environ:
                    os.environ[key] = value


def get_environment() -> str:
    """
    Get the current environment name.
    
    Returns:
        The environment name (development, test, production)
    """
    return os.getenv("ENVIRONMENT", "development").lower()


def setup_environment(env_name: Optional[str] = None) -> None:
    """
    Set up the environment by loading the appropriate configuration file.
    
    Args:
        env_name: The environment name to load. If None, uses ENVIRONMENT env var.
    """
    if env_name is None:
        env_name = get_environment()
    
    # Load the environment-specific configuration
    load_env_file(env_name)
    
    # Set the environment variable if not already set
    if "ENVIRONMENT" not in os.environ:
        os.environ["ENVIRONMENT"] = env_name


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        env = sys.argv[1]
    else:
        env = get_environment()
    
    setup_environment(env)
    print(f"Environment set to: {env}")
    print(f"ENVIRONMENT variable: {os.getenv('ENVIRONMENT')}")
    print(f"DEFAULT_CATEGORIES_MAX_PAGES_TO_CRAWL: {os.getenv('DEFAULT_CATEGORIES_MAX_PAGES_TO_CRAWL')}")
    print(f"DEFAULT_CATEGORIES_DATA_COLLECTION_GOAL: {os.getenv('DEFAULT_CATEGORIES_DATA_COLLECTION_GOAL')}") 