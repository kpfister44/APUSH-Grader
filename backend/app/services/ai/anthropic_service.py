"""
Anthropic AI service for real Claude Sonnet 4 integration.

Provides real AI grading responses using Anthropic's Claude API.
"""

import logging
import time
from typing import Dict, Any, List

from anthropic import Anthropic
import anthropic
from pydantic import BaseModel

from app.models.core import EssayType, RubricType
from app.models.structured_outputs import get_output_schema_for_essay
from app.services.ai.base import AIService
from app.exceptions import ProcessingError, ValidationError
logger = logging.getLogger(__name__)

# DIAGNOSTIC: Log anthropic version at import
logger.warning(f"🔍 DIAGNOSTIC: anthropic SDK version: {anthropic.__version__}")


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

            # DIAGNOSTIC: Check if client has beta.messages.parse
            has_beta = hasattr(self.client, 'beta')
            logger.warning(f"🔍 DIAGNOSTIC: client.beta exists: {has_beta}")
            if has_beta:
                has_messages = hasattr(self.client.beta, 'messages')
                logger.warning(f"🔍 DIAGNOSTIC: client.beta.messages exists: {has_messages}")
                if has_messages:
                    has_parse = hasattr(self.client.beta.messages, 'parse')
                    logger.warning(f"🔍 DIAGNOSTIC: client.beta.messages.parse exists: {has_parse}")
                    if not has_parse:
                        logger.error(f"🔍 DIAGNOSTIC: Available methods: {dir(self.client.beta.messages)}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise ValidationError(f"Anthropic client initialization failed: {e}")
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        essay_type: EssayType,
        rubric_type: RubricType = RubricType.COLLEGE_BOARD
    ) -> BaseModel:
        """
        Generate AI response using Anthropic Structured Outputs.

        Uses Claude Sonnet 4.5 with Structured Outputs beta to guarantee
        schema-compliant responses via constrained decoding.

        Args:
            system_prompt: System prompt with grading instructions
            user_message: User message with essay content
            essay_type: Type of essay being graded
            rubric_type: Rubric type (only used for SAQ essays)

        Returns:
            Parsed Pydantic model (DBQGradeOutput, LEQGradeOutput, etc.)
            matching the essay/rubric type

        Raises:
            ProcessingError: If the AI service fails
            ValidationError: If configuration is invalid
        """
        if not self.client:
            raise ValidationError("Anthropic client not initialized - check API key configuration")

        try:
            logger.info(f"Starting Anthropic Structured Outputs API call for {essay_type.value} essay")

            start_time = time.time()

            # Get appropriate output schema for this essay/rubric type
            output_schema = get_output_schema_for_essay(
                essay_type.value,
                rubric_type.value if essay_type == EssayType.SAQ else "college_board"
            )

            logger.debug(f"Using Structured Output schema: {output_schema.__name__}")

            # Structured Outputs (beta) - guarantees schema compliance
            # First request compiles grammar (~2-3s), then cached 24h
            message = self.client.beta.messages.parse(
                model="claude-sonnet-4-5-20250929",
                betas=["structured-outputs-2025-11-13"],
                max_tokens=1500,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                output_format=output_schema
            )

            # Calculate API call duration
            api_duration_ms = (time.time() - start_time) * 1000

            # Check for refusal stop reason (safety refusal may not match schema)
            if message.stop_reason == "refusal":
                logger.warning("Claude 4 refused to generate content for safety reasons")
                raise ProcessingError("AI model declined to generate content for safety reasons")

            # Extract parsed response (already validated Pydantic model)
            parsed_response = message.content

            # Log detailed metrics for Structured Outputs
            logger.info(
                f"Anthropic Structured Outputs API call successful "
                f"({api_duration_ms:.0f}ms, schema={output_schema.__name__}, "
                f"score={parsed_response.score}/{parsed_response.max_score})"
            )

            # Log grammar compilation metrics (first request will have latency)
            # Note: Anthropic caches compiled grammars for 24 hours
            if api_duration_ms > 3000:  # >3s suggests grammar compilation
                logger.info(
                    f"Structured Output grammar compilation detected "
                    f"(latency: {api_duration_ms:.0f}ms) - subsequent requests will be cached"
                )

            return parsed_response

        except Exception as e:
            # Calculate duration for failed call
            api_duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0

            logger.error(f"Anthropic Structured Outputs API call failed ({api_duration_ms:.0f}ms): {str(e)}")

            raise ProcessingError(f"Anthropic AI service failed: {str(e)}")

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
        Generate AI response with vision support using Structured Outputs.

        Uses Anthropic prompt caching + Structured Outputs for DBQ grading with
        document images. Caching reduces costs by ~90% when grading multiple essays.

        Args:
            system_prompt: System prompt with grading instructions
            user_message: User message with essay content
            documents: List of document metadata (doc_num, base64, size_bytes)
            essay_type: Type of essay being graded
            rubric_type: Rubric type (only used for SAQ essays)
            enable_caching: Whether to enable prompt caching (default: True)

        Returns:
            Tuple of (Parsed Pydantic model, cache usage metrics dict)

        Raises:
            ProcessingError: If the AI service fails
            ValidationError: If configuration is invalid
        """
        if not self.client:
            raise ValidationError("Anthropic client not initialized - check API key configuration")

        try:
            logger.info(
                f"Starting Anthropic Vision + Structured Outputs API call for {essay_type.value} "
                f"with {len(documents)} documents (caching: {enable_caching})"
            )

            start_time = time.time()

            # Get appropriate output schema for this essay/rubric type
            output_schema = get_output_schema_for_essay(
                essay_type.value,
                rubric_type.value if essay_type == EssayType.SAQ else "college_board"
            )

            logger.debug(f"Using Structured Output schema: {output_schema.__name__}")

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

            # Structured Outputs (beta) - guarantees schema compliance
            # First request compiles grammar (~2-3s), then cached 24h
            message = self.client.beta.messages.parse(
                model="claude-sonnet-4-5-20250929",
                betas=["structured-outputs-2025-11-13"],
                max_tokens=1500,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                output_format=output_schema
            )

            # Calculate API call duration
            api_duration_ms = (time.time() - start_time) * 1000

            # Check for refusal stop reason
            if message.stop_reason == "refusal":
                logger.warning("Claude 4 refused to generate content for safety reasons")
                raise ProcessingError("AI model declined to generate content for safety reasons")

            # Extract parsed response (already validated Pydantic model)
            parsed_response = message.content

            # Extract cache usage metrics
            cache_metrics = self._extract_cache_metrics(message.usage)

            # Log success with cache metrics and Structured Outputs info
            cache_info = ""
            if cache_metrics["cache_read_tokens"] > 0:
                cache_info = f", cache HIT ({cache_metrics['cache_read_tokens']} tokens)"
            elif cache_metrics["cache_creation_tokens"] > 0:
                cache_info = f", cache MISS (created {cache_metrics['cache_creation_tokens']} tokens)"

            logger.info(
                f"Anthropic Vision + Structured Outputs API call successful "
                f"({api_duration_ms:.0f}ms, {len(documents)} images, "
                f"schema={output_schema.__name__}, score={parsed_response.score}/{parsed_response.max_score}{cache_info})"
            )

            # Log grammar compilation metrics for vision calls
            if api_duration_ms > 3000 and cache_metrics["cache_read_tokens"] == 0:
                logger.info(
                    f"Structured Output grammar compilation detected in vision call "
                    f"(latency: {api_duration_ms:.0f}ms) - subsequent requests will be cached"
                )

            return parsed_response, cache_metrics

        except Exception as e:
            # Calculate duration for failed call
            api_duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0

            logger.error(f"Anthropic Vision + Structured Outputs API call failed ({api_duration_ms:.0f}ms): {str(e)}")

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