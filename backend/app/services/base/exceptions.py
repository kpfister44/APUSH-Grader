"""Custom exception hierarchy for APUSH Grader services"""

from typing import Optional, Any, Dict


class ServiceError(Exception):
    """Base service exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class GradingError(ServiceError):
    """Essay grading related errors"""
    pass


class EssayValidationError(GradingError):
    """Essay validation errors"""
    
    def __init__(self, message: str, word_count: Optional[int] = None, essay_type: Optional[str] = None):
        super().__init__(message, {"word_count": word_count, "essay_type": essay_type})
        self.word_count = word_count
        self.essay_type = essay_type


class EssayTooShortError(EssayValidationError):
    """Essay too short error"""
    pass


class EssayTooLongError(EssayValidationError):
    """Essay too long error"""
    pass


class TextAnalysisError(GradingError):
    """Text analysis processing errors"""
    pass


class APIError(ServiceError):
    """API related errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, provider: Optional[str] = None):
        super().__init__(message, {"status_code": status_code, "provider": provider})
        self.status_code = status_code
        self.provider = provider


class RateLimitExceededError(GradingError):
    """Rate limit exceeded error"""
    pass


class NetworkError(GradingError):
    """Network related error"""
    pass


class ParseError(GradingError):
    """Response parsing error"""
    pass


class APIKeyMissingError(GradingError):
    """API key missing error"""
    pass


class InvalidResponseError(GradingError):
    """Invalid API response error"""
    pass


class InvalidScoreError(GradingError):
    """Invalid score data error"""
    pass


class ConfigurationError(ServiceError):
    """Service configuration errors"""
    pass


class DependencyError(ServiceError):
    """Dependency injection errors"""
    pass