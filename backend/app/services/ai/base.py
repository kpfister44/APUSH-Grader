"""
Base AI service interface for APUSH Grader.

Defines the contract for AI services that can grade essays.
"""

from abc import ABC, abstractmethod
import logging
from typing import Optional
from app.models.core import EssayType
from app.config.settings import Settings, get_settings


class AIService(ABC):
    """
    Abstract base class for AI grading services.
    
    Provides the interface that all AI services (mock, Anthropic, etc.) must implement.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validate_configuration()
    
    @abstractmethod
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        essay_type: EssayType
    ) -> str:
        """
        Generate AI response for essay grading.
        
        Args:
            system_prompt: System prompt with grading instructions
            user_message: User message with essay content
            essay_type: Type of essay being graded
            
        Returns:
            AI response as JSON string
            
        Raises:
            AIServiceError: If the AI service fails
        """
        pass
    
    @abstractmethod
    def _validate_configuration(self) -> None:
        """Validate AI service configuration."""
        pass