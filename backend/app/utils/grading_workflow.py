"""
Simplified grading workflow for hobby project.
Replaces complex API coordinator with direct function calls.
"""

import logging
from app.models.core import EssayType, GradeResponse
from app.services.ai.factory import create_ai_service
from app.utils.essay_processing import preprocess_essay
from app.utils.prompt_generation import generate_grading_prompt
from app.utils.response_processing import process_ai_response
from app.exceptions import ValidationError, ProcessingError, APIError

logger = logging.getLogger(__name__)


async def grade_essay(essay_text: str, essay_type: EssayType, prompt: str) -> GradeResponse:
    """
    Complete essay grading workflow using simplified utilities.
    
    Args:
        essay_text: The student's essay text
        essay_type: The type of essay (DBQ, LEQ, SAQ)
        prompt: The essay question/prompt
        
    Returns:
        GradeResponse with scores, feedback, and breakdown
        
    Raises:
        ValidationError: If essay fails validation
        ProcessingError: If any processing step fails
        APIError: If the AI service fails
    """
    try:
        logger.info(f"Starting simplified grading workflow for {essay_type.value}")
        
        # Step 1: Preprocess and validate essay
        logger.debug("Step 1: Preprocessing essay")
        preprocessing_result = preprocess_essay(essay_text, essay_type)
        
        # Basic validation - fail if essay is too short
        if not preprocessing_result.is_valid():
            critical_warnings = [w for w in preprocessing_result.warnings if "too short" in w]
            if critical_warnings:
                raise ValidationError(f"Essay validation failed: {critical_warnings[0]}")
        
        # Step 2: Generate AI prompts
        logger.debug("Step 2: Generating AI prompts")
        system_prompt, user_message = generate_grading_prompt(
            essay_text, essay_type, prompt, preprocessing_result
        )
        
        # Step 3: Call AI service
        logger.debug("Step 3: Calling AI grading service")
        ai_service = create_ai_service()
        raw_ai_response = await ai_service.generate_response(
            system_prompt, user_message, essay_type
        )
        
        # Step 4: Process AI response
        logger.debug("Step 4: Processing AI response")
        grade_response = process_ai_response(raw_ai_response, essay_type)
        
        # Add preprocessing warnings to response
        if preprocessing_result.warnings:
            grade_response.warnings = preprocessing_result.warnings
        
        logger.info(f"Essay grading completed successfully with score {grade_response.score}/{grade_response.max_score}")
        return grade_response
        
    except ValidationError:
        logger.error("Essay validation failed")
        raise
        
    except ProcessingError:
        logger.error("Essay processing failed")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in grading workflow: {e}")
        raise APIError(f"Grading workflow failed: {str(e)}")


def validate_grading_request(essay_text: str, essay_type: EssayType, prompt: str) -> None:
    """
    Basic validation of grading request parameters.
    
    Raises:
        ValidationError: If parameters are invalid
    """
    if not essay_text or not essay_text.strip():
        raise ValidationError("Essay text cannot be empty")
    
    if not prompt or not prompt.strip():
        raise ValidationError("Essay prompt cannot be empty")
    
    if len(essay_text) > 50000:  # Reasonable limit for hobby project
        raise ValidationError("Essay text is too long (max 50,000 characters)")
    
    if len(prompt) > 5000:
        raise ValidationError("Essay prompt is too long (max 5,000 characters)")


async def grade_essay_with_validation(essay_text: str, essay_type: EssayType, prompt: str) -> GradeResponse:
    """
    Grade essay with input validation.
    Convenience function that combines validation and grading.
    """
    # Validate inputs
    validate_grading_request(essay_text, essay_type, prompt)
    
    # Perform grading
    return await grade_essay(essay_text, essay_type, prompt)