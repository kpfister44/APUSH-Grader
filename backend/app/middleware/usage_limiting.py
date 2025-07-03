"""
Usage limiting middleware for basic daily limits and cost protection
"""

from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.usage.tracker import get_usage_tracker
from app.services.logging.structured_logger import get_logger


class UsageLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce daily usage limits"""
    
    def __init__(self, app):
        super().__init__(app)
        self.usage_tracker = get_usage_tracker()
        self.logger = get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check usage limits before processing essay grading requests"""
        
        # Only apply usage limits to essay grading endpoint
        if not (request.method == "POST" and request.url.path == "/api/v1/grade"):
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Get essay word count from request body for validation
        # We need to read the body to check word count, but we need to be careful
        # not to consume it (FastAPI will need it later)
        try:
            body = await request.body()
            # Parse the JSON to get essay text length
            import json
            data = json.loads(body) if body else {}
            essay_text = data.get("essay_text", "")
            word_count = len(essay_text.split()) if essay_text else 0
            
            # Restore the body for FastAPI to process
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive
            
        except Exception as e:
            # If we can't parse the request, let it through 
            # (FastAPI will handle the validation error)
            self.logger.warning(
                "Could not parse request body for usage checking",
                client_ip=client_ip,
                error=str(e)
            )
            return await call_next(request)
        
        # Check if essay can be processed
        can_process, reason = self.usage_tracker.can_process_essay(client_ip, word_count)
        
        if not can_process:
            self.logger.warning(
                "Essay request rejected due to usage limits",
                client_ip=client_ip,
                reason=reason,
                word_count=word_count
            )
            
            return JSONResponse(
                status_code=429,  # Too Many Requests
                content={
                    "detail": {
                        "error": "Daily usage limit exceeded",
                        "message": f"{reason}. This helps manage costs and ensures the service remains available for all teachers.",
                        "limit_type": "daily_usage"
                    }
                }
            )
        
        # Process the request
        response = await call_next(request)
        
        # If the request was successful, record the usage
        if response.status_code == 200:
            try:
                # Extract essay type from the successful response or original request
                essay_type = data.get("essay_type", "UNKNOWN")
                
                self.usage_tracker.record_essay_processed(
                    client_ip=client_ip,
                    essay_type=essay_type,
                    word_count=word_count
                )
                
            except Exception as e:
                self.logger.error(
                    "Failed to record essay usage",
                    client_ip=client_ip,
                    error=str(e)
                )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers"""
        # Check for forwarded headers first (for load balancers/proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        # Fallback to direct client IP
        client_host = getattr(request.client, "host", None)
        return client_host or "unknown"