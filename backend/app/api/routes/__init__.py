"""API routes package"""

from .health import router as health_router
from .grading import router as grading_router
from .auth import router as auth_router

__all__ = ["health_router", "grading_router", "auth_router"]