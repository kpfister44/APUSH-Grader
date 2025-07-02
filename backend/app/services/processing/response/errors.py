"""Error presentation service for user-friendly error messages."""

from abc import ABC, abstractmethod
from typing import Dict, Tuple

from app.services.base.exceptions import (
    GradingError, NetworkError, APIKeyMissingError, RateLimitExceededError,
    EssayTooShortError, EssayTooLongError, InvalidResponseError, 
    ParseError, InvalidScoreError
)
from app.models.processing.display import ErrorIcons
from app.services.base.base_service import BaseService


class ErrorPresentationProtocol(ABC):
    """Protocol for error presentation services."""
    
    @abstractmethod
    def get_user_friendly_message(self, error: Exception) -> str:
        """Convert technical error to user-friendly message."""
        pass
    
    @abstractmethod
    def get_error_icon(self, error: Exception) -> str:
        """Get appropriate icon for error type."""
        pass


class ErrorPresentation(BaseService, ErrorPresentationProtocol):
    """Converts technical errors to user-friendly messages and icons."""
    
    def __init__(self):
        super().__init__()
        self._error_messages: Dict[type, str] = {
            NetworkError: "Network connection issue: {message}. Please check your internet connection and try again.",
            APIKeyMissingError: "API configuration missing. Please contact support or check your app settings.",
            RateLimitExceededError: "Service temporarily busy. Please wait a moment and try again.",
            EssayTooShortError: "Your essay appears to be too short for accurate grading. Please expand your response.",
            EssayTooLongError: "Your essay is quite long and may exceed processing limits. Consider shortening it.",
            InvalidResponseError: "Received an unexpected response from the grading service. Please try again.",
            ParseError: "Received an unexpected response from the grading service. Please try again.",
            InvalidScoreError: "Received invalid scoring data. Please try grading again."
        }
        
        self._error_icons: Dict[type, str] = {
            NetworkError: ErrorIcons.NETWORK_ERROR,
            RateLimitExceededError: ErrorIcons.NETWORK_ERROR,
            APIKeyMissingError: ErrorIcons.API_KEY_ERROR,
            EssayTooShortError: ErrorIcons.ESSAY_LENGTH_ERROR,
            EssayTooLongError: ErrorIcons.ESSAY_LENGTH_ERROR,
            InvalidResponseError: ErrorIcons.VALIDATION_ERROR,
            ParseError: ErrorIcons.VALIDATION_ERROR,
            InvalidScoreError: ErrorIcons.VALIDATION_ERROR
        }
    
    def get_user_friendly_message(self, error: Exception) -> str:
        """
        Convert a technical error to a user-friendly message.
        
        Args:
            error: The exception that occurred
            
        Returns:
            User-friendly error message
        """
        try:
            # Check for specific grading errors first
            if isinstance(error, GradingError):
                error_type = type(error)
                if error_type in self._error_messages:
                    message_template = self._error_messages[error_type]
                    # Handle network errors that might have a message attribute
                    if hasattr(error, 'message') and '{message}' in message_template:
                        return message_template.format(message=error.message)
                    else:
                        return message_template
            
            # Fall back to generic error message
            return f"An unexpected error occurred: {str(error)}. Please try again."
            
        except Exception as e:
            self.logger.error(f"Error creating user-friendly message: {e}")
            return "An unexpected error occurred. Please try again."
    
    def get_error_icon(self, error: Exception) -> str:
        """
        Get an appropriate icon for the error type.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Icon string (emoji) for the error
        """
        try:
            if isinstance(error, GradingError):
                error_type = type(error)
                return self._error_icons.get(error_type, ErrorIcons.GENERAL_ERROR)
            
            return ErrorIcons.GENERAL_ERROR
            
        except Exception as e:
            self.logger.error(f"Error getting error icon: {e}")
            return ErrorIcons.GENERAL_ERROR
    
    def get_error_details(self, error: Exception) -> Tuple[str, str]:
        """
        Get both message and icon for an error.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Tuple of (user_friendly_message, icon)
        """
        return (
            self.get_user_friendly_message(error),
            self.get_error_icon(error)
        )