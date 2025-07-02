"""Response validation service for AI grading responses."""

from typing import List
from abc import ABC, abstractmethod

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse, GradeBreakdown, RubricItem
from app.models.processing.response import ValidationResult
from app.services.base.base_service import BaseService


class ResponseValidatorProtocol(ABC):
    """Protocol for response validation services."""
    
    @abstractmethod
    def validate_response(self, response: GradeResponse, essay_type: EssayType) -> ValidationResult:
        """Validate a grading response for correctness and consistency."""
        pass


class ResponseValidator(BaseService, ResponseValidatorProtocol):
    """Validates AI grading responses for correctness and consistency."""
    
    def validate_response(self, response: GradeResponse, essay_type: EssayType) -> ValidationResult:
        """
        Validate a grading response against essay type requirements.
        
        Args:
            response: The AI grading response to validate
            essay_type: The type of essay being graded
            
        Returns:
            ValidationResult with any issues and warnings found
        """
        issues: List[str] = []
        warnings: List[str] = []
        
        try:
            # Validate score ranges
            self._validate_score_ranges(response, essay_type, issues)
            
            # Validate breakdown scores
            self._validate_breakdown_scores(response, essay_type, issues)
            
            # Validate feedback quality
            self._validate_feedback_quality(response, warnings)
            
            # Check for consistency
            self._validate_score_consistency(response, essay_type, issues)
            
        except Exception as e:
            self.logger.error(f"Error during response validation: {e}")
            issues.append(f"Validation error: {str(e)}")
        
        return ValidationResult(issues=issues, warnings=warnings)
    
    def _validate_score_ranges(self, response: GradeResponse, essay_type: EssayType, issues: List[str]) -> None:
        """Validate that scores are within acceptable ranges."""
        # Check total score range
        if response.score < 0 or response.score > response.max_score:
            issues.append(f"Invalid total score: {response.score}/{response.max_score}")
        
        # Check max score matches essay type
        if response.max_score != essay_type.max_score:
            issues.append(f"Incorrect maximum score for {essay_type.value}")
    
    def _validate_breakdown_scores(self, response: GradeResponse, essay_type: EssayType, issues: List[str]) -> None:
        """Validate individual rubric item scores."""
        breakdown = response.breakdown
        
        if essay_type in [EssayType.DBQ, EssayType.LEQ]:
            self._validate_rubric_item(breakdown.thesis, 1, "thesis", issues)
            self._validate_rubric_item(breakdown.contextualization, 1, "contextualization", issues)
            self._validate_rubric_item(breakdown.evidence, 2, "evidence", issues)
            self._validate_rubric_item(breakdown.analysis, 2, "analysis", issues)
        elif essay_type == EssayType.SAQ:
            # For SAQ, structure is different but mapped to same fields
            self._validate_rubric_item(breakdown.thesis, 1, "partA", issues)
            self._validate_rubric_item(breakdown.contextualization, 1, "partB", issues)
            self._validate_rubric_item(breakdown.evidence, 1, "partC", issues)
    
    def _validate_rubric_item(self, item: RubricItem, expected_max: int, name: str, issues: List[str]) -> None:
        """Validate a single rubric item."""
        if item.max_score != expected_max:
            issues.append(f"{name}: incorrect max score ({item.max_score}, expected {expected_max})")
        
        if item.score < 0 or item.score > item.max_score:
            issues.append(f"{name}: invalid score ({item.score}/{item.max_score})")
        
        if not item.feedback.strip():
            issues.append(f"{name}: missing feedback")
    
    def _validate_feedback_quality(self, response: GradeResponse, warnings: List[str]) -> None:
        """Validate the quality of feedback provided."""
        if len(response.overall_feedback) < 50:
            warnings.append("Overall feedback is quite brief")
        
        if len(response.suggestions) < 2:
            warnings.append("Limited suggestions provided")
    
    def _validate_score_consistency(self, response: GradeResponse, essay_type: EssayType, issues: List[str]) -> None:
        """Check that breakdown scores sum to total score."""
        calculated_total = self._calculate_total_score(response.breakdown, essay_type)
        
        if calculated_total != response.score:
            issues.append(f"Score mismatch: reported {response.score}, calculated {calculated_total}")
    
    def _calculate_total_score(self, breakdown: GradeBreakdown, essay_type: EssayType) -> int:
        """Calculate total score from breakdown components."""
        if essay_type in [EssayType.DBQ, EssayType.LEQ]:
            return (breakdown.thesis.score + breakdown.contextualization.score + 
                   breakdown.evidence.score + breakdown.analysis.score)
        elif essay_type == EssayType.SAQ:
            return (breakdown.thesis.score + breakdown.contextualization.score + 
                   breakdown.evidence.score)
        else:
            raise ValueError(f"Unknown essay type: {essay_type}")