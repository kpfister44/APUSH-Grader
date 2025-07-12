"""
Simplified processing models for APUSH essay grading.
Removed UI/display logic for hobby project scope.
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from .core import GradeResponse


# Basic preprocessing result
class PreprocessingResult(BaseModel):
    """Result of essay preprocessing"""
    
    cleaned_text: str
    word_count: int
    paragraph_count: int
    warnings: List[str]
    
    def is_valid(self) -> bool:
        """Check if essay meets basic requirements"""
        return not any("too short" in w or "too long" in w for w in self.warnings)


# Simplified insight models
class InsightType(str, Enum):
    """Types of insights that can be generated"""
    PERFORMANCE = "performance"
    STRENGTH = "strength" 
    IMPROVEMENT = "improvement"
    TIP = "tip"
    WARNING = "warning"


class InsightSeverity(str, Enum):
    """Severity levels for insights"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class GradingInsight(BaseModel):
    """Individual insight about grading performance"""
    type: InsightType = Field(..., description="Type of insight")
    title: str = Field(..., description="Brief title for the insight")
    message: str = Field(..., description="Detailed insight message")
    severity: InsightSeverity = Field(..., description="Severity level")


# Validation result
class ValidationResult(BaseModel):
    """Result of validating a grading response"""
    issues: List[str] = Field(default_factory=list, description="Critical validation issues")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")


# Basic color representation (kept minimal for hobby project)
class PerformanceColor(BaseModel):
    """Simple color representation for performance levels"""
    hex: str = Field(..., description="Hex color code")
    rgb: tuple[int, int, int] = Field(..., description="RGB color values")
    name: str = Field(..., description="Color name")


# Simplified display data (minimal UI logic)
class BreakdownDisplayItem(BaseModel):
    """Display item for a single rubric component"""
    name: str
    score: int
    max_score: int
    feedback: str
    performance_level: str
    is_full_credit: bool


class GradeDisplayData(BaseModel):
    """Basic display data for grading results"""
    score_text: str
    percentage_text: str
    letter_grade: str
    performance_color: PerformanceColor
    breakdown_items: List[BreakdownDisplayItem]
    insights: List[GradingInsight]


# Final processed result
class ProcessedGradingResult(BaseModel):
    """Complete processed result from AI grading response"""
    original_response: GradeResponse
    formatted_text: str
    insights: List[GradingInsight]
    validation_issues: List[str]
    display_data: GradeDisplayData