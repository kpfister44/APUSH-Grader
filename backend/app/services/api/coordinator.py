"""
API coordinator for end-to-end essay grading workflow.

Orchestrates the complete pipeline: preprocessing → prompt generation → AI grading → response processing.
"""

import json
import logging
from typing import Dict, Any

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
            
            # Step 3: Call mock AI service (Phase 1C-3 uses mock, Phase 2 will use real AI)
            logger.debug("Step 3: Calling AI grading service (mock)")
            raw_ai_response = await self._call_mock_ai_service(
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
    
    async def _call_mock_ai_service(
        self, 
        system_prompt: str,
        user_message: str,
        essay_type: EssayType
    ) -> str:
        """
        Mock AI service call for Phase 1C-3 testing.
        
        In Phase 2, this will be replaced with real OpenAI/Anthropic API calls.
        Returns realistic mock responses that match the expected JSON structure.
        
        Args:
            system_prompt: AI system prompt with grading instructions
            user_message: User message with essay content
            essay_type: Essay type for appropriate mock response
            
        Returns:
            Mock AI response in expected JSON format
        """
        logger.debug(f"Generating mock AI response for {essay_type.value}")
        
        # Generate mock response based on essay type
        if essay_type == EssayType.DBQ:
            mock_response = self._generate_mock_dbq_response()
        elif essay_type == EssayType.LEQ:
            mock_response = self._generate_mock_leq_response()
        elif essay_type == EssayType.SAQ:
            mock_response = self._generate_mock_saq_response()
        else:
            raise ProcessingError(f"Unknown essay type for mock response: {essay_type}")
        
        # Simulate AI processing delay
        import asyncio
        await asyncio.sleep(0.1)
        
        return json.dumps(mock_response, indent=2)
    
    def _generate_mock_dbq_response(self) -> Dict[str, Any]:
        """Generate realistic mock DBQ response."""
        return {
            "score": 4,
            "maxScore": 6,
            "breakdown": {
                "thesis": {
                    "score": 1,
                    "maxScore": 1,
                    "feedback": "Clear thesis with line of reasoning addressing the prompt."
                },
                "contextualization": {
                    "score": 0,
                    "maxScore": 1,
                    "feedback": "Limited contextualization. Need broader historical context."
                },
                "evidence": {
                    "score": 2,
                    "maxScore": 2,
                    "feedback": "Good use of documents and outside evidence to support argument."
                },
                "analysis": {
                    "score": 1,
                    "maxScore": 2,
                    "feedback": "Some document analysis present but lacks complexity."
                }
            },
            "overallFeedback": "Solid essay with clear thesis and good evidence use. Strengthen contextualization and add more sophisticated analysis for higher score.",
            "suggestions": [
                "Provide broader historical context in introduction",
                "Analyze document perspective and purpose more thoroughly",
                "Connect evidence to argument more explicitly"
            ]
        }
    
    def _generate_mock_leq_response(self) -> Dict[str, Any]:
        """Generate realistic mock LEQ response."""
        return {
            "score": 5,
            "maxScore": 6,
            "breakdown": {
                "thesis": {
                    "score": 1,
                    "maxScore": 1,
                    "feedback": "Strong thesis addressing all parts of the prompt."
                },
                "contextualization": {
                    "score": 1,
                    "maxScore": 1,
                    "feedback": "Good contextualization situating argument in broader context."
                },
                "evidence": {
                    "score": 2,
                    "maxScore": 2,
                    "feedback": "Excellent use of specific historical examples."
                },
                "analysis": {
                    "score": 1,
                    "maxScore": 2,
                    "feedback": "Good historical reasoning but could demonstrate more complexity."
                }
            },
            "overallFeedback": "Very strong essay with clear argument and excellent evidence. Minor improvements in analysis complexity needed for top score.",
            "suggestions": [
                "Add more sophisticated historical reasoning",
                "Consider multiple perspectives on the topic",
                "Strengthen conclusion with broader implications"
            ]
        }
    
    def _generate_mock_saq_response(self) -> Dict[str, Any]:
        """Generate realistic mock SAQ response."""
        return {
            "score": 2,
            "maxScore": 3,
            "breakdown": {
                "partA": {
                    "score": 1,
                    "maxScore": 1,
                    "feedback": "Correctly identifies the historical development."
                },
                "partB": {
                    "score": 1,
                    "maxScore": 1,
                    "feedback": "Good explanation with supporting evidence."
                },
                "partC": {
                    "score": 0,
                    "maxScore": 1,
                    "feedback": "Explanation lacks sufficient detail about significance."
                }
            },
            "overallFeedback": "Good responses to parts A and B. Part C needs more detailed explanation of significance.",
            "suggestions": [
                "Provide more specific details in part C",
                "Explain the broader historical significance",
                "Connect to larger historical themes"
            ]
        }
    
    def _validate_configuration(self) -> None:
        """Validate service configuration and dependencies."""
        try:
            # Just check that the service locator exists - don't try to resolve services yet
            # as they may be lazy-loaded and this validation runs during construction
            logger.debug("APICoordinator configuration validated successfully")
        except Exception as e:
            logger.warning(f"APICoordinator configuration warning: {e}")
            # Don't fail during construction - let services fail at runtime if needed