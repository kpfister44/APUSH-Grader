"""Service locator for dependency injection"""

from typing import Dict, Type, TypeVar, Optional, Callable, Any
from functools import lru_cache
from app.config.settings import Settings, get_settings
from app.services.base.exceptions import DependencyError

T = TypeVar('T')


class ServiceLocator:
    """Central service locator for dependency injection"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_factory(self, interface: Type[T], factory: Callable[[Settings], T]) -> None:
        """Register a factory for creating service instances"""
        if not callable(factory):
            raise DependencyError(f"Factory for {interface} must be callable")
        self._factories[interface] = factory
    
    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """Register a singleton service instance"""
        if instance is None:
            raise DependencyError(f"Cannot register None as singleton for {interface}")
        self._singletons[interface] = instance
    
    def register_type(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a type to be instantiated when requested"""
        if not isinstance(implementation, type):
            raise DependencyError(f"Implementation must be a type, got {type(implementation)}")
        
        def factory(settings: Settings) -> T:
            try:
                return implementation(settings)
            except TypeError:
                # Try without settings parameter
                return implementation()
        
        self.register_factory(interface, factory)
    
    def get(self, interface: Type[T]) -> T:
        """Get service instance"""
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check if already instantiated as singleton from factory
        if interface in self._services:
            return self._services[interface]
        
        # Check factories
        if interface in self._factories:
            try:
                instance = self._factories[interface](self.settings)
                # Store as singleton for future requests
                self._services[interface] = instance
                return instance
            except Exception as e:
                raise DependencyError(f"Failed to create service {interface}: {e}")
        
        raise DependencyError(f"No service registered for {interface}")
    
    def get_optional(self, interface: Type[T]) -> Optional[T]:
        """Get service instance or None if not registered"""
        try:
            return self.get(interface)
        except DependencyError:
            return None
    
    def is_registered(self, interface: Type[T]) -> bool:
        """Check if service is registered"""
        return (interface in self._factories or 
                interface in self._singletons or 
                interface in self._services)
    
    def clear(self) -> None:
        """Clear all registered services (useful for testing)"""
        self._services.clear()
        self._factories.clear() 
        self._singletons.clear()
    
    def clear_singletons(self) -> None:
        """Clear singleton instances (keeps registrations)"""
        self._services.clear()
        self._singletons.clear()
    
    # Convenience methods for essay processing services
    def get_essay_processor(self):
        """Get essay processor service"""
        from app.services.base.protocols import EssayProcessorProtocol
        return self.get(EssayProcessorProtocol)
    
    def get_essay_validator(self):
        """Get essay validator service"""
        from app.services.base.protocols import EssayValidatorProtocol
        return self.get(EssayValidatorProtocol)
    
    def get_text_analyzer(self):
        """Get text analyzer service"""
        from app.services.base.protocols import TextAnalyzerProtocol
        return self.get(TextAnalyzerProtocol)
    
    def get_text_cleaner(self):
        """Get text cleaner service"""
        from app.services.base.protocols import TextCleanerProtocol
        return self.get(TextCleanerProtocol)
    
    def get_warning_generator(self):
        """Get warning generator service"""
        from app.services.base.protocols import WarningGeneratorProtocol
        return self.get(WarningGeneratorProtocol)
    
    # Convenience methods for response processing services
    def get_response_processor(self):
        """Get response processor service"""
        from app.services.processing.response import ResponseProcessorProtocol
        return self.get(ResponseProcessorProtocol)
    
    def get_response_validator(self):
        """Get response validator service"""
        from app.services.processing.response import ResponseValidatorProtocol
        return self.get(ResponseValidatorProtocol)
    
    def get_insights_generator(self):
        """Get insights generator service"""
        from app.services.processing.response import InsightsGeneratorProtocol
        return self.get(InsightsGeneratorProtocol)
    
    def get_response_formatter(self):
        """Get response formatter service"""
        from app.services.processing.response import ResponseFormatterProtocol
        return self.get(ResponseFormatterProtocol)
    
    def get_error_presentation(self):
        """Get error presentation service"""
        from app.services.processing.response import ErrorPresentationProtocol
        return self.get(ErrorPresentationProtocol)
    
    def get_prompt_generator(self):
        """Get prompt generator service"""
        from app.services.base.protocols import PromptGeneratorProtocol
        return self.get(PromptGeneratorProtocol)
    
    def get_api_coordinator(self):
        """Get API coordinator service"""
        from app.services.base.protocols import APICoordinatorProtocol
        return self.get(APICoordinatorProtocol)


