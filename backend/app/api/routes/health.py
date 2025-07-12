"""Health check API routes"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.models.requests.health import HealthResponse
from app.config.settings import Settings
from app.config.settings import get_settings
from app.utils.simple_usage import get_simple_usage_tracker

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Enhanced health check endpoint that returns the current status of the application
    and its dependencies.
    """
    # Check service configurations
    services = {}
    
    # Check if API keys are configured
    if settings.openai_api_key:
        services["openai"] = "configured"
    else:
        services["openai"] = "not_configured"
    
    if settings.anthropic_api_key:
        services["anthropic"] = "configured"
    else:
        services["anthropic"] = "not_configured"
    
    # Check AI service type matches configuration
    services["ai_service_type"] = settings.ai_service_type
    if settings.ai_service_type == "anthropic" and not settings.anthropic_api_key:
        services["ai_service_status"] = "misconfigured"
    elif settings.ai_service_type == "openai" and not settings.openai_api_key:
        services["ai_service_status"] = "misconfigured"
    else:
        services["ai_service_status"] = "configured"
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.environment,
        services=services
    )


@router.get("/usage/summary")
async def get_usage_summary() -> Dict[str, Any]:
    """
    Get daily usage summary for monitoring.
    Simple endpoint for administrators to monitor system usage.
    """
    usage_tracker = get_simple_usage_tracker()
    return usage_tracker.get_usage_summary()


