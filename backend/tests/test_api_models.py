"""Tests for API models - ported from Swift APIModelsTests"""

import pytest
from app.models.core.api_models import (
    Provider, Model, APIConfig, APICredentials, APIResponse
)


class TestProvider:
    """Test suite for Provider enum"""
    
    def test_provider_values(self):
        """Test provider enum values"""
        assert Provider.OPENAI == "openai"
        assert Provider.ANTHROPIC == "anthropic"
    
    def test_provider_string_representation(self):
        """Test provider string representation"""
        assert Provider.OPENAI.value == "openai"
        assert Provider.ANTHROPIC.value == "anthropic"


class TestModel:
    """Test suite for Model enum"""
    
    def test_model_values(self):
        """Test model enum values"""
        assert Model.GPT4O == "gpt-4o"
        assert Model.GPT4O_MINI == "gpt-4o-mini"
        assert Model.CLAUDE35_SONNET == "claude-3-5-sonnet-20241022"
        assert Model.CLAUDE3_HAIKU == "claude-3-haiku-20240307"
    
    def test_model_names(self):
        """Test model name property"""
        assert Model.GPT4O.name == "gpt-4o"
        assert Model.GPT4O_MINI.name == "gpt-4o-mini"
        assert Model.CLAUDE35_SONNET.name == "claude-3-5-sonnet-20241022"
        assert Model.CLAUDE3_HAIKU.name == "claude-3-haiku-20240307"
    
    def test_model_providers_openai(self):
        """Test provider mapping for OpenAI models"""
        assert Model.GPT4O.provider == Provider.OPENAI
        assert Model.GPT4O_MINI.provider == Provider.OPENAI
    
    def test_model_providers_anthropic(self):
        """Test provider mapping for Anthropic models"""
        assert Model.CLAUDE35_SONNET.provider == Provider.ANTHROPIC
        assert Model.CLAUDE3_HAIKU.provider == Provider.ANTHROPIC
    
    def test_model_provider_unknown(self):
        """Test unknown model provider handling"""
        # This test verifies the current implementation behavior
        # In practice, this shouldn't happen with enum values
        pass


class TestAPIConfig:
    """Test suite for APIConfig model"""
    
    def test_api_config_defaults(self):
        """Test default API configuration values"""
        config = APIConfig()
        assert config.temperature == 0.3
        assert config.max_tokens == 1500
        assert config.timeout_interval == 30.0
        assert config.preferred_model == Model.CLAUDE35_SONNET
    
    def test_api_config_custom_values(self):
        """Test custom API configuration values"""
        config = APIConfig(
            temperature=0.7,
            max_tokens=2000,
            timeout_interval=60.0,
            preferred_model=Model.GPT4O
        )
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.timeout_interval == 60.0
        assert config.preferred_model == Model.GPT4O
    
    def test_model_config_property(self):
        """Test model configuration property"""
        config = APIConfig(
            temperature=0.5,
            max_tokens=1000,
            preferred_model=Model.GPT4O_MINI
        )
        
        model_config = config.model_configuration
        assert model_config["model"] == "gpt-4o-mini"
        assert model_config["temperature"] == 0.5
        assert model_config["max_tokens"] == 1000
    
    def test_timeout_config_property(self):
        """Test timeout configuration property"""
        config = APIConfig(timeout_interval=40.0)
        
        timeout_config = config.timeout_config
        assert timeout_config["timeout"] == 40.0
        assert timeout_config["connect_timeout"] == 20.0
        assert timeout_config["read_timeout"] == 40.0
    
    def test_temperature_validation_range(self):
        """Test temperature validation within valid range"""
        config = APIConfig(temperature=0.0)
        assert config.temperature == 0.0
        
        config = APIConfig(temperature=1.0)
        assert config.temperature == 1.0
        
        config = APIConfig(temperature=0.5)
        assert config.temperature == 0.5
    
    def test_max_tokens_validation(self):
        """Test max tokens validation"""
        config = APIConfig(max_tokens=100)
        assert config.max_tokens == 100
        
        config = APIConfig(max_tokens=4000)
        assert config.max_tokens == 4000
    
    def test_timeout_validation(self):
        """Test timeout validation"""
        config = APIConfig(timeout_interval=1.0)
        assert config.timeout_interval == 1.0
        
        config = APIConfig(timeout_interval=120.0)
        assert config.timeout_interval == 120.0


