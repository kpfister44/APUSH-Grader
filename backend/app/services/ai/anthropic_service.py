"""
Anthropic AI service for real Claude 3.5 Sonnet integration.

Provides real AI grading responses using Anthropic's Claude API.
"""

import logging
from typing import Dict, Any

from anthropic import Anthropic

from app.models.core.essay_types import EssayType
from app.services.ai.base import AIService
from app.services.base.exceptions import ProcessingError, ValidationError


logger = logging.getLogger(__name__)


class AnthropicService(AIService):
    """
    Anthropic Claude AI service for real essay grading.
    
    Uses Claude 3.5 Sonnet model to provide actual AI grading responses.
    """
    
    def __init__(self, settings=None):
        self.client = None
        super().__init__(settings)
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Anthropic client with API key."""
        if not self.settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            return
        
        try:
            self.client = Anthropic(api_key=self.settings.anthropic_api_key)
            logger.debug("Anthropic client initialized successfully")
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
            logger.debug(f"Calling Anthropic API for {essay_type.value} essay")
            
            # Call Claude 3.5 Sonnet with system prompt and user message
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
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
            
            # Extract response content
            response_content = message.content[0].text
            logger.debug(f"Received response from Anthropic API ({len(response_content)} characters)")
            
            return response_content
            
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise ProcessingError(f"Anthropic AI service failed: {str(e)}")
    
    def _validate_configuration(self) -> None:
        """Validate Anthropic service configuration."""
        if not self.settings.anthropic_api_key:
            raise ValidationError("Anthropic API key is required but not configured")
        
        if not self.client:
            raise ValidationError("Anthropic client failed to initialize")
        
        logger.debug("AnthropicService configuration validated successfully")