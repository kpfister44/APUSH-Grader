"""Service interfaces and protocols for APUSH Grader"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable, List, Any
from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse
from app.models.processing.preprocessing import PreprocessingResult


@runtime_checkable
class APIServiceProtocol(Protocol):
    """Main API service interface"""
    
    async def grade_essay(
        self, 
        essay: str, 
        essay_type: EssayType, 
        prompt: str
    ) -> GradeResponse:
        """Grade an essay and return the response"""
        ...


@runtime_checkable
class AIProviderProtocol(Protocol):
    """AI provider service interface"""
    
    async def grade_essay(
        self,
        essay: str,
        essay_type: EssayType,
        prompt: str,
        preprocessing_result: PreprocessingResult
    ) -> GradeResponse:
        """Grade essay with preprocessing context"""
        ...


@runtime_checkable
class EssayProcessorProtocol(Protocol):
    """Essay processing service interface"""
    
    def preprocess_essay(self, text: str, essay_type: EssayType) -> PreprocessingResult:
        """Preprocess essay text and return analysis result"""
        ...
    
    def validate_essay(self, text: str, essay_type: EssayType) -> None:
        """Validate essay text (raises exceptions on failure)"""
        ...


@runtime_checkable
class EssayValidatorProtocol(Protocol):
    """Essay validation service interface"""
    
    def validate_essay(self, text: str, essay_type: EssayType) -> None:
        """Validate essay text (raises exceptions on failure)"""
        ...
    
    def get_max_word_count(self, essay_type: EssayType) -> int:
        """Get maximum word count for essay type"""
        ...


@runtime_checkable
class TextAnalyzerProtocol(Protocol):
    """Text analysis service interface"""
    
    def analyze_text(self, text: str, essay_type: EssayType) -> PreprocessingResult:
        """Analyze text and return preprocessing result"""
        ...
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        ...
    
    def count_paragraphs(self, text: str) -> int:
        """Count paragraphs in text"""
        ...
    
    def count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        ...
    
    def get_first_paragraph(self, text: str) -> str:
        """Extract first paragraph for analysis"""
        ...
    
    def contains_thesis_indicators(self, text: str) -> bool:
        """Check if text contains thesis indicators"""
        ...
    
    def contains_evidence_keywords(self, text: str, essay_type: EssayType) -> bool:
        """Check if text contains evidence keywords"""
        ...
    
    def contains_informal_language(self, text: str) -> bool:
        """Check if text contains informal language"""
        ...


@runtime_checkable
class TextCleanerProtocol(Protocol):
    """Text cleaning service interface"""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        ...


@runtime_checkable
class WarningGeneratorProtocol(Protocol):
    """Warning generation service interface"""
    
    def generate_warnings(
        self, 
        text: str, 
        word_count: int, 
        paragraph_count: int, 
        essay_type: EssayType
    ) -> List[str]:
        """Generate warnings for essay structure and content"""
        ...
    
    def get_max_word_count(self, essay_type: EssayType) -> int:
        """Get maximum word count for essay type"""
        ...


@runtime_checkable
class PromptGeneratorProtocol(Protocol):
    """Prompt generation service interface"""
    
    def generate_system_prompt(self, essay_type: EssayType) -> str:
        """Generate system prompt with essay-specific grading instructions"""
        ...
    
    def generate_user_message(
        self,
        essay_text: str,
        essay_type: EssayType, 
        prompt: str,
        preprocessing_result: PreprocessingResult
    ) -> str:
        """Generate user message containing essay content and metadata"""
        ...


@runtime_checkable  
class ResponseProcessorProtocol(Protocol):
    """Response processing service interface"""
    
    def process_response(
        self,
        raw_response: str,
        essay_type: EssayType,
        preprocessing_result: PreprocessingResult
    ) -> GradeResponse:
        """Process AI response into structured grade response"""
        ...
    
    def process_grading_response(
        self,
        response: GradeResponse,
        essay_type: EssayType
    ) -> Any:
        """Process a grading response through validation, formatting, and insights"""
        ...


@runtime_checkable
class APICoordinatorProtocol(Protocol):
    """API coordination service interface"""
    
    async def grade_essay(
        self,
        essay_text: str,
        essay_type: EssayType,
        prompt: str
    ) -> GradeResponse:
        """Coordinate end-to-end essay grading workflow"""
        ...


# Abstract base classes for implementation

class BaseService(ABC):
    """Base class for all services"""
    
    def __init__(self, settings=None):
        from app.config.settings import get_settings
        self.settings = settings or get_settings()
    
    @abstractmethod
    def _validate_configuration(self) -> None:
        """Validate service configuration"""
        pass


class BaseEssayProcessor(BaseService):
    """Base class for essay processing services"""
    
    @abstractmethod
    def process(self, *args, **kwargs):
        """Main processing method"""
        pass