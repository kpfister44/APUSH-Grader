"""Insights generation service for AI grading responses."""

from typing import List
from abc import ABC, abstractmethod

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse, GradeBreakdown
from app.models.processing.response import GradingInsight, InsightType, InsightSeverity
from app.models.processing.display import DisplayConstants
from app.services.base.base_service import BaseService


class InsightsGeneratorProtocol(ABC):
    """Protocol for insights generation services."""
    
    @abstractmethod
    def generate_insights(self, response: GradeResponse, essay_type: EssayType) -> List[GradingInsight]:
        """Generate insights and recommendations from grading response."""
        pass


class InsightsGenerator(BaseService, InsightsGeneratorProtocol):
    """Generates performance insights and recommendations from grading responses."""
    
    def generate_insights(self, response: GradeResponse, essay_type: EssayType) -> List[GradingInsight]:
        """
        Generate insights from a grading response.
        
        Args:
            response: The AI grading response
            essay_type: The type of essay that was graded
            
        Returns:
            List of generated insights
        """
        insights: List[GradingInsight] = []
        
        try:
            # Performance level insight
            performance_insight = self._generate_performance_insight(response.percentage_score)
            insights.append(performance_insight)
            
            # Strength analysis
            strengths = self._identify_strengths(response.breakdown, essay_type)
            if strengths:
                strength_insight = GradingInsight(
                    type=InsightType.STRENGTH,
                    title="Key Strengths",
                    message=f"Strong performance in: {', '.join(strengths)}",
                    severity=InsightSeverity.INFO
                )
                insights.append(strength_insight)
            
            # Areas for improvement
            improvements = self._identify_improvements(response.breakdown, essay_type)
            if improvements:
                improvement_insight = GradingInsight(
                    type=InsightType.IMPROVEMENT,
                    title="Focus Areas",
                    message=f"Consider improving: {', '.join(improvements)}",
                    severity=InsightSeverity.WARNING
                )
                insights.append(improvement_insight)
            
            # Essay type specific insights
            essay_specific_insights = self._generate_essay_type_insights(response, essay_type)
            insights.extend(essay_specific_insights)
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            # Add a generic insight if generation fails
            insights.append(GradingInsight(
                type=InsightType.WARNING,
                title="Analysis Incomplete",
                message="Unable to generate detailed insights. Please review your essay manually.",
                severity=InsightSeverity.WARNING
            ))
        
        return insights
    
    def _generate_performance_insight(self, percentage: float) -> GradingInsight:
        """Generate overall performance level insight."""
        performance_level = DisplayConstants.get_performance_level(percentage)
        severity = self._get_severity_for_performance(percentage)
        
        return GradingInsight(
            type=InsightType.PERFORMANCE,
            title="Overall Performance",
            message=f"This essay demonstrates {performance_level.lower()} understanding of APUSH concepts.",
            severity=severity
        )
    
    def _identify_strengths(self, breakdown: GradeBreakdown, essay_type: EssayType) -> List[str]:
        """Identify areas of strong performance."""
        strengths: List[str] = []
        
        if essay_type in [EssayType.DBQ, EssayType.LEQ]:
            if breakdown.thesis.is_full_credit:
                strengths.append("thesis development")
            if breakdown.contextualization.is_full_credit:
                strengths.append("historical contextualization")
            if breakdown.evidence.score >= breakdown.evidence.max_score - 1:
                strengths.append("use of evidence")
            if breakdown.analysis.score >= breakdown.analysis.max_score - 1:
                strengths.append("historical analysis")
        elif essay_type == EssayType.SAQ:
            if breakdown.thesis.is_full_credit:
                strengths.append("Part A response")
            if breakdown.contextualization.is_full_credit:
                strengths.append("Part B response")
            if breakdown.evidence.is_full_credit:
                strengths.append("Part C response")
        
        return strengths
    
    def _identify_improvements(self, breakdown: GradeBreakdown, essay_type: EssayType) -> List[str]:
        """Identify areas needing improvement."""
        improvements: List[str] = []
        
        if essay_type in [EssayType.DBQ, EssayType.LEQ]:
            if breakdown.thesis.score < breakdown.thesis.max_score:
                improvements.append("thesis clarity")
            if breakdown.contextualization.score < breakdown.contextualization.max_score:
                improvements.append("historical context")
            if breakdown.evidence.score < breakdown.evidence.max_score:
                improvements.append("evidence usage")
            if breakdown.analysis.score < breakdown.analysis.max_score:
                improvements.append("analytical complexity")
        elif essay_type == EssayType.SAQ:
            if breakdown.thesis.score < breakdown.thesis.max_score:
                improvements.append("Part A completeness")
            if breakdown.contextualization.score < breakdown.contextualization.max_score:
                improvements.append("Part B accuracy")
            if breakdown.evidence.score < breakdown.evidence.max_score:
                improvements.append("Part C development")
        
        return improvements
    
    def _generate_essay_type_insights(self, response: GradeResponse, essay_type: EssayType) -> List[GradingInsight]:
        """Generate essay-type specific strategic insights."""
        insights: List[GradingInsight] = []
        
        if essay_type == EssayType.DBQ:
            if response.breakdown.evidence.score < 2:
                insights.append(GradingInsight(
                    type=InsightType.TIP,
                    title="DBQ Strategy",
                    message="Remember to use at least 3 documents AND include outside historical evidence.",
                    severity=InsightSeverity.INFO
                ))
        elif essay_type == EssayType.LEQ:
            if response.breakdown.analysis.score < 2:
                insights.append(GradingInsight(
                    type=InsightType.TIP,
                    title="LEQ Strategy",
                    message="Focus on sophisticated analysis - compare multiple perspectives or explain change over time.",
                    severity=InsightSeverity.INFO
                ))
        elif essay_type == EssayType.SAQ:
            if response.score < 3:
                insights.append(GradingInsight(
                    type=InsightType.TIP,
                    title="SAQ Strategy",
                    message="Ensure each part directly answers the question with specific historical evidence.",
                    severity=InsightSeverity.INFO
                ))
        
        return insights
    
    def _get_severity_for_performance(self, percentage: float) -> InsightSeverity:
        """Get appropriate severity level for performance percentage."""
        if percentage >= 80:
            return InsightSeverity.SUCCESS
        elif percentage >= 60:
            return InsightSeverity.WARNING
        else:
            return InsightSeverity.ERROR