"""Response formatting service for platform-agnostic display."""

from typing import List
from abc import ABC, abstractmethod

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse, GradeBreakdown, RubricItem
from app.models.processing.response import (
    ValidationResult, GradingInsight, GradeDisplayData, BreakdownDisplayItem
)
from app.models.processing.display import DisplayColors, DisplayConstants
from app.services.base.base_service import BaseService


class ResponseFormatterProtocol(ABC):
    """Protocol for response formatting services."""
    
    @abstractmethod
    def format_for_display(self, response: GradeResponse, validation_result: ValidationResult) -> str:
        """Format response as markdown text for display."""
        pass
    
    @abstractmethod
    def create_display_data(self, response: GradeResponse, insights: List[GradingInsight]) -> GradeDisplayData:
        """Create platform-agnostic display data structure."""
        pass


class ResponseFormatter(BaseService, ResponseFormatterProtocol):
    """Formats AI grading responses for platform-agnostic display."""
    
    def format_for_display(self, response: GradeResponse, validation_result: ValidationResult) -> str:
        """
        Format a grading response as markdown for display.
        
        Args:
            response: The AI grading response
            validation_result: Results from response validation
            
        Returns:
            Markdown-formatted string for display
        """
        try:
            formatted = ""
            
            # Header with score
            formatted += f"{DisplayConstants.SCORE_EMOJI} **Grade: {response.score}/{response.max_score}** "
            formatted += f"({int(response.percentage_score)}% - {response.letter_grade})\n\n"
            
            # Validation issues (if any)
            if validation_result.issues:
                formatted += f"{DisplayConstants.WARNING_EMOJI} **Validation Issues:**\n"
                for issue in validation_result.issues:
                    formatted += f"• {issue}\n"
                formatted += "\n"
            
            # Warnings (preprocessing + validation)
            all_warnings = (response.warnings or []) + validation_result.warnings
            if all_warnings:
                formatted += f"{DisplayConstants.WARNING_EMOJI} **Notes:**\n"
                for warning in all_warnings:
                    formatted += f"• {warning}\n"
                formatted += "\n"
            
            # Detailed breakdown
            formatted += f"{DisplayConstants.BREAKDOWN_EMOJI} **Detailed Breakdown:**\n\n"
            essay_type = self._determine_essay_type(response)
            formatted += self._format_breakdown(response.breakdown, essay_type)
            
            # Overall feedback
            formatted += f"\n{DisplayConstants.FEEDBACK_EMOJI} **Overall Feedback:**\n{response.overall_feedback}\n\n"
            
            # Suggestions
            if response.suggestions:
                formatted += f"{DisplayConstants.SUGGESTIONS_EMOJI} **Suggestions for Improvement:**\n"
                for i, suggestion in enumerate(response.suggestions, 1):
                    formatted += f"{i}. {suggestion}\n"
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"Error formatting response for display: {e}")
            return f"Error formatting response: {str(e)}"
    
    def create_display_data(self, response: GradeResponse, insights: List[GradingInsight]) -> GradeDisplayData:
        """
        Create platform-agnostic display data structure.
        
        Args:
            response: The AI grading response
            insights: Generated insights for the response
            
        Returns:
            GradeDisplayData with all display information
        """
        try:
            return GradeDisplayData(
                score_text=f"{response.score}/{response.max_score}",
                percentage_text=f"{int(response.percentage_score)}%",
                letter_grade=response.letter_grade,
                performance_color=DisplayColors.get_performance_color(response.percentage_score),
                breakdown_items=self._create_breakdown_display_items(response.breakdown),
                insights=insights
            )
        except Exception as e:
            self.logger.error(f"Error creating display data: {e}")
            # Return minimal display data on error
            return GradeDisplayData(
                score_text=f"{response.score}/{response.max_score}",
                percentage_text=f"{int(response.percentage_score)}%",
                letter_grade=response.letter_grade,
                performance_color=DisplayColors.BEGINNING,
                breakdown_items=[],
                insights=[]
            )
    
    def _format_breakdown(self, breakdown: GradeBreakdown, essay_type: EssayType) -> str:
        """Format the grade breakdown for display."""
        formatted = ""
        
        if essay_type in [EssayType.DBQ, EssayType.LEQ]:
            formatted += self._format_rubric_item("Thesis", breakdown.thesis)
            formatted += self._format_rubric_item("Contextualization", breakdown.contextualization)
            formatted += self._format_rubric_item("Evidence", breakdown.evidence)
            formatted += self._format_rubric_item("Analysis & Reasoning", breakdown.analysis)
        elif essay_type == EssayType.SAQ:
            formatted += self._format_rubric_item("Part A", breakdown.thesis)
            formatted += self._format_rubric_item("Part B", breakdown.contextualization)
            formatted += self._format_rubric_item("Part C", breakdown.evidence)
        
        return formatted
    
    def _format_rubric_item(self, name: str, item: RubricItem) -> str:
        """Format a single rubric item for display."""
        emoji = DisplayConstants.get_rubric_emoji(item.score, item.max_score)
        performance = item.performance_level
        
        return f"""{emoji} **{name}: {item.score}/{item.max_score}** ({performance})
   {item.feedback}

"""
    
    def _create_breakdown_display_items(self, breakdown: GradeBreakdown) -> List[BreakdownDisplayItem]:
        """Create display items for breakdown components."""
        return [
            BreakdownDisplayItem(
                name="Thesis",
                score=breakdown.thesis.score,
                max_score=breakdown.thesis.max_score,
                feedback=breakdown.thesis.feedback,
                performance_level=breakdown.thesis.performance_level,
                is_full_credit=breakdown.thesis.is_full_credit
            ),
            BreakdownDisplayItem(
                name="Context",
                score=breakdown.contextualization.score,
                max_score=breakdown.contextualization.max_score,
                feedback=breakdown.contextualization.feedback,
                performance_level=breakdown.contextualization.performance_level,
                is_full_credit=breakdown.contextualization.is_full_credit
            ),
            BreakdownDisplayItem(
                name="Evidence",
                score=breakdown.evidence.score,
                max_score=breakdown.evidence.max_score,
                feedback=breakdown.evidence.feedback,
                performance_level=breakdown.evidence.performance_level,
                is_full_credit=breakdown.evidence.is_full_credit
            ),
            BreakdownDisplayItem(
                name="Analysis",
                score=breakdown.analysis.score,
                max_score=breakdown.analysis.max_score,
                feedback=breakdown.analysis.feedback,
                performance_level=breakdown.analysis.performance_level,
                is_full_credit=breakdown.analysis.is_full_credit
            )
        ]
    
    def _determine_essay_type(self, response: GradeResponse) -> EssayType:
        """Determine essay type from response structure."""
        # Determine based on max score
        if response.max_score == 6:
            return EssayType.DBQ  # Could be LEQ too, but formatting is the same
        else:
            return EssayType.SAQ