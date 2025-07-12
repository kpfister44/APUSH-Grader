"""
Simplified essay processing utilities for hobby project.
Replaces complex service architecture with direct functions.
"""

import re
import logging
from typing import List, Set
from functools import lru_cache

from app.models.core import EssayType
from app.models.processing import PreprocessingResult

logger = logging.getLogger(__name__)


def preprocess_essay(essay_text: str, essay_type: EssayType) -> PreprocessingResult:
    """
    Preprocess and validate essay text.
    Combines essay cleaning, analysis, and warning generation.
    """
    # Clean the text
    cleaned_text = clean_text(essay_text)
    
    # Analyze text
    word_count = count_words(cleaned_text)
    paragraph_count = count_paragraphs(cleaned_text)
    
    # Generate warnings
    warnings = generate_warnings(cleaned_text, word_count, paragraph_count, essay_type)
    
    logger.info(f"Preprocessed {essay_type.value} essay: {word_count} words, {len(warnings)} warnings")
    
    return PreprocessingResult(
        cleaned_text=cleaned_text,
        word_count=word_count,
        paragraph_count=paragraph_count,
        warnings=warnings
    )


def clean_text(text: str) -> str:
    """Clean and normalize essay text"""
    if not text:
        return ""
    
    # Basic text cleaning
    cleaned = text.strip()
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove excessive punctuation
    cleaned = re.sub(r'[.]{3,}', '...', cleaned)
    cleaned = re.sub(r'[!]{2,}', '!', cleaned)
    cleaned = re.sub(r'[?]{2,}', '?', cleaned)
    
    return cleaned


def count_words(text: str) -> int:
    """Count words in text"""
    if not text or not text.strip():
        return 0
    
    # Use regex to find word boundaries
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def count_paragraphs(text: str) -> int:
    """Count paragraphs in text"""
    if not text or not text.strip():
        return 0
    
    # Split by double newlines and filter empty paragraphs
    paragraphs = re.split(r'\n\s*\n', text.strip())
    non_empty_paragraphs = [p for p in paragraphs if p.strip()]
    
    # If no double newlines found, treat as single paragraph
    return max(1, len(non_empty_paragraphs))


def generate_warnings(text: str, word_count: int, paragraph_count: int, essay_type: EssayType) -> List[str]:
    """Generate warnings for essay quality"""
    warnings = []
    
    # Length warnings based on essay type
    min_words = _get_min_words(essay_type)
    max_words = _get_max_words(essay_type)
    
    if word_count < min_words:
        warnings.append(f"Essay is too short ({word_count} words). Minimum {min_words} words required for {essay_type.value}.")
    elif word_count > max_words:
        warnings.append(f"Essay is too long ({word_count} words). Maximum {max_words} words recommended for {essay_type.value}.")
    
    # Paragraph warnings
    expected_paragraphs = _get_expected_paragraphs(essay_type)
    if paragraph_count < expected_paragraphs:
        warnings.append(f"Consider adding more paragraphs. {essay_type.value} essays typically need {expected_paragraphs} paragraphs (introduction, body paragraphs, conclusion).")
    
    # Content warnings
    if not _contains_thesis_indicators(text):
        warnings.append("Consider including a clear thesis statement with words like 'argue', 'demonstrate', or 'thesis'.")
    
    if not _contains_evidence_keywords(text):
        warnings.append("Consider including more specific document evidence and historical examples.")
    
    # Essay-specific warnings
    if essay_type == EssayType.DBQ:
        warnings.append("DBQ essays should reference and analyze provided documents.")
    elif essay_type == EssayType.LEQ:
        warnings.append("LEQ essays should have a clear historical argument supported by specific evidence.")
    elif essay_type == EssayType.SAQ:
        warnings.append("SAQ responses should be concise and directly answer the question.")
    
    return warnings


def _get_min_words(essay_type: EssayType) -> int:
    """Get minimum word count for essay type"""
    return {
        EssayType.DBQ: 200,
        EssayType.LEQ: 200,
        EssayType.SAQ: 50
    }[essay_type]


def _get_max_words(essay_type: EssayType) -> int:
    """Get maximum word count for essay type"""
    return {
        EssayType.DBQ: 1000,
        EssayType.LEQ: 1000,
        EssayType.SAQ: 300
    }[essay_type]


def _get_expected_paragraphs(essay_type: EssayType) -> int:
    """Get expected paragraph count for essay type"""
    return {
        EssayType.DBQ: 4,
        EssayType.LEQ: 4,
        EssayType.SAQ: 1
    }[essay_type]


@lru_cache(maxsize=1)
def _get_thesis_keywords() -> Set[str]:
    """Get cached thesis indicator keywords"""
    return {
        "argue", "argues", "argued", "argument",
        "thesis", "claim", "claims", "contend", "contends",
        "assert", "asserts", "maintain", "maintains",
        "demonstrate", "demonstrates", "prove", "proves"
    }


@lru_cache(maxsize=1)
def _get_evidence_keywords() -> Set[str]:
    """Get cached evidence keywords"""
    return {
        "evidence", "document", "source", "according to",
        "demonstrates", "illustrates", "reveals", "indicates",
        "example", "instance", "case", "data"
    }


def _contains_thesis_indicators(text: str) -> bool:
    """Check if text contains thesis indicators"""
    if not text:
        return False
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in _get_thesis_keywords())


def _contains_evidence_keywords(text: str) -> bool:
    """Check if text contains evidence keywords"""
    if not text:
        return False
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in _get_evidence_keywords())