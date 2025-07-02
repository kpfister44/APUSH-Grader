"""Tests for EssayValidator service"""

import pytest
from app.models.core.essay_types import EssayType
from app.services.processing.essay.validator import EssayValidator
from app.services.base.exceptions import EssayTooShortError, EssayTooLongError
from tests.services.base.test_base import EssayServiceTestBase, MockServiceMixin


class TestEssayValidator(EssayServiceTestBase, MockServiceMixin):
    """Test suite for EssayValidator service"""
    
    @pytest.fixture
    def validator(self, mock_settings):
        """Create EssayValidator instance"""
        return EssayValidator(mock_settings)
    
    def test_validate_essay_empty_text(self, validator, real_service_locator):
        """Test validation with empty text raises exception"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 0)
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        with pytest.raises(EssayTooShortError):
            validator.validate_essay("", EssayType.SAQ)
        
        with pytest.raises(EssayTooShortError):
            validator.validate_essay("   ", EssayType.SAQ)
    
    def test_validate_essay_too_short_dbq(self, validator, real_service_locator):
        """Test DBQ essay too short validation"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 150)  # Below 200 threshold
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        with pytest.raises(EssayTooShortError) as exc_info:
            validator.validate_essay("Short essay", EssayType.DBQ)
        
        assert "150 words" in str(exc_info.value)
        assert "200 words required" in str(exc_info.value)
        assert exc_info.value.word_count == 150
        assert exc_info.value.essay_type == "DBQ"
    
    def test_validate_essay_too_short_leq(self, validator, real_service_locator):
        """Test LEQ essay too short validation"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 100)  # Below 150 threshold
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        with pytest.raises(EssayTooShortError):
            validator.validate_essay("Short essay", EssayType.LEQ)
    
    def test_validate_essay_too_short_saq(self, validator, real_service_locator):
        """Test SAQ essay too short validation"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 20)  # Below 25 threshold
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        with pytest.raises(EssayTooShortError):
            validator.validate_essay("Short", EssayType.SAQ)
    
    def test_validate_essay_too_long_dbq(self, validator, real_service_locator):
        """Test DBQ essay too long validation"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 2500)  # Above 2400 limit
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        with pytest.raises(EssayTooLongError) as exc_info:
            validator.validate_essay("Very long essay", EssayType.DBQ)
        
        assert "2500 words" in str(exc_info.value)
        assert "2400 words allowed" in str(exc_info.value)
        assert exc_info.value.word_count == 2500
        assert exc_info.value.essay_type == "DBQ"
    
    def test_validate_essay_too_long_leq(self, validator, real_service_locator):
        """Test LEQ essay too long validation"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 2100)  # Above 2000 limit
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        with pytest.raises(EssayTooLongError):
            validator.validate_essay("Very long essay", EssayType.LEQ)
    
    def test_validate_essay_too_long_saq(self, validator, real_service_locator):
        """Test SAQ essay too long validation"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 700)  # Above 600 limit
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        with pytest.raises(EssayTooLongError):
            validator.validate_essay("Very long essay", EssayType.SAQ)
    
    def test_validate_essay_valid_length(self, validator, real_service_locator):
        """Test validation passes for valid length essays"""
        # Test valid lengths for each essay type
        test_cases = [
            (EssayType.DBQ, 500),   # Valid DBQ length
            (EssayType.LEQ, 400),   # Valid LEQ length
            (EssayType.SAQ, 100),   # Valid SAQ length
        ]
        
        from app.services.base.protocols import TextAnalyzerProtocol
        
        for essay_type, word_count in test_cases:
            analyzer = self.create_mock_text_analyzer(count_words=lambda text: word_count)
            real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
            
            # Should not raise any exception
            validator.validate_essay("Valid essay text", essay_type)
    
    def test_get_max_word_count(self, validator):
        """Test getting maximum word counts"""
        assert validator.get_max_word_count(EssayType.DBQ) == 2400
        assert validator.get_max_word_count(EssayType.LEQ) == 2000
        assert validator.get_max_word_count(EssayType.SAQ) == 600
    
    def test_get_min_word_count(self, validator):
        """Test getting minimum word counts"""
        assert validator.get_min_word_count(EssayType.DBQ) == 200
        assert validator.get_min_word_count(EssayType.LEQ) == 150
        assert validator.get_min_word_count(EssayType.SAQ) == 25
    
    def test_is_valid_length_true(self, validator, real_service_locator):
        """Test is_valid_length returns True for valid essays"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 300)
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        assert validator.is_valid_length("Valid essay", EssayType.SAQ) is True
    
    def test_is_valid_length_false(self, validator, real_service_locator):
        """Test is_valid_length returns False for invalid essays"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 10)  # Too short
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        assert validator.is_valid_length("Short", EssayType.SAQ) is False
    
    def test_get_validation_info_valid(self, validator, real_service_locator):
        """Test getting validation info for valid essay"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 300)
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        info = validator.get_validation_info("Valid essay", EssayType.SAQ)
        
        assert info["is_valid"] is True
        assert info["status"] == "valid"
        assert info["word_count"] == 300
        assert info["min_required"] == 25
        assert info["max_allowed"] == 600
        assert info["essay_type"] == "SAQ"
        assert "Valid length" in info["message"]
    
    def test_get_validation_info_too_short(self, validator, real_service_locator):
        """Test getting validation info for too short essay"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 10)
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        info = validator.get_validation_info("Short", EssayType.SAQ)
        
        assert info["is_valid"] is False
        assert info["status"] == "too_short"
        assert info["word_count"] == 10
        assert "Too short" in info["message"]
    
    def test_get_validation_info_too_long(self, validator, real_service_locator):
        """Test getting validation info for too long essay"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 700)
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        info = validator.get_validation_info("Long essay", EssayType.SAQ)
        
        assert info["is_valid"] is False
        assert info["status"] == "too_long"
        assert info["word_count"] == 700
        assert "Too long" in info["message"]
    
    def test_get_validation_info_empty(self, validator, real_service_locator):
        """Test getting validation info for empty essay"""
        analyzer = self.create_mock_text_analyzer(count_words=lambda text: 0)
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        info = validator.get_validation_info("", EssayType.SAQ)
        
        assert info["is_valid"] is False
        assert info["status"] == "empty"
        assert info["word_count"] == 0
        assert "empty" in info["message"].lower()
    
    def test_check_quick_validation_valid(self, validator):
        """Test quick validation for valid word count"""
        result = validator.check_quick_validation(300, EssayType.SAQ)
        
        assert result["is_valid"] is True
        assert result["status"] == "valid"
        assert "Valid word count" in result["message"]
    
    def test_check_quick_validation_too_short(self, validator):
        """Test quick validation for too short word count"""
        result = validator.check_quick_validation(10, EssayType.SAQ)
        
        assert result["is_valid"] is False
        assert result["status"] == "too_short"
        assert "Below minimum threshold" in result["message"]
    
    def test_check_quick_validation_too_long(self, validator):
        """Test quick validation for too long word count"""
        result = validator.check_quick_validation(700, EssayType.SAQ)
        
        assert result["is_valid"] is False
        assert result["status"] == "too_long"
        assert "Exceeds maximum limit" in result["message"]
    
    def test_validation_thresholds_consistency(self, validator):
        """Test that validation thresholds are consistent across methods"""
        for essay_type in [EssayType.DBQ, EssayType.LEQ, EssayType.SAQ]:
            min_count = validator.get_min_word_count(essay_type)
            max_count = validator.get_max_word_count(essay_type)
            
            # Min should be less than max
            assert min_count < max_count
            
            # Quick validation should match get_validation_info
            below_min = validator.check_quick_validation(min_count - 1, essay_type)
            above_max = validator.check_quick_validation(max_count + 1, essay_type)
            valid_range = validator.check_quick_validation(min_count + 10, essay_type)
            
            assert below_min["is_valid"] is False
            assert above_max["is_valid"] is False
            assert valid_range["is_valid"] is True