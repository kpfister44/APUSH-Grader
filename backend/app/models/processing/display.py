"""Platform-agnostic display models replacing SwiftUI dependencies."""

from typing import Dict
from pydantic import BaseModel, Field

from app.models.processing.response import PerformanceColor


class DisplayColors:
    """Platform-agnostic color definitions replacing SwiftUI Colors."""
    
    # Performance-based colors
    EXCELLENT = PerformanceColor(
        hex="#00C851", 
        rgb=(0, 200, 81), 
        name="green"
    )
    
    PROFICIENT = PerformanceColor(
        hex="#007ACC", 
        rgb=(0, 122, 204), 
        name="blue"
    )
    
    DEVELOPING = PerformanceColor(
        hex="#FF8800", 
        rgb=(255, 136, 0), 
        name="orange"
    )
    
    APPROACHING = PerformanceColor(
        hex="#FFCC00", 
        rgb=(255, 204, 0), 
        name="yellow"
    )
    
    BEGINNING = PerformanceColor(
        hex="#FF4444", 
        rgb=(255, 68, 68), 
        name="red"
    )
    
    @classmethod
    def get_performance_color(cls, percentage: float) -> PerformanceColor:
        """Get color based on performance percentage."""
        if percentage >= 90:
            return cls.EXCELLENT
        elif percentage >= 80:
            return cls.PROFICIENT
        elif percentage >= 70:
            return cls.DEVELOPING
        elif percentage >= 60:
            return cls.APPROACHING
        else:
            return cls.BEGINNING


class DisplayConstants:
    """Constants for display formatting."""
    
    # Emojis for different elements
    SCORE_EMOJI = "📊"
    WARNING_EMOJI = "⚠️"
    BREAKDOWN_EMOJI = "📋"
    FEEDBACK_EMOJI = "💬"
    SUGGESTIONS_EMOJI = "💡"
    
    # Status emojis for rubric items
    FULL_CREDIT_EMOJI = "✅"
    PARTIAL_CREDIT_EMOJI = "🔶"
    NO_CREDIT_EMOJI = "❌"
    
    # Performance level thresholds
    PERFORMANCE_THRESHOLDS = {
        "Excellent": (90, 100),
        "Proficient": (80, 90),
        "Developing": (70, 80),
        "Approaching": (60, 70),
        "Beginning": (0, 60)
    }
    
    @classmethod
    def get_performance_level(cls, percentage: float) -> str:
        """Get performance level name based on percentage."""
        for level, (min_val, max_val) in cls.PERFORMANCE_THRESHOLDS.items():
            if min_val <= percentage < max_val or (level == "Excellent" and percentage >= 90):
                return level
        return "Beginning"
    
    @classmethod
    def get_rubric_emoji(cls, score: int, max_score: int) -> str:
        """Get emoji for rubric item based on score."""
        if score == max_score:
            return cls.FULL_CREDIT_EMOJI
        elif score > 0:
            return cls.PARTIAL_CREDIT_EMOJI
        else:
            return cls.NO_CREDIT_EMOJI


class ErrorIcons:
    """Platform-agnostic error icons (using emoji equivalents)."""
    
    NETWORK_ERROR = "📡❌"
    API_KEY_ERROR = "🔑❌"
    ESSAY_LENGTH_ERROR = "📄🔍"
    VALIDATION_ERROR = "⚠️⚠️"
    GENERAL_ERROR = "❌"
    
    @classmethod
    def get_error_icon(cls, error_type: str) -> str:
        """Get appropriate icon for error type."""
        icon_map = {
            "network": cls.NETWORK_ERROR,
            "api_key": cls.API_KEY_ERROR,
            "essay_length": cls.ESSAY_LENGTH_ERROR,
            "validation": cls.VALIDATION_ERROR,
        }
        return icon_map.get(error_type, cls.GENERAL_ERROR)