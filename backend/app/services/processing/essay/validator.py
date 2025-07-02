"""Essay validation service for length and structure validation"""

from typing import Optional
from app.config.settings import Settings
from app.models.core.essay_types import EssayType
from app.services.base.base_service import BaseEssayService
from app.services.base.protocols import EssayValidatorProtocol
from app.services.base.exceptions import EssayTooShortError, EssayTooLongError


class EssayValidator(BaseEssayService):
    """Service for validating essay length and structure requirements"""
    
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)
        self._initialize_thresholds()
    
    def _initialize_thresholds(self) -> None:
        """Initialize validation thresholds matching Swift implementation"""
        # Critical minimum thresholds (half of target word counts)
        self._min_word_counts = {
            EssayType.DBQ: 200,  # Half of 400 target
            EssayType.LEQ: 150,  # Half of 300 target
            EssayType.SAQ: 25    # Half of 50 target
        }
        
        # Maximum word limits
        self._max_word_counts = {
            EssayType.DBQ: 2400,
            EssayType.LEQ: 2000,
            EssayType.SAQ: 600
        }
    
    def validate_essay(self, text: str, essay_type: EssayType) -> None:
        """
        Validate essay text and raise exceptions if invalid
        
        Args:
            text: Essay text to validate
            essay_type: Type of essay (DBQ, LEQ, SAQ)
            
        Raises:
            EssayTooShortError: If essay is below minimum threshold
            EssayTooLongError: If essay exceeds maximum limit
            ValueError: If input parameters are invalid
        """
        self._validate_essay_input(text, essay_type)
        
        self._safe_execute(
            self._validate_essay_impl,
            "essay validation",
            text, essay_type
        )
    
    def _validate_essay_impl(self, text: str, essay_type: EssayType) -> None:
        """Internal implementation of essay validation"""
        # Check for empty text
        if not text or not text.strip():
            raise EssayTooShortError(
                "Essay cannot be empty",
                word_count=0,
                essay_type=essay_type.value
            )
        
        # Get word count using text analyzer
        from app.services.dependencies.service_locator import get_service_locator
        from app.services.base.protocols import TextAnalyzerProtocol
        
        locator = get_service_locator()
        analyzer = locator.get(TextAnalyzerProtocol)
        
        word_count = analyzer.count_words(text)
        
        # Check minimum threshold
        min_threshold = self._min_word_counts[essay_type]
        if word_count < min_threshold:
            raise EssayTooShortError(
                f"Essay is too short ({word_count} words). Minimum {min_threshold} words required for {essay_type.value}.",
                word_count=word_count,
                essay_type=essay_type.value
            )
        
        # Check maximum limit
        max_limit = self._max_word_counts[essay_type]
        if word_count > max_limit:
            raise EssayTooLongError(
                f"Essay is too long ({word_count} words). Maximum {max_limit} words allowed for {essay_type.value}.",
                word_count=word_count,
                essay_type=essay_type.value
            )
        
        self._log_operation("essay validation passed",
                          word_count=word_count,
                          essay_type=essay_type.value,
                          min_threshold=min_threshold,
                          max_limit=max_limit)
    
    def get_max_word_count(self, essay_type: EssayType) -> int:
        """
        Get maximum word count for essay type
        
        Args:
            essay_type: Type of essay
            
        Returns:
            Maximum word count allowed
        """
        return self._max_word_counts[essay_type]
    
    def get_min_word_count(self, essay_type: EssayType) -> int:
        """
        Get minimum word count for essay type
        
        Args:
            essay_type: Type of essay
            
        Returns:
            Minimum word count required
        """
        return self._min_word_counts[essay_type]
    
    def is_valid_length(self, text: str, essay_type: EssayType) -> bool:
        """
        Check if essay length is valid without raising exceptions
        
        Args:
            text: Essay text to check
            essay_type: Type of essay
            
        Returns:
            True if length is valid, False otherwise
        """
        try:
            self.validate_essay(text, essay_type)
            return True
        except (EssayTooShortError, EssayTooLongError):
            return False
    
    def get_validation_info(self, text: str, essay_type: EssayType) -> dict:
        """
        Get comprehensive validation information without raising exceptions
        
        Args:
            text: Essay text to analyze
            essay_type: Type of essay
            
        Returns:
            Dictionary with validation details
        """
        try:
            # Get word count
            from app.services.dependencies.service_locator import get_service_locator
            from app.services.base.protocols import TextAnalyzerProtocol
            
            locator = get_service_locator()
            analyzer = locator.get(TextAnalyzerProtocol)
            word_count = analyzer.count_words(text) if text else 0
            
            min_threshold = self._min_word_counts[essay_type]
            max_limit = self._max_word_counts[essay_type]
            
            # Determine status
            if word_count == 0:
                status = "empty"
                message = "Essay is empty"
            elif word_count < min_threshold:
                status = "too_short"
                message = f"Too short ({word_count} words). Minimum: {min_threshold}"
            elif word_count > max_limit:
                status = "too_long"
                message = f"Too long ({word_count} words). Maximum: {max_limit}"
            else:
                status = "valid"
                message = f"Valid length ({word_count} words)"
            
            return {
                "is_valid": status == "valid",
                "status": status,
                "message": message,
                "word_count": word_count,
                "min_required": min_threshold,
                "max_allowed": max_limit,
                "essay_type": essay_type.value
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "status": "error",
                "message": f"Validation error: {e}",
                "word_count": 0,
                "min_required": self._min_word_counts.get(essay_type, 0),
                "max_allowed": self._max_word_counts.get(essay_type, 0),
                "essay_type": essay_type.value if essay_type else "unknown"
            }
    
    def check_quick_validation(self, word_count: int, essay_type: EssayType) -> dict:
        """
        Quick validation check using word count only
        
        Args:
            word_count: Number of words
            essay_type: Type of essay
            
        Returns:
            Dictionary with validation status
        """
        min_threshold = self._min_word_counts[essay_type]
        max_limit = self._max_word_counts[essay_type]
        
        if word_count < min_threshold:
            return {
                "is_valid": False,
                "status": "too_short",
                "message": f"Below minimum threshold ({word_count} < {min_threshold})"
            }
        elif word_count > max_limit:
            return {
                "is_valid": False,
                "status": "too_long", 
                "message": f"Exceeds maximum limit ({word_count} > {max_limit})"
            }
        else:
            return {
                "is_valid": True,
                "status": "valid",
                "message": f"Valid word count ({word_count})"
            }


# Register implementation
EssayValidatorProtocol.register(EssayValidator)