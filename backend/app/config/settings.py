"""Application configuration settings using Pydantic Settings"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    
    # AI Service Configuration
    ai_service_type: str = Field(default="mock")  # "mock" or "anthropic"
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    
    # CORS Configuration - Specific origins (wildcard + credentials not allowed)
    allowed_origins: List[str] = Field(default=[
        "http://localhost:8001", 
        "http://127.0.0.1:8001"
    ])
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()