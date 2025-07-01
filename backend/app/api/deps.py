"""API dependency injection"""

from functools import lru_cache
from app.config.settings import Settings, get_settings


@lru_cache()
def get_app_settings() -> Settings:
    """Get application settings dependency"""
    return get_settings()