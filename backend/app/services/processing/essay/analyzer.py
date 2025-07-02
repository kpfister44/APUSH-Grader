"""Text analysis service for essay processing"""

import re
from typing import Optional, Set, List
from functools import lru_cache
from app.config.settings import Settings
from app.models.core.essay_types import EssayType
from app.models.processing.preprocessing import PreprocessingResult
from app.services.base.base_service import BaseTextProcessor
from app.services.base.protocols import TextAnalyzerProtocol, TextCleanerProtocol, WarningGeneratorProtocol
from app.services.base.exceptions import TextAnalysisError


class TextAnalyzer(BaseTextProcessor):
    """Service for comprehensive text analysis and content detection"""
    
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)
        self._compile_patterns()
        self._initialize_word_sets()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for performance"""
        # Word pattern for counting
        self._word_pattern = re.compile(r'\b\w+\b')
        
        # Sentence pattern for counting
        self._sentence_pattern = re.compile(r'[.!?]+')
        
        # Paragraph pattern for counting
        self._paragraph_pattern = re.compile(r'\n\s*\n')
    
    def _initialize_word_sets(self) -> None:
        """Initialize keyword sets for content detection"""
        self._thesis_keywords = self._get_thesis_keywords()
        self._evidence_keywords = self._get_evidence_keywords()
        self._historical_terms = self._get_historical_terms()
        self._informal_words = self._get_informal_words()
    
    def analyze_text(self, text: str, essay_type: EssayType) -> PreprocessingResult:
        """
        Analyze text and return comprehensive preprocessing result
        
        Args:
            text: Essay text to analyze
            essay_type: Type of essay (DBQ, LEQ, SAQ)
            
        Returns:
            PreprocessingResult with analysis data
        """
        self._validate_essay_input(text, essay_type)
        
        return self._safe_execute(
            self._analyze_text_impl, 
            "text analysis", 
            text, essay_type
        )
    
    def _analyze_text_impl(self, text: str, essay_type: EssayType) -> PreprocessingResult:
        """Internal implementation of text analysis"""
        # Get dependencies
        from app.services.dependencies.service_locator import get_service_locator
        locator = get_service_locator()
        
        try:
            text_cleaner = locator.get(TextCleanerProtocol)
            warning_generator = locator.get(WarningGeneratorProtocol)
        except Exception as e:
            raise TextAnalysisError(f"Failed to get required services: {e}")
        
        # Clean the text
        cleaned_text = text_cleaner.clean_text(text)
        
        # Perform analysis
        word_count = self.count_words(cleaned_text)
        paragraph_count = self.count_paragraphs(cleaned_text)
        
        # Generate warnings
        warnings = warning_generator.generate_warnings(
            cleaned_text, word_count, paragraph_count, essay_type
        )
        
        self._log_operation("text analysis completed",
                          word_count=word_count,
                          paragraph_count=paragraph_count,
                          warning_count=len(warnings),
                          essay_type=essay_type.value)
        
        return PreprocessingResult(
            cleaned_text=cleaned_text,
            word_count=word_count,
            paragraph_count=paragraph_count,
            warnings=warnings
        )
    
    def count_words(self, text: str) -> int:
        """
        Count words in text with proper whitespace handling
        
        Args:
            text: Text to analyze
            
        Returns:
            Number of words
        """
        if not text or not text.strip():
            return 0
        
        # Use regex to find word boundaries
        words = self._word_pattern.findall(text)
        return len(words)
    
    def count_paragraphs(self, text: str) -> int:
        """
        Count paragraphs with double newline detection
        
        Args:
            text: Text to analyze
            
        Returns:
            Number of paragraphs
        """
        if not text or not text.strip():
            return 0
        
        # Split by double newlines and filter empty paragraphs
        paragraphs = self._paragraph_pattern.split(text.strip())
        non_empty_paragraphs = [p for p in paragraphs if p.strip()]
        
        # If no double newlines found, treat as single paragraph
        return max(1, len(non_empty_paragraphs))
    
    def count_sentences(self, text: str) -> int:
        """
        Count sentences with punctuation detection
        
        Args:
            text: Text to analyze
            
        Returns:
            Number of sentences
        """
        if not text or not text.strip():
            return 0
        
        sentences = self._sentence_pattern.split(text)
        # Filter out empty sentences
        non_empty_sentences = [s for s in sentences if s.strip()]
        return len(non_empty_sentences)
    
    def get_first_paragraph(self, text: str) -> str:
        """
        Extract first paragraph for thesis analysis
        
        Args:
            text: Text to analyze
            
        Returns:
            First paragraph text
        """
        if not text or not text.strip():
            return ""
        
        paragraphs = self._paragraph_pattern.split(text.strip())
        return paragraphs[0].strip() if paragraphs else text.strip()
    
    def contains_thesis_indicators(self, text: str) -> bool:
        """
        Check if text contains thesis indicators
        
        Args:
            text: Text to analyze
            
        Returns:
            True if thesis indicators found
        """
        if not text:
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self._thesis_keywords)
    
    def contains_evidence_keywords(self, text: str, essay_type: EssayType) -> bool:
        """
        Check if text contains evidence keywords
        
        Requires BOTH common evidence words AND historical terms
        
        Args:
            text: Text to analyze
            essay_type: Type of essay
            
        Returns:
            True if evidence keywords found
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for evidence keywords
        has_evidence = any(keyword in text_lower for keyword in self._evidence_keywords)
        
        # Check for historical terms
        has_historical = any(term in text_lower for term in self._historical_terms)
        
        # Require both for strong evidence detection
        return has_evidence and has_historical
    
    def contains_informal_language(self, text: str) -> bool:
        """
        Check if text contains informal language
        
        Args:
            text: Text to analyze
            
        Returns:
            True if informal language found
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for contractions and informal words
        return any(word in text_lower for word in self._informal_words)
    
    @staticmethod
    @lru_cache(maxsize=1)
    def _get_thesis_keywords() -> Set[str]:
        """Get cached thesis indicator keywords"""
        return {
            "argue", "argues", "argued", "argument",
            "thesis", "claim", "claims", "contend", "contends",
            "assert", "asserts", "maintain", "maintains",
            "demonstrate", "demonstrates", "prove", "proves",
            "evidence suggests", "analysis reveals", "shows",
            "indicates", "supports", "establishes"
        }
    
    @staticmethod
    @lru_cache(maxsize=1)
    def _get_evidence_keywords() -> Set[str]:
        """Get cached evidence keywords"""
        return {
            "evidence", "document", "source", "according to",
            "as shown", "demonstrates", "illustrates", "reveals",
            "indicates", "suggests", "supports", "proves",
            "example", "instance", "case", "data", "statistics",
            "quote", "quotation", "cited", "reference"
        }
    
    @staticmethod
    @lru_cache(maxsize=1)
    def _get_historical_terms() -> Set[str]:
        """Get cached historical terms for evidence detection"""
        return {
            # Time periods
            "colonial", "revolution", "civil war", "reconstruction",
            "industrial", "progressive", "world war", "depression",
            "new deal", "cold war", "civil rights",
            
            # Key figures
            "washington", "jefferson", "lincoln", "roosevelt",
            "wilson", "kennedy", "king", "malcolm",
            
            # Events
            "constitution", "amendment", "act", "treaty",
            "battle", "war", "movement", "reform",
            
            # Concepts
            "slavery", "freedom", "democracy", "capitalism",
            "federalism", "states rights", "manifest destiny"
        }
    
    @staticmethod
    @lru_cache(maxsize=1)
    def _get_informal_words() -> Set[str]:
        """Get cached informal language indicators"""
        return {
            # Contractions
            "don't", "won't", "can't", "shouldn't", "wouldn't",
            "couldn't", "didn't", "isn't", "aren't", "wasn't",
            "weren't", "haven't", "hasn't", "hadn't",
            
            # Casual words
            "stuff", "things", "gonna", "wanna", "kinda",
            "sorta", "yeah", "nah", "ok", "okay",
            "super", "really", "pretty", "way", "like",
            
            # Intensifiers
            "totally", "basically", "literally", "actually",
            "obviously", "definitely", "seriously"
        }
    
    def get_text_statistics(self, text: str) -> dict:
        """
        Get comprehensive text statistics
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with text statistics
        """
        return {
            "word_count": self.count_words(text),
            "paragraph_count": self.count_paragraphs(text),
            "sentence_count": self.count_sentences(text),
            "character_count": len(text),
            "has_thesis_indicators": self.contains_thesis_indicators(text),
            "has_informal_language": self.contains_informal_language(text),
            "first_paragraph": self.get_first_paragraph(text)[:100] + "..."
        }


# Register implementation
TextAnalyzerProtocol.register(TextAnalyzer)