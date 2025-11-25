"""
Mock AI service for testing and development.

Provides realistic mock responses for all essay types without external API calls.
"""

import logging
import asyncio
from typing import Dict, Any, List

from pydantic import BaseModel

from app.models.core import EssayType, RubricType
from app.models.structured_outputs import get_output_schema_for_essay
from app.services.ai.base import AIService
from app.exceptions import ProcessingError


logger = logging.getLogger(__name__)


class MockAIService(AIService):
    """
    Mock AI service that generates realistic responses for testing.
    
    Provides consistent, realistic mock responses for all essay types
    without requiring external API calls or API keys.
    """
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        essay_type: EssayType,
        rubric_type: RubricType = RubricType.COLLEGE_BOARD
    ) -> BaseModel:
        """
        Generate mock Structured Output response for essay grading.

        Returns Pydantic models matching Structured Output schemas instead of JSON strings.

        Args:
            system_prompt: System prompt with grading instructions (not used in mock)
            user_message: User message with essay content (not used in mock)
            essay_type: Type of essay being graded
            rubric_type: Rubric type (only used for SAQ essays)

        Returns:
            Parsed Pydantic model (DBQGradeOutput, LEQGradeOutput, etc.)

        Raises:
            ProcessingError: If unknown essay type
        """
        logger.debug(f"Generating mock Structured Output for {essay_type.value}")

        # Get appropriate output schema
        output_schema = get_output_schema_for_essay(
            essay_type.value,
            rubric_type.value if essay_type == EssayType.SAQ else "college_board"
        )

        # Generate mock response data based on essay type
        if essay_type == EssayType.DBQ:
            mock_data = self._generate_mock_dbq_data()
        elif essay_type == EssayType.LEQ:
            mock_data = self._generate_mock_leq_data()
        elif essay_type == EssayType.SAQ:
            if rubric_type == RubricType.EG:
                mock_data = self._generate_mock_saq_eg_data()
            else:
                mock_data = self._generate_mock_saq_data()
        else:
            raise ProcessingError(f"Unknown essay type for mock response: {essay_type}")

        # Simulate AI processing delay
        await asyncio.sleep(0.1)

        # Return as parsed Pydantic model (simulates Structured Output)
        return output_schema(**mock_data)
    
    def _generate_mock_dbq_data(self) -> Dict[str, Any]:
        """Generate realistic mock DBQ response data."""
        return {
            "score": 4,
            "max_score": 6,
            "letter_grade": "C",
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
            "overall_feedback": "Solid essay with clear thesis and good evidence use. Strengthen contextualization and add more sophisticated analysis for higher score.",
            "suggestions": [
                "Provide broader historical context in introduction",
                "Analyze document perspective and purpose more thoroughly",
                "Connect evidence to argument more explicitly"
            ]
        }
    
    def _generate_mock_leq_data(self) -> Dict[str, Any]:
        """Generate realistic mock LEQ response data."""
        return {
            "score": 5,
            "max_score": 6,
            "letter_grade": "B",
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
            "overall_feedback": "Very strong essay with clear argument and excellent evidence. Minor improvements in analysis complexity needed for top score.",
            "suggestions": [
                "Add more sophisticated historical reasoning",
                "Consider multiple perspectives on the topic",
                "Strengthen conclusion with broader implications"
            ]
        }
    
    def _generate_mock_saq_data(self) -> Dict[str, Any]:
        """Generate realistic mock SAQ response data."""
        return {
            "score": 2,
            "max_score": 3,
            "letter_grade": "C",
            "breakdown": {
                "part_a": {
                    "score": 1,
                    "max_score": 1,
                    "feedback": "Correctly identifies the historical development."
                },
                "part_b": {
                    "score": 1,
                    "max_score": 1,
                    "feedback": "Good explanation with supporting evidence."
                },
                "part_c": {
                    "score": 0,
                    "max_score": 1,
                    "feedback": "Explanation lacks sufficient detail about significance."
                }
            },
            "overall_feedback": "Good responses to parts A and B. Part C needs more detailed explanation of significance.",
            "suggestions": [
                "Provide more specific details in part C",
                "Explain the broader historical significance",
                "Connect to larger historical themes"
            ]
        }

    def _generate_mock_saq_eg_data(self) -> Dict[str, Any]:
        """Generate realistic mock SAQ EG rubric response data."""
        return {
            "score": 7,
            "max_score": 10,
            "letter_grade": "B",
            "breakdown": {
                "criterion_a": {
                    "score": 1,
                    "max_score": 1,
                    "feedback": "Addresses all parts of prompt in complete sentences."
                },
                "criterion_c": {
                    "score": 2,
                    "max_score": 3,
                    "feedback": "Cites specific evidence from correct time period, but missing one citation."
                },
                "criterion_e": {
                    "score": 4,
                    "max_score": 6,
                    "feedback": "Good explanation of evidence, but could demonstrate deeper historical understanding."
                }
            },
            "overall_feedback": "Solid SAQ response with clear addressing of prompt and good use of evidence. Strengthen explanations to demonstrate deeper historical knowledge.",
            "suggestions": [
                "Provide more specific evidence for part B",
                "Explain connections to broader historical themes",
                "Demonstrate deeper analysis of historical significance"
            ]
        }

    async def generate_response_with_vision(
        self,
        system_prompt: str,
        user_message: str,
        documents: List[Dict],
        essay_type: EssayType,
        rubric_type: RubricType = RubricType.COLLEGE_BOARD,
        enable_caching: bool = True
    ) -> tuple[BaseModel, Dict[str, Any]]:
        """
        Generate mock Structured Output with vision support (for testing).

        Args:
            system_prompt: System prompt with grading instructions (not used in mock)
            user_message: User message with essay content (not used in mock)
            documents: List of document metadata (not used in mock)
            essay_type: Type of essay being graded
            rubric_type: Rubric type (only used for SAQ essays)
            enable_caching: Whether to enable prompt caching (not used in mock)

        Returns:
            Tuple of (Parsed Pydantic model, mock cache metrics dict)

        Raises:
            ProcessingError: If unknown essay type
        """
        logger.debug(
            f"Generating mock vision Structured Output for {essay_type.value} "
            f"with {len(documents)} documents (caching: {enable_caching})"
        )

        # For mock, return the same Structured Output as non-vision plus mock cache metrics
        response = await self.generate_response(system_prompt, user_message, essay_type, rubric_type)

        # Mock cache metrics (simulates cache miss on first call, hit on subsequent)
        mock_cache_metrics = {
            "input_tokens": 5000,
            "cache_creation_tokens": 4500 if enable_caching else 0,
            "cache_read_tokens": 0,  # First call is always cache miss
            "output_tokens": 500,
        }

        return response, mock_cache_metrics

    def _validate_configuration(self) -> None:
        """Validate mock AI service configuration (no validation needed)."""
        logger.debug("MockAIService configuration validated successfully")
        pass