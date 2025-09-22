"""
Anthropic AI service for real Claude Sonnet 4 integration.

Provides real AI grading responses using Anthropic's Claude API.
"""

import logging
import time
from typing import Dict, Any

from anthropic import Anthropic

from app.models.core import EssayType
from app.services.ai.base import AIService
from app.exceptions import ProcessingError, ValidationError
logger = logging.getLogger(__name__)


class AnthropicService(AIService):
    """
    Anthropic Claude AI service for real essay grading.
    
    Uses Claude Sonnet 4 model to provide actual AI grading responses.
    """
    
    def __init__(self, settings=None):
        self.client = None
        super().__init__(settings)
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Anthropic client with API key."""
        logger.debug(f"Initializing Anthropic client with API key: {self.settings.anthropic_api_key[:20]}...")
        
        if not self.settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            return
        
        try:
            self.client = Anthropic(api_key=self.settings.anthropic_api_key)
            logger.debug(f"Anthropic client initialized successfully: {type(self.client)}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise ValidationError(f"Anthropic client initialization failed: {e}")
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        essay_type: EssayType
    ) -> str:
        """
        Generate real AI response using Anthropic Claude.
        
        Args:
            system_prompt: System prompt with grading instructions
            user_message: User message with essay content
            essay_type: Type of essay being graded
            
        Returns:
            AI response as JSON string
            
        Raises:
            ProcessingError: If the AI service fails
            ValidationError: If configuration is invalid
        """
        if not self.client:
            raise ValidationError("Anthropic client not initialized - check API key configuration")
        
        try:
            logger.info(f"Starting Anthropic API call for {essay_type.value} essay")
            
            start_time = time.time()
            
            # Call Claude Sonnet 4 with system prompt and user message
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            # Calculate API call duration
            api_duration_ms = (time.time() - start_time) * 1000
            
            # Check for refusal stop reason (new in Claude 4)
            if message.stop_reason == "refusal":
                logger.warning("Claude 4 refused to generate content for safety reasons")
                raise ProcessingError("AI model declined to generate content for safety reasons")

            # Extract response content
            response_content = message.content[0].text

            logger.info(f"Anthropic API call successful ({api_duration_ms:.0f}ms, {len(response_content)} chars)")

            return response_content
            
        except Exception as e:
            # Calculate duration for failed call
            api_duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            
            logger.error(f"Anthropic API call failed ({api_duration_ms}ms): {str(e)}")
            
            raise ProcessingError(f"Anthropic AI service failed: {str(e)}")
    
    def _validate_configuration(self) -> None:
        """Validate Anthropic service configuration."""
        if not self.settings.anthropic_api_key:
            raise ValidationError("Anthropic API key is required but not configured")
        
        logger.debug("AnthropicService configuration validated successfully")