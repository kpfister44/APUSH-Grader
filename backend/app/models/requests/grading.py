"""
API request and response models for essay grading endpoints.

Defines the contract for the /api/v1/grade endpoint used by the iOS frontend.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse


class GradingRequest(BaseModel):
    """
    Request model for POST /api/v1/grade endpoint.
    
    Contains the essay content and metadata needed for grading.
    """
    
    essay_text: str = Field(
        ...,
        description="The student's essay text to be graded",
        min_length=1,
        max_length=10000
    )
    
    essay_type: EssayType = Field(
        ...,
        description="The type of essay (DBQ, LEQ, or SAQ)"
    )
    
    prompt: str = Field(
        ...,
        description="The essay question/prompt provided to the student",
        min_length=1,
        max_length=2000
    )
    
    @validator('essay_text')
    def validate_essay_text(cls, v):
        """Validate essay text is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Essay text cannot be empty or just whitespace")
        return v.strip()
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty or just whitespace")
        return v.strip()
    
    class Config:
        json_encoders = {
            EssayType: lambda v: v.value
        }
        
        schema_extra = {
            "example": {
                "essay_text": "The American Revolution was a pivotal moment in history...",
                "essay_type": "LEQ",
                "prompt": "Evaluate the extent to which the American Revolution changed American society in the period from 1775 to 1800."
            }
        }


class GradingResponse(BaseModel):
    """
    Response model for POST /api/v1/grade endpoint.
    
    Contains the grading results including scores, feedback, and suggestions.
    Based on the existing GradeResponse model but optimized for API transport.
    """
    
    score: int = Field(
        ...,
        description="The total score achieved",
        ge=0
    )
    
    max_score: int = Field(
        ...,
        description="The maximum possible score for this essay type",
        gt=0
    )
    
    percentage: float = Field(
        ...,
        description="Score as percentage (0-100)",
        ge=0.0,
        le=100.0
    )
    
    letter_grade: str = Field(
        ...,
        description="Letter grade (A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F)"
    )
    
    performance_level: str = Field(
        ...,
        description="Performance level (Excellent, Proficient, Developing, Inadequate)"
    )
    
    breakdown: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Detailed breakdown by rubric section"
    )
    
    overall_feedback: str = Field(
        ...,
        description="Overall feedback about the essay"
    )
    
    suggestions: List[str] = Field(
        default_factory=list,
        description="Specific suggestions for improvement"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings about essay structure or content"
    )
    
    # Metadata fields
    word_count: int = Field(
        ...,
        description="Word count of the essay",
        ge=0
    )
    
    paragraph_count: int = Field(
        ...,
        description="Paragraph count of the essay", 
        ge=0
    )
    
    processing_time_ms: Optional[int] = Field(
        None,
        description="Processing time in milliseconds",
        ge=0
    )
    
    @validator('percentage')
    def validate_percentage(cls, v, values):
        """Ensure percentage matches score/max_score calculation."""
        if 'score' in values and 'max_score' in values:
            expected = (values['score'] / values['max_score']) * 100
            if abs(v - expected) > 0.1:  # Allow small floating point differences
                raise ValueError(f"Percentage {v} doesn't match calculated value {expected}")
        return v
    
    @classmethod
    def from_grade_response(
        cls, 
        grade_response: GradeResponse,
        word_count: int,
        paragraph_count: int,
        warnings: List[str] = None,
        processing_time_ms: int = None
    ) -> 'GradingResponse':
        """
        Create GradingResponse from internal GradeResponse model.
        
        Args:
            grade_response: Internal grade response model
            word_count: Essay word count
            paragraph_count: Essay paragraph count  
            warnings: Processing warnings
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            API-optimized grading response
        """
        return cls(
            score=grade_response.score,
            max_score=grade_response.max_score,
            percentage=grade_response.percentage_score,
            letter_grade=grade_response.letter_grade,
            performance_level=grade_response.performance_level,
            breakdown=grade_response.breakdown,
            overall_feedback=grade_response.overall_feedback,
            suggestions=grade_response.suggestions,
            warnings=warnings or [],
            word_count=word_count,
            paragraph_count=paragraph_count,
            processing_time_ms=processing_time_ms
        )
    
    class Config:
        schema_extra = {
            "example": {
                "score": 5,
                "max_score": 6,
                "percentage": 83.3,
                "letter_grade": "B",
                "performance_level": "Proficient",
                "breakdown": {
                    "thesis": {
                        "score": 1,
                        "maxScore": 1,
                        "feedback": "Clear thesis with line of reasoning."
                    },
                    "contextualization": {
                        "score": 1,
                        "maxScore": 1,
                        "feedback": "Good historical context provided."
                    },
                    "evidence": {
                        "score": 2,
                        "maxScore": 2,
                        "feedback": "Strong use of specific evidence."
                    },
                    "analysis": {
                        "score": 1,
                        "maxScore": 2,
                        "feedback": "Analysis present but could be more sophisticated."
                    }
                },
                "overall_feedback": "Strong essay with clear argument and good evidence use.",
                "suggestions": [
                    "Add more sophisticated analysis",
                    "Consider multiple perspectives"
                ],
                "warnings": [],
                "word_count": 487,
                "paragraph_count": 4,
                "processing_time_ms": 1250
            }
        }


class GradingErrorResponse(BaseModel):
    """
    Error response model for grading endpoint failures.
    
    Provides structured error information for client handling.
    """
    
    error: str = Field(
        ...,
        description="Error type identifier"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Essay text is too short for the selected essay type",
                "details": {
                    "min_words": 150,
                    "actual_words": 75,
                    "essay_type": "LEQ"
                }
            }
        }