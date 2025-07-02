"""Tests for preprocessing models - ported from Swift PreprocessingModelsTests"""

import pytest
from app.models.processing.preprocessing import PreprocessingResult


class TestPreprocessingResult:
    """Test suite for PreprocessingResult model"""
    
    def test_preprocessing_result_creation(self):
        """Test creating a preprocessing result"""
        result = PreprocessingResult(
            cleaned_text="This is a test essay.",
            word_count=5,
            paragraph_count=1,
            warnings=[]
        )
        
        assert result.cleaned_text == "This is a test essay."
        assert result.word_count == 5
        assert result.paragraph_count == 1
        assert result.warnings == []
    
    def test_preprocessing_result_with_warnings(self):
        """Test creating preprocessing result with warnings"""
        warnings = ["Essay is quite short", "Consider adding more examples"]
        result = PreprocessingResult(
            cleaned_text="Short essay.",
            word_count=2,
            paragraph_count=1,
            warnings=warnings
        )
        
        assert result.warnings == warnings
    
    def test_is_valid_no_warnings(self):
        """Test is_valid returns True when no warnings"""
        result = PreprocessingResult(
            cleaned_text="Good essay with sufficient content.",
            word_count=6,
            paragraph_count=1,
            warnings=[]
        )
        
        assert result.is_valid is True
    
    def test_is_valid_advisory_warnings_only(self):
        """Test is_valid returns True for advisory warnings only"""
        result = PreprocessingResult(
            cleaned_text="Essay with minor issues.",
            word_count=5,
            paragraph_count=1,
            warnings=["Consider using more formal language", "Check grammar"]
        )
        
        assert result.is_valid is True
    
    def test_is_valid_false_with_too_short(self):
        """Test is_valid returns False with 'too short' warning"""
        result = PreprocessingResult(
            cleaned_text="Short",
            word_count=1,
            paragraph_count=1,
            warnings=["Essay is too short for accurate grading"]
        )
        
        assert result.is_valid is False
    
    def test_is_valid_false_with_too_long(self):
        """Test is_valid returns False with 'too long' warning"""
        result = PreprocessingResult(
            cleaned_text="Very long essay content...",
            word_count=3000,
            paragraph_count=20,
            warnings=["Essay is too long and exceeds maximum word limit"]
        )
        
        assert result.is_valid is False
    
    def test_is_valid_mixed_warnings(self):
        """Test is_valid with mix of critical and advisory warnings"""
        result = PreprocessingResult(
            cleaned_text="Content",
            word_count=1,
            paragraph_count=1,
            warnings=[
                "Essay is too short for grading",
                "Consider adding examples",
                "Check spelling"
            ]
        )
        
        assert result.is_valid is False
    
    def test_has_warnings_true(self):
        """Test has_warnings returns True when warnings present"""
        result = PreprocessingResult(
            cleaned_text="Test",
            word_count=1,
            paragraph_count=1,
            warnings=["Some warning"]
        )
        
        assert result.has_warnings is True
    
    def test_has_warnings_false(self):
        """Test has_warnings returns False when no warnings"""
        result = PreprocessingResult(
            cleaned_text="Good content",
            word_count=2,
            paragraph_count=1,
            warnings=[]
        )
        
        assert result.has_warnings is False
    
    def test_warning_count_zero(self):
        """Test warning_count returns 0 for no warnings"""
        result = PreprocessingResult(
            cleaned_text="Content",
            word_count=1,
            paragraph_count=1,
            warnings=[]
        )
        
        assert result.warning_count == 0
    
    def test_warning_count_multiple(self):
        """Test warning_count returns correct count"""
        warnings = ["Warning 1", "Warning 2", "Warning 3"]
        result = PreprocessingResult(
            cleaned_text="Content",
            word_count=1,
            paragraph_count=1,
            warnings=warnings
        )
        
        assert result.warning_count == 3
    
    def test_critical_warnings_empty(self):
        """Test critical_warnings returns empty list when none present"""
        result = PreprocessingResult(
            cleaned_text="Content",
            word_count=1,
            paragraph_count=1,
            warnings=["Advisory warning", "Grammar check needed"]
        )
        
        assert result.critical_warnings == []
    
    def test_critical_warnings_too_short(self):
        """Test critical_warnings identifies 'too short' warnings"""
        warnings = [
            "Essay is too short for grading",
            "Consider adding examples",
            "Content too short to analyze"
        ]
        result = PreprocessingResult(
            cleaned_text="Short",
            word_count=1,
            paragraph_count=1,
            warnings=warnings
        )
        
        critical = result.critical_warnings
        assert len(critical) == 2
        assert "Essay is too short for grading" in critical
        assert "Content too short to analyze" in critical
    
    def test_critical_warnings_too_long(self):
        """Test critical_warnings identifies 'too long' warnings"""
        warnings = [
            "Essay is too long and exceeds limit",
            "Check grammar",
            "Content too long for processing"
        ]
        result = PreprocessingResult(
            cleaned_text="Long content...",
            word_count=5000,
            paragraph_count=50,
            warnings=warnings
        )
        
        critical = result.critical_warnings
        assert len(critical) == 2
        assert "Essay is too long and exceeds limit" in critical
        assert "Content too long for processing" in critical
    
    def test_advisory_warnings_empty(self):
        """Test advisory_warnings returns empty when only critical warnings"""
        result = PreprocessingResult(
            cleaned_text="Short",
            word_count=1,
            paragraph_count=1,
            warnings=["Essay is too short", "Content too short"]
        )
        
        assert result.advisory_warnings == []
    
    def test_advisory_warnings_only_advisory(self):
        """Test advisory_warnings returns all warnings when no critical ones"""
        warnings = ["Check grammar", "Consider more examples", "Improve structure"]
        result = PreprocessingResult(
            cleaned_text="Good content",
            word_count=2,
            paragraph_count=1,
            warnings=warnings
        )
        
        assert result.advisory_warnings == warnings
    
    def test_advisory_warnings_mixed(self):
        """Test advisory_warnings filters out critical warnings"""
        warnings = [
            "Essay is too short",
            "Check grammar",
            "Content too long",
            "Add more examples",
            "Improve clarity"
        ]
        result = PreprocessingResult(
            cleaned_text="Content",
            word_count=1,
            paragraph_count=1,
            warnings=warnings
        )
        
        advisory = result.advisory_warnings
        assert len(advisory) == 3
        assert "Check grammar" in advisory
        assert "Add more examples" in advisory
        assert "Improve clarity" in advisory
    
    def test_has_critical_warnings_false(self):
        """Test has_critical_warnings returns False when none present"""
        result = PreprocessingResult(
            cleaned_text="Content",
            word_count=1,
            paragraph_count=1,
            warnings=["Advisory warning", "Grammar suggestion"]
        )
        
        assert result.has_critical_warnings is False
    
    def test_has_critical_warnings_true_too_short(self):
        """Test has_critical_warnings returns True for 'too short'"""
        result = PreprocessingResult(
            cleaned_text="Short",
            word_count=1,
            paragraph_count=1,
            warnings=["Essay is too short", "Add examples"]
        )
        
        assert result.has_critical_warnings is True
    
    def test_has_critical_warnings_true_too_long(self):
        """Test has_critical_warnings returns True for 'too long'"""
        result = PreprocessingResult(
            cleaned_text="Long content",
            word_count=2,
            paragraph_count=1,
            warnings=["Essay is too long", "Check format"]
        )
        
        assert result.has_critical_warnings is True
    
    def test_case_insensitive_critical_warning_detection(self):
        """Test critical warning detection is case insensitive"""
        result = PreprocessingResult(
            cleaned_text="Content",
            word_count=1,
            paragraph_count=1,
            warnings=["Essay is TOO SHORT", "Content TOO LONG for processing"]
        )
        
        assert result.has_critical_warnings is True
        assert len(result.critical_warnings) == 2
        assert result.is_valid is False
    
    def test_word_count_validation(self):
        """Test word count property"""
        result = PreprocessingResult(
            cleaned_text="This is a test essay with multiple words",
            word_count=9,
            paragraph_count=1,
            warnings=[]
        )
        
        assert result.word_count == 9
    
    def test_paragraph_count_validation(self):
        """Test paragraph count property"""
        result = PreprocessingResult(
            cleaned_text="Paragraph one.\n\nParagraph two.\n\nParagraph three.",
            word_count=6,
            paragraph_count=3,
            warnings=[]
        )
        
        assert result.paragraph_count == 3