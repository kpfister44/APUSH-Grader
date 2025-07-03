"""Integration tests for AI services with service locator"""

import pytest
from unittest.mock import patch

from app.config.settings import Settings
from app.services.dependencies.service_locator import ServiceLocator
from app.services.ai.base import AIService
from app.services.ai.mock_service import MockAIService
from app.services.ai.anthropic_service import AnthropicService


class TestAIServiceIntegration:
    """Test AI service integration with service locator"""
    
    def test_service_locator_mock_service(self):
        """Test service locator creates mock AI service"""
        settings = Settings(ai_service_type="mock")
        locator = ServiceLocator(settings)
        
        # Configure the service (since we're not using the global configuration)
        from app.services.ai.factory import create_ai_service
        locator.register_factory(AIService, lambda s: create_ai_service(s))
        
        service = locator.get_ai_service()
        
        assert isinstance(service, MockAIService)
    
    @patch('app.services.ai.anthropic_service.Anthropic')
    def test_service_locator_anthropic_service(self, mock_anthropic_class):
        """Test service locator creates Anthropic AI service"""
        mock_anthropic_class.return_value = None  # Mock the client
        
        settings = Settings(
            ai_service_type="anthropic",
            anthropic_api_key="test-key"
        )
        locator = ServiceLocator(settings)
        
        # Configure the service
        from app.services.ai.factory import create_ai_service
        locator.register_factory(AIService, lambda s: create_ai_service(s))
        
        service = locator.get_ai_service()
        
        assert isinstance(service, AnthropicService)
    
    def test_service_locator_singleton_behavior(self):
        """Test that service locator returns the same AI service instance"""
        settings = Settings(ai_service_type="mock")
        locator = ServiceLocator(settings)
        
        # Configure the service
        from app.services.ai.factory import create_ai_service
        locator.register_factory(AIService, lambda s: create_ai_service(s))
        
        service1 = locator.get_ai_service()
        service2 = locator.get_ai_service()
        
        # Should be the same instance (singleton behavior)
        assert service1 is service2
    
    def test_ai_service_interface_compliance(self):
        """Test that AI services implement the expected interface"""
        settings = Settings(ai_service_type="mock")
        locator = ServiceLocator(settings)
        
        # Configure the service
        from app.services.ai.factory import create_ai_service
        locator.register_factory(AIService, lambda s: create_ai_service(s))
        
        service = locator.get_ai_service()
        
        # Should have the required methods
        assert hasattr(service, 'generate_response')
        assert callable(service.generate_response)
        assert hasattr(service, '_validate_configuration')
        assert callable(service._validate_configuration)