"""Tests for ResponseFormatter service."""

import pytest

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse, GradeBreakdown, RubricItem
from app.models.processing.response import ValidationResult, GradingInsight, InsightType, InsightSeverity
from app.models.processing.display import DisplayColors
from app.services.processing.response.formatter import ResponseFormatter


class TestResponseFormatter:
    """Test suite for ResponseFormatter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = ResponseFormatter()
    
    def create_sample_dbq_response(self) -> GradeResponse:
        """Create a sample DBQ response for testing."""
        breakdown = GradeBreakdown(
            thesis=RubricItem(score=1, max_score=1, feedback="Strong thesis"),
            contextualization=RubricItem(score=1, max_score=1, feedback="Good context"),
            evidence=RubricItem(score=2, max_score=2, feedback="Excellent evidence"),
            analysis=RubricItem(score=1, max_score=2, feedback="Analysis needs work")
        )
        
        return GradeResponse(
            score=5,
            max_score=6,
            breakdown=breakdown,
            overall_feedback="Good essay with room for improvement in analysis.",
            suggestions=["Develop more complex arguments", "Connect evidence to thesis"],
            warnings=["Essay slightly shorter than recommended"]
        )
    
    def create_sample_saq_response(self) -> GradeResponse:
        """Create a sample SAQ response for testing."""
        breakdown = GradeBreakdown(
            thesis=RubricItem(score=1, max_score=1, feedback="Part A complete"),
            contextualization=RubricItem(score=0, max_score=1, feedback="Part B needs detail"),
            evidence=RubricItem(score=1, max_score=1, feedback="Part C good"),
            analysis=RubricItem(score=0, max_score=0, feedback="Not applicable for SAQ")
        )
        
        return GradeResponse(
            score=2,
            max_score=3,
            breakdown=breakdown,
            overall_feedback="Solid response with one incomplete part.",
            suggestions=["Add more detail to Part B"]
        )
    
    def create_sample_validation_result(self) -> ValidationResult:
        """Create a sample validation result for testing."""
        return ValidationResult(
            issues=["Score mismatch: reported 5, calculated 4"],
            warnings=["Limited suggestions provided"]
        )
    
    def create_sample_insights(self) -> list[GradingInsight]:
        """Create sample insights for testing."""
        return [
            GradingInsight(
                type=InsightType.PERFORMANCE,
                title="Overall Performance",
                message="This essay demonstrates proficient understanding.",
                severity=InsightSeverity.SUCCESS
            ),
            GradingInsight(
                type=InsightType.IMPROVEMENT,
                title="Focus Areas",
                message="Consider improving: analytical complexity",
                severity=InsightSeverity.WARNING
            )
        ]
    
    def test_format_for_display_basic(self):
        """Test basic formatting for display."""
        response = self.create_sample_dbq_response()
        validation_result = ValidationResult(issues=[], warnings=[])
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        assert isinstance(formatted, str)
        assert "📊 **Grade: 5/6**" in formatted
        assert "(83% - B)" in formatted
        assert "📋 **Detailed Breakdown:**" in formatted
        assert "💬 **Overall Feedback:**" in formatted
        assert "💡 **Suggestions for Improvement:**" in formatted
    
    def test_format_with_validation_issues(self):
        """Test formatting with validation issues."""
        response = self.create_sample_dbq_response()
        validation_result = self.create_sample_validation_result()
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        assert "⚠️ **Validation Issues:**" in formatted
        assert "Score mismatch" in formatted
    
    def test_format_with_warnings(self):
        """Test formatting with warnings."""
        response = self.create_sample_dbq_response()
        validation_result = ValidationResult(
            issues=[],
            warnings=["Validation warning"]
        )
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        assert "⚠️ **Notes:**" in formatted
        assert "Essay slightly shorter" in formatted  # From response warnings
        assert "Validation warning" in formatted  # From validation warnings
    
    def test_format_dbq_breakdown(self):
        """Test DBQ breakdown formatting."""
        response = self.create_sample_dbq_response()
        validation_result = ValidationResult(issues=[], warnings=[])
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        # Check DBQ-specific rubric items
        assert "✅ **Thesis: 1/1**" in formatted
        assert "✅ **Contextualization: 1/1**" in formatted
        assert "✅ **Evidence: 2/2**" in formatted
        assert "🔶 **Analysis & Reasoning: 1/2**" in formatted  # Partial credit
    
    def test_format_saq_breakdown(self):
        """Test SAQ breakdown formatting."""
        response = self.create_sample_saq_response()
        validation_result = ValidationResult(issues=[], warnings=[])
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        # Check SAQ-specific rubric items (Parts A, B, C)
        assert "✅ **Part A: 1/1**" in formatted
        assert "❌ **Part B: 0/1**" in formatted  # No credit
        assert "✅ **Part C: 1/1**" in formatted
    
    def test_format_suggestions(self):
        """Test suggestions formatting."""
        response = self.create_sample_dbq_response()
        validation_result = ValidationResult(issues=[], warnings=[])
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        assert "1. Develop more complex arguments" in formatted
        assert "2. Connect evidence to thesis" in formatted
    
    def test_format_without_suggestions(self):
        """Test formatting when no suggestions are provided."""
        response = self.create_sample_dbq_response()
        response.suggestions = []
        validation_result = ValidationResult(issues=[], warnings=[])
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        # Should not include suggestions section
        assert "💡 **Suggestions for Improvement:**" not in formatted
    
    def test_create_display_data(self):
        """Test creation of display data structure."""
        response = self.create_sample_dbq_response()
        insights = self.create_sample_insights()
        
        display_data = self.formatter.create_display_data(response, insights)
        
        assert display_data.score_text == "5/6"
        assert display_data.percentage_text == "83%"
        assert display_data.letter_grade == "B"
        assert display_data.performance_color == DisplayColors.PROFICIENT
        assert len(display_data.breakdown_items) == 4
        assert display_data.insights == insights
    
    def test_breakdown_display_items(self):
        """Test creation of breakdown display items."""
        response = self.create_sample_dbq_response()
        
        items = self.formatter._create_breakdown_display_items(response.breakdown)
        
        assert len(items) == 4
        
        # Check thesis item
        thesis_item = items[0]
        assert thesis_item.name == "Thesis"
        assert thesis_item.score == 1
        assert thesis_item.max_score == 1
        assert thesis_item.is_full_credit == True
        
        # Check analysis item (partial credit)
        analysis_item = items[3]
        assert analysis_item.name == "Analysis"
        assert analysis_item.score == 1
        assert analysis_item.max_score == 2
        assert analysis_item.is_full_credit == False
    
    def test_determine_essay_type(self):
        """Test essay type determination from response."""
        # DBQ/LEQ (max score 6)
        dbq_response = self.create_sample_dbq_response()
        essay_type = self.formatter._determine_essay_type(dbq_response)
        assert essay_type == EssayType.DBQ
        
        # SAQ (max score 3)
        saq_response = self.create_sample_saq_response()
        essay_type = self.formatter._determine_essay_type(saq_response)
        assert essay_type == EssayType.SAQ
    
    def test_performance_color_mapping(self):
        """Test performance color mapping."""
        # Test excellent performance (90-100%)
        response = self.create_sample_dbq_response()
        response.score = 6  # 100%
        insights = []
        
        display_data = self.formatter.create_display_data(response, insights)
        assert display_data.performance_color == DisplayColors.EXCELLENT
        
        # Test proficient performance (80-90%)
        response.score = 5  # 83.33%
        display_data = self.formatter.create_display_data(response, insights)
        assert display_data.performance_color == DisplayColors.PROFICIENT
        
        # Test developing performance (70-80%)
        response.score = 4  # 66.67% -> actually approaching
        display_data = self.formatter.create_display_data(response, insights)
        assert display_data.performance_color == DisplayColors.APPROACHING
    
    def test_format_rubric_item(self):
        """Test individual rubric item formatting."""
        item = RubricItem(
            score=2,
            max_score=2,
            feedback="Excellent work on this component"
        )
        
        formatted = self.formatter._format_rubric_item("Evidence", item)
        
        assert "✅ **Evidence: 2/2**" in formatted
        assert "(Excellent)" in formatted  # Performance level
        assert "Excellent work on this component" in formatted
    
    def test_format_error_handling(self):
        """Test error handling during formatting."""
        response = self.create_sample_dbq_response()
        response.breakdown = None  # This should cause an error
        validation_result = ValidationResult(issues=[], warnings=[])
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        # Should return error message instead of crashing
        assert isinstance(formatted, str)
        assert "Error formatting response" in formatted
    
    def test_display_data_error_handling(self):
        """Test error handling during display data creation."""
        response = self.create_sample_dbq_response()
        response.breakdown = None  # This should cause an error
        insights = self.create_sample_insights()
        
        display_data = self.formatter.create_display_data(response, insights)
        
        # Should return minimal display data instead of crashing
        assert display_data.score_text == "5/6"
        assert display_data.performance_color == DisplayColors.BEGINNING
        assert len(display_data.breakdown_items) == 0
        assert len(display_data.insights) == 0
    
    def test_format_without_warnings(self):
        """Test formatting when no warnings are present."""
        response = self.create_sample_dbq_response()
        response.warnings = None
        validation_result = ValidationResult(issues=[], warnings=[])
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        # Should not include notes section
        assert "⚠️ **Notes:**" not in formatted
    
    def test_format_empty_warnings(self):
        """Test formatting with empty warnings list."""
        response = self.create_sample_dbq_response()
        response.warnings = []
        validation_result = ValidationResult(issues=[], warnings=[])
        
        formatted = self.formatter.format_for_display(response, validation_result)
        
        # Should not include notes section
        assert "⚠️ **Notes:**" not in formatted