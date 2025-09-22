"""
Simplified response processing for AI grading responses.
Replaces complex service architecture with direct functions.
"""

import json
import logging
from typing import Dict, Any

from app.models.core import GradeResponse, RubricItem, DBQLeqBreakdown, SAQBreakdown, EGBreakdown, EssayType, RubricType
from app.exceptions import ProcessingError

logger = logging.getLogger(__name__)


def _extract_json_from_response(raw_response: str) -> str:
    """
    Extract JSON from AI response, handling Claude Sonnet 4 markdown format.

    Claude Sonnet 4 wraps JSON in markdown code blocks like:
    ```json
    { "key": "value" }
    ```

    This function strips the markdown and returns clean JSON.
    """
    response = raw_response.strip()

    # Check if response is wrapped in markdown code blocks
    if response.startswith('```json\n') and response.endswith('\n```'):
        # Extract JSON content between markdown markers
        json_content = response[8:-4]  # Remove ```json\n at start and \n``` at end
        logger.debug("Extracted JSON from markdown code blocks")
        return json_content.strip()
    elif response.startswith('```\n') and response.endswith('\n```'):
        # Handle generic code blocks
        json_content = response[4:-4]  # Remove ```\n at start and \n``` at end
        logger.debug("Extracted JSON from generic code blocks")
        return json_content.strip()
    else:
        # Return as-is (for Claude 3.5 Sonnet compatibility)
        return response


def process_ai_response(raw_response: str, essay_type: EssayType, rubric_type: RubricType = RubricType.COLLEGE_BOARD) -> GradeResponse:
    """
    Process raw AI response into structured GradeResponse.
    Handles validation and error recovery.
    """
    try:
        # Clean and parse JSON response (handle Claude Sonnet 4 markdown format)
        cleaned_response = _extract_json_from_response(raw_response)
        response_data = json.loads(cleaned_response)

        # Validate required fields
        _validate_response_structure(response_data, essay_type, rubric_type)
        
        # Build GradeResponse
        grade_response = _build_grade_response(response_data, essay_type, rubric_type)
        
        logger.info(f"Successfully processed AI response: {grade_response.score}/{grade_response.max_score}")
        return grade_response
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise ProcessingError(f"Invalid JSON response from AI service: {e}")
    
    except Exception as e:
        logger.error(f"Error processing AI response: {e}")
        raise ProcessingError(f"Failed to process AI response: {e}")


def _validate_response_structure(data: Dict[str, Any], essay_type: EssayType, rubric_type: RubricType = RubricType.COLLEGE_BOARD) -> None:
    """Validate that response has required structure"""
    required_fields = ["score", "max_score", "letter_grade", "overall_feedback", "suggestions", "breakdown"]
    
    for field in required_fields:
        if field not in data:
            raise ProcessingError(f"Missing required field: {field}")
    
    # Validate breakdown structure based on essay type and rubric type
    breakdown = data["breakdown"]
    
    if essay_type == EssayType.SAQ:
        if rubric_type == RubricType.EG:
            required_breakdown_fields = ["criterion_a", "criterion_c", "criterion_e"]
        else:  # College Board rubric
            required_breakdown_fields = ["part_a", "part_b", "part_c"]
    else:  # DBQ and LEQ
        required_breakdown_fields = ["thesis", "contextualization", "evidence", "analysis"]
    
    for field in required_breakdown_fields:
        if field not in breakdown:
            raise ProcessingError(f"Missing breakdown field: {field}")
        
        # Validate rubric item structure (handle both max_score and maxScore)
        item = breakdown[field]
        required_keys = ["score", "feedback"]
        max_score_key = "max_score" if "max_score" in item else "maxScore"
        if not all(key in item for key in required_keys) or max_score_key not in item:
            raise ProcessingError(f"Invalid rubric item structure for {field}")


def _build_grade_response(data: Dict[str, Any], essay_type: EssayType, rubric_type: RubricType = RubricType.COLLEGE_BOARD) -> GradeResponse:
    """Build GradeResponse from validated data"""
    
    breakdown_data = data["breakdown"]
    
    # Build appropriate breakdown based on essay type and rubric type
    if essay_type == EssayType.SAQ:
        if rubric_type == RubricType.EG:
            # Build EG breakdown
            criterion_a = _build_rubric_item(breakdown_data["criterion_a"])
            criterion_c = _build_rubric_item(breakdown_data["criterion_c"])
            criterion_e = _build_rubric_item(breakdown_data["criterion_e"])
            
            breakdown = EGBreakdown(
                criterion_a=criterion_a,
                criterion_c=criterion_c,
                criterion_e=criterion_e
            )
        else:
            # Build College Board SAQ breakdown
            part_a = _build_rubric_item(breakdown_data["part_a"])
            part_b = _build_rubric_item(breakdown_data["part_b"])
            part_c = _build_rubric_item(breakdown_data["part_c"])
            
            breakdown = SAQBreakdown(
                part_a=part_a,
                part_b=part_b,
                part_c=part_c
            )
    else:
        # Build DBQ/LEQ breakdown
        thesis = _build_rubric_item(breakdown_data["thesis"])
        contextualization = _build_rubric_item(breakdown_data["contextualization"])
        evidence = _build_rubric_item(breakdown_data["evidence"])
        analysis = _build_rubric_item(breakdown_data["analysis"])
        
        breakdown = DBQLeqBreakdown(
            thesis=thesis,
            contextualization=contextualization,
            evidence=evidence,
            analysis=analysis
        )
    
    # Build main response
    return GradeResponse(
        score=int(data["score"]),
        max_score=int(data["max_score"]),
        letter_grade=str(data["letter_grade"]),
        overall_feedback=str(data["overall_feedback"]),
        suggestions=data.get("suggestions", []),
        warnings=None,  # Warnings handled in preprocessing
        breakdown=breakdown
    )


def _build_rubric_item(item_data: Dict[str, Any]) -> RubricItem:
    """Build RubricItem from data, handling field name variations"""
    
    # Handle both 'max_score' and 'maxScore' field names
    max_score = item_data.get("max_score") or item_data.get("maxScore")
    if max_score is None:
        raise ProcessingError("Missing max_score field in rubric item")
    
    return RubricItem(
        score=int(item_data["score"]),
        max_score=int(max_score),
        feedback=str(item_data["feedback"])
    )


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