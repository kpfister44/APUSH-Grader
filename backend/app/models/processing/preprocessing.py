"""Preprocessing models for text analysis and validation"""

from pydantic import BaseModel, computed_field
from typing import List


class PreprocessingResult(BaseModel):
    """Result of essay preprocessing with validation and warnings"""
    
    cleaned_text: str
    word_count: int
    paragraph_count: int
    warnings: List[str]
    
    @computed_field
    @property
    def is_valid(self) -> bool:
        """Check if preprocessing result is valid (no critical warnings)"""
        if not self.warnings:
            return True
        
        # Check for critical warnings (too short/too long)
        critical_warnings = [
            warning for warning in self.warnings
            if "too short" in warning.lower() or "too long" in warning.lower()
        ]
        
        return len(critical_warnings) == 0
    
    @computed_field
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0
    
    @computed_field
    @property
    def warning_count(self) -> int:
        """Get total number of warnings"""
        return len(self.warnings)
    
    @computed_field
    @property
    def critical_warnings(self) -> List[str]:
        """Get only critical warnings (too short/too long)"""
        return [
            warning for warning in self.warnings
            if "too short" in warning.lower() or "too long" in warning.lower()
        ]
    
    @computed_field
    @property
    def advisory_warnings(self) -> List[str]:
        """Get only advisory warnings (non-critical)"""
        return [
            warning for warning in self.warnings
            if "too short" not in warning.lower() and "too long" not in warning.lower()
        ]
    
    @computed_field
    @property
    def has_critical_warnings(self) -> bool:
        """Check if there are critical warnings"""
        return len(self.critical_warnings) > 0