"""Text cleaning service for essay preprocessing"""

import re
import unicodedata
from typing import Optional
from app.config.settings import Settings
from app.services.base.base_service import BaseTextProcessor
from app.services.base.protocols import TextCleanerProtocol


class TextCleaner(BaseTextProcessor):
    """Service for cleaning and normalizing essay text"""
    
    def __init__(self, settings: Optional[Settings] = None):
        super().__init__(settings)
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for performance"""
        # Pattern for multiple whitespace characters
        self._whitespace_pattern = re.compile(r'\s+')
        
        # Pattern for multiple newlines (paragraph separation)
        self._paragraph_pattern = re.compile(r'\n\s*\n+')
        
        # Pattern for leading/trailing whitespace
        self._trim_pattern = re.compile(r'^\s+|\s+$')
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for analysis
        
        Args:
            text: Raw essay text
            
        Returns:
            Cleaned and normalized text
        """
        return self._safe_text_operation(text, self._clean_text_impl, "text cleaning")
    
    def _clean_text_impl(self, text: str) -> str:
        """Internal implementation of text cleaning"""
        if not text:
            return ""
        
        # Step 1: Normalize Unicode characters
        cleaned = self._normalize_unicode(text)
        
        # Step 2: Normalize whitespace
        cleaned = self._normalize_whitespace(cleaned)
        
        # Step 3: Normalize paragraph breaks
        cleaned = self._normalize_paragraphs(cleaned)
        
        # Step 4: Trim leading/trailing whitespace
        cleaned = cleaned.strip()
        
        self._log_debug("Text cleaning completed", 
                       original_length=len(text), 
                       cleaned_length=len(cleaned))
        
        return cleaned
    
    def _normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters to standard ASCII equivalents
        
        Replaces smart quotes, em dashes, etc. with standard characters
        """
        # Unicode character replacements
        replacements = {
            # Smart quotes
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark
            
            # Dashes
            '\u2013': '-',  # En dash
            '\u2014': '-',  # Em dash
            '\u2015': '-',  # Horizontal bar
            
            # Ellipsis
            '\u2026': '...',  # Horizontal ellipsis
            
            # Spaces
            '\u00a0': ' ',  # Non-breaking space
            '\u2002': ' ',  # En space
            '\u2003': ' ',  # Em space
            '\u2009': ' ',  # Thin space
            
            # Other common characters
            '\u2022': '*',  # Bullet
            '\u00b7': '*',  # Middle dot
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Normalize Unicode combining characters
        text = unicodedata.normalize('NFKC', text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace characters
        
        Converts multiple spaces/tabs to single spaces
        """
        # Replace multiple whitespace characters (except newlines) with single space
        lines = text.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Normalize whitespace within each line
            normalized_line = self._whitespace_pattern.sub(' ', line)
            normalized_lines.append(normalized_line.strip())
        
        return '\n'.join(normalized_lines)
    
    def _normalize_paragraphs(self, text: str) -> str:
        """
        Normalize paragraph breaks
        
        Converts multiple newlines to double newlines (paragraph separation)
        """
        # Replace multiple newlines with double newline (paragraph break)
        normalized = self._paragraph_pattern.sub('\n\n', text)
        
        return normalized
    
    def get_cleaned_length(self, text: str) -> int:
        """Get length of text after cleaning"""
        return len(self.clean_text(text))
    
    def preview_cleaning(self, text: str, max_length: int = 200) -> dict:
        """
        Preview text cleaning changes (useful for debugging)
        
        Returns:
            Dictionary with original and cleaned text previews
        """
        cleaned = self.clean_text(text)
        
        return {
            "original": text[:max_length] + "..." if len(text) > max_length else text,
            "cleaned": cleaned[:max_length] + "..." if len(cleaned) > max_length else cleaned,
            "original_length": len(text),
            "cleaned_length": len(cleaned),
            "changes": len(text) != len(cleaned)
        }


# Register implementation
TextCleanerProtocol.register(TextCleaner)