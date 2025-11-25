"""
Simplified response processing for AI grading responses.
Converts Structured Outputs to core models with computed fields.
"""

import logging
from pydantic import BaseModel

from app.models.core import GradeResponse, RubricItem, DBQLeqBreakdown, SAQBreakdown, EGBreakdown, EssayType, RubricType
from app.models.structured_outputs import RubricItemOutput
from app.exceptions import ProcessingError

logger = logging.getLogger(__name__)


def process_ai_response(
    structured_response: BaseModel,
    essay_type: EssayType,
    rubric_type: RubricType = RubricType.COLLEGE_BOARD
) -> GradeResponse:
    """
    Convert Structured Output to full GradeResponse with computed fields.

    Structured Outputs returns parsed Pydantic model (without computed fields).
    This converts to core GradeResponse which includes percentage/performance_level.

    Args:
        structured_response: Parsed Pydantic model from Structured Outputs
        essay_type: Type of essay being graded
        rubric_type: Rubric type (only used for SAQ essays)

    Returns:
        Full GradeResponse model with computed fields

    Raises:
        ProcessingError: If conversion fails
    """
    try:
        logger.debug(f"Converting Structured Output to GradeResponse for {essay_type.value}")

        # Convert breakdown from output models to core models (adds computed fields)
        breakdown = _convert_breakdown(structured_response.breakdown, essay_type, rubric_type)

        # Build full GradeResponse with computed fields
        grade_response = GradeResponse(
            score=structured_response.score,
            max_score=structured_response.max_score,
            letter_grade=structured_response.letter_grade,
            overall_feedback=structured_response.overall_feedback,
            suggestions=structured_response.suggestions,
            warnings=None,  # Warnings added by preprocessing layer
            breakdown=breakdown
        )

        logger.info(
            f"Successfully converted Structured Output to GradeResponse: "
            f"{grade_response.score}/{grade_response.max_score} "
            f"({grade_response.percentage_score:.1f}%, {grade_response.performance_level})"
        )

        return grade_response

    except Exception as e:
        logger.error(f"Error converting Structured Output to GradeResponse: {e}")
        raise ProcessingError(f"Failed to process structured AI response: {e}")


def _convert_breakdown(
    breakdown_output: BaseModel,
    essay_type: EssayType,
    rubric_type: RubricType = RubricType.COLLEGE_BOARD
) -> DBQLeqBreakdown | SAQBreakdown | EGBreakdown:
    """
    Convert breakdown from Structured Output model to core model.

    Structured Output models don't have computed fields. Core models do.
    This conversion ensures percentage calculations are available.

    Args:
        breakdown_output: Parsed breakdown from Structured Output
        essay_type: Type of essay
        rubric_type: Rubric type (only used for SAQ)

    Returns:
        Core breakdown model with computed percentage fields
    """
    if essay_type == EssayType.SAQ:
        if rubric_type == RubricType.EG:
            # EG rubric breakdown
            return EGBreakdown(
                criterion_a=_convert_rubric_item(breakdown_output.criterion_a),
                criterion_c=_convert_rubric_item(breakdown_output.criterion_c),
                criterion_e=_convert_rubric_item(breakdown_output.criterion_e)
            )
        else:
            # College Board SAQ breakdown
            return SAQBreakdown(
                part_a=_convert_rubric_item(breakdown_output.part_a),
                part_b=_convert_rubric_item(breakdown_output.part_b),
                part_c=_convert_rubric_item(breakdown_output.part_c)
            )
    else:
        # DBQ/LEQ breakdown
        return DBQLeqBreakdown(
            thesis=_convert_rubric_item(breakdown_output.thesis),
            contextualization=_convert_rubric_item(breakdown_output.contextualization),
            evidence=_convert_rubric_item(breakdown_output.evidence),
            analysis=_convert_rubric_item(breakdown_output.analysis)
        )


def _convert_rubric_item(item_output: RubricItemOutput) -> RubricItem:
    """
    Convert RubricItemOutput (no computed fields) to RubricItem (with percentage).

    Args:
        item_output: Parsed rubric item from Structured Output

    Returns:
        Core RubricItem with computed percentage field
    """
    return RubricItem(
        score=item_output.score,
        max_score=item_output.max_score,
        feedback=item_output.feedback
    )
    # percentage field is auto-computed by RubricItem's @computed_field decorator


def get_letter_grade(percentage: float) -> str:
    """Convert percentage to letter grade"""
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


def validate_score_range(score: int, max_score: int, essay_type: EssayType) -> bool:
    """Validate that score is within expected range"""
    if score < 0 or score > max_score:
        return False
    
    expected_max = essay_type.max_score
    if max_score != expected_max:
        logger.warning(f"Unexpected max_score {max_score} for {essay_type.value}, expected {expected_max}")
    
    return True