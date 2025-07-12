"""
Simple exceptions for APUSH Grader backend.
Replaces complex services/base/exceptions.py with minimal error handling.
"""


class GradingError(Exception):
    """Base exception for grading-related errors"""
    pass


class ValidationError(GradingError):
    """Essay validation errors"""
    pass


class ProcessingError(GradingError):
    """Essay processing errors"""
    pass


class APIError(GradingError):
    """API related errors"""
    pass


class ConfigurationError(GradingError):
    """Configuration related errors"""
    pass