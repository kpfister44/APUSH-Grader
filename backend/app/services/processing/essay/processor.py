"""Essay processor service - main coordinator for essay processing"""

from typing import Optional
from app.config.settings import Settings
from app.models.core.essay_types import EssayType
from app.models.processing.preprocessing import PreprocessingResult
from app.services.base.base_service import BaseEssayService
from app.services.base.protocols import (
    EssayProcessorProtocol, 
    EssayValidatorProtocol,
    TextAnalyzerProtocol
)
from app.services.base.exceptions import GradingError


class EssayProcessor(BaseEssayService):
    """Main coordinator service for essay preprocessing and validation"""
    
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)
    
    def preprocess_essay(self, text: str, essay_type: EssayType) -> PreprocessingResult:
        """
        Preprocess essay text and return analysis result
        
        Args:
            text: Raw essay text
            essay_type: Type of essay (DBQ, LEQ, SAQ)
            
        Returns:
            PreprocessingResult with cleaned text and analysis
        """
        self._validate_essay_input(text, essay_type)
        
        return self._safe_execute(
            self._preprocess_essay_impl,
            "essay preprocessing",
            text, essay_type
        )
    
    def _preprocess_essay_impl(self, text: str, essay_type: EssayType) -> PreprocessingResult:
        """Internal implementation of essay preprocessing"""
        # Get required services
        from app.services.dependencies.service_locator import get_service_locator
        locator = get_service_locator()
        
        try:
            text_analyzer = locator.get(TextAnalyzerProtocol)
        except Exception as e:
            raise GradingError(f"Failed to get text analysis service: {e}")
        
        # Perform text analysis (includes cleaning and warning generation)
        result = text_analyzer.analyze_text(text, essay_type)
        
        self._log_operation("essay preprocessing completed",
                          original_length=len(text),
                          cleaned_length=len(result.cleaned_text),
                          word_count=result.word_count,
                          paragraph_count=result.paragraph_count,
                          warning_count=len(result.warnings),
                          is_valid=result.is_valid,
                          essay_type=essay_type.value)
        
        return result
    
    def validate_essay(self, text: str, essay_type: EssayType) -> None:
        """
        Validate essay text and raise exceptions if invalid
        
        Args:
            text: Essay text to validate
            essay_type: Type of essay
            
        Raises:
            EssayTooShortError: If essay is too short
            EssayTooLongError: If essay is too long
            ValueError: If invalid input parameters
        """
        self._validate_essay_input(text, essay_type)
        
        self._safe_execute(
            self._validate_essay_impl,
            "essay validation",
            text, essay_type
        )
    
    def _validate_essay_impl(self, text: str, essay_type: EssayType) -> None:
        """Internal implementation of essay validation"""
        # Get essay validator service
        from app.services.dependencies.service_locator import get_service_locator
        locator = get_service_locator()
        
        try:
            validator = locator.get(EssayValidatorProtocol)
        except Exception as e:
            raise GradingError(f"Failed to get validation service: {e}")
        
        # Perform validation (will raise exceptions if invalid)
        validator.validate_essay(text, essay_type)
        
        self._log_operation("essay validation completed",
                          essay_type=essay_type.value)
    
    def process_and_validate(self, text: str, essay_type: EssayType) -> PreprocessingResult:
        """
        Combined preprocessing and validation workflow
        
        Args:
            text: Essay text to process
            essay_type: Type of essay
            
        Returns:
            PreprocessingResult if validation passes
            
        Raises:
            EssayTooShortError: If essay is too short
            EssayTooLongError: If essay is too long
        """
        self._validate_essay_input(text, essay_type)
        
        # First validate the essay
        self.validate_essay(text, essay_type)
        
        # Then preprocess if validation passes
        result = self.preprocess_essay(text, essay_type)
        
        self._log_operation("combined processing completed",
                          is_valid=result.is_valid,
                          has_critical_warnings=result.has_critical_warnings,
                          essay_type=essay_type.value)
        
        return result
    
    def get_processing_info(self, text: str, essay_type: EssayType) -> dict:
        """
        Get comprehensive processing information without raising exceptions
        
        Args:
            text: Essay text to analyze
            essay_type: Type of essay
            
        Returns:
            Dictionary with processing details and any errors
        """
        try:
            # Try to preprocess
            result = self.preprocess_essay(text, essay_type)
            
            # Try to validate
            validation_passed = True
            validation_error = None
            try:
                self.validate_essay(text, essay_type)
            except Exception as e:
                validation_passed = False
                validation_error = str(e)
            
            return {
                "success": True,
                "validation_passed": validation_passed,
                "validation_error": validation_error,
                "preprocessing_result": {
                    "word_count": result.word_count,
                    "paragraph_count": result.paragraph_count,
                    "is_valid": result.is_valid,
                    "has_warnings": result.has_warnings,
                    "has_critical_warnings": result.has_critical_warnings,
                    "warning_count": result.warning_count,
                    "warnings": result.warnings
                },
                "essay_type": essay_type.value
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "validation_passed": False,
                "validation_error": f"Processing failed: {e}",
                "preprocessing_result": None,
                "essay_type": essay_type.value if essay_type else "unknown"
            }
    
    def preview_processing(self, text: str, essay_type: EssayType, max_preview: int = 200) -> dict:
        """
        Preview processing results with text samples
        
        Args:
            text: Essay text to preview
            essay_type: Type of essay  
            max_preview: Maximum characters to include in preview
            
        Returns:
            Dictionary with preview information
        """
        try:
            result = self.preprocess_essay(text, essay_type)
            
            return {
                "original_preview": text[:max_preview] + "..." if len(text) > max_preview else text,
                "cleaned_preview": result.cleaned_text[:max_preview] + "..." if len(result.cleaned_text) > max_preview else result.cleaned_text,
                "statistics": {
                    "original_length": len(text),
                    "cleaned_length": len(result.cleaned_text),
                    "word_count": result.word_count,
                    "paragraph_count": result.paragraph_count
                },
                "warnings": result.warnings[:5],  # First 5 warnings
                "total_warnings": len(result.warnings),
                "is_valid": result.is_valid,
                "essay_type": essay_type.value
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "original_preview": text[:max_preview] + "..." if len(text) > max_preview else text,
                "essay_type": essay_type.value if essay_type else "unknown"
            }


# Register implementation
EssayProcessorProtocol.register(EssayProcessor)