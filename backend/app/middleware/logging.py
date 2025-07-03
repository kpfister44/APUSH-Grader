"""
Logging middleware for request correlation and structured logging
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.logging.structured_logger import get_logger, set_correlation_id


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs and log requests"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("middleware.request_logging")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with correlation ID and logging"""
        
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())[:8]  # Short correlation ID
        set_correlation_id(correlation_id)
        
        # Add correlation ID to request headers for downstream services
        request.state.correlation_id = correlation_id
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Log request start
        start_time = time.time()
        self.logger.log_request_start(
            method=request.method,
            path=str(request.url.path),
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            query_params=dict(request.query_params) if request.query_params else {}
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful request
            self.logger.log_request_end(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration_ms=duration_ms,
                client_ip=client_ip
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration for failed request
            duration_ms = (time.time() - start_time) * 1000
            
            # Log failed request
            self.logger.log_error(
                error_type="request_processing_error",
                error_message=str(e),
                http_method=request.method,
                http_path=str(request.url.path),
                duration_ms=duration_ms,
                client_ip=client_ip
            )
            
            # Re-raise the exception
            raise
    
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