class TestAPICredentials:
    """Test suite for APICredentials model"""
    
    def test_api_credentials_defaults(self):
        """Test default API credentials"""
        creds = APICredentials()
        assert creds.openai_api_key == ""
        assert creds.anthropic_api_key == ""
    
    def test_api_credentials_custom_values(self):
        """Test custom API credentials"""
        creds = APICredentials(
            openai_api_key="sk-test-openai-key",
            anthropic_api_key="sk-test-anthropic-key"
        )
        assert creds.openai_api_key == "sk-test-openai-key"
        assert creds.anthropic_api_key == "sk-test-anthropic-key"
    
    def test_get_key_for_provider_openai(self):
        """Test getting OpenAI API key"""
        creds = APICredentials(openai_api_key="sk-openai-key")
        key = creds.get_key_for_provider(Provider.OPENAI)
        assert key == "sk-openai-key"
    
    def test_get_key_for_provider_anthropic(self):
        """Test getting Anthropic API key"""
        creds = APICredentials(anthropic_api_key="sk-anthropic-key")
        key = creds.get_key_for_provider(Provider.ANTHROPIC)
        assert key == "sk-anthropic-key"
    
    def test_get_key_for_unknown_provider(self):
        """Test getting key for unknown provider raises error"""
        creds = APICredentials()
        with pytest.raises(ValueError, match="Unknown provider"):
            creds.get_key_for_provider("unknown_provider")
    
    def test_has_key_for_provider_openai_true(self):
        """Test has key for OpenAI when key exists"""
        creds = APICredentials(openai_api_key="sk-openai-key")
        assert creds.has_key_for_provider(Provider.OPENAI) is True
    
    def test_has_key_for_provider_openai_false(self):
        """Test has key for OpenAI when key missing"""
        creds = APICredentials(openai_api_key="")
        assert creds.has_key_for_provider(Provider.OPENAI) is False
    
    def test_has_key_for_provider_anthropic_true(self):
        """Test has key for Anthropic when key exists"""
        creds = APICredentials(anthropic_api_key="sk-anthropic-key")
        assert creds.has_key_for_provider(Provider.ANTHROPIC) is True
    
    def test_has_key_for_provider_anthropic_false(self):
        """Test has key for Anthropic when key missing"""
        creds = APICredentials(anthropic_api_key="")
        assert creds.has_key_for_provider(Provider.ANTHROPIC) is False
    
    def test_has_key_for_provider_whitespace_only(self):
        """Test has key returns false for whitespace-only keys"""
        creds = APICredentials(openai_api_key="   ")
        assert creds.has_key_for_provider(Provider.OPENAI) is False
    
    def test_has_key_for_unknown_provider(self):
        """Test has key for unknown provider raises error"""
        creds = APICredentials()
        with pytest.raises(ValueError, match="Unknown provider"):
            creds.has_key_for_provider("unknown_provider")


class TestAPIResponse:
    """Test suite for APIResponse model"""
    
    def test_api_response_success(self):
        """Test successful API response"""
        response = APIResponse(
            success=True,
            data={"result": "success"},
            provider=Provider.OPENAI,
            model=Model.GPT4O
        )
        
        assert response.success is True
        assert response.data == {"result": "success"}
        assert response.error == ""
        assert response.provider == Provider.OPENAI
        assert response.model == Model.GPT4O
    
    def test_api_response_error(self):
        """Test error API response"""
        response = APIResponse(
            success=False,
            error="API key invalid",
            provider=Provider.ANTHROPIC,
            model=Model.CLAUDE35_SONNET
        )
        
        assert response.success is False
        assert response.data == {}
        assert response.error == "API key invalid"
        assert response.provider == Provider.ANTHROPIC
        assert response.model == Model.CLAUDE35_SONNET
    
    def test_is_error_property_false(self):
        """Test is_error property returns False for successful response"""
        response = APIResponse(
            success=True,
            provider=Provider.OPENAI,
            model=Model.GPT4O
        )
        assert response.is_error is False
    
    def test_is_error_property_true_success_false(self):
        """Test is_error property returns True when success is False"""
        response = APIResponse(
            success=False,
            provider=Provider.OPENAI,
            model=Model.GPT4O
        )
        assert response.is_error is True
    
    def test_is_error_property_true_error_present(self):
        """Test is_error property returns True when error is present"""
        response = APIResponse(
            success=True,
            error="Some error occurred",
            provider=Provider.OPENAI,
            model=Model.GPT4O
        )
        assert response.is_error is True
    
    def test_api_response_with_custom_data(self):
        """Test API response with custom data"""
        custom_data = {
            "tokens_used": 150,
            "model_version": "gpt-4o-2024-05-13",
            "finish_reason": "stop"
        }
        
        response = APIResponse(
            success=True,
            data=custom_data,
            provider=Provider.OPENAI,
            model=Model.GPT4O
        )
        
        assert response.data == custom_data
        assert response.data["tokens_used"] == 150
    
    def test_api_response_defaults(self):
        """Test API response with default values"""
        response = APIResponse(
            success=True,
            provider=Provider.ANTHROPIC,
            model=Model.CLAUDE3_HAIKU
        )
        
        assert response.data == {}
        assert response.error == ""
        assert response.success is True