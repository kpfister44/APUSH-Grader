"""Health check API routes"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.models.requests.health import HealthResponse
from app.config.settings import Settings
from app.api.deps import get_app_settings
from app.services.usage.tracker import get_usage_tracker
from app.services.dependencies.service_locator import get_service_locator

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_app_settings)) -> HealthResponse:
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
    usage_tracker = get_usage_tracker()
    summary = usage_tracker.get_usage_summary()
    
    return {
        "usage_summary": summary,
        "limits": {
            "daily_essay_limit": usage_tracker.daily_essay_limit,
            "daily_word_limit": usage_tracker.daily_word_limit,
            "cost_alert_threshold": usage_tracker.cost_alert_threshold
        }
    }


@router.get("/health/detailed")
async def detailed_health_check(settings: Settings = Depends(get_app_settings)) -> Dict[str, Any]:
    """
    Detailed health check with service verification for administrators.
    Simple checks without heavy dependencies.
    """
    # Basic service checks
    service_checks = {}
    
    # Check service locator
    try:
        service_locator = get_service_locator()
        api_coordinator = service_locator.get_api_coordinator()
        service_checks["service_locator"] = "healthy"
        service_checks["api_coordinator"] = "available"
    except Exception as e:
        service_checks["service_locator"] = f"error: {str(e)}"
        service_checks["api_coordinator"] = "unavailable"
    
    # Check AI service
    try:
        ai_service = service_locator.get_ai_service()
        if settings.ai_service_type == "mock":
            service_checks["ai_service"] = "healthy (mock)"
        elif settings.ai_service_type == "anthropic":
            if hasattr(ai_service, 'client') and ai_service.client:
                service_checks["ai_service"] = "healthy (anthropic)"
            else:
                service_checks["ai_service"] = "degraded (anthropic not initialized)"
        else:
            service_checks["ai_service"] = f"unknown type: {settings.ai_service_type}"
    except Exception as e:
        service_checks["ai_service"] = f"error: {str(e)}"
    
    # Check usage tracker
    try:
        usage_tracker = get_usage_tracker()
        can_process, _ = usage_tracker.can_process_essay("health-check", 100)
        service_checks["usage_tracker"] = "healthy"
    except Exception as e:
        service_checks["usage_tracker"] = f"error: {str(e)}"
    
    # Get usage statistics
    try:
        usage_stats = usage_tracker.get_usage_summary()
    except Exception:
        usage_stats = {"error": "unable to get usage stats"}
    
    # Simple status determination
    errors = [check for check in service_checks.values() if "error" in check.lower()]
    degraded = [check for check in service_checks.values() if "degraded" in check.lower()]
    
    if errors:
        overall_status = "unhealthy"
    elif degraded:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    return {
        "overall_status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": settings.environment,
        "version": "1.0.0",
        "service_checks": service_checks,
        "configuration": {
            "ai_service_type": settings.ai_service_type,
            "environment": settings.environment,
            "debug": settings.debug
        },
        "usage_today": usage_stats
    }