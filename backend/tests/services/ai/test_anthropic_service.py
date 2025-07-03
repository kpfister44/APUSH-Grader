"""Tests for Anthropic AI Service"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.config.settings import Settings
from app.models.core.essay_types import EssayType
from app.services.ai.anthropic_service import AnthropicService
from app.services.base.exceptions import ProcessingError, ValidationError


class TestAnthropicService:
    """Test cases for AnthropicService"""
    
    @pytest.fixture
    def settings_with_api_key(self):
        """Settings with valid API key"""
        return Settings(
            ai_service_type="anthropic",
            anthropic_api_key="test-api-key-123"
        )
    
    @pytest.fixture
    def settings_without_api_key(self):
        """Settings without API key"""
        return Settings(
            ai_service_type="anthropic",
            anthropic_api_key=""
        )
    
    @patch('app.services.ai.anthropic_service.Anthropic')
    def test_initialization_with_api_key(self, mock_anthropic_class, settings_with_api_key):
        """Test successful initialization with API key"""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(settings_with_api_key)
        
        assert service.client == mock_client
        mock_anthropic_class.assert_called_once_with(api_key="test-api-key-123")
    
    def test_initialization_without_api_key(self, settings_without_api_key):
        """Test initialization without API key"""
        service = AnthropicService(settings_without_api_key)
        
        # Should not fail during initialization, but client should be None
        assert service.client is None
    
    @patch('app.services.ai.anthropic_service.Anthropic')
    def test_initialization_failure(self, mock_anthropic_class, settings_with_api_key):
        """Test initialization failure"""
        mock_anthropic_class.side_effect = Exception("API initialization failed")
        
        with pytest.raises(ValidationError, match="Anthropic client initialization failed"):
            AnthropicService(settings_with_api_key)
    
    @patch('app.services.ai.anthropic_service.Anthropic')
    @pytest.mark.asyncio
    async def test_generate_response_success(self, mock_anthropic_class, settings_with_api_key):
        """Test successful response generation"""
        # Setup mock client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Setup mock response
        mock_content = Mock()
        mock_content.text = '{"score": 4, "maxScore": 6, "breakdown": {}}'
        mock_message = Mock()
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message
        
        service = AnthropicService(settings_with_api_key)
        
        response = await service.generate_response(
            "system prompt", "user message", EssayType.DBQ
        )
        
        assert response == '{"score": 4, "maxScore": 6, "breakdown": {}}'
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.3,
            system="system prompt",
            messages=[
                {
                    "role": "user",
                    "content": "user message"
                }
            ]
        )
    
    @pytest.mark.asyncio
    async def test_generate_response_no_client(self, settings_without_api_key):
        """Test response generation without initialized client"""
        service = AnthropicService(settings_without_api_key)
        
        with pytest.raises(ValidationError, match="Anthropic client not initialized"):
            await service.generate_response(
                "system prompt", "user message", EssayType.DBQ
            )
    
    @patch('app.services.ai.anthropic_service.Anthropic')
    @pytest.mark.asyncio
    async def test_generate_response_api_failure(self, mock_anthropic_class, settings_with_api_key):
        """Test API call failure"""
        # Setup mock client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API call failed")
        
        service = AnthropicService(settings_with_api_key)
        
        with pytest.raises(ProcessingError, match="Anthropic AI service failed"):
            await service.generate_response(
                "system prompt", "user message", EssayType.DBQ
            )
    
    @patch('app.services.ai.anthropic_service.Anthropic')
    def test_validate_configuration_success(self, mock_anthropic_class, settings_with_api_key):
        """Test successful configuration validation"""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        service = AnthropicService(settings_with_api_key)
        
        # Should not raise any exceptions
        service._validate_configuration()
    
    def test_validate_configuration_no_api_key(self, settings_without_api_key):
        """Test configuration validation without API key"""
        service = AnthropicService(settings_without_api_key)
        
        with pytest.raises(ValidationError, match="Anthropic API key is required"):
            service._validate_configuration()
    
    def test_validate_configuration_no_client(self, settings_without_api_key):
        """Test configuration validation without client"""
        service = AnthropicService(settings_without_api_key)
        
        with pytest.raises(ValidationError, match="Anthropic client failed to initialize"):
            service._validate_configuration()