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
from app.services.base.protocols import APICoordinatorProtocol
from app.services.base.exceptions import (
    ValidationError,
    ProcessingError,
    APIError
)
from app.services.dependencies.service_locator import get_service_locator
from app.api.deps import get_api_coordinator
from app.middleware.rate_limiting import limiter
from app.services.logging.structured_logger import get_logger, PerformanceTimer


logger = logging.getLogger(__name__)
structured_logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["grading"])


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
    
    This endpoint orchestrates the complete grading workflow:
    1. Preprocesses and validates the essay text
    2. Generates AI prompts based on essay type and rubric
    3. Calls AI grading service (currently mock, will be real in Phase 2)
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
    grading_request: GradingRequest,
    api_coordinator: APICoordinatorProtocol = Depends(get_api_coordinator)
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
        # Enhanced structured logging
        structured_logger.info(
            "Grading request received",
            essay_type=grading_request.essay_type.value,
            essay_length=len(grading_request.essay_text),
            prompt_length=len(grading_request.prompt)
        )
        
        # Use performance timer for the grading workflow
        with PerformanceTimer(structured_logger, "essay_grading_workflow", 
                            essay_type=grading_request.essay_type.value):
            
            # Call the API coordinator to handle the complete workflow  
            grade_response = await api_coordinator.grade_essay(
                essay_text=grading_request.essay_text,
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
            word_count=len(grading_request.essay_text.split()),  # Simple word count
            paragraph_count=len([p for p in grading_request.essay_text.split('\n\n') if p.strip()]),
            warnings=[],  # Will be populated from preprocessing result
            processing_time_ms=processing_time_ms
        )
        
        # Log successful grading with structured data
        structured_logger.log_essay_grading(
            essay_type=grading_request.essay_type.value,
            word_count=api_response.word_count,
            processing_time_ms=processing_time_ms,
            score=api_response.score,
            max_score=api_response.max_score
        )
        
        return api_response
        
    except ValidationError as e:
        structured_logger.log_error(
            error_type="VALIDATION_ERROR",
            error_message=str(e),
            essay_type=grading_request.essay_type.value,
            essay_length=len(grading_request.essay_text)
        )
        error_response = GradingErrorResponse(
            error="VALIDATION_ERROR",
            message=str(e),
            details={"essay_type": grading_request.essay_type.value}
        )
        raise HTTPException(status_code=400, detail=error_response.dict())
        
    except ProcessingError as e:
        structured_logger.log_error(
            error_type="PROCESSING_ERROR",
            error_message=str(e),
            essay_type=grading_request.essay_type.value,
            essay_length=len(grading_request.essay_text)
        )
        error_response = GradingErrorResponse(
            error="PROCESSING_ERROR", 
            message=str(e),
            details={"essay_type": grading_request.essay_type.value}
        )
        raise HTTPException(status_code=422, detail=error_response.dict())
        
    except APIError as e:
        structured_logger.log_error(
            error_type="API_ERROR",
            error_message=str(e),
            essay_type=grading_request.essay_type.value,
            essay_length=len(grading_request.essay_text)
        )
        error_response = GradingErrorResponse(
            error="API_ERROR",
            message=str(e),
            details={"essay_type": grading_request.essay_type.value}
        )
        raise HTTPException(status_code=500, detail=error_response.dict())
        
    except Exception as e:
        structured_logger.log_error(
            error_type="INTERNAL_ERROR",
            error_message=str(e),
            essay_type=grading_request.essay_type.value,
            essay_length=len(grading_request.essay_text),
            unexpected=True
        )
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
        # Check if API coordinator can be resolved
        service_locator = get_service_locator()
        api_coordinator = service_locator.get_api_coordinator()
        
        return {
            "status": "operational",
            "services": {
                "api_coordinator": "available",
                "essay_processor": "available", 
                "prompt_generator": "available",
                "response_processor": "available"
            },
            "supported_essay_types": ["DBQ", "LEQ", "SAQ"],
            "mode": "mock_ai"  # Will change to "production" in Phase 2
        }
        
    except Exception as e:
        logger.error(f"Service status check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
            "services": {
                "api_coordinator": "unavailable"
            }
        }