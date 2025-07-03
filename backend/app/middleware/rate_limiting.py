"""Rate limiting middleware for APUSH Grader API"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


def get_remote_address_or_default(request: Request) -> str:
    """Get the remote address, with fallback for development"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
        
    client_host = getattr(request.client, "host", None)
    if client_host:
        return client_host
        
    return "127.0.0.1"


# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address_or_default,
    storage_uri="memory://",
    default_limits=["100 per hour"]  # Default fallback limit
)


def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler with user-friendly messages"""
    # Extract retry_after from the exception detail if available
    retry_after = getattr(exc, 'retry_after', 60)  # Default to 60 seconds
    
    return JSONResponse(
        status_code=429,
        content={
            "detail": {
                "error": "Rate limit exceeded",
                "message": "Please wait a moment before submitting another essay. This helps us manage costs and ensure quality service for all teachers.",
                "retry_after": retry_after
            }
        }
    )