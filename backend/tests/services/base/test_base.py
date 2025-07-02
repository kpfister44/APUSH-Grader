"""Base test classes for service testing"""

import pytest
from unittest.mock import Mock
from typing import Type, TypeVar
from app.services.dependencies.service_locator import ServiceLocator, ServiceScope
from app.config.settings import Settings

T = TypeVar('T')


class ServiceTestBase:
    """Base class for service tests with common utilities"""
    
    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Mock settings for testing"""
        return Settings(
            environment="test",
            debug=True,
            openai_api_key="test-openai-key",
            anthropic_api_key="test-anthropic-key"
        )
    
    @pytest.fixture
    def service_scope(self, mock_settings: Settings):
        """Clean service scope for each test"""
        with ServiceScope(mock_settings) as locator:
            yield locator
    
    def register_mock_service(
        self, 
        locator: ServiceLocator, 
        interface: Type[T], 
        mock_instance: T
    ) -> None:
        """Helper to register mock services"""
        locator.register_singleton(interface, mock_instance)
    
    def create_mock_service(self, interface: Type[T], **kwargs) -> Mock:
        """Create a mock service with specified behavior"""
        mock = Mock(spec=interface)
        for attr, value in kwargs.items():
            setattr(mock, attr, value)
        return mock


class EssayServiceTestBase(ServiceTestBase):
    """Base class for essay processing service tests"""
    
    @pytest.fixture
    def sample_essay_text(self) -> str:
        """Sample essay text for testing"""
        return """
        This is a sample essay about the American Revolution.
        
        The American Revolution was a significant event in history. It demonstrated
        the colonists' desire for independence from British rule. According to 
        historical documents, the revolution began with protests against taxation
        without representation.
        
        In conclusion, the American Revolution established the United States
        as an independent nation and set precedents for democratic governance.
        """
    
    @pytest.fixture
    def short_essay_text(self) -> str:
        """Short essay text for testing validation"""
        return "This is too short."
    
    @pytest.fixture
    def long_essay_text(self) -> str:
        """Long essay text for testing validation"""
        # Generate a very long essay (over 2400 words)
        long_text = "This is a very long essay. " * 300
        return long_text
    
    @pytest.fixture
    def informal_essay_text(self) -> str:
        """Essay with informal language for testing"""
        return """
        The American Revolution was like, super important. It basically showed
        that the colonists didn't wanna be under British rule anymore. They were
        totally fed up with all the taxes and stuff.
        
        I think the revolution was really cool because it established democracy
        and freedom. The colonists were basically fighting for their rights.
        """
    
    def get_word_count(self, text: str) -> int:
        """Helper to count words in text"""
        import re
        words = re.findall(r'\b\w+\b', text)
        return len(words)


class IntegrationTestBase(ServiceTestBase):
    """Base class for integration tests"""
    
    @pytest.fixture
    def real_service_locator(self, mock_settings: Settings) -> ServiceLocator:
        """Service locator with real service implementations"""
        with ServiceScope(mock_settings) as locator:
            # Register real services
            self._register_real_services(locator)
            yield locator
    
    def _register_real_services(self, locator: ServiceLocator) -> None:
        """Register real service implementations"""
        from app.services.base.protocols import (
            EssayProcessorProtocol,
            EssayValidatorProtocol,
            TextAnalyzerProtocol,
            TextCleanerProtocol,
            WarningGeneratorProtocol
        )
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


class MockServiceMixin:
    """Mixin for creating mock services"""
    
    def create_mock_text_analyzer(self, **overrides):
        """Create mock text analyzer with default behavior"""
        from app.services.base.protocols import TextAnalyzerProtocol
        from app.models.processing.preprocessing import PreprocessingResult
        
        mock = Mock(spec=TextAnalyzerProtocol)
        
        # Default behavior
        mock.count_words.return_value = 150
        mock.count_paragraphs.return_value = 3
        mock.count_sentences.return_value = 8
        mock.contains_thesis_indicators.return_value = True
        mock.contains_evidence_keywords.return_value = True
        mock.contains_informal_language.return_value = False
        mock.get_first_paragraph.return_value = "Sample first paragraph"
        
        # Default analyze_text result
        mock.analyze_text.return_value = PreprocessingResult(
            cleaned_text="Cleaned sample text",
            word_count=150,
            paragraph_count=3,
            warnings=[]
        )
        
        # Apply overrides
        for attr, value in overrides.items():
            setattr(mock, attr, value)
        
        return mock
    
    def create_mock_text_cleaner(self, **overrides):
        """Create mock text cleaner with default behavior"""
        from app.services.base.protocols import TextCleanerProtocol
        
        mock = Mock(spec=TextCleanerProtocol)
        mock.clean_text.side_effect = lambda text: text.strip()
        
        # Apply overrides
        for attr, value in overrides.items():
            setattr(mock, attr, value)
        
        return mock
    
    def create_mock_warning_generator(self, **overrides):
        """Create mock warning generator with default behavior"""
        from app.services.base.protocols import WarningGeneratorProtocol
        
        mock = Mock(spec=WarningGeneratorProtocol)
        mock.generate_warnings.return_value = []
        mock.get_max_word_count.return_value = 2400
        
        # Apply overrides
        for attr, value in overrides.items():
            setattr(mock, attr, value)
        
        return mock