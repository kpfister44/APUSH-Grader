"""
Pydantic models for Anthropic Structured Outputs.

WHY SEPARATE SCHEMAS?
Structured Outputs doesn't support @computed_field decorators.
We maintain two sets of models:

1. OUTPUT SCHEMAS (this file): For API responses (no computed fields)
   - No computed fields (percentage, performance_level)
   - Match exact JSON structure from Claude
   - Used with client.beta.messages.parse()

2. CORE MODELS (models/core.py): For application logic (with computed fields)
   - Include percentage, performance_level as @computed_field
   - Used throughout application logic
   - Converted from output schemas post-parsing

FLOW:
Claude API → Output Schema (parsed) → Core Model (computed) → Application

This separation ensures we get Structured Outputs benefits while maintaining
our existing computed field functionality.
"""

from pydantic import BaseModel, Field
from typing import List


class RubricItemOutput(BaseModel):
    """Rubric item from Structured Output (no computed percentage field)"""
    score: int = Field(..., description="Points earned for this criterion")
    max_score: int = Field(..., description="Maximum points possible")
    feedback: str = Field(..., description="Specific feedback for this criterion")


class DBQLeqBreakdownOutput(BaseModel):
    """DBQ/LEQ breakdown for Structured Output (6-point rubric)"""
    thesis: RubricItemOutput = Field(..., description="Thesis evaluation (0-1 points)")
    contextualization: RubricItemOutput = Field(..., description="Contextualization evaluation (0-1 points)")
    evidence: RubricItemOutput = Field(..., description="Evidence evaluation (0-2 points)")
    analysis: RubricItemOutput = Field(..., description="Analysis evaluation (0-2 points)")


class SAQBreakdownOutput(BaseModel):
    """SAQ breakdown for Structured Output (3-point College Board rubric)"""
    part_a: RubricItemOutput = Field(..., description="Part A evaluation (0-1 points)")
    part_b: RubricItemOutput = Field(..., description="Part B evaluation (0-1 points)")
    part_c: RubricItemOutput = Field(..., description="Part C evaluation (0-1 points)")


class EGBreakdownOutput(BaseModel):
    """EG rubric breakdown for Structured Output (10-point A/C/E rubric)"""
    criterion_a: RubricItemOutput = Field(..., description="Criterion A: Addresses prompt, complete sentences (0-1 points)")
    criterion_c: RubricItemOutput = Field(..., description="Criterion C: Cites specific evidence (0-3 points)")
    criterion_e: RubricItemOutput = Field(..., description="Criterion E: Explains thoroughly (0-6 points)")


class DBQGradeOutput(BaseModel):
    """Complete DBQ grading response for Structured Output"""
    score: int = Field(..., description="Total score earned")
    max_score: int = Field(..., description="Maximum possible score (6 for DBQ)")
    letter_grade: str = Field(..., description="Letter grade (A/B/C/D/F)")
    overall_feedback: str = Field(..., description="Comprehensive feedback")
    suggestions: List[str] = Field(..., description="Actionable improvement suggestions")
    breakdown: DBQLeqBreakdownOutput = Field(..., description="Detailed rubric breakdown")


class LEQGradeOutput(BaseModel):
    """Complete LEQ grading response for Structured Output"""
    score: int = Field(..., description="Total score earned")
    max_score: int = Field(..., description="Maximum possible score (6 for LEQ)")
    letter_grade: str = Field(..., description="Letter grade (A/B/C/D/F)")
    overall_feedback: str = Field(..., description="Comprehensive feedback")
    suggestions: List[str] = Field(..., description="Actionable improvement suggestions")
    breakdown: DBQLeqBreakdownOutput = Field(..., description="Detailed rubric breakdown")


class SAQCollegeBoardGradeOutput(BaseModel):
    """Complete SAQ grading response for Structured Output (College Board rubric)"""
    score: int = Field(..., description="Total score earned")
    max_score: int = Field(..., description="Maximum possible score (3 for College Board SAQ)")
    letter_grade: str = Field(..., description="Letter grade (A/B/C/D/F)")
    overall_feedback: str = Field(..., description="Comprehensive feedback")
    suggestions: List[str] = Field(..., description="Actionable improvement suggestions")
    breakdown: SAQBreakdownOutput = Field(..., description="Detailed rubric breakdown")


class SAQEGGradeOutput(BaseModel):
    """Complete SAQ grading response for Structured Output (EG rubric)"""
    score: int = Field(..., description="Total score earned")
    max_score: int = Field(..., description="Maximum possible score (10 for EG rubric)")
    letter_grade: str = Field(..., description="Letter grade (A/B/C/D/F)")
    overall_feedback: str = Field(..., description="Comprehensive feedback")
    suggestions: List[str] = Field(..., description="Actionable improvement suggestions")
    breakdown: EGBreakdownOutput = Field(..., description="Detailed rubric breakdown")


def get_output_schema_for_essay(essay_type: str, rubric_type: str = "college_board"):
    """
    Get the appropriate Structured Output schema class for essay/rubric type.

    Args:
        essay_type: "DBQ", "LEQ", or "SAQ"
        rubric_type: "college_board" or "eg" (only used for SAQ)

    Returns:
        Pydantic model class for parsing Structured Output

    Raises:
        ValueError: If unknown essay type or rubric type
    """
    if essay_type == "DBQ":
        return DBQGradeOutput
    elif essay_type == "LEQ":
        return LEQGradeOutput
    elif essay_type == "SAQ":
        if rubric_type == "eg":
            return SAQEGGradeOutput
        elif rubric_type == "college_board":
            return SAQCollegeBoardGradeOutput
        else:
            raise ValueError(f"Unknown SAQ rubric type: {rubric_type}")
    else:
        raise ValueError(f"Unknown essay type: {essay_type}")
