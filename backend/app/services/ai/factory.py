"""
AI service factory for creating appropriate AI service implementations.

Provides a factory function to create AI services based on configuration.
"""

import logging
from typing import Optional

from app.config.settings import Settings
from app.services.ai.base import AIService
from app.services.ai.mock_service import MockAIService
from app.services.ai.anthropic_service import AnthropicService
from app.services.base.exceptions import ConfigurationError


logger = logging.getLogger(__name__)


def create_ai_service(settings: Optional[Settings] = None) -> AIService:
    """
    Create appropriate AI service based on configuration.
    
    Args:
        settings: Application settings (optional, will load from config if not provided)
        
    Returns:
        Configured AI service instance
        
    Raises:
        ConfigurationError: If AI service type is not supported
    """
    if settings is None:
        from app.config.settings import get_settings
        settings = get_settings()
    
    ai_service_type = settings.ai_service_type.lower()
    
    if ai_service_type == "mock":
        logger.debug("Creating mock AI service")
        return MockAIService(settings)
    elif ai_service_type == "anthropic":
        logger.debug("Creating Anthropic AI service")
        return AnthropicService(settings)
    else:
        raise ConfigurationError(f"Unsupported AI service type: {ai_service_type}")


def get_available_ai_services() -> list[str]:
    """
    Get list of available AI service types.
    
    Returns:
        List of supported AI service type names
    """
    return ["mock", "anthropic"]