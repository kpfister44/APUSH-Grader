"""Tests for grade models - ported from Swift GradeModelsTests"""

import pytest
from app.models.core.grade_models import (
    RubricItem, GradeBreakdown, GradeResponse, 
    GradingError, GradingErrorType
)


class TestRubricItem:
    """Test suite for RubricItem model"""
    
    def test_rubric_item_creation(self):
        """Test creating a rubric item"""
        item = RubricItem(score=4, max_score=6, feedback="Good analysis")
        assert item.score == 4
        assert item.max_score == 6
        assert item.feedback == "Good analysis"
    
    def test_is_full_credit_true(self):
        """Test full credit detection when score equals max"""
        item = RubricItem(score=6, max_score=6, feedback="Perfect")
        assert item.is_full_credit is True
    
    def test_is_full_credit_false(self):
        """Test full credit detection when score less than max"""
        item = RubricItem(score=4, max_score=6, feedback="Good")
        assert item.is_full_credit is False
    
    def test_percentage_calculation(self):
        """Test percentage calculation"""
        item = RubricItem(score=4, max_score=6, feedback="Good")
        assert item.percentage == 66.66666666666666
    
    def test_percentage_zero_max_score(self):
        """Test percentage with zero max score"""
        item = RubricItem(score=0, max_score=0, feedback="N/A")
        assert item.percentage == 0.0
    
    def test_percentage_full_credit(self):
        """Test percentage with full credit"""
        item = RubricItem(score=6, max_score=6, feedback="Perfect")
        assert item.percentage == 100.0
    
    def test_performance_level_excellent(self):
        """Test performance level for perfect score"""
        item = RubricItem(score=6, max_score=6, feedback="Perfect")
        assert item.performance_level == "Excellent"
    
    def test_performance_level_proficient(self):
        """Test performance level for 80-99%"""
        item = RubricItem(score=5, max_score=6, feedback="Very good")
        assert item.performance_level == "Proficient"
    
    def test_performance_level_developing(self):
        """Test performance level for 50-79%"""
        item = RubricItem(score=3, max_score=6, feedback="Developing")
        assert item.performance_level == "Developing"
    
    def test_performance_level_needs_improvement(self):
        """Test performance level for below 50%"""
        item = RubricItem(score=2, max_score=6, feedback="Needs work")
        assert item.performance_level == "Needs Improvement"
    
    def test_performance_level_zero_score(self):
        """Test performance level for zero score"""
        item = RubricItem(score=0, max_score=6, feedback="No evidence")
        assert item.performance_level == "Needs Improvement"


class TestGradeBreakdown:
    """Test suite for GradeBreakdown model"""
    
    def test_grade_breakdown_creation_with_complexity(self):
        """Test creating grade breakdown with complexity (DBQ/LEQ)"""
        thesis = RubricItem(score=1, max_score=1, feedback="Clear thesis")
        contextualization = RubricItem(score=1, max_score=1, feedback="Good context")
        evidence = RubricItem(score=2, max_score=2, feedback="Strong evidence")
        analysis = RubricItem(score=1, max_score=2, feedback="Some analysis")
        complexity = RubricItem(score=0, max_score=1, feedback="No complexity")
        
        breakdown = GradeBreakdown(
            thesis=thesis,
            contextualization=contextualization,
            evidence=evidence,
            analysis=analysis,
            complexity=complexity
        )
        
        assert breakdown.thesis == thesis
        assert breakdown.contextualization == contextualization
        assert breakdown.evidence == evidence
        assert breakdown.analysis == analysis
        assert breakdown.complexity == complexity
    
    def test_grade_breakdown_creation_without_complexity(self):
        """Test creating grade breakdown without complexity (SAQ)"""
        thesis = RubricItem(score=1, max_score=1, feedback="Clear thesis")
        contextualization = RubricItem(score=1, max_score=1, feedback="Good context")
        evidence = RubricItem(score=1, max_score=1, feedback="Evidence present")
        analysis = RubricItem(score=0, max_score=1, feedback="No analysis")
        
        breakdown = GradeBreakdown(
            thesis=thesis,
            contextualization=contextualization,
            evidence=evidence,
            analysis=analysis
        )
        
        assert breakdown.complexity is None


