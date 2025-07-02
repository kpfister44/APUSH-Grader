"""Tests for ResponseValidator service."""

import pytest

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse, GradeBreakdown, RubricItem
from app.models.processing.response import ValidationResult
from app.services.processing.response.validator import ResponseValidator


class TestResponseValidator:
    """Test suite for ResponseValidator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ResponseValidator()
    
    def create_valid_dbq_response(self) -> GradeResponse:
        """Create a valid DBQ response for testing."""
        breakdown = GradeBreakdown(
            thesis=RubricItem(score=1, max_score=1, feedback="Strong thesis"),
            contextualization=RubricItem(score=1, max_score=1, feedback="Good context"),
            evidence=RubricItem(score=2, max_score=2, feedback="Excellent evidence"),
            analysis=RubricItem(score=2, max_score=2, feedback="Sophisticated analysis")
        )
        
        return GradeResponse(
            score=6,
            max_score=6,
            breakdown=breakdown,
            overall_feedback="Excellent essay demonstrating mastery of historical analysis.",
            suggestions=["Continue developing complex arguments", "Expand document usage"]
        )
    
    def create_valid_saq_response(self) -> GradeResponse:
        """Create a valid SAQ response for testing."""
        breakdown = GradeBreakdown(
            thesis=RubricItem(score=1, max_score=1, feedback="Part A complete"),
            contextualization=RubricItem(score=1, max_score=1, feedback="Part B accurate"),
            evidence=RubricItem(score=1, max_score=1, feedback="Part C well-developed"),
            analysis=RubricItem(score=0, max_score=0, feedback="Not applicable for SAQ")
        )
        
        return GradeResponse(
            score=3,
            max_score=3,
            breakdown=breakdown,
            overall_feedback="Good SAQ response addressing all parts with specific historical evidence and clear answers to each component.",
            suggestions=["Add more specific details", "Consider multiple perspectives"]
        )
    
    def test_validate_valid_dbq_response(self):
        """Test validation of a valid DBQ response."""
        response = self.create_valid_dbq_response()
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert isinstance(result, ValidationResult)
        assert len(result.issues) == 0
        assert len(result.warnings) == 0
    
    def test_validate_valid_leq_response(self):
        """Test validation of a valid LEQ response."""
        response = self.create_valid_dbq_response()  # Same structure as DBQ
        result = self.validator.validate_response(response, EssayType.LEQ)
        
        assert isinstance(result, ValidationResult)
        assert len(result.issues) == 0
        assert len(result.warnings) == 0
    
    def test_validate_valid_saq_response(self):
        """Test validation of a valid SAQ response."""
        response = self.create_valid_saq_response()
        result = self.validator.validate_response(response, EssayType.SAQ)
        
        assert isinstance(result, ValidationResult)
        assert len(result.issues) == 0
        assert len(result.warnings) == 0
    
    def test_invalid_total_score_range(self):
        """Test validation catches invalid total scores."""
        response = self.create_valid_dbq_response()
        response.score = 7  # Above max
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.issues) > 0
        assert any("Invalid total score" in issue for issue in result.issues)
    
    def test_negative_total_score(self):
        """Test validation catches negative scores."""
        response = self.create_valid_dbq_response()
        response.score = -1
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.issues) > 0
        assert any("Invalid total score" in issue for issue in result.issues)
    
    def test_incorrect_max_score_for_essay_type(self):
        """Test validation catches incorrect max scores."""
        response = self.create_valid_dbq_response()
        response.max_score = 3  # Should be 6 for DBQ
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.issues) > 0
        assert any("Incorrect maximum score" in issue for issue in result.issues)
    
    def test_invalid_rubric_item_score(self):
        """Test validation catches invalid rubric item scores."""
        response = self.create_valid_dbq_response()
        response.breakdown.thesis.score = 2  # Above max of 1
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.issues) > 0
        assert any("thesis: invalid score" in issue for issue in result.issues)
    
    def test_incorrect_rubric_item_max_score(self):
        """Test validation catches incorrect rubric item max scores."""
        response = self.create_valid_dbq_response()
        response.breakdown.evidence.max_score = 1  # Should be 2 for DBQ
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.issues) > 0
        assert any("evidence: incorrect max score" in issue for issue in result.issues)
    
    def test_missing_feedback(self):
        """Test validation catches missing feedback."""
        response = self.create_valid_dbq_response()
        response.breakdown.thesis.feedback = ""
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.issues) > 0
        assert any("thesis: missing feedback" in issue for issue in result.issues)
    
    def test_score_consistency_check(self):
        """Test validation catches score inconsistencies."""
        response = self.create_valid_dbq_response()
        response.score = 5  # Breakdown adds up to 6
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.issues) > 0
        assert any("Score mismatch" in issue for issue in result.issues)
    
    def test_brief_feedback_warning(self):
        """Test validation warns about brief feedback."""
        response = self.create_valid_dbq_response()
        response.overall_feedback = "Good"  # Too brief
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.warnings) > 0
        assert any("feedback is quite brief" in warning for warning in result.warnings)
    
    def test_limited_suggestions_warning(self):
        """Test validation warns about limited suggestions."""
        response = self.create_valid_dbq_response()
        response.suggestions = ["One suggestion"]  # Less than 2
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        assert len(result.warnings) > 0
        assert any("Limited suggestions" in warning for warning in result.warnings)
    
    def test_saq_structure_validation(self):
        """Test SAQ-specific validation rules."""
        response = self.create_valid_saq_response()
        response.breakdown.evidence.max_score = 2  # Should be 1 for SAQ Part C
        
        result = self.validator.validate_response(response, EssayType.SAQ)
        
        assert len(result.issues) > 0
        assert any("partC: incorrect max score" in issue for issue in result.issues)
    
    def test_calculate_total_score_dbq(self):
        """Test total score calculation for DBQ."""
        response = self.create_valid_dbq_response()
        calculated = self.validator._calculate_total_score(response.breakdown, EssayType.DBQ)
        
        assert calculated == 6
    
    def test_calculate_total_score_saq(self):
        """Test total score calculation for SAQ."""
        response = self.create_valid_saq_response()
        calculated = self.validator._calculate_total_score(response.breakdown, EssayType.SAQ)
        
        assert calculated == 3
    
    def test_validation_error_handling(self):
        """Test graceful error handling during validation."""
        # Create malformed response
        response = self.create_valid_dbq_response()
        response.breakdown = None  # This should cause an error
        
        result = self.validator.validate_response(response, EssayType.DBQ)
        
        # Should still return a result with error information
        assert isinstance(result, ValidationResult)
        assert len(result.issues) > 0
        assert any("Validation error" in issue for issue in result.issues)