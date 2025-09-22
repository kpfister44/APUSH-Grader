"""
Consolidated core models for APUSH essay grading.
Simplified for hobby project serving 2-12 teachers.
"""

from enum import Enum
from pydantic import BaseModel, computed_field
from typing import List, Optional, Dict, Any, Union


# Essay Types
class EssayType(str, Enum):
    """Essay type enumeration"""
    
    DBQ = "DBQ"
    LEQ = "LEQ"
    SAQ = "SAQ"
    
    @property
    def description(self) -> str:
        """Get essay type description"""
        descriptions = {
            "DBQ": "Document Based Question",
            "LEQ": "Long Essay Question",
            "SAQ": "Short Answer Question"
        }
        return descriptions[self.value]
    
    @property
    def max_score(self) -> int:
        """Get maximum score for essay type"""
        scores = {
            "DBQ": 6,
            "LEQ": 6,
            "SAQ": 3
        }
        return scores[self.value]


# Rubric Type for SAQ Essays
class RubricType(str, Enum):
    """Rubric type enumeration for SAQ essays"""
    
    COLLEGE_BOARD = "college_board"
    EG = "eg"
    
    @property
    def description(self) -> str:
        """Get rubric type description"""
        descriptions = {
            "college_board": "College Board official rubric (3 points)",
            "eg": "EG custom rubric (10 points with A/C/E criteria)"
        }
        return descriptions[self.value]
    
    @property
    def max_score(self) -> int:
        """Get maximum score for rubric type"""
        scores = {
            "college_board": 3,
            "eg": 10
        }
        return scores[self.value]


# SAQ Type Differentiation
class SAQType(str, Enum):
    """SAQ type enumeration for different question formats"""
    
    STIMULUS = "stimulus"
    NON_STIMULUS = "non_stimulus"
    SECONDARY_COMPARISON = "secondary_comparison"
    
    @property
    def description(self) -> str:
        """Get SAQ type description"""
        descriptions = {
            "stimulus": "Stimulus-based SAQ with primary/secondary source analysis",
            "non_stimulus": "Non-stimulus SAQ with pure content questions",
            "secondary_comparison": "Secondary stimulus comparison SAQ with historiographical analysis"
        }
        return descriptions[self.value]
    
    @property
    def display_name(self) -> str:
        """Get user-friendly display name"""
        names = {
            "stimulus": "Source Analysis",
            "non_stimulus": "Content Question",
            "secondary_comparison": "Historical Comparison"
        }
        return names[self.value]


# AI Provider Configuration 
class Provider(str, Enum):
    """AI provider enumeration"""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class Model(str, Enum):
    """AI model enumeration with provider mapping"""
    
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    CLAUDE4_SONNET = "claude-sonnet-4-20250514"
    CLAUDE3_HAIKU = "claude-3-haiku-20240307"
    
    @property
    def name(self) -> str:
        """Get model name for API calls"""
        return self.value
    
    @property
    def provider(self) -> Provider:
        """Get provider for this model"""
        if self.value.startswith("gpt"):
            return Provider.OPENAI
        elif self.value.startswith("claude"):
            return Provider.ANTHROPIC
        else:
            raise ValueError(f"Unknown provider for model: {self.value}")


# Grade Models
class RubricItem(BaseModel):
    """Individual rubric item with score and feedback"""
    
    score: int
    max_score: int
    feedback: str
    
    @computed_field
    @property
    def percentage(self) -> float:
        """Get percentage score for this item"""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100


class GradeResponse(BaseModel):
    """Response from AI grading service"""
    
    score: int
    max_score: int
    letter_grade: str
    overall_feedback: str
    suggestions: List[str]
    warnings: Optional[List[str]] = None
    breakdown: Optional['GradeBreakdown'] = None
    
    @computed_field
    @property
    def percentage_score(self) -> float:
        """Get percentage score"""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100
    
    @computed_field
    @property
    def performance_level(self) -> str:
        """Get performance level based on score"""
        percentage = self.percentage_score
        if percentage >= 90:
            return "Advanced"
        elif percentage >= 80:
            return "Proficient"
        elif percentage >= 70:
            return "Developing"
        elif percentage >= 60:
            return "Beginning"
        else:
            return "Below Basic"


class DBQLeqBreakdown(BaseModel):
    """Detailed rubric breakdown for DBQ/LEQ essays (6-point rubric)"""
    
    thesis: RubricItem
    contextualization: RubricItem
    evidence: RubricItem
    analysis: RubricItem


class SAQBreakdown(BaseModel):
    """Detailed rubric breakdown for SAQ essays (3-point College Board rubric)"""
    
    part_a: RubricItem
    part_b: RubricItem
    part_c: RubricItem


class EGBreakdown(BaseModel):
    """Detailed rubric breakdown for EG rubric SAQ essays (10-point A/C/E rubric)"""
    
    criterion_a: RubricItem  # 1 point - addresses prompt, complete sentences
    criterion_c: RubricItem  # 3 points - cites specific evidence from time period
    criterion_e: RubricItem  # 6 points - explains evidence thoroughly


# Union type for essay breakdowns
GradeBreakdown = Union[DBQLeqBreakdown, SAQBreakdown, EGBreakdown]


# Custom Exceptions
class GradingError(Exception):
    """Base exception for grading-related errors"""
    pass


class GradingErrorType(str, Enum):
    """Types of grading errors"""
    
    VALIDATION_ERROR = "validation_error"
    PROCESSING_ERROR = "processing_error"
    API_ERROR = "api_error"
    TIMEOUT_ERROR = "timeout_error"


# Update forward references
GradeResponse.model_rebuild()