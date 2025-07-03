"""Tests for AI Service Factory"""

import pytest
from unittest.mock import Mock

from app.config.settings import Settings
from app.services.ai.factory import create_ai_service, get_available_ai_services
from app.services.ai.mock_service import MockAIService
from app.services.ai.anthropic_service import AnthropicService
from app.services.base.exceptions import ConfigurationError


class TestAIServiceFactory:
    """Test cases for AI service factory"""
    
    def test_create_mock_service(self):
        """Test creating mock AI service"""
        settings = Settings(ai_service_type="mock")
        service = create_ai_service(settings)
        
        assert isinstance(service, MockAIService)
    
    def test_create_anthropic_service(self):
        """Test creating Anthropic AI service"""
        settings = Settings(
            ai_service_type="anthropic",
            anthropic_api_key="test-key-123"
        )
        service = create_ai_service(settings)
        
        assert isinstance(service, AnthropicService)
    
    def test_create_service_case_insensitive(self):
        """Test factory is case insensitive"""
        settings = Settings(ai_service_type="MOCK")
        service = create_ai_service(settings)
        
        assert isinstance(service, MockAIService)
    
    def test_create_service_unsupported_type(self):
        """Test error for unsupported service type"""
        settings = Settings(ai_service_type="openai")  # Not supported yet
        
        with pytest.raises(ConfigurationError, match="Unsupported AI service type"):
            create_ai_service(settings)
    
    def test_create_service_with_none_settings(self):
        """Test creating service with None settings (should load from config)"""
        # This will use default settings which should be mock
        service = create_ai_service(None)
        
        assert isinstance(service, MockAIService)
    
    def test_get_available_ai_services(self):
        """Test getting list of available AI services"""
        services = get_available_ai_services()
        
        assert "mock" in services
        assert "anthropic" in services
        assert isinstance(services, list)
        assert len(services) >= 2