"""Essay type definitions and rules"""

from enum import Enum
from typing import Dict
from pydantic import BaseModel


class EssayType(str, Enum):
    """Essay type enumeration"""
    
    DBQ = "DBQ"
    LEQ = "LEQ"
    SAQ = "SAQ"
    
    @property
    def description(self) -> str:
        """Get essay type description"""
        descriptions = {
            "DBQ": "Document Based Question",
            "LEQ": "Long Essay Question",
            "SAQ": "Short Answer Question"
        }
        return descriptions[self.value]
    
    @property
    def max_score(self) -> int:
        """Get maximum score for essay type"""
        scores = {
            "DBQ": 6,
            "LEQ": 6,
            "SAQ": 3
        }
        return scores[self.value]
    
    @property
    def min_word_count(self) -> int:
        """Get minimum word count for essay type"""
        counts = {
            "DBQ": 400,
            "LEQ": 300,
            "SAQ": 50
        }
        return counts[self.value]
    
    @property
    def max_word_count(self) -> int:
        """Get maximum word count for essay type"""
        counts = {
            "DBQ": 2400,
            "LEQ": 2000,
            "SAQ": 600
        }
        return counts[self.value]
    
    @property
    def validation_threshold(self) -> int:
        """Get validation threshold (minimum for critical warning)"""
        thresholds = {
            "DBQ": 200,
            "LEQ": 150,
            "SAQ": 25
        }
        return thresholds[self.value]


class EssayTypeInfo(BaseModel):
    """Essay type information model"""
    
    essay_type: EssayType
    description: str
    max_score: int
    min_word_count: int
    max_word_count: int
    validation_threshold: int
    
    @classmethod
    def from_essay_type(cls, essay_type: EssayType) -> "EssayTypeInfo":
        """Create essay type info from essay type enum"""
        return cls(
            essay_type=essay_type,
            description=essay_type.description,
            max_score=essay_type.max_score,
            min_word_count=essay_type.min_word_count,
            max_word_count=essay_type.max_word_count,
            validation_threshold=essay_type.validation_threshold
        )