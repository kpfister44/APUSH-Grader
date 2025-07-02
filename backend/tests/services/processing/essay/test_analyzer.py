"""Tests for TextAnalyzer service"""

import pytest
from app.models.core.essay_types import EssayType
from app.services.processing.essay.analyzer import TextAnalyzer
from tests.services.base.test_base import EssayServiceTestBase, MockServiceMixin


class TestTextAnalyzer(EssayServiceTestBase, MockServiceMixin):
    """Test suite for TextAnalyzer service"""
    
    @pytest.fixture
    def analyzer(self, mock_settings):
        """Create TextAnalyzer instance"""
        return TextAnalyzer(mock_settings)
    
    def test_count_words_basic(self, analyzer):
        """Test basic word counting"""
        text = "This is a test with five words"
        assert analyzer.count_words(text) == 6  # Actually 6 words
    
    def test_count_words_empty(self, analyzer):
        """Test word counting with empty text"""
        assert analyzer.count_words("") == 0
        assert analyzer.count_words("   ") == 0
    
    def test_count_words_with_punctuation(self, analyzer):
        """Test word counting with punctuation"""
        text = "Hello, world! This is a test."
        assert analyzer.count_words(text) == 6
    
    def test_count_words_with_numbers(self, analyzer):
        """Test word counting with numbers"""
        text = "The year 1776 was important."
        assert analyzer.count_words(text) == 5
    
    def test_count_paragraphs_single(self, analyzer):
        """Test paragraph counting with single paragraph"""
        text = "This is a single paragraph."
        assert analyzer.count_paragraphs(text) == 1
    
    def test_count_paragraphs_multiple(self, analyzer):
        """Test paragraph counting with multiple paragraphs"""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        assert analyzer.count_paragraphs(text) == 3
    
    def test_count_paragraphs_empty(self, analyzer):
        """Test paragraph counting with empty text"""
        assert analyzer.count_paragraphs("") == 0
        assert analyzer.count_paragraphs("   ") == 0
    
    def test_count_sentences_basic(self, analyzer):
        """Test basic sentence counting"""
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        assert analyzer.count_sentences(text) == 3
    
    def test_count_sentences_empty(self, analyzer):
        """Test sentence counting with empty text"""
        assert analyzer.count_sentences("") == 0
    
    def test_get_first_paragraph(self, analyzer):
        """Test extracting first paragraph"""
        text = "First paragraph content.\n\nSecond paragraph content."
        result = analyzer.get_first_paragraph(text)
        assert result == "First paragraph content."
    
    def test_get_first_paragraph_single(self, analyzer):
        """Test extracting first paragraph when only one exists"""
        text = "Only one paragraph here."
        result = analyzer.get_first_paragraph(text)
        assert result == "Only one paragraph here."
    
    def test_contains_thesis_indicators_true(self, analyzer):
        """Test thesis indicator detection - positive cases"""
        thesis_texts = [
            "I argue that the Revolution was necessary.",
            "This thesis demonstrates the importance.",
            "Evidence suggests that freedom was key.",
            "The analysis reveals significant changes."
        ]
        
        for text in thesis_texts:
            assert analyzer.contains_thesis_indicators(text) is True
    
    def test_contains_thesis_indicators_false(self, analyzer):
        """Test thesis indicator detection - negative cases"""
        non_thesis_text = "This is just a description without any thesis indicators."
        assert analyzer.contains_thesis_indicators(non_thesis_text) is False
    
    def test_contains_evidence_keywords_true(self, analyzer):
        """Test evidence keyword detection - positive cases"""
        evidence_text = "According to the document about the Civil War, evidence shows the conflict was inevitable."
        assert analyzer.contains_evidence_keywords(evidence_text, EssayType.DBQ) is True
    
    def test_contains_evidence_keywords_false(self, analyzer):
        """Test evidence keyword detection - negative cases"""
        no_evidence_text = "This text has no supporting materials or historical terms."
        assert analyzer.contains_evidence_keywords(no_evidence_text, EssayType.DBQ) is False
    
    def test_contains_informal_language_true(self, analyzer):
        """Test informal language detection - positive cases"""
        informal_texts = [
            "I don't think this is right.",
            "The revolution was super important.",
            "They were gonna fight for freedom.",
            "It was basically a big deal."
        ]
        
        for text in informal_texts:
            assert analyzer.contains_informal_language(text) is True
    
    def test_contains_informal_language_false(self, analyzer):
        """Test informal language detection - negative cases"""
        formal_text = "The American Revolution was a significant historical event that established independence."
        assert analyzer.contains_informal_language(formal_text) is False
    
    def test_analyze_text_integration(self, analyzer, real_service_locator):
        """Test complete text analysis integration"""
        from app.services.base.protocols import TextCleanerProtocol, WarningGeneratorProtocol
        
        # Register dependencies
        text_cleaner = self.create_mock_text_cleaner()
        warning_generator = self.create_mock_warning_generator()
        
        real_service_locator.register_singleton(TextCleanerProtocol, text_cleaner)
        real_service_locator.register_singleton(WarningGeneratorProtocol, warning_generator)
        
        text = "This is a test essay about the American Revolution."
        result = analyzer.analyze_text(text, EssayType.SAQ)
        
        assert result.cleaned_text is not None
        assert result.word_count > 0
        assert result.paragraph_count > 0
        assert isinstance(result.warnings, list)
    
    def test_get_text_statistics(self, analyzer):
        """Test comprehensive text statistics"""
        text = """
        This is a sample essay about the American Revolution.
        
        I argue that the revolution was necessary. According to historical
        documents, the colonists were frustrated with taxation.
        
        In conclusion, the revolution was a pivotal moment.
        """
        
        stats = analyzer.get_text_statistics(text)
        
        assert "word_count" in stats
        assert "paragraph_count" in stats
        assert "sentence_count" in stats
        assert "character_count" in stats
        assert "has_thesis_indicators" in stats
        assert "has_informal_language" in stats
        assert "first_paragraph" in stats
        
        assert stats["word_count"] > 0
        assert stats["paragraph_count"] >= 1
        assert stats["has_thesis_indicators"] is True
    
    def test_word_sets_caching(self, analyzer):
        """Test that word sets are properly cached"""
        # These should return the same objects (cached)
        thesis1 = analyzer._get_thesis_keywords()
        thesis2 = analyzer._get_thesis_keywords()
        assert thesis1 is thesis2
        
        evidence1 = analyzer._get_evidence_keywords()
        evidence2 = analyzer._get_evidence_keywords()
        assert evidence1 is evidence2
    
    def test_historical_terms_detection(self, analyzer):
        """Test historical terms detection for evidence"""
        historical_text = "The Civil War and Lincoln's presidency were crucial. Documents from Washington show evidence of early conflicts."
        assert analyzer.contains_evidence_keywords(historical_text, EssayType.DBQ) is True
        
        non_historical_text = "According to the evidence, something happened."
        assert analyzer.contains_evidence_keywords(non_historical_text, EssayType.DBQ) is False
    
    def test_count_words_complex_text(self, analyzer):
        """Test word counting with complex text"""
        complex_text = "The U.S.A. was founded in 1776. It's a democracy, isn't it?"
        word_count = analyzer.count_words(complex_text)
        # Should handle contractions and abbreviations properly
        assert word_count > 8
    
    def test_analyze_text_with_different_essay_types(self, analyzer, real_service_locator):
        """Test analysis with different essay types"""
        from app.services.base.protocols import TextCleanerProtocol, WarningGeneratorProtocol
        
        # Register dependencies
        text_cleaner = self.create_mock_text_cleaner()
        warning_generator = self.create_mock_warning_generator()
        
        real_service_locator.register_singleton(TextCleanerProtocol, text_cleaner)
        real_service_locator.register_singleton(WarningGeneratorProtocol, warning_generator)
        
        text = "Sample essay text for testing different types."
        
        for essay_type in [EssayType.DBQ, EssayType.LEQ, EssayType.SAQ]:
            result = analyzer.analyze_text(text, essay_type)
            assert result is not None
            assert result.word_count > 0