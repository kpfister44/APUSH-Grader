"""Response processing data models for AI grading responses."""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from app.models.core.grade_models import GradeResponse


class InsightType(str, Enum):
    """Types of insights that can be generated."""
    PERFORMANCE = "performance"
    STRENGTH = "strength"
    IMPROVEMENT = "improvement"
    TIP = "tip"
    WARNING = "warning"


class InsightSeverity(str, Enum):
    """Severity levels for insights."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class GradingInsight(BaseModel):
    """Individual insight about grading performance."""
    type: InsightType = Field(..., description="Type of insight")
    title: str = Field(..., description="Brief title for the insight")
    message: str = Field(..., description="Detailed insight message")
    severity: InsightSeverity = Field(..., description="Severity level of the insight")


class ValidationResult(BaseModel):
    """Result of validating a grading response."""
    issues: List[str] = Field(default_factory=list, description="Critical validation issues")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")


class PerformanceColor(BaseModel):
    """Platform-agnostic color representation for performance levels."""
    hex: str = Field(..., description="Hex color code (e.g., #FF0000)")
    rgb: tuple[int, int, int] = Field(..., description="RGB color values (0-255)")
    name: str = Field(..., description="Human-readable color name")


class BreakdownDisplayItem(BaseModel):
    """Display item for a single rubric breakdown component."""
    name: str = Field(..., description="Display name for the rubric item")
    score: int = Field(..., description="Points earned")
    max_score: int = Field(..., description="Maximum possible points")
    feedback: str = Field(..., description="Feedback for this component")
    performance_level: str = Field(..., description="Performance level description")
    is_full_credit: bool = Field(..., description="Whether full credit was earned")


class GradeDisplayData(BaseModel):
    """Platform-agnostic display data for grading results."""
    score_text: str = Field(..., description="Formatted score text (e.g., '5/6')")
    percentage_text: str = Field(..., description="Formatted percentage text (e.g., '83%')")
    letter_grade: str = Field(..., description="Letter grade (A, B, C, D, F)")
    performance_color: PerformanceColor = Field(..., description="Color for performance level")
    breakdown_items: List[BreakdownDisplayItem] = Field(..., description="Individual rubric components")
    insights: List[GradingInsight] = Field(..., description="Generated insights")


class ProcessedGradingResult(BaseModel):
    """Complete processed result from AI grading response."""
    original_response: GradeResponse = Field(..., description="Original AI grading response")
    formatted_text: str = Field(..., description="Markdown-formatted display text")
    insights: List[GradingInsight] = Field(..., description="Generated insights and recommendations")
    validation_issues: List[str] = Field(..., description="Any validation issues found")
    display_data: GradeDisplayData = Field(..., description="Platform-agnostic display data")