# Global service locator instance
_service_locator: Optional[ServiceLocator] = None


@lru_cache()
def get_service_locator() -> ServiceLocator:
    """Get the global service locator instance"""
    global _service_locator
    if _service_locator is None:
        _service_locator = ServiceLocator()
        _configure_default_services(_service_locator)
    return _service_locator


def reset_service_locator() -> None:
    """Reset global service locator (for testing)"""
    global _service_locator
    _service_locator = None
    get_service_locator.cache_clear()


def _configure_default_services(locator: ServiceLocator) -> None:
    """Configure default service registrations"""
    from app.services.base.protocols import (
        EssayProcessorProtocol,
        EssayValidatorProtocol, 
        TextAnalyzerProtocol,
        TextCleanerProtocol,
        WarningGeneratorProtocol,
        PromptGeneratorProtocol,
        APICoordinatorProtocol
    )
    
    # Register essay processing services
    try:
        from app.services.processing.essay.processor import EssayProcessor
        from app.services.processing.essay.validator import EssayValidator
        from app.services.processing.essay.analyzer import TextAnalyzer
        from app.services.processing.essay.cleaner import TextCleaner
        from app.services.processing.essay.warnings import WarningGenerator
        
        locator.register_factory(EssayProcessorProtocol, lambda s: EssayProcessor(s))
        locator.register_factory(EssayValidatorProtocol, lambda s: EssayValidator(s))
        locator.register_factory(TextAnalyzerProtocol, lambda s: TextAnalyzer(s))
        locator.register_factory(TextCleanerProtocol, lambda s: TextCleaner(s))
        locator.register_factory(WarningGeneratorProtocol, lambda s: WarningGenerator(s))
        
    except ImportError as e:
        # Services not yet implemented, will be registered when available
        import logging
        logging.getLogger(__name__).warning(f"Could not register essay services: {e}")
    
    # Register response processing services
    try:
        from app.services.processing.response import (
            ResponseProcessorProtocol,
            ResponseValidatorProtocol,
            InsightsGeneratorProtocol,
            ResponseFormatterProtocol,
            ErrorPresentationProtocol,
            ResponseProcessor,
            ResponseValidator,
            InsightsGenerator,
            ResponseFormatter,
            ErrorPresentation
        )
        
        locator.register_factory(ResponseProcessorProtocol, lambda s: ResponseProcessor())
        locator.register_factory(ResponseValidatorProtocol, lambda s: ResponseValidator())
        locator.register_factory(InsightsGeneratorProtocol, lambda s: InsightsGenerator())
        locator.register_factory(ResponseFormatterProtocol, lambda s: ResponseFormatter())
        locator.register_factory(ErrorPresentationProtocol, lambda s: ErrorPresentation())
        
    except ImportError as e:
        # Services not yet implemented, will be registered when available
        import logging
        logging.getLogger(__name__).warning(f"Could not register response services: {e}")
    
    # Register prompt generation services
    try:
        from app.services.processing.prompt.generator import PromptGenerator
        
        locator.register_factory(PromptGeneratorProtocol, lambda s: PromptGenerator(s))
        
    except ImportError as e:
        # Services not yet implemented, will be registered when available
        import logging
        logging.getLogger(__name__).warning(f"Could not register prompt services: {e}")
    
    # Register API coordination services
    try:
        from app.services.api.coordinator import APICoordinator
        
        locator.register_factory(APICoordinatorProtocol, lambda s: APICoordinator(s))
        
    except ImportError as e:
        # Services not yet implemented, will be registered when available
        import logging
        logging.getLogger(__name__).warning(f"Could not register API services: {e}")


# Service dependency helpers

class ServiceDependency:
    """Helper class for service dependencies"""
    
    def __init__(self, interface: Type[T]):
        self.interface = interface
    
    def __call__(self) -> T:
        """Get service instance"""
        return get_service_locator().get(self.interface)


def service_dependency(interface: Type[T]) -> Callable[[], T]:
    """Create a service dependency function"""
    return ServiceDependency(interface)


# Context manager for testing

class ServiceScope:
    """Context manager for isolated service scope (testing)"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings
        self._original_locator = None
        self._test_locator = None
    
    def __enter__(self) -> ServiceLocator:
        global _service_locator
        self._original_locator = _service_locator
        self._test_locator = ServiceLocator(self.settings)
        _service_locator = self._test_locator
        return self._test_locator
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _service_locator
        _service_locator = self._original_locator