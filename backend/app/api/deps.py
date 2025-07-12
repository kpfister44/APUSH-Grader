"""API dependencies for simplified architecture"""

from typing import Annotated
from functools import lru_cache
from fastapi import Depends
from app.config.settings import Settings, get_settings


@lru_cache()
def get_app_settings() -> Settings:
    """Get application settings dependency"""
    return get_settings()


# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_app_settings)]