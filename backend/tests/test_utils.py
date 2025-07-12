"""Tests for utility functions (simplified architecture)"""

import pytest
from app.utils.essay_processing import (
    preprocess_essay, clean_text, count_words, count_paragraphs, generate_warnings
)
from app.utils.prompt_generation import generate_grading_prompt
from app.utils.response_processing import process_ai_response
from app.models.core import EssayType
from app.models.processing import PreprocessingResult


class TestEssayProcessing:
    """Test essay processing utilities"""
    
    def test_clean_text_basic(self):
        """Test basic text cleaning"""
        text = "  Hello    world!  \n\n  More text.  "
        cleaned = clean_text(text)
        assert cleaned == "Hello world! More text."
    
    def test_count_words(self):
        """Test word counting"""
        assert count_words("Hello world") == 2
        assert count_words("") == 0
        assert count_words("  ") == 0
        assert count_words("One, two; three!") == 3
    
    def test_count_paragraphs(self):
        """Test paragraph counting"""
        text = "Para 1\n\nPara 2\n\nPara 3"
        assert count_paragraphs(text) == 3
        assert count_paragraphs("Single para") == 1
        assert count_paragraphs("") == 0
    
    def test_generate_warnings_short_essay(self):
        """Test warnings for short essays"""
        warnings = generate_warnings("Short text", 10, 1, EssayType.DBQ)
        assert any("too short" in w for w in warnings)
    
    def test_preprocess_essay_integration(self):
        """Test complete essay preprocessing"""
        essay = "This is a test essay about American history. It argues that the Revolution was caused by taxation without representation."
        result = preprocess_essay(essay, EssayType.DBQ)
        
        assert isinstance(result, PreprocessingResult)
        assert result.word_count > 0
        assert result.paragraph_count >= 1
        assert result.cleaned_text
        assert isinstance(result.warnings, list)


class TestPromptGeneration:
    """Test prompt generation utilities"""
    
    def test_generate_grading_prompt_dbq(self):
        """Test DBQ prompt generation"""
        preprocessing_result = PreprocessingResult(
            cleaned_text="Test essay",
            word_count=250,
            paragraph_count=3,
            warnings=[]
        )
        
        system_prompt, user_message = generate_grading_prompt(
            "Test essay", EssayType.DBQ, "Test prompt", preprocessing_result
        )
        
        assert "DBQ RUBRIC" in system_prompt
        assert "6 points total" in system_prompt
        assert "ESSAY TYPE: DBQ" in user_message
        assert "Word count: 250" in user_message
    
    def test_generate_grading_prompt_saq(self):
        """Test SAQ prompt generation"""
        preprocessing_result = PreprocessingResult(
            cleaned_text="Test essay",
            word_count=100,
            paragraph_count=1,
            warnings=[]
        )
        
        system_prompt, user_message = generate_grading_prompt(
            "Test essay", EssayType.SAQ, "Test prompt", preprocessing_result
        )
        
        assert "SAQ RUBRIC" in system_prompt
        assert "3 points total" in system_prompt
        assert "ESSAY TYPE: SAQ" in user_message


class TestResponseProcessing:
    """Test AI response processing utilities"""
    
    def test_process_valid_ai_response(self):
        """Test processing valid AI response"""
        mock_response = '''
        {
            "score": 4,
            "max_score": 6,
            "letter_grade": "B",
            "overall_feedback": "Good essay with solid analysis",
            "suggestions": ["Add more evidence", "Strengthen thesis"],
            "breakdown": {
                "thesis": {"score": 1, "max_score": 1, "feedback": "Clear thesis"},
                "contextualization": {"score": 1, "max_score": 1, "feedback": "Good context"},
                "evidence": {"score": 1, "max_score": 2, "feedback": "Need more evidence"},
                "analysis": {"score": 1, "max_score": 2, "feedback": "Basic analysis"}
            }
        }
        '''
        
        grade_response = process_ai_response(mock_response, EssayType.DBQ)
        
        assert grade_response.score == 4
        assert grade_response.max_score == 6
        assert grade_response.letter_grade == "B"
        assert "Good essay" in grade_response.overall_feedback
        assert len(grade_response.suggestions) == 2
        assert grade_response.breakdown.thesis.score == 1
    
    def test_process_invalid_json_response(self):
        """Test handling invalid JSON response"""
        from app.exceptions import ProcessingError
        
        invalid_response = "This is not JSON"
        
        with pytest.raises(ProcessingError, match="Invalid JSON response"):
            process_ai_response(invalid_response, EssayType.DBQ)
    
    def test_process_response_with_field_variations(self):
        """Test handling maxScore vs max_score field variations"""
        mock_response = '''
        {
            "score": 3,
            "max_score": 6,
            "letter_grade": "C",
            "overall_feedback": "Needs improvement",
            "suggestions": [],
            "breakdown": {
                "thesis": {"score": 1, "maxScore": 1, "feedback": "OK thesis"},
                "contextualization": {"score": 0, "max_score": 1, "feedback": "No context"},
                "evidence": {"score": 1, "maxScore": 2, "feedback": "Some evidence"},
                "analysis": {"score": 1, "max_score": 2, "feedback": "Weak analysis"}
            }
        }
        '''
        
        grade_response = process_ai_response(mock_response, EssayType.DBQ)
        assert grade_response.score == 3
        assert grade_response.breakdown.thesis.max_score == 1
        assert grade_response.breakdown.evidence.max_score == 2