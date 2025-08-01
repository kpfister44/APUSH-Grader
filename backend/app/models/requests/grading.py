"""
API request and response models for essay grading endpoints.

Defines the contract for the /api/v1/grade endpoint used by the iOS frontend.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum

from app.models.core import EssayType, SAQType
from app.models.core import GradeResponse


class SAQParts(BaseModel):
    """Model for SAQ three-part structure."""
    
    part_a: Optional[str] = Field(
        None,
        description="Student response to SAQ Part A",
        max_length=2000
    )
    
    part_b: Optional[str] = Field(
        None,
        description="Student response to SAQ Part B", 
        max_length=2000
    )
    
    part_c: Optional[str] = Field(
        None,
        description="Student response to SAQ Part C",
        max_length=2000
    )
    
    @validator('part_a', 'part_b', 'part_c')
    def validate_parts(cls, v):
        """Validate SAQ part text if provided."""
        if v is not None and v.strip():
            return v.strip()
        return v  # Allow None or empty strings


class GradingRequest(BaseModel):
    """
    Request model for POST /api/v1/grade endpoint.
    
    Contains the essay content and metadata needed for grading.
    """
    
    essay_text: Optional[str] = Field(
        None,
        description="The student's essay text to be graded (for DBQ/LEQ or legacy SAQ)",
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
    
    saq_parts: Optional[SAQParts] = Field(
        None,
        description="SAQ essay parts (Part A, B, C) - used when essay_type is SAQ"
    )
    
    saq_type: Optional[SAQType] = Field(
        None,
        description="SAQ subtype (stimulus, non_stimulus, secondary_comparison) - used when essay_type is SAQ"
    )
    
    # Note: essay_text validation moved to root_validator to handle SAQ vs non-SAQ logic
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty or just whitespace")
        return v.strip()
    
    @validator('saq_parts')
    def validate_saq_parts(cls, v, values):
        """Validate SAQ parts are provided when essay_type is SAQ."""
        essay_type = values.get('essay_type')
        essay_text = values.get('essay_text')
        
        if essay_type == EssayType.SAQ:
            # For SAQ, require either saq_parts or essay_text (for backward compatibility)
            if not v and not essay_text:
                raise ValueError("SAQ essays require either saq_parts or essay_text")
        elif v is not None:
            # For non-SAQ essays, saq_parts should not be provided
            raise ValueError("saq_parts can only be used with SAQ essay type")
        
        return v
    
    @validator('saq_type')
    def validate_saq_type(cls, v, values):
        """Validate SAQ type is provided when essay_type is SAQ."""
        essay_type = values.get('essay_type')
        
        if essay_type == EssayType.SAQ:
            # For SAQ, saq_type is optional but recommended
            pass
        elif v is not None:
            # For non-SAQ essays, saq_type should not be provided
            raise ValueError("saq_type can only be used with SAQ essay type")
        
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_essay_content(cls, values):
        """Validate essay content requirements based on essay type."""
        essay_type = values.get('essay_type')
        essay_text = values.get('essay_text')
        saq_parts = values.get('saq_parts')
        
        if essay_type == EssayType.SAQ:
            # SAQ can use either saq_parts or essay_text
            if not saq_parts and (not essay_text or not essay_text.strip()):
                raise ValueError("SAQ essays require either saq_parts or essay_text")
        else:
            # For non-SAQ essays, require non-empty essay_text
            if not essay_text or not essay_text.strip():
                raise ValueError("DBQ and LEQ essays require essay_text")
        
        # Clean essay_text if it exists
        if essay_text:
            values['essay_text'] = essay_text.strip()
        
        return values
    
    class Config:
        json_encoders = {
            EssayType: lambda v: v.value,
            SAQType: lambda v: v.value
        }
        
        schema_extra = {
            "examples": [
                {
                    "summary": "LEQ/DBQ Example",
                    "description": "Standard essay format for LEQ and DBQ",
                    "value": {
                        "essay_text": "The American Revolution was a pivotal moment in history...",
                        "essay_type": "LEQ",
                        "prompt": "Evaluate the extent to which the American Revolution changed American society in the period from 1775 to 1800."
                    }
                },
                {
                    "summary": "SAQ Multi-Part Example",
                    "description": "New SAQ format with separate parts",
                    "value": {
                        "essay_type": "SAQ",
                        "prompt": "Use the image above to answer parts A, B, and C.",
                        "saq_type": "stimulus",
                        "saq_parts": {
                            "part_a": "The Second Great Awakening was a religious revival movement in the early 1800s that emphasized personal salvation.",
                            "part_b": "The Second Great Awakening led to increased participation in reform movements like abolition and temperance.",
                            "part_c": "The Second Great Awakening was significant because it democratized religion and promoted social reform."
                        }
                    }
                }
            ]
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
            breakdown=grade_response.breakdown.model_dump() if grade_response.breakdown else {},
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