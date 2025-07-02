"""Tests for EssayProcessor service"""

import pytest
from app.models.core.essay_types import EssayType
from app.models.processing.preprocessing import PreprocessingResult
from app.services.processing.essay.processor import EssayProcessor
from app.services.base.exceptions import EssayTooShortError
from tests.services.base.test_base import EssayServiceTestBase, MockServiceMixin


class TestEssayProcessor(EssayServiceTestBase, MockServiceMixin):
    """Test suite for EssayProcessor service"""
    
    @pytest.fixture
    def processor(self, mock_settings):
        """Create EssayProcessor instance"""
        return EssayProcessor(mock_settings)
    
    def test_preprocess_essay_success(self, processor, real_service_locator):
        """Test successful essay preprocessing"""
        # Mock text analyzer
        analyzer = self.create_mock_text_analyzer()
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        result = processor.preprocess_essay("Sample essay text", EssayType.SAQ)
        
        assert isinstance(result, PreprocessingResult)
        assert analyzer.analyze_text.called
    
    def test_validate_essay_success(self, processor, real_service_locator):
        """Test successful essay validation"""
        # Mock validator
        from app.services.base.protocols import EssayValidatorProtocol
        from unittest.mock import Mock
        
        validator = Mock(spec=EssayValidatorProtocol)
        validator.validate_essay.return_value = None  # No exception = valid
        real_service_locator.register_singleton(EssayValidatorProtocol, validator)
        
        # Should not raise any exception
        processor.validate_essay("Valid essay text", EssayType.SAQ)
        assert validator.validate_essay.called
    
    def test_validate_essay_failure(self, processor, real_service_locator):
        """Test essay validation failure"""
        # Mock validator that raises exception
        from app.services.base.protocols import EssayValidatorProtocol
        from unittest.mock import Mock
        
        validator = Mock(spec=EssayValidatorProtocol)
        validator.validate_essay.side_effect = EssayTooShortError("Too short", word_count=10, essay_type="SAQ")
        real_service_locator.register_singleton(EssayValidatorProtocol, validator)
        
        with pytest.raises(EssayTooShortError):
            processor.validate_essay("Short", EssayType.SAQ)
    
    def test_process_and_validate_success(self, processor, real_service_locator):
        """Test combined processing and validation workflow - success"""
        # Mock dependencies
        from app.services.base.protocols import TextAnalyzerProtocol, EssayValidatorProtocol
        from unittest.mock import Mock
        
        analyzer = self.create_mock_text_analyzer()
        validator = Mock(spec=EssayValidatorProtocol)
        validator.validate_essay.return_value = None
        
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        real_service_locator.register_singleton(EssayValidatorProtocol, validator)
        
        result = processor.process_and_validate("Valid essay text", EssayType.SAQ)
        
        assert isinstance(result, PreprocessingResult)
        assert validator.validate_essay.called
        assert analyzer.analyze_text.called
    
    def test_process_and_validate_validation_failure(self, processor, real_service_locator):
        """Test combined processing fails on validation"""
        # Mock validator that fails
        from app.services.base.protocols import EssayValidatorProtocol
        from unittest.mock import Mock
        
        validator = Mock(spec=EssayValidatorProtocol)
        validator.validate_essay.side_effect = EssayTooShortError("Too short", word_count=10, essay_type="SAQ")
        real_service_locator.register_singleton(EssayValidatorProtocol, validator)
        
        with pytest.raises(EssayTooShortError):
            processor.process_and_validate("Short", EssayType.SAQ)
    
    def test_get_processing_info_success(self, processor, real_service_locator):
        """Test getting processing info for successful case"""
        # Mock dependencies
        from app.services.base.protocols import TextAnalyzerProtocol, EssayValidatorProtocol
        from unittest.mock import Mock
        
        analyzer = self.create_mock_text_analyzer()
        validator = Mock(spec=EssayValidatorProtocol)
        validator.validate_essay.return_value = None
        
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        real_service_locator.register_singleton(EssayValidatorProtocol, validator)
        
        info = processor.get_processing_info("Valid essay", EssayType.SAQ)
        
        assert info["success"] is True
        assert info["validation_passed"] is True
        assert info["validation_error"] is None
        assert info["preprocessing_result"] is not None
        assert info["essay_type"] == "SAQ"
        
        # Check preprocessing result structure
        result = info["preprocessing_result"]
        assert "word_count" in result
        assert "paragraph_count" in result
        assert "is_valid" in result
        assert "warnings" in result
    
    def test_get_processing_info_validation_failure(self, processor, real_service_locator):
        """Test getting processing info with validation failure"""
        # Mock dependencies
        from app.services.base.protocols import TextAnalyzerProtocol, EssayValidatorProtocol
        from unittest.mock import Mock
        
        analyzer = self.create_mock_text_analyzer()
        validator = Mock(spec=EssayValidatorProtocol)
        validator.validate_essay.side_effect = EssayTooShortError("Too short", word_count=10, essay_type="SAQ")
        
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        real_service_locator.register_singleton(EssayValidatorProtocol, validator)
        
        info = processor.get_processing_info("Short essay", EssayType.SAQ)
        
        assert info["success"] is True  # Preprocessing succeeded
        assert info["validation_passed"] is False
        assert "Too short" in info["validation_error"]
        assert info["preprocessing_result"] is not None
    
    def test_get_processing_info_complete_failure(self, processor, real_service_locator):
        """Test getting processing info with complete failure"""
        # Don't register any dependencies to cause failure
        
        info = processor.get_processing_info("Any text", EssayType.SAQ)
        
        assert info["success"] is False
        assert "error" in info
        assert info["validation_passed"] is False
        assert info["preprocessing_result"] is None
    
    def test_preview_processing_success(self, processor, real_service_locator):
        """Test processing preview functionality"""
        analyzer = self.create_mock_text_analyzer()
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        long_text = "This is a long essay text that will be truncated in the preview. " * 10
        preview = processor.preview_processing(long_text, EssayType.SAQ, max_preview=50)
        
        assert "original_preview" in preview
        assert "cleaned_preview" in preview
        assert "statistics" in preview
        assert "warnings" in preview
        assert "is_valid" in preview
        assert "essay_type" in preview
        
        # Check preview is actually truncated
        assert len(preview["original_preview"]) <= 53  # 50 + "..."
        
        # Check statistics
        stats = preview["statistics"]
        assert "original_length" in stats
        assert "cleaned_length" in stats
        assert "word_count" in stats
        assert "paragraph_count" in stats
    
    def test_preview_processing_failure(self, processor, real_service_locator):
        """Test processing preview with failure"""
        # Don't register dependencies to cause failure
        
        text = "Sample text"
        preview = processor.preview_processing(text, EssayType.SAQ)
        
        assert "error" in preview
        assert "original_preview" in preview
        assert preview["original_preview"] == text
        assert "essay_type" in preview
    
    def test_input_validation(self, processor):
        """Test input validation for processor methods"""
        # Test with None essay type
        with pytest.raises(ValueError):
            processor.preprocess_essay("text", None)
        
        # Test with empty text (should not raise ValueError, but might raise other exceptions)
        # This depends on the validator implementation
        pass
    
    def test_different_essay_types(self, processor, real_service_locator):
        """Test processing with different essay types"""
        analyzer = self.create_mock_text_analyzer()
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        text = "Sample essay text for testing"
        
        for essay_type in [EssayType.DBQ, EssayType.LEQ, EssayType.SAQ]:
            result = processor.preprocess_essay(text, essay_type)
            assert isinstance(result, PreprocessingResult)
            
            # Verify analyzer was called with correct essay type
            analyzer.analyze_text.assert_called_with(text, essay_type)
    
    def test_error_handling_and_logging(self, processor, real_service_locator):
        """Test error handling and logging functionality"""
        # Mock analyzer that raises an exception
        from app.services.base.protocols import TextAnalyzerProtocol
        from unittest.mock import Mock
        
        analyzer = Mock(spec=TextAnalyzerProtocol)
        analyzer.analyze_text.side_effect = Exception("Test error")
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        with pytest.raises(Exception):
            processor.preprocess_essay("text", EssayType.SAQ)
    
    def test_service_dependency_injection(self, processor, real_service_locator):
        """Test that processor correctly uses dependency injection"""
        # This test verifies the processor uses the service locator correctly
        analyzer = self.create_mock_text_analyzer()
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        # Process essay
        result = processor.preprocess_essay("test", EssayType.SAQ)
        
        # Verify the mock was called (proving DI worked)
        assert analyzer.analyze_text.called
        assert isinstance(result, PreprocessingResult)