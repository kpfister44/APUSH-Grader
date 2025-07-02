"""Tests for ErrorPresentation service."""

import pytest

from app.services.base.exceptions import (
    NetworkError, APIKeyMissingError, RateLimitExceededError,
    EssayTooShortError, EssayTooLongError, InvalidResponseError,
    ParseError, InvalidScoreError
)
from app.models.processing.display import ErrorIcons
from app.services.processing.response.errors import ErrorPresentation


class TestErrorPresentation:
    """Test suite for ErrorPresentation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.error_presentation = ErrorPresentation()
    
    def test_network_error_message(self):
        """Test user-friendly message for network errors."""
        error = NetworkError("Connection timeout")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "Network connection issue" in message
        assert "Connection timeout" in message
        assert "check your internet connection" in message
    
    def test_api_key_missing_error_message(self):
        """Test user-friendly message for API key errors."""
        error = APIKeyMissingError("API key not found")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "API configuration missing" in message
        assert "contact support" in message
    
    def test_rate_limit_error_message(self):
        """Test user-friendly message for rate limit errors."""
        error = RateLimitExceededError("Rate limit exceeded")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "Service temporarily busy" in message
        assert "wait a moment" in message
    
    def test_essay_too_short_error_message(self):
        """Test user-friendly message for essay too short errors."""
        error = EssayTooShortError("Essay too short")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "too short for accurate grading" in message
        assert "expand your response" in message
    
    def test_essay_too_long_error_message(self):
        """Test user-friendly message for essay too long errors."""
        error = EssayTooLongError("Essay too long")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "quite long" in message
        assert "processing limits" in message
        assert "shortening" in message
    
    def test_invalid_response_error_message(self):
        """Test user-friendly message for invalid response errors."""
        error = InvalidResponseError("Invalid response")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "unexpected response" in message
        assert "grading service" in message
        assert "try again" in message
    
    def test_parse_error_message(self):
        """Test user-friendly message for parse errors."""
        error = ParseError("Parse error")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "unexpected response" in message
        assert "grading service" in message
        assert "try again" in message
    
    def test_invalid_score_error_message(self):
        """Test user-friendly message for invalid score errors."""
        error = InvalidScoreError("Invalid score")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "invalid scoring data" in message
        assert "try grading again" in message
    
    def test_generic_error_message(self):
        """Test user-friendly message for generic errors."""
        error = ValueError("Something went wrong")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "unexpected error occurred" in message
        assert "Something went wrong" in message
        assert "try again" in message
    
    def test_network_error_icon(self):
        """Test icon for network errors."""
        error = NetworkError("Connection failed")
        icon = self.error_presentation.get_error_icon(error)
        
        assert icon == ErrorIcons.NETWORK_ERROR
    
    def test_rate_limit_error_icon(self):
        """Test icon for rate limit errors."""
        error = RateLimitExceededError("Rate limit exceeded")
        icon = self.error_presentation.get_error_icon(error)
        
        assert icon == ErrorIcons.NETWORK_ERROR
    
    def test_api_key_error_icon(self):
        """Test icon for API key errors."""
        error = APIKeyMissingError("API key missing")
        icon = self.error_presentation.get_error_icon(error)
        
        assert icon == ErrorIcons.API_KEY_ERROR
    
    def test_essay_length_error_icons(self):
        """Test icons for essay length errors."""
        short_error = EssayTooShortError("Essay too short")
        long_error = EssayTooLongError("Essay too long")
        
        short_icon = self.error_presentation.get_error_icon(short_error)
        long_icon = self.error_presentation.get_error_icon(long_error)
        
        assert short_icon == ErrorIcons.ESSAY_LENGTH_ERROR
        assert long_icon == ErrorIcons.ESSAY_LENGTH_ERROR
    
    def test_validation_error_icons(self):
        """Test icons for validation errors."""
        invalid_response = InvalidResponseError("Invalid response")
        parse_error = ParseError("Parse error")
        invalid_score = InvalidScoreError("Invalid score")
        
        assert self.error_presentation.get_error_icon(invalid_response) == ErrorIcons.VALIDATION_ERROR
        assert self.error_presentation.get_error_icon(parse_error) == ErrorIcons.VALIDATION_ERROR
        assert self.error_presentation.get_error_icon(invalid_score) == ErrorIcons.VALIDATION_ERROR
    
    def test_generic_error_icon(self):
        """Test icon for generic errors."""
        error = ValueError("Generic error")
        icon = self.error_presentation.get_error_icon(error)
        
        assert icon == ErrorIcons.GENERAL_ERROR
    
    def test_get_error_details(self):
        """Test getting both message and icon together."""
        error = NetworkError("Connection failed")
        message, icon = self.error_presentation.get_error_details(error)
        
        assert "Network connection issue" in message
        assert "Connection failed" in message
        assert icon == ErrorIcons.NETWORK_ERROR
    
    def test_network_error_with_message_formatting(self):
        """Test network error message formatting with placeholders."""
        error = NetworkError("Timeout after 30 seconds")
        message = self.error_presentation.get_user_friendly_message(error)
        
        assert "Timeout after 30 seconds" in message
        assert "Network connection issue: Timeout after 30 seconds" in message
    
    def test_error_without_message_attribute(self):
        """Test handling of errors without message attribute."""
        error = APIKeyMissingError("API key missing")  # No message attribute
        message = self.error_presentation.get_user_friendly_message(error)
        
        # Should still return appropriate message without crashing
        assert "API configuration missing" in message
    
    def test_error_message_creation_error_handling(self):
        """Test error handling during message creation."""
        # Create a mock error that might cause issues
        error = Exception("Test error")
        
        message = self.error_presentation.get_user_friendly_message(error)
        
        # Should still return a message
        assert isinstance(message, str)
        assert "unexpected error occurred" in message
        assert "Test error" in message
    
    def test_error_icon_creation_error_handling(self):
        """Test error handling during icon creation."""
        # Create a mock error that might cause issues
        error = Exception("Test error")
        
        icon = self.error_presentation.get_error_icon(error)
        
        # Should still return an icon
        assert isinstance(icon, str)
        assert icon == ErrorIcons.GENERAL_ERROR
    
    def test_multiple_error_types(self):
        """Test handling multiple different error types in sequence."""
        errors = [
            NetworkError("Network issue"),
            APIKeyMissingError("API key missing"),
            EssayTooShortError("Essay too short"),
            ValueError("Generic error")
        ]
        
        for error in errors:
            message = self.error_presentation.get_user_friendly_message(error)
            icon = self.error_presentation.get_error_icon(error)
            
            # All should return valid strings
            assert isinstance(message, str)
            assert isinstance(icon, str)
            assert len(message) > 0
            assert len(icon) > 0
    
    def test_error_message_templates(self):
        """Test that all error message templates are properly defined."""
        # Verify all expected error types have templates
        error_types = [
            NetworkError,
            APIKeyMissingError,
            RateLimitExceededError,
            EssayTooShortError,
            EssayTooLongError,
            InvalidResponseError,
            ParseError,
            InvalidScoreError
        ]
        
        for error_type in error_types:
            assert error_type in self.error_presentation._error_messages
            assert error_type in self.error_presentation._error_icons
    
    def test_error_icon_mapping(self):
        """Test that error icon mapping is complete."""
        # Test specific mappings
        assert self.error_presentation._error_icons[NetworkError] == ErrorIcons.NETWORK_ERROR
        assert self.error_presentation._error_icons[APIKeyMissingError] == ErrorIcons.API_KEY_ERROR
        assert self.error_presentation._error_icons[EssayTooShortError] == ErrorIcons.ESSAY_LENGTH_ERROR
        assert self.error_presentation._error_icons[InvalidResponseError] == ErrorIcons.VALIDATION_ERROR