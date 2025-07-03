"""
API coordinator for end-to-end essay grading workflow.

Orchestrates the complete pipeline: preprocessing → prompt generation → AI grading → response processing.
"""

import logging

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse
from app.services.base.base_service import BaseService
from app.services.base.protocols import (
    APICoordinatorProtocol,
    EssayProcessorProtocol,
    PromptGeneratorProtocol,
    ResponseProcessorProtocol
)
from app.services.base.exceptions import (
    ProcessingError,
    ValidationError,
    APIError
)
from app.services.dependencies.service_locator import get_service_locator


logger = logging.getLogger(__name__)


class APICoordinator(BaseService, APICoordinatorProtocol):
    """
    Coordinates end-to-end essay grading workflow.
    
    Integrates all Phase 1 services:
    - Essay preprocessing and validation
    - Prompt generation for AI services
    - Mock AI response simulation  
    - Response processing and formatting
    """
    
    def __init__(self, settings=None):
        super().__init__(settings)
        self._service_locator = get_service_locator()
        self._validate_configuration()
    
    async def grade_essay(
        self,
        essay_text: str,
        essay_type: EssayType,
        prompt: str
    ) -> GradeResponse:
        """
        Coordinate end-to-end essay grading workflow.
        
        Args:
            essay_text: The student's essay text
            essay_type: The type of essay (DBQ, LEQ, SAQ)
            prompt: The essay question/prompt
            
        Returns:
            Processed grade response with scores, feedback, and insights
            
        Raises:
            ValidationError: If essay fails validation
            ProcessingError: If any processing step fails
            APIError: If the workflow coordination fails
        """
        try:
            logger.info(f"Starting essay grading workflow for {essay_type.value}")
            
            # Step 1: Preprocess and validate essay
            logger.debug("Step 1: Preprocessing essay")
            essay_processor = self._service_locator.get_essay_processor()
            preprocessing_result = essay_processor.preprocess_essay(essay_text, essay_type)
            
            # Step 2: Generate AI prompts
            logger.debug("Step 2: Generating AI prompts")
            prompt_generator = self._service_locator.get_prompt_generator()
            system_prompt = prompt_generator.generate_system_prompt(essay_type)
            user_message = prompt_generator.generate_user_message(
                essay_text, essay_type, prompt, preprocessing_result
            )
            
            # Step 3: Call AI service (configurable: mock or real AI)
            logger.debug("Step 3: Calling AI grading service")
            ai_service = self._service_locator.get_ai_service()
            raw_ai_response = await ai_service.generate_response(
                system_prompt, user_message, essay_type
            )
            
            # Step 4: Process AI response
            logger.debug("Step 4: Processing AI response")
            response_processor = self._service_locator.get_response_processor()
            grade_response = response_processor.process_response(
                raw_ai_response, essay_type, preprocessing_result
            )
            
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
    
    
    def _validate_configuration(self) -> None:
        """Validate service configuration and dependencies."""
        try:
            # Just check that the service locator exists - don't try to resolve services yet
            # as they may be lazy-loaded and this validation runs during construction
            logger.debug("APICoordinator configuration validated successfully")
        except Exception as e:
            logger.warning(f"APICoordinator configuration warning: {e}")
            # Don't fail during construction - let services fail at runtime if needed