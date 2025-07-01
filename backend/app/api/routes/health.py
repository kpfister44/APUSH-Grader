"""Health check API routes"""

from fastapi import APIRouter, Depends
from app.models.requests.health import HealthResponse
from app.config.settings import Settings
from app.api.deps import get_app_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_app_settings)) -> HealthResponse:
    """
    Health check endpoint that returns the current status of the application
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
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.environment,
        services=services
    )