"""
Grading API endpoints for essay grading functionality.

Provides the main /api/v1/grade endpoint for iOS frontend integration.
"""

import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from app.models.requests.grading import (
    GradingRequest, 
    GradingResponse, 
    GradingErrorResponse
)
from app.models.core import EssayType
from app.services.base.exceptions import (
    ValidationError,
    ProcessingError,
    APIError
)
from app.middleware.rate_limiting import limiter
from app.utils.simple_usage import get_simple_usage_tracker
from app.utils.grading_workflow import grade_essay_with_validation


logger = logging.getLogger(__name__)
usage_tracker = get_simple_usage_tracker()
router = APIRouter(prefix="/api/v1", tags=["grading"])


def _combine_saq_parts(grading_request: GradingRequest) -> str:
    """
    Combine SAQ parts into a single text for processing.
    
    Args:
        grading_request: The grading request containing SAQ parts
        
    Returns:
        Combined essay text with parts labeled
    """
    if grading_request.saq_parts:
        return f"""A) {grading_request.saq_parts.part_a}

B) {grading_request.saq_parts.part_b}

C) {grading_request.saq_parts.part_c}"""
    else:
        return grading_request.essay_text


@router.post(
    "/grade",
    response_model=GradingResponse,
    responses={
        400: {"model": GradingErrorResponse, "description": "Validation Error"},
        422: {"model": GradingErrorResponse, "description": "Processing Error"},
        429: {"description": "Rate limit exceeded"},
        500: {"model": GradingErrorResponse, "description": "Internal Server Error"}
    },
    summary="Grade an essay",
    description="""
    Grade a student essay using AI-powered analysis.
    
    This endpoint uses a simplified grading workflow:
    1. Preprocesses and validates the essay text
    2. Generates AI prompts based on essay type and rubric
    3. Calls AI grading service (Anthropic Claude 3.5 Sonnet)
    4. Processes and formats the response
    
    **Essay Types:**
    - **DBQ** (Document-Based Question): 6-point rubric
    - **LEQ** (Long Essay Question): 6-point rubric  
    - **SAQ** (Short Answer Question): 3-point rubric
    
    **Response includes:**
    - Overall score and letter grade
    - Detailed breakdown by rubric sections
    - Specific feedback and suggestions
    - Essay metadata (word count, warnings, etc.)
    
    **Rate Limits:**
    - 20 requests per minute
    - 50 essays per hour
    """
)
@limiter.limit("20/minute")
@limiter.limit("50/hour")
async def grade_essay(
    request: Request,
    grading_request: GradingRequest
) -> GradingResponse:
    """
    Grade an essay using the complete grading workflow.
    
    Args:
        request: FastAPI request object for rate limiting
        grading_request: Grading request containing essay text, type, and prompt
        api_coordinator: Injected API coordinator service
        
    Returns:
        Structured grading response with scores, feedback, and metadata
        
    Raises:
        HTTPException: For validation, processing, or server errors
    """
    start_time = time.time()
    
    try:
        # Get the essay text (combined for SAQ parts or regular text)
        essay_text = _combine_saq_parts(grading_request)
        word_count = len(essay_text.split())
        
        # Get client IP for usage tracking
        client_ip = request.client.host if request.client else "unknown"
        
        # Check usage limits
        can_process, reason = usage_tracker.can_process_essay(client_ip, word_count)
        if not can_process:
            logger.warning(f"Usage limit exceeded for {client_ip}: {reason}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Daily usage limit exceeded",
                    "message": f"{reason}. This helps manage costs and ensures the service remains available for all teachers.",
                    "limit_type": "daily_usage"
                }
            )
        
        # Simple logging
        logger.info(f"Grading {grading_request.essay_type.value} essay ({word_count} words) for {client_ip}")
        
        # Call the simplified grading workflow
        grade_response = await grade_essay_with_validation(
            essay_text=essay_text,
            essay_type=grading_request.essay_type,
            prompt=grading_request.prompt
        )
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Convert to API response format
        # Note: We'll need to extract word count and warnings from the coordinator
        # For now, using placeholder values - this will be refined in integration
        api_response = GradingResponse.from_grade_response(
            grade_response=grade_response,
            word_count=len(essay_text.split()),  # Simple word count
            paragraph_count=len([p for p in essay_text.split('\n\n') if p.strip()]),
            warnings=[],  # Will be populated from preprocessing result
            processing_time_ms=processing_time_ms
        )
        
        # Record successful processing and log
        usage_tracker.record_essay_processed(client_ip, grading_request.essay_type.value, word_count)
        logger.info(f"Successfully graded essay: {api_response.score}/{api_response.max_score} ({processing_time_ms}ms)")
        
        return api_response
        
    except ValidationError as e:
        logger.error(f"Validation error for {grading_request.essay_type.value}: {str(e)}")
        error_response = GradingErrorResponse(
            error="VALIDATION_ERROR",
            message=str(e),
            details={"essay_type": grading_request.essay_type.value}
        )
        raise HTTPException(status_code=400, detail=error_response.dict())
        
    except ProcessingError as e:
        logger.error(f"Processing error for {grading_request.essay_type.value}: {str(e)}")
        error_response = GradingErrorResponse(
            error="PROCESSING_ERROR", 
            message=str(e),
            details={"essay_type": grading_request.essay_type.value}
        )
        raise HTTPException(status_code=422, detail=error_response.dict())
        
    except APIError as e:
        logger.error(f"API error for {grading_request.essay_type.value}: {str(e)}")
        error_response = GradingErrorResponse(
            error="API_ERROR",
            message=str(e),
            details={"essay_type": grading_request.essay_type.value}
        )
        raise HTTPException(status_code=500, detail=error_response.dict())
        
    except Exception as e:
        logger.error(f"Unexpected error for {grading_request.essay_type.value}: {str(e)}")
        error_response = GradingErrorResponse(
            error="INTERNAL_ERROR",
            message="An internal server error occurred",
            details={"essay_type": grading_request.essay_type.value}
        )
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.get(
    "/grade/status",
    summary="Get grading service status",
    description="Check if the grading service is available and operational."
)
async def get_grading_status() -> Dict[str, Any]:
    """
    Get the current status of the grading service.
    
    Returns:
        Status information including service availability and configuration
    """
    try:
        # Check simplified workflow components
        from app.utils import essay_processing, prompt_generation, response_processing, grading_workflow
        from app.services.ai.factory import create_ai_service
        
        # Test that we can create AI service
        ai_service = create_ai_service()
        
        return {
            "status": "operational",
            "services": {
                "grading_workflow": "available",
                "essay_processing": "available", 
                "prompt_generation": "available",
                "response_processing": "available",
                "ai_service": "available"
            },
            "supported_essay_types": ["DBQ", "LEQ", "SAQ"],
            "mode": "simplified_architecture"
        }
        
    except Exception as e:
        logger.error(f"Service status check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
            "services": {
                "grading_workflow": "unavailable"
            }
        }