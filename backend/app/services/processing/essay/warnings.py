"""Warning generation service for essay analysis"""

from typing import List, Optional
from app.config.settings import Settings
from app.models.core.essay_types import EssayType
from app.services.base.base_service import BaseEssayService
from app.services.base.protocols import WarningGeneratorProtocol


class WarningGenerator(BaseEssayService):
    """Service for generating warnings about essay structure and content"""
    
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)
        self._initialize_thresholds()
    
    def _initialize_thresholds(self) -> None:
        """Initialize warning thresholds for different essay types"""
        # Maximum word counts (from Swift implementation)
        self._max_word_counts = {
            EssayType.DBQ: 2400,
            EssayType.LEQ: 2000,
            EssayType.SAQ: 600
        }
        
        # Minimum word counts for critical warnings (half of targets)
        self._critical_min_counts = {
            EssayType.DBQ: 200,  # Half of 400 target
            EssayType.LEQ: 150,  # Half of 300 target
            EssayType.SAQ: 25    # Half of 50 target
        }
        
        # Target word counts for advisory warnings
        self._target_word_counts = {
            EssayType.DBQ: 400,
            EssayType.LEQ: 300,
            EssayType.SAQ: 50
        }
    
    def generate_warnings(
        self, 
        text: str, 
        word_count: int, 
        paragraph_count: int, 
        essay_type: EssayType
    ) -> List[str]:
        """
        Generate warnings for essay structure and content issues
        
        Args:
            text: Essay text
            word_count: Number of words
            paragraph_count: Number of paragraphs
            essay_type: Type of essay
            
        Returns:
            List of warning messages
        """
        self._validate_essay_input(text, essay_type)
        
        return self._safe_execute(
            self._generate_warnings_impl,
            "warning generation",
            text, word_count, paragraph_count, essay_type
        )
    
    def _generate_warnings_impl(
        self, 
        text: str, 
        word_count: int, 
        paragraph_count: int, 
        essay_type: EssayType
    ) -> List[str]:
        """Internal implementation of warning generation"""
        warnings = []
        
        # Length warnings (critical)
        warnings.extend(self._check_length_warnings(word_count, essay_type))
        
        # Structure warnings (advisory)
        warnings.extend(self._check_structure_warnings(text, paragraph_count, essay_type))
        
        # Content warnings (advisory)
        warnings.extend(self._check_content_warnings(text, essay_type))
        
        # Essay-specific warnings
        warnings.extend(self._check_essay_specific_warnings(text, word_count, essay_type))
        
        self._log_operation("warnings generated",
                          warning_count=len(warnings),
                          word_count=word_count,
                          paragraph_count=paragraph_count,
                          essay_type=essay_type.value)
        
        return warnings
    
    def _check_length_warnings(self, word_count: int, essay_type: EssayType) -> List[str]:
        """Check for length-based warnings (critical warnings)"""
        warnings = []
        
        critical_min = self._critical_min_counts[essay_type]
        max_count = self._max_word_counts[essay_type]
        target_count = self._target_word_counts[essay_type]
        
        # Critical warning - too short
        if word_count < critical_min:
            warnings.append(f"Essay is too short ({word_count} words). Minimum {critical_min} words required for {essay_type.value}.")
        
        # Critical warning - too long
        elif word_count > max_count:
            warnings.append(f"Essay is too long ({word_count} words). Maximum {max_count} words allowed for {essay_type.value}.")
        
        # Advisory warning - below target but above critical
        elif word_count < target_count:
            warnings.append(f"Essay is shorter than recommended ({word_count} words). Target: {target_count}+ words for {essay_type.value}.")
        
        return warnings
    
    def _check_structure_warnings(self, text: str, paragraph_count: int, essay_type: EssayType) -> List[str]:
        """Check for structural warnings (advisory)"""
        warnings = []
        
        # Get text analyzer for content checks
        from app.services.dependencies.service_locator import get_service_locator
        locator = get_service_locator()
        
        try:
            from app.services.base.protocols import TextAnalyzerProtocol
            analyzer = locator.get(TextAnalyzerProtocol)
        except:
            # If analyzer not available, skip content-based structure checks
            analyzer = None
        
        # Paragraph count warnings
        if essay_type in [EssayType.DBQ, EssayType.LEQ]:
            if paragraph_count < 3:
                warnings.append(f"Consider adding more paragraphs. {essay_type.value} essays typically need 4-5 paragraphs (introduction, body paragraphs, conclusion).")
        elif essay_type == EssayType.SAQ:
            if paragraph_count > 3:
                warnings.append("SAQ responses should be concise. Consider consolidating into 1-2 focused paragraphs.")
        
        # Thesis warnings
        if analyzer and not analyzer.contains_thesis_indicators(text):
            if essay_type in [EssayType.DBQ, EssayType.LEQ]:
                warnings.append("Consider including a clear thesis statement with words like 'argue', 'demonstrate', or 'thesis'.")
        
        return warnings
    
    def _check_content_warnings(self, text: str, essay_type: EssayType) -> List[str]:
        """Check for content-related warnings (advisory)"""
        warnings = []
        
        # Get text analyzer for content checks
        from app.services.dependencies.service_locator import get_service_locator
        locator = get_service_locator()
        
        try:
            from app.services.base.protocols import TextAnalyzerProtocol
            analyzer = locator.get(TextAnalyzerProtocol)
        except:
            # If analyzer not available, skip content checks
            return warnings
        
        # Evidence warnings
        if not analyzer.contains_evidence_keywords(text, essay_type):
            if essay_type == EssayType.DBQ:
                warnings.append("Consider including more specific document evidence and historical examples.")
            elif essay_type == EssayType.LEQ:
                warnings.append("Consider including more specific historical evidence and examples.")
            elif essay_type == EssayType.SAQ:
                warnings.append("Consider including specific historical evidence to support your answer.")
        
        # Informal language warnings
        if analyzer.contains_informal_language(text):
            warnings.append("Consider using more formal academic language. Avoid contractions and casual expressions.")
        
        return warnings
    
    def _check_essay_specific_warnings(self, text: str, word_count: int, essay_type: EssayType) -> List[str]:
        """Check for essay-type specific warnings"""
        warnings = []
        
        if essay_type == EssayType.SAQ:
            # SAQ conciseness warnings
            if word_count > 400:
                warnings.append("SAQ responses should be concise and focused. Consider being more direct in your answer.")
        
        elif essay_type == EssayType.DBQ:
            # DBQ document usage warnings
            if "document" not in text.lower():
                warnings.append("DBQ essays should reference and analyze provided documents.")
        
        elif essay_type == EssayType.LEQ:
            # LEQ analysis warnings
            if word_count > 100 and "analysis" not in text.lower() and "analyze" not in text.lower():
                warnings.append("LEQ essays should demonstrate historical analysis and interpretation.")
        
        return warnings
    
    def get_max_word_count(self, essay_type: EssayType) -> int:
        """
        Get maximum word count for essay type
        
        Args:
            essay_type: Type of essay
            
        Returns:
            Maximum word count
        """
        return self._max_word_counts[essay_type]
    
    def get_target_word_count(self, essay_type: EssayType) -> int:
        """Get target word count for essay type"""
        return self._target_word_counts[essay_type]
    
    def get_critical_min_count(self, essay_type: EssayType) -> int:
        """Get critical minimum word count for essay type"""
        return self._critical_min_counts[essay_type]
    
    def is_critical_warning(self, warning: str) -> bool:
        """Check if warning is critical (length-based)"""
        critical_indicators = ["too short", "too long"]
        warning_lower = warning.lower()
        return any(indicator in warning_lower for indicator in critical_indicators)
    
    def categorize_warnings(self, warnings: List[str]) -> dict:
        """
        Categorize warnings into critical and advisory
        
        Returns:
            Dictionary with 'critical' and 'advisory' warning lists
        """
        critical = []
        advisory = []
        
        for warning in warnings:
            if self.is_critical_warning(warning):
                critical.append(warning)
            else:
                advisory.append(warning)
        
        return {
            "critical": critical,
            "advisory": advisory,
            "total_count": len(warnings)
        }


# Register implementation
WarningGeneratorProtocol.register(WarningGenerator)