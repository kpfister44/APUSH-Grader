"""Health check request/response models"""

from pydantic import BaseModel
from typing import Dict, Any


class HealthResponse(BaseModel):
    """Health check response model"""
    
    status: str
    version: str
    environment: str
    services: Dict[str, str] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development",
                "services": {
                    "database": "connected",
                    "openai": "configured",
                    "anthropic": "configured"
                }
            }
        }