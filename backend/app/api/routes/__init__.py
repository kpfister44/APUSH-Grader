"""API routes package"""

from .health import router as health_router
from .grading import router as grading_router

__all__ = ["health_router", "grading_router"]