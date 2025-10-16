"""
Anthropic AI service for real Claude Sonnet 4 integration.

Provides real AI grading responses using Anthropic's Claude API.
"""

import logging
import time
from typing import Dict, Any, List

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

    async def generate_response_with_vision(
        self,
        system_prompt: str,
        user_message: str,
        documents: List[Dict],
        essay_type: EssayType,
        enable_caching: bool = True
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate AI response with vision support for document images.

        Uses Anthropic prompt caching to cache documents across multiple grading requests,
        reducing costs by ~90% when grading multiple essays with the same documents.

        Args:
            system_prompt: System prompt with grading instructions
            user_message: User message with essay content
            documents: List of document metadata (doc_num, base64, size_bytes)
            essay_type: Type of essay being graded
            enable_caching: Whether to enable prompt caching (default: True)

        Returns:
            Tuple of (AI response as JSON string, cache usage metrics dict)

        Raises:
            ProcessingError: If the AI service fails
            ValidationError: If configuration is invalid
        """
        if not self.client:
            raise ValidationError("Anthropic client not initialized - check API key configuration")

        try:
            logger.info(f"Starting Anthropic Vision API call for {essay_type.value} with {len(documents)} documents (caching: {enable_caching})")

            start_time = time.time()

            # Build content array with images and text
            content = []

            # Add all documents with labels
            for i, doc in enumerate(documents):
                is_last_doc = (i == len(documents) - 1)

                # Add document label
                content.append({
                    "type": "text",
                    "text": f"Document {doc['doc_num']}:"
                })

                # Add document image with cache control on last document
                image_block = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": doc["base64"]
                    }
                }

                # Mark last document for caching to cache all documents
                if is_last_doc and enable_caching:
                    image_block["cache_control"] = {"type": "ephemeral"}

                content.append(image_block)

            # Add the user message with prompt and essay (NOT cached - changes per request)
            content.append({
                "type": "text",
                "text": user_message
            })

            # Call Claude Sonnet 4 with vision
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            # Calculate API call duration
            api_duration_ms = (time.time() - start_time) * 1000

            # Check for refusal stop reason
            if message.stop_reason == "refusal":
                logger.warning("Claude 4 refused to generate content for safety reasons")
                raise ProcessingError("AI model declined to generate content for safety reasons")

            # Extract response content
            response_content = message.content[0].text

            # Extract cache usage metrics
            cache_metrics = self._extract_cache_metrics(message.usage)

            # Log success with cache metrics
            cache_info = ""
            if cache_metrics["cache_read_tokens"] > 0:
                cache_info = f", cache HIT ({cache_metrics['cache_read_tokens']} tokens)"
            elif cache_metrics["cache_creation_tokens"] > 0:
                cache_info = f", cache MISS (created {cache_metrics['cache_creation_tokens']} tokens)"

            logger.info(
                f"Anthropic Vision API call successful "
                f"({api_duration_ms:.0f}ms, {len(documents)} images, {len(response_content)} chars{cache_info})"
            )

            return response_content, cache_metrics

        except Exception as e:
            # Calculate duration for failed call
            api_duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0

            logger.error(f"Anthropic Vision API call failed ({api_duration_ms}ms): {str(e)}")

            raise ProcessingError(f"Anthropic Vision AI service failed: {str(e)}")

    def _extract_cache_metrics(self, usage) -> Dict[str, int]:
        """
        Extract cache usage metrics from Anthropic API response.

        Prompt caching reduces costs when reusing the same content (documents, rubric)
        across multiple requests. Metrics help track cache performance and cost savings.

        Args:
            usage: Usage object from Anthropic API response

        Returns:
            Dict with cache metrics:
            - input_tokens: Total input tokens
            - cache_creation_tokens: Tokens used to create new cache entries
            - cache_read_tokens: Tokens read from cache (cost savings)
        """
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "cache_creation_tokens": getattr(usage, "cache_creation_input_tokens", 0),
            "cache_read_tokens": getattr(usage, "cache_read_input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
        }

    def _validate_configuration(self) -> None:
        """Validate Anthropic service configuration."""
        if not self.settings.anthropic_api_key:
            raise ValidationError("Anthropic API key is required but not configured")

        logger.debug("AnthropicService configuration validated successfully")