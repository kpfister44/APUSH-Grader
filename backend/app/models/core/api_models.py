"""API configuration models for APUSH essay grading"""

from enum import Enum
from pydantic import BaseModel, computed_field
from typing import Dict, Any


class Provider(str, Enum):
    """API provider enumeration"""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class Model(str, Enum):
    """AI model enumeration with provider mapping"""
    
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    CLAUDE35_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE3_HAIKU = "claude-3-haiku-20240307"
    
    @property
    def name(self) -> str:
        """Get model name for API calls"""
        return self.value
    
    @property
    def provider(self) -> Provider:
        """Get provider for this model"""
        if self.value in ["gpt-4o", "gpt-4o-mini"]:
            return Provider.OPENAI
        elif self.value in ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]:
            return Provider.ANTHROPIC
        else:
            raise ValueError(f"Unknown provider for model: {self.value}")


class APIConfig(BaseModel):
    """API configuration settings"""
    
    temperature: float = 0.3
    max_tokens: int = 1500
    timeout_interval: float = 30.0
    preferred_model: Model = Model.CLAUDE35_SONNET
    
    @computed_field
    @property  
    def model_configuration(self) -> Dict[str, Any]:
        """Get model-specific configuration"""
        return {
            "model": self.preferred_model.name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    @computed_field
    @property
    def timeout_config(self) -> Dict[str, float]:
        """Get timeout configuration"""
        return {
            "timeout": self.timeout_interval,
            "connect_timeout": self.timeout_interval / 2,
            "read_timeout": self.timeout_interval
        }


class APICredentials(BaseModel):
    """API credentials configuration"""
    
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    def get_key_for_provider(self, provider: Provider) -> str:
        """Get API key for specific provider"""
        if provider == Provider.OPENAI:
            return self.openai_api_key
        elif provider == Provider.ANTHROPIC:
            return self.anthropic_api_key
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def has_key_for_provider(self, provider: Provider) -> bool:
        """Check if API key exists for provider"""
        key = self.get_key_for_provider(provider)
        return bool(key and key.strip())


class APIResponse(BaseModel):
    """Base API response model"""
    
    success: bool
    data: Dict[str, Any] = {}
    error: str = ""
    provider: Provider
    model: Model
    
    @computed_field
    @property
    def is_error(self) -> bool:
        """Check if response contains an error"""
        return not self.success or bool(self.error)