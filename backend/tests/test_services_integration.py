"""Integration tests for Phase 1C-1 services"""

import pytest
from app.models.core.essay_types import EssayType
from app.services.dependencies.service_locator import get_service_locator
from app.services.base.protocols import (
    EssayProcessorProtocol,
    TextCleanerProtocol,
    TextAnalyzerProtocol,
    EssayValidatorProtocol,
    WarningGeneratorProtocol
)


def test_service_locator_registration():
    """Test that all services are properly registered"""
    locator = get_service_locator()
    
    # Test that all services can be retrieved
    cleaner = locator.get(TextCleanerProtocol)
    analyzer = locator.get(TextAnalyzerProtocol)
    validator = locator.get(EssayValidatorProtocol)
    warning_generator = locator.get(WarningGeneratorProtocol)
    processor = locator.get(EssayProcessorProtocol)
    
    assert cleaner is not None
    assert analyzer is not None
    assert validator is not None
    assert warning_generator is not None
    assert processor is not None


def test_text_cleaner_basic():
    """Test TextCleaner basic functionality"""
    locator = get_service_locator()
    cleaner = locator.get(TextCleanerProtocol)
    
    text = "  This   has   extra   spaces  "
    result = cleaner.clean_text(text)
    
    assert result == "This has extra spaces"


def test_text_analyzer_basic():
    """Test TextAnalyzer basic functionality"""
    locator = get_service_locator()
    analyzer = locator.get(TextAnalyzerProtocol)
    
    text = "This is a test essay about history."
    word_count = analyzer.count_words(text)
    paragraph_count = analyzer.count_paragraphs(text)
    
    assert word_count == 7
    assert paragraph_count == 1


def test_essay_validator_basic():
    """Test EssayValidator basic functionality"""
    locator = get_service_locator()
    validator = locator.get(EssayValidatorProtocol)
    
    # Test valid length (need at least 25 words for SAQ)
    long_text = "This is a valid SAQ response with enough words to pass validation requirements. " * 3
    assert validator.is_valid_length(long_text, EssayType.SAQ)
    
    # Test invalid length 
    assert not validator.is_valid_length("Short", EssayType.SAQ)


def test_warning_generator_basic():
    """Test WarningGenerator basic functionality"""
    locator = get_service_locator()
    warning_generator = locator.get(WarningGeneratorProtocol)
    
    # Test with good essay (should have minimal warnings)
    warnings = warning_generator.generate_warnings("Good essay text", 300, 3, EssayType.SAQ)
    assert isinstance(warnings, list)
    
    # Test with short essay (should have warnings)
    warnings = warning_generator.generate_warnings("Short", 10, 1, EssayType.SAQ)
    assert len(warnings) > 0


def test_essay_processor_integration():
    """Test EssayProcessor integration with all services"""
    locator = get_service_locator()
    processor = locator.get(EssayProcessorProtocol)
    
    essay_text = """
    This is a sample essay about the American Revolution.
    
    The American Revolution was a significant event that established
    the United States as an independent nation. Historical evidence
    demonstrates that the colonists fought for freedom from British rule.
    
    In conclusion, the revolution was a pivotal moment in history.
    """
    
    result = processor.preprocess_essay(essay_text, EssayType.SAQ)
    
    assert result.cleaned_text is not None
    assert result.word_count > 20
    assert result.paragraph_count >= 1
    assert isinstance(result.warnings, list)


def test_essay_processor_validation_success():
    """Test essay processor validation with valid essay"""
    locator = get_service_locator()
    processor = locator.get(EssayProcessorProtocol)
    
    valid_essay = "This is a valid SAQ response that has enough words to pass the minimum threshold for validation requirements set by the system. " * 2
    
    # Should not raise exception
    processor.validate_essay(valid_essay, EssayType.SAQ)


def test_essay_processor_validation_failure():
    """Test essay processor validation with invalid essay"""
    locator = get_service_locator()
    processor = locator.get(EssayProcessorProtocol)
    
    from app.services.base.exceptions import EssayTooShortError
    
    # Should raise exception for too short essay
    with pytest.raises(EssayTooShortError):
        processor.validate_essay("Short", EssayType.SAQ)


def test_end_to_end_processing():
    """Test complete end-to-end processing workflow"""
    locator = get_service_locator()
    processor = locator.get(EssayProcessorProtocol)
    
    essay_text = """
    The American Revolution was a transformative period in American history that fundamentally changed the political and social landscape of North America.
    I argue that the revolution was necessary for establishing democratic principles and individual freedoms that would become the foundation of American government.
    
    According to historical documents, the colonists faced numerous grievances against British rule, including taxation without representation, quartering of soldiers, and restrictions on trade.
    Evidence suggests that peaceful resolution was no longer possible after years of failed diplomatic attempts and increasing tensions between colonial and British authorities.
    The Declaration of Independence outlined these grievances and justified the colonial decision to seek independence from British rule.
    
    Furthermore, the Revolution established important precedents for democratic governance, including the separation of powers, checks and balances, and protection of individual rights.
    These principles would later be enshrined in the Constitution and Bill of Rights, creating a lasting legacy for future generations.
    
    In conclusion, the American Revolution was justified and established the foundation for modern American democracy and constitutional government that continues to influence political systems worldwide.
    """
    
    # Test preprocessing
    result = processor.preprocess_essay(essay_text, EssayType.LEQ)
    
    assert result.word_count > 50
    assert result.paragraph_count == 4
    assert len(result.cleaned_text) > 0
    
    # Test validation
    processor.validate_essay(essay_text, EssayType.LEQ)  # Should not raise
    
    # Test combined workflow
    combined_result = processor.process_and_validate(essay_text, EssayType.LEQ)
    assert combined_result.word_count == result.word_count
    assert combined_result.paragraph_count == result.paragraph_count