"""Tests for InsightsGenerator service."""

import pytest

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse, GradeBreakdown, RubricItem
from app.models.processing.response import GradingInsight, InsightType, InsightSeverity
from app.services.processing.response.insights import InsightsGenerator


class TestInsightsGenerator:
    """Test suite for InsightsGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = InsightsGenerator()
    
    def create_excellent_dbq_response(self) -> GradeResponse:
        """Create an excellent DBQ response for testing."""
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
            overall_feedback="Excellent essay demonstrating mastery.",
            suggestions=["Continue developing complex arguments"]
        )
    
    def create_poor_dbq_response(self) -> GradeResponse:
        """Create a poor DBQ response for testing."""
        breakdown = GradeBreakdown(
            thesis=RubricItem(score=0, max_score=1, feedback="Unclear thesis"),
            contextualization=RubricItem(score=0, max_score=1, feedback="No context"),
            evidence=RubricItem(score=1, max_score=2, feedback="Limited evidence"),
            analysis=RubricItem(score=0, max_score=2, feedback="No analysis")
        )
        
        return GradeResponse(
            score=1,
            max_score=6,
            breakdown=breakdown,
            overall_feedback="Needs significant improvement.",
            suggestions=["Focus on thesis development", "Add historical context"]
        )
    
    def create_partial_saq_response(self) -> GradeResponse:
        """Create a partial SAQ response for testing."""
        breakdown = GradeBreakdown(
            thesis=RubricItem(score=1, max_score=1, feedback="Part A complete"),
            contextualization=RubricItem(score=0, max_score=1, feedback="Part B incomplete"),
            evidence=RubricItem(score=1, max_score=1, feedback="Part C good"),
            analysis=RubricItem(score=0, max_score=0, feedback="Not applicable for SAQ")
        )
        
        return GradeResponse(
            score=2,
            max_score=3,
            breakdown=breakdown,
            overall_feedback="Partial SAQ response.",
            suggestions=["Complete Part B"]
        )
    
    def test_generate_insights_excellent_performance(self):
        """Test insights generation for excellent performance."""
        response = self.create_excellent_dbq_response()
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        
        assert len(insights) > 0
        
        # Should have performance insight
        performance_insights = [i for i in insights if i.type == InsightType.PERFORMANCE]
        assert len(performance_insights) == 1
        assert "excellent" in performance_insights[0].message.lower()
        assert performance_insights[0].severity == InsightSeverity.SUCCESS
        
        # Should have strength insight
        strength_insights = [i for i in insights if i.type == InsightType.STRENGTH]
        assert len(strength_insights) == 1
        assert "thesis development" in strength_insights[0].message
    
    def test_generate_insights_poor_performance(self):
        """Test insights generation for poor performance."""
        response = self.create_poor_dbq_response()
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        
        assert len(insights) > 0
        
        # Should have performance insight with error severity
        performance_insights = [i for i in insights if i.type == InsightType.PERFORMANCE]
        assert len(performance_insights) == 1
        assert "beginning" in performance_insights[0].message.lower()
        assert performance_insights[0].severity == InsightSeverity.ERROR
        
        # Should have improvement insight
        improvement_insights = [i for i in insights if i.type == InsightType.IMPROVEMENT]
        assert len(improvement_insights) == 1
        assert "thesis clarity" in improvement_insights[0].message
    
    def test_identify_strengths_dbq(self):
        """Test strength identification for DBQ essays."""
        response = self.create_excellent_dbq_response()
        strengths = self.generator._identify_strengths(response.breakdown, EssayType.DBQ)
        
        expected_strengths = [
            "thesis development",
            "historical contextualization", 
            "use of evidence",
            "historical analysis"
        ]
        
        for strength in expected_strengths:
            assert strength in strengths
    
    def test_identify_improvements_dbq(self):
        """Test improvement identification for DBQ essays."""
        response = self.create_poor_dbq_response()
        improvements = self.generator._identify_improvements(response.breakdown, EssayType.DBQ)
        
        expected_improvements = [
            "thesis clarity",
            "historical context",
            "evidence usage",
            "analytical complexity"
        ]
        
        for improvement in expected_improvements:
            assert improvement in improvements
    
    def test_identify_strengths_saq(self):
        """Test strength identification for SAQ essays."""
        response = self.create_partial_saq_response()
        strengths = self.generator._identify_strengths(response.breakdown, EssayType.SAQ)
        
        # Should identify Parts A and C as strengths
        assert "Part A response" in strengths
        assert "Part C response" in strengths
        assert "Part B response" not in strengths  # This one scored 0
    
    def test_identify_improvements_saq(self):
        """Test improvement identification for SAQ essays."""
        response = self.create_partial_saq_response()
        improvements = self.generator._identify_improvements(response.breakdown, EssayType.SAQ)
        
        # Should identify Part B as needing improvement
        assert "Part B accuracy" in improvements
        assert "Part A completeness" not in improvements  # This one got full credit
    
    def test_dbq_specific_insights(self):
        """Test DBQ-specific strategic insights."""
        response = self.create_poor_dbq_response()
        # Make evidence score low to trigger DBQ tip
        response.breakdown.evidence.score = 1
        
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        
        # Should have DBQ strategy tip
        tip_insights = [i for i in insights if i.type == InsightType.TIP]
        assert len(tip_insights) > 0
        dbq_tips = [i for i in tip_insights if "DBQ Strategy" in i.title]
        assert len(dbq_tips) == 1
        assert "at least 3 documents" in dbq_tips[0].message
    
    def test_leq_specific_insights(self):
        """Test LEQ-specific strategic insights."""
        response = self.create_poor_dbq_response()
        # Make analysis score low to trigger LEQ tip
        response.breakdown.analysis.score = 1
        
        insights = self.generator.generate_insights(response, EssayType.LEQ)
        
        # Should have LEQ strategy tip
        tip_insights = [i for i in insights if i.type == InsightType.TIP]
        assert len(tip_insights) > 0
        leq_tips = [i for i in tip_insights if "LEQ Strategy" in i.title]
        assert len(leq_tips) == 1
        assert "sophisticated analysis" in leq_tips[0].message
    
    def test_saq_specific_insights(self):
        """Test SAQ-specific strategic insights."""
        response = self.create_partial_saq_response()
        
        insights = self.generator.generate_insights(response, EssayType.SAQ)
        
        # Should have SAQ strategy tip for score < 3
        tip_insights = [i for i in insights if i.type == InsightType.TIP]
        assert len(tip_insights) > 0
        saq_tips = [i for i in tip_insights if "SAQ Strategy" in i.title]
        assert len(saq_tips) == 1
        assert "directly answers the question" in saq_tips[0].message
    
    def test_performance_level_classification(self):
        """Test performance level classification."""
        # Test excellent (90-100%)
        response = self.create_excellent_dbq_response()  # 100%
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        performance_insight = next(i for i in insights if i.type == InsightType.PERFORMANCE)
        assert "excellent" in performance_insight.message.lower()
        assert performance_insight.severity == InsightSeverity.SUCCESS
        
        # Test proficient (80-90%)
        response.score = 5  # 83.33%
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        performance_insight = next(i for i in insights if i.type == InsightType.PERFORMANCE)
        assert "proficient" in performance_insight.message.lower()
        assert performance_insight.severity == InsightSeverity.SUCCESS
        
        # Test developing (70-80%)
        response.score = 4  # 66.67% -> actually approaching
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        performance_insight = next(i for i in insights if i.type == InsightType.PERFORMANCE)
        assert "approaching" in performance_insight.message.lower()
        assert performance_insight.severity == InsightSeverity.WARNING
    
    def test_severity_mapping(self):
        """Test severity mapping for different performance levels."""
        # Test success severity (80-100%)
        assert self.generator._get_severity_for_performance(90.0) == InsightSeverity.SUCCESS
        assert self.generator._get_severity_for_performance(80.0) == InsightSeverity.SUCCESS
        
        # Test warning severity (60-80%)
        assert self.generator._get_severity_for_performance(70.0) == InsightSeverity.WARNING
        assert self.generator._get_severity_for_performance(60.0) == InsightSeverity.WARNING
        
        # Test error severity (<60%)
        assert self.generator._get_severity_for_performance(50.0) == InsightSeverity.ERROR
        assert self.generator._get_severity_for_performance(0.0) == InsightSeverity.ERROR
    
    def test_error_handling(self):
        """Test graceful error handling during insights generation."""
        # Create malformed response
        response = self.create_excellent_dbq_response()
        response.breakdown = None  # This should cause an error
        
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        
        # Should still return insights with error information
        assert len(insights) > 0
        warning_insights = [i for i in insights if i.type == InsightType.WARNING]
        assert len(warning_insights) > 0
        assert any("Analysis Incomplete" in i.title for i in warning_insights)
    
    def test_no_strengths_no_insight(self):
        """Test that no strength insight is generated when there are no strengths."""
        response = self.create_poor_dbq_response()
        # Make sure all scores are 0 or very low
        response.breakdown.thesis.score = 0
        response.breakdown.contextualization.score = 0
        response.breakdown.evidence.score = 0  # Below threshold for strength
        response.breakdown.analysis.score = 0
        
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        
        # Should not have strength insight
        strength_insights = [i for i in insights if i.type == InsightType.STRENGTH]
        assert len(strength_insights) == 0
    
    def test_no_improvements_no_insight(self):
        """Test that no improvement insight is generated when there are no improvements."""
        response = self.create_excellent_dbq_response()
        # All scores are already at max
        
        insights = self.generator.generate_insights(response, EssayType.DBQ)
        
        # Should not have improvement insight
        improvement_insights = [i for i in insights if i.type == InsightType.IMPROVEMENT]
        assert len(improvement_insights) == 0