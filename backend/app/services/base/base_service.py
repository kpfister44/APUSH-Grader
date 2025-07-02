"""Base service class with common functionality"""

import logging
from typing import Optional, Any
from app.config.settings import Settings, get_settings
from app.services.base.exceptions import ServiceError, ConfigurationError


class BaseService:
    """Base class for all services with common functionality"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate service configuration - override in subclasses"""
        if not self.settings:
            raise ConfigurationError("Settings not provided")
    
    def _log_operation(self, operation: str, **kwargs) -> None:
        """Log service operations with context"""
        context = {k: v for k, v in kwargs.items() if v is not None}
        self.logger.info(f"{operation}: {context}")
    
    def _log_error(self, error: Exception, context: str, **kwargs) -> None:
        """Log errors with context"""
        error_context = {k: v for k, v in kwargs.items() if v is not None}
        self.logger.error(
            f"Error in {context}: {error}", 
            exc_info=True, 
            extra={"context": error_context}
        )
    
    def _handle_error(self, error: Exception, context: str, **kwargs) -> ServiceError:
        """Convert and log errors consistently"""
        self._log_error(error, context, **kwargs)
        
        if isinstance(error, ServiceError):
            return error
        
        return ServiceError(f"Unexpected error in {context}: {str(error)}")
    
    def _log_debug(self, message: str, **kwargs) -> None:
        """Log debug messages with context"""
        if self.settings.debug:
            context = {k: v for k, v in kwargs.items() if v is not None}
            self.logger.debug(f"{message}: {context}")
    
    def _validate_input(self, value: Any, name: str, required: bool = True) -> None:
        """Validate input parameters"""
        if required and (value is None or (isinstance(value, str) and not value.strip())):
            raise ValueError(f"{name} is required and cannot be empty")
    
    def _safe_execute(self, operation: callable, context: str, *args, **kwargs) -> Any:
        """Safely execute operation with error handling"""
        try:
            self._log_debug(f"Executing {context}", args=args, kwargs=kwargs)
            result = operation(*args, **kwargs)
            self._log_debug(f"Completed {context}", result_type=type(result).__name__)
            return result
        except Exception as e:
            raise self._handle_error(e, context)


class BaseEssayService(BaseService):
    """Base class for essay processing services"""
    
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)
        self._initialize_patterns()
    
    def _initialize_patterns(self) -> None:
        """Initialize regex patterns and word lists - override in subclasses"""
        pass
    
    def _validate_essay_input(self, text: str, essay_type: Any) -> None:
        """Validate essay processing inputs"""
        self._validate_input(text, "essay text")
        self._validate_input(essay_type, "essay type")
        
        if not hasattr(essay_type, 'value'):
            raise ValueError("Invalid essay type - must be EssayType enum")


class BaseTextProcessor(BaseEssayService):
    """Base class for text processing services"""
    
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for performance - override in subclasses"""
        pass
    
    def _safe_text_operation(self, text: str, operation: callable, context: str) -> Any:
        """Safely execute text operations with validation"""
        if not isinstance(text, str):
            raise ValueError(f"Text must be string, got {type(text)}")
        
        return self._safe_execute(operation, context, text)