class TestGradeResponse:
    """Test suite for GradeResponse model"""
    
    def create_sample_breakdown(self) -> GradeBreakdown:
        """Helper to create sample grade breakdown"""
        return GradeBreakdown(
            thesis=RubricItem(score=1, max_score=1, feedback="Clear thesis"),
            contextualization=RubricItem(score=1, max_score=1, feedback="Good context"),
            evidence=RubricItem(score=2, max_score=2, feedback="Strong evidence"),
            analysis=RubricItem(score=1, max_score=2, feedback="Some analysis")
        )
    
    def test_grade_response_creation(self):
        """Test creating a grade response"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=5,
            max_score=6,
            breakdown=breakdown,
            overall_feedback="Good essay overall",
            suggestions=["Improve analysis", "Add more evidence"]
        )
        
        assert response.score == 5
        assert response.max_score == 6
        assert response.breakdown == breakdown
        assert response.overall_feedback == "Good essay overall"
        assert response.suggestions == ["Improve analysis", "Add more evidence"]
        assert response.warnings is None
    
    def test_grade_response_with_warnings(self):
        """Test creating grade response with warnings"""
        breakdown = self.create_sample_breakdown()
        warnings = ["Essay is quite short", "Check spelling"]
        
        response = GradeResponse(
            score=4,
            max_score=6,
            breakdown=breakdown,
            overall_feedback="Needs improvement",
            suggestions=["Expand analysis"],
            warnings=warnings
        )
        
        assert response.warnings == warnings
    
    def test_percentage_score_calculation(self):
        """Test percentage score calculation"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=5,
            max_score=6,
            breakdown=breakdown,
            overall_feedback="Good work",
            suggestions=[]
        )
        
        assert response.percentage_score == 83.33333333333334
    
    def test_percentage_score_zero_max(self):
        """Test percentage score with zero max score"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=0,
            max_score=0,
            breakdown=breakdown,
            overall_feedback="No scoring",
            suggestions=[]
        )
        
        assert response.percentage_score == 0.0
    
    def test_letter_grade_a(self):
        """Test letter grade A (90-100%)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=6, max_score=6, breakdown=breakdown,
            overall_feedback="Excellent", suggestions=[]
        )
        assert response.letter_grade == "A"
    
    def test_letter_grade_b(self):
        """Test letter grade B (80-89%)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=5, max_score=6, breakdown=breakdown,
            overall_feedback="Good", suggestions=[]
        )
        assert response.letter_grade == "B"
    
    def test_letter_grade_c(self):
        """Test letter grade C (70-79%)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=4, max_score=6, breakdown=breakdown,
            overall_feedback="Satisfactory", suggestions=[]
        )
        # 4/6 = 66.67%, should be D not C
        assert response.letter_grade == "D"
    
    def test_letter_grade_d(self):
        """Test letter grade D (60-69%)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=4, max_score=6, breakdown=breakdown,
            overall_feedback="Below average", suggestions=[]
        )
        assert response.letter_grade == "D"
    
    def test_letter_grade_f(self):
        """Test letter grade F (below 60%)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=2, max_score=6, breakdown=breakdown,
            overall_feedback="Failing", suggestions=[]
        )
        assert response.letter_grade == "F"
    
    def test_performance_level_excellent(self):
        """Test performance level excellent (90%+)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=6, max_score=6, breakdown=breakdown,
            overall_feedback="Excellent", suggestions=[]
        )
        assert response.performance_level == "Excellent"
    
    def test_performance_level_proficient(self):
        """Test performance level proficient (80-89%)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=5, max_score=6, breakdown=breakdown,
            overall_feedback="Proficient", suggestions=[]
        )
        assert response.performance_level == "Proficient"
    
    def test_performance_level_developing(self):
        """Test performance level developing (70-79%)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=4, max_score=6, breakdown=breakdown,
            overall_feedback="Developing", suggestions=[]
        )
        # 4/6 = 66.67%, should be Needs Improvement
        assert response.performance_level == "Needs Improvement"
    
    def test_performance_level_needs_improvement(self):
        """Test performance level needs improvement (below 70%)"""
        breakdown = self.create_sample_breakdown()
        response = GradeResponse(
            score=3, max_score=6, breakdown=breakdown,
            overall_feedback="Needs work", suggestions=[]
        )
        assert response.performance_level == "Needs Improvement"


class TestGradingErrorType:
    """Test suite for GradingErrorType enum"""
    
    def test_error_type_values(self):
        """Test all error type values"""
        assert GradingErrorType.INVALID_RESPONSE == "invalid_response"
        assert GradingErrorType.INVALID_SCORE == "invalid_score"
        assert GradingErrorType.NETWORK_ERROR == "network_error"
        assert GradingErrorType.API_KEY_MISSING == "api_key_missing"
        assert GradingErrorType.RATE_LIMIT_EXCEEDED == "rate_limit_exceeded"
        assert GradingErrorType.ESSAY_TOO_SHORT == "essay_too_short"
        assert GradingErrorType.ESSAY_TOO_LONG == "essay_too_long"
        assert GradingErrorType.PARSE_ERROR == "parse_error"
    
    def test_error_descriptions(self):
        """Test error descriptions"""
        assert GradingErrorType.INVALID_RESPONSE.description == "Received invalid response from grading service"
        assert GradingErrorType.INVALID_SCORE.description == "Received invalid score from grading service"
        assert GradingErrorType.NETWORK_ERROR.description == "Network error occurred"
        assert GradingErrorType.API_KEY_MISSING.description == "API key is missing. Please check your configuration"
        assert GradingErrorType.RATE_LIMIT_EXCEEDED.description == "Rate limit exceeded. Please try again later"
        assert GradingErrorType.ESSAY_TOO_SHORT.description == "Essay is too short for accurate grading"
        assert GradingErrorType.ESSAY_TOO_LONG.description == "Essay exceeds maximum length"
        assert GradingErrorType.PARSE_ERROR.description == "Failed to parse response"


class TestGradingError:
    """Test suite for GradingError exception"""
    
    def test_grading_error_creation(self):
        """Test creating a grading error"""
        error = GradingError("Test error message")
        assert str(error) == "Test error message"
    
    def test_grading_error_inheritance(self):
        """Test that GradingError inherits from Exception"""
        error = GradingError("Test error")
        assert isinstance(error, Exception)