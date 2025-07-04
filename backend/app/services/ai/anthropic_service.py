"""
Anthropic AI service for real Claude 3.5 Sonnet integration.

Provides real AI grading responses using Anthropic's Claude API.
"""

import logging
import time
from typing import Dict, Any

from anthropic import Anthropic

from app.models.core.essay_types import EssayType
from app.services.ai.base import AIService
from app.services.base.exceptions import ProcessingError, ValidationError
from app.services.logging.structured_logger import get_logger


logger = logging.getLogger(__name__)
structured_logger = get_logger(__name__)


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
            structured_logger.info(
                "Starting Anthropic API call",
                essay_type=essay_type.value,
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.3
            )
            
            start_time = time.time()
            
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
            
            # Calculate API call duration
            api_duration_ms = (time.time() - start_time) * 1000
            
            # Extract response content
            response_content = message.content[0].text
            
            # Log successful API call with structured data
            structured_logger.log_ai_service_call(
                service_type="anthropic",
                duration_ms=api_duration_ms,
                success=True,
                essay_type=essay_type.value,
                response_length=len(response_content),
                model="claude-3-5-sonnet-20241022"
            )
            
            return response_content
            
        except Exception as e:
            # Calculate duration for failed call
            api_duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            
            # Log failed API call
            structured_logger.log_ai_service_call(
                service_type="anthropic",
                duration_ms=api_duration_ms,
                success=False,
                essay_type=essay_type.value,
                error_message=str(e),
                model="claude-3-5-sonnet-20241022"
            )
            
            raise ProcessingError(f"Anthropic AI service failed: {str(e)}")
    
    def _validate_configuration(self) -> None:
        """Validate Anthropic service configuration."""
        if not self.settings.anthropic_api_key:
            raise ValidationError("Anthropic API key is required but not configured")
        
        logger.debug("AnthropicService configuration validated successfully")