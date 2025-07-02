"""Grade models for APUSH essay grading"""

from pydantic import BaseModel, computed_field
from typing import List, Optional
from enum import Enum


class RubricItem(BaseModel):
    """Individual rubric item with score and feedback"""
    
    score: int
    max_score: int
    feedback: str
    
    @computed_field
    @property
    def is_full_credit(self) -> bool:
        """Check if this item received full credit"""
        return self.score == self.max_score
    
    @computed_field
    @property
    def percentage(self) -> float:
        """Get percentage score for this item"""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100
    
    @computed_field
    @property
    def performance_level(self) -> str:
        """Get performance level based on percentage"""
        percentage = self.percentage
        if percentage == 100:
            return "Excellent"
        elif percentage >= 80:
            return "Proficient"
        elif percentage >= 50:
            return "Developing"
        else:
            return "Needs Improvement"


class GradeBreakdown(BaseModel):
    """Detailed breakdown of essay grade by rubric components"""
    
    thesis: RubricItem
    contextualization: RubricItem
    evidence: RubricItem
    analysis: RubricItem
    complexity: Optional[RubricItem] = None


class GradeResponse(BaseModel):
    """Complete grading response"""
    
    score: int
    max_score: int
    breakdown: GradeBreakdown
    overall_feedback: str
    suggestions: List[str]
    warnings: Optional[List[str]] = None
    
    @computed_field
    @property
    def percentage_score(self) -> float:
        """Get percentage score"""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100
    
    @computed_field
    @property
    def letter_grade(self) -> str:
        """Get letter grade based on percentage"""
        percentage = self.percentage_score
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    @computed_field
    @property
    def performance_level(self) -> str:
        """Get overall performance level"""
        percentage = self.percentage_score
        if percentage >= 90:
            return "Excellent"
        elif percentage >= 80:
            return "Proficient"
        elif percentage >= 70:
            return "Developing"
        else:
            return "Needs Improvement"


class GradingError(Exception):
    """Custom exception for grading errors"""
    pass


class GradingErrorType(str, Enum):
    """Enumeration of grading error types"""
    
    INVALID_RESPONSE = "invalid_response"
    INVALID_SCORE = "invalid_score" 
    NETWORK_ERROR = "network_error"
    API_KEY_MISSING = "api_key_missing"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ESSAY_TOO_SHORT = "essay_too_short"
    ESSAY_TOO_LONG = "essay_too_long"
    PARSE_ERROR = "parse_error"
    
    @property
    def description(self) -> str:
        """Get error description"""
        descriptions = {
            "invalid_response": "Received invalid response from grading service",
            "invalid_score": "Received invalid score from grading service",
            "network_error": "Network error occurred",
            "api_key_missing": "API key is missing. Please check your configuration",
            "rate_limit_exceeded": "Rate limit exceeded. Please try again later",
            "essay_too_short": "Essay is too short for accurate grading",
            "essay_too_long": "Essay exceeds maximum length",
            "parse_error": "Failed to parse response"
        }
        return descriptions[self.value]