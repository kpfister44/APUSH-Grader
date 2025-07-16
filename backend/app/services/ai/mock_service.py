"""
Mock AI service for testing and development.

Provides realistic mock responses for all essay types without external API calls.
"""

import json
import logging
import asyncio
from typing import Dict, Any

from app.models.core import EssayType
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
        essay_type: EssayType
    ) -> str:
        """
        Generate mock AI response for essay grading.
        
        Args:
            system_prompt: System prompt with grading instructions (not used in mock)
            user_message: User message with essay content (not used in mock)
            essay_type: Type of essay being graded
            
        Returns:
            Mock AI response as JSON string
            
        Raises:
            ProcessingError: If unknown essay type
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
        await asyncio.sleep(0.1)
        
        return json.dumps(mock_response, indent=2)
    
    def _generate_mock_dbq_response(self) -> Dict[str, Any]:
        """Generate realistic mock DBQ response."""
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
    
    def _generate_mock_leq_response(self) -> Dict[str, Any]:
        """Generate realistic mock LEQ response."""
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
    
    def _generate_mock_saq_response(self) -> Dict[str, Any]:
        """Generate realistic mock SAQ response."""
        return {
            "score": 2,
            "max_score": 3,
            "letter_grade": "C",
            "breakdown": {
                "part_a": {
                    "score": 1,
                    "maxScore": 1,
                    "feedback": "Correctly identifies the historical development."
                },
                "part_b": {
                    "score": 1,
                    "maxScore": 1,
                    "feedback": "Good explanation with supporting evidence."
                },
                "part_c": {
                    "score": 0,
                    "maxScore": 1,
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
    
    def _validate_configuration(self) -> None:
        """Validate mock AI service configuration (no validation needed)."""
        logger.debug("MockAIService configuration validated successfully")
        pass