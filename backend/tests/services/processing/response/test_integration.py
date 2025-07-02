"""Integration tests for response processing workflow."""

import pytest

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse, GradeBreakdown, RubricItem
from app.models.processing.response import ProcessedGradingResult, InsightType
from app.services.processing.response.processor import ResponseProcessor
from app.services.dependencies.service_locator import ServiceLocator


class TestResponseProcessingIntegration:
    """Integration tests for end-to-end response processing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service_locator = ServiceLocator()
        self._configure_test_services()
        self.processor = ResponseProcessor()
    
    def _configure_test_services(self):
        """Configure services for testing."""
        from app.services.processing.response import (
            ResponseValidator, InsightsGenerator, ResponseFormatter, ErrorPresentation
        )
        
        # Register test services
        self.service_locator.register_singleton(
            self.processor.__class__, 
            ResponseValidator()
        )
    
    def create_complete_dbq_response(self) -> GradeResponse:
        """Create a complete DBQ response for integration testing."""
        breakdown = GradeBreakdown(
            thesis=RubricItem(score=1, max_score=1, feedback="Clear and defensible thesis"),
            contextualization=RubricItem(score=1, max_score=1, feedback="Effective historical context"),
            evidence=RubricItem(score=2, max_score=2, feedback="Uses multiple documents effectively"),
            analysis=RubricItem(score=1, max_score=2, feedback="Some analysis, needs complexity")
        )
        
        return GradeResponse(
            score=5,
            max_score=6,
            breakdown=breakdown,
            overall_feedback="Strong essay demonstrating good understanding of the historical period. The thesis is clear and the use of documents is effective. However, the analysis could be more sophisticated to earn full points.",
            suggestions=[
                "Develop more complex analytical arguments",
                "Connect document evidence more explicitly to the thesis",
                "Consider multiple perspectives on the historical issue"
            ],
            warnings=["Essay length is near the minimum recommendation"]
        )
    
    def create_poor_saq_response(self) -> GradeResponse:
        """Create a poor SAQ response for integration testing."""
        breakdown = GradeBreakdown(
            thesis=RubricItem(score=0, max_score=1, feedback="Part A incomplete or unclear"),
            contextualization=RubricItem(score=1, max_score=1, feedback="Part B provides some relevant information"),
            evidence=RubricItem(score=0, max_score=1, feedback="Part C lacks specific examples"),
            analysis=RubricItem(score=0, max_score=0, feedback="Not applicable for SAQ")
        )
        
        return GradeResponse(
            score=1,
            max_score=3,
            breakdown=breakdown,
            overall_feedback="This response shows some understanding but needs significant improvement in directly answering the questions and providing specific historical evidence.",
            suggestions=[
                "Address each part of the question directly",
                "Include specific historical examples",
                "Ensure responses are complete and developed"
            ]
        )
    
    def test_complete_dbq_processing_workflow(self):
        """Test complete processing workflow for a DBQ response."""
        response = self.create_complete_dbq_response()
        
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Verify result structure
        assert isinstance(result, ProcessedGradingResult)
        assert result.original_response == response
        
        # Verify validation completed
        assert isinstance(result.validation_issues, list)
        # Should have no validation issues for this valid response
        assert len(result.validation_issues) == 0
        
        # Verify insights generated
        assert len(result.insights) > 0
        
        # Should have performance insight
        performance_insights = [i for i in result.insights if i.type == InsightType.PERFORMANCE]
        assert len(performance_insights) == 1
        assert "proficient" in performance_insights[0].message.lower()
        
        # Should have strength insights (high scoring areas)
        strength_insights = [i for i in result.insights if i.type == InsightType.STRENGTH]
        assert len(strength_insights) == 1
        assert "thesis development" in strength_insights[0].message
        
        # Should have improvement insights (low scoring areas)
        improvement_insights = [i for i in result.insights if i.type == InsightType.IMPROVEMENT]
        assert len(improvement_insights) == 1
        assert "analytical complexity" in improvement_insights[0].message
        
        # Verify formatted text
        assert isinstance(result.formatted_text, str)
        assert "📊 **Grade: 5/6**" in result.formatted_text
        assert "📋 **Detailed Breakdown:**" in result.formatted_text
        assert "✅ **Thesis: 1/1**" in result.formatted_text
        assert "🔶 **Analysis & Reasoning: 1/2**" in result.formatted_text
        
        # Verify display data
        assert result.display_data.score_text == "5/6"
        assert result.display_data.percentage_text == "83%"
        assert result.display_data.letter_grade == "B"
        assert len(result.display_data.breakdown_items) == 4
        assert result.display_data.insights == result.insights
    
    def test_complete_saq_processing_workflow(self):
        """Test complete processing workflow for a SAQ response."""
        response = self.create_poor_saq_response()
        
        result = self.processor.process_grading_response(response, EssayType.SAQ)
        
        # Verify result structure
        assert isinstance(result, ProcessedGradingResult)
        assert result.original_response == response
        
        # Verify validation completed
        assert isinstance(result.validation_issues, list)
        # Should have no validation issues for this valid response
        assert len(result.validation_issues) == 0
        
        # Verify insights generated
        assert len(result.insights) > 0
        
        # Should have performance insight with poor performance
        performance_insights = [i for i in result.insights if i.type == InsightType.PERFORMANCE]
        assert len(performance_insights) == 1
        assert "beginning" in performance_insights[0].message.lower()
        
        # Should have SAQ-specific strategy tip
        tip_insights = [i for i in result.insights if i.type == InsightType.TIP]
        assert len(tip_insights) > 0
        saq_tips = [i for i in tip_insights if "SAQ Strategy" in i.title]
        assert len(saq_tips) == 1
        
        # Verify formatted text for SAQ structure
        assert "❌ **Part A: 0/1**" in result.formatted_text
        assert "✅ **Part B: 1/1**" in result.formatted_text
        assert "❌ **Part C: 0/1**" in result.formatted_text
        
        # Verify display data
        assert result.display_data.score_text == "1/3"
        assert result.display_data.percentage_text == "33%"
    
    def test_response_with_validation_issues(self):
        """Test processing response with validation issues."""
        response = self.create_complete_dbq_response()
        # Introduce validation issue
        response.score = 4  # Should be 5 based on breakdown
        
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Should have validation issues
        assert len(result.validation_issues) > 0
        assert any("Score mismatch" in issue for issue in result.validation_issues)
        
        # Should still have formatted text with validation issues
        assert "⚠️ **Validation Issues:**" in result.formatted_text
        assert "Score mismatch" in result.formatted_text
    
    def test_response_with_warnings(self):
        """Test processing response with warnings."""
        response = self.create_complete_dbq_response()
        # Add more warnings
        response.warnings.append("Additional warning")
        
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Should include warnings in formatted text
        assert "⚠️ **Notes:**" in result.formatted_text
        assert "Essay length is near the minimum" in result.formatted_text
        assert "Additional warning" in result.formatted_text
    
    def test_insights_integration_with_formatter(self):
        """Test that insights are properly integrated with formatter."""
        response = self.create_complete_dbq_response()
        
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Insights should be included in display data
        assert len(result.display_data.insights) == len(result.insights)
        assert result.display_data.insights == result.insights
        
        # All insights should have proper structure
        for insight in result.insights:
            assert hasattr(insight, 'type')
            assert hasattr(insight, 'title')
            assert hasattr(insight, 'message')
            assert hasattr(insight, 'severity')
    
    def test_error_handling_during_processing(self):
        """Test error handling during processing workflow."""
        response = self.create_complete_dbq_response()
        # Create a malformed response that might cause errors
        response.breakdown = None
        
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Should still return a result
        assert isinstance(result, ProcessedGradingResult)
        
        # Should have error information
        assert len(result.validation_issues) > 0
        assert any("Processing error" in issue for issue in result.validation_issues)
        
        # Should have error insight
        error_insights = [i for i in result.insights if "Processing Error" in i.title]
        assert len(error_insights) > 0
    
    def test_performance_color_integration(self):
        """Test performance color integration across workflow."""
        # Test excellent performance
        response = self.create_complete_dbq_response()
        response.score = 6  # Perfect score
        
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Performance color should reflect excellent performance
        assert result.display_data.performance_color.name == "green"
        
        # Test poor performance
        response.score = 1
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Performance color should reflect poor performance
        assert result.display_data.performance_color.name == "red"
    
    def test_essay_type_specific_processing(self):
        """Test that processing correctly handles different essay types."""
        # Test DBQ processing
        dbq_response = self.create_complete_dbq_response()
        dbq_result = self.processor.process_grading_response(dbq_response, EssayType.DBQ)
        
        # Should format as DBQ structure
        assert "**Thesis:" in dbq_result.formatted_text
        assert "**Evidence:" in dbq_result.formatted_text
        assert "**Analysis & Reasoning:" in dbq_result.formatted_text
        
        # Test SAQ processing
        saq_response = self.create_poor_saq_response()
        saq_result = self.processor.process_grading_response(saq_response, EssayType.SAQ)
        
        # Should format as SAQ structure
        assert "**Part A:" in saq_result.formatted_text
        assert "**Part B:" in saq_result.formatted_text
        assert "**Part C:" in saq_result.formatted_text
    
    def test_end_to_end_data_consistency(self):
        """Test data consistency across the entire processing pipeline."""
        response = self.create_complete_dbq_response()
        
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Original response should be preserved
        assert result.original_response == response
        
        # Score information should be consistent
        assert result.original_response.score == 5
        assert "5/6" in result.formatted_text
        assert result.display_data.score_text == "5/6"
        
        # Breakdown information should be consistent
        assert len(result.display_data.breakdown_items) == 4
        thesis_item = next(item for item in result.display_data.breakdown_items if item.name == "Thesis")
        assert thesis_item.score == response.breakdown.thesis.score
        assert thesis_item.max_score == response.breakdown.thesis.max_score
        
    def test_logging_during_processing(self):
        """Test that appropriate logging occurs during processing."""
        response = self.create_complete_dbq_response()
        
        # This test verifies the processing completes without logging errors
        # In a real implementation, you might capture log messages
        result = self.processor.process_grading_response(response, EssayType.DBQ)
        
        # Processing should complete successfully
        assert isinstance(result, ProcessedGradingResult)
        assert len(result.validation_issues) == 0  # No processing errors