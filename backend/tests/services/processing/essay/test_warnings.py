"""Tests for WarningGenerator service"""

import pytest
from app.models.core.essay_types import EssayType
from app.services.processing.essay.warnings import WarningGenerator
from tests.services.base.test_base import EssayServiceTestBase, MockServiceMixin


class TestWarningGenerator(EssayServiceTestBase, MockServiceMixin):
    """Test suite for WarningGenerator service"""
    
    @pytest.fixture
    def warning_generator(self, mock_settings):
        """Create WarningGenerator instance"""
        return WarningGenerator(mock_settings)
    
    def test_generate_warnings_empty_for_good_essay(self, warning_generator, real_service_locator):
        """Test that good essays generate no warnings"""
        # Mock analyzer for content checks
        analyzer = self.create_mock_text_analyzer(
            contains_thesis_indicators=lambda text: True,
            contains_evidence_keywords=lambda text, essay_type: True,
            contains_informal_language=lambda text: False
        )
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        text = "Good essay text"
        warnings = warning_generator.generate_warnings(text, 300, 3, EssayType.SAQ)
        
        assert isinstance(warnings, list)
        # Should have minimal warnings for a good essay
        assert len(warnings) <= 1  # Maybe just advisory warnings
    
    def test_generate_warnings_too_short_critical(self, warning_generator, real_service_locator):
        """Test critical warning for too short essay"""
        text = "Short essay"
        warnings = warning_generator.generate_warnings(text, 20, 1, EssayType.SAQ)  # Below 25 word threshold
        
        critical_warnings = [w for w in warnings if "too short" in w.lower()]
        assert len(critical_warnings) > 0
        assert "25 words required" in critical_warnings[0]
    
    def test_generate_warnings_too_long_critical(self, warning_generator, real_service_locator):
        """Test critical warning for too long essay"""
        text = "Very long essay"
        warnings = warning_generator.generate_warnings(text, 700, 10, EssayType.SAQ)  # Above 600 limit
        
        critical_warnings = [w for w in warnings if "too long" in w.lower()]
        assert len(critical_warnings) > 0
        assert "600 words allowed" in critical_warnings[0]
    
    def test_generate_warnings_below_target_advisory(self, warning_generator, real_service_locator):
        """Test advisory warning for below target but above critical"""
        text = "Somewhat short essay"
        warnings = warning_generator.generate_warnings(text, 40, 2, EssayType.SAQ)  # Above 25, below 50
        
        advisory_warnings = [w for w in warnings if "shorter than recommended" in w.lower()]
        assert len(advisory_warnings) > 0
        assert "Target: 50+" in advisory_warnings[0]
    
    def test_generate_warnings_paragraph_count_dbq(self, warning_generator, real_service_locator):
        """Test paragraph count warnings for DBQ"""
        analyzer = self.create_mock_text_analyzer()
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        text = "Essay with few paragraphs"
        warnings = warning_generator.generate_warnings(text, 400, 2, EssayType.DBQ)  # Only 2 paragraphs
        
        paragraph_warnings = [w for w in warnings if "more paragraphs" in w.lower()]
        assert len(paragraph_warnings) > 0
        assert "4-5 paragraphs" in paragraph_warnings[0]
    
    def test_generate_warnings_paragraph_count_saq(self, warning_generator, real_service_locator):
        """Test paragraph count warnings for SAQ"""
        analyzer = self.create_mock_text_analyzer()
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        text = "SAQ with too many paragraphs"
        warnings = warning_generator.generate_warnings(text, 100, 5, EssayType.SAQ)  # Too many paragraphs
        
        paragraph_warnings = [w for w in warnings if "concise" in w.lower()]
        assert len(paragraph_warnings) > 0
        assert "1-2 focused paragraphs" in paragraph_warnings[0]
    
    def test_generate_warnings_missing_thesis(self, warning_generator, real_service_locator):
        """Test thesis missing warning"""
        analyzer = self.create_mock_text_analyzer(
            contains_thesis_indicators=lambda text: False
        )
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        text = "Essay without thesis"
        warnings = warning_generator.generate_warnings(text, 400, 3, EssayType.DBQ)
        
        thesis_warnings = [w for w in warnings if "thesis" in w.lower()]
        assert len(thesis_warnings) > 0
    
    def test_generate_warnings_missing_evidence(self, warning_generator, real_service_locator):
        """Test missing evidence warning"""
        analyzer = self.create_mock_text_analyzer(
            contains_evidence_keywords=lambda text, essay_type: False
        )
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        text = "Essay without evidence"
        warnings = warning_generator.generate_warnings(text, 400, 3, EssayType.DBQ)
        
        evidence_warnings = [w for w in warnings if "evidence" in w.lower()]
        assert len(evidence_warnings) > 0
        assert "document evidence" in evidence_warnings[0]
    
    def test_generate_warnings_informal_language(self, warning_generator, real_service_locator):
        """Test informal language warning"""
        analyzer = self.create_mock_text_analyzer(
            contains_informal_language=lambda text: True
        )
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        text = "Essay with informal language"
        warnings = warning_generator.generate_warnings(text, 300, 3, EssayType.SAQ)
        
        informal_warnings = [w for w in warnings if "formal" in w.lower()]
        assert len(informal_warnings) > 0
        assert "contractions" in informal_warnings[0]
    
    def test_generate_warnings_saq_specific(self, warning_generator, real_service_locator):
        """Test SAQ-specific warnings"""
        text = "Very long SAQ response"
        warnings = warning_generator.generate_warnings(text, 450, 2, EssayType.SAQ)  # Over 400 words
        
        saq_warnings = [w for w in warnings if "concise" in w.lower()]
        assert len(saq_warnings) > 0
    
    def test_generate_warnings_dbq_specific(self, warning_generator, real_service_locator):
        """Test DBQ-specific warnings"""
        text = "Essay without document references"
        warnings = warning_generator.generate_warnings(text, 400, 3, EssayType.DBQ)
        
        dbq_warnings = [w for w in warnings if "document" in w.lower()]
        assert len(dbq_warnings) > 0
    
    def test_generate_warnings_leq_specific(self, warning_generator, real_service_locator):
        """Test LEQ-specific warnings"""
        text = "Essay without analysis keywords"
        warnings = warning_generator.generate_warnings(text, 400, 3, EssayType.LEQ)
        
        leq_warnings = [w for w in warnings if "analysis" in w.lower()]
        assert len(leq_warnings) > 0
    
    def test_get_max_word_count(self, warning_generator):
        """Test getting maximum word counts"""
        assert warning_generator.get_max_word_count(EssayType.DBQ) == 2400
        assert warning_generator.get_max_word_count(EssayType.LEQ) == 2000
        assert warning_generator.get_max_word_count(EssayType.SAQ) == 600
    
    def test_get_target_word_count(self, warning_generator):
        """Test getting target word counts"""
        assert warning_generator.get_target_word_count(EssayType.DBQ) == 400
        assert warning_generator.get_target_word_count(EssayType.LEQ) == 300
        assert warning_generator.get_target_word_count(EssayType.SAQ) == 50
    
    def test_get_critical_min_count(self, warning_generator):
        """Test getting critical minimum counts"""
        assert warning_generator.get_critical_min_count(EssayType.DBQ) == 200
        assert warning_generator.get_critical_min_count(EssayType.LEQ) == 150
        assert warning_generator.get_critical_min_count(EssayType.SAQ) == 25
    
    def test_is_critical_warning(self, warning_generator):
        """Test critical warning detection"""
        critical_warnings = [
            "Essay is too short for grading",
            "Essay is too long and exceeds limit"
        ]
        
        advisory_warnings = [
            "Consider adding more evidence",
            "Use more formal language"
        ]
        
        for warning in critical_warnings:
            assert warning_generator.is_critical_warning(warning) is True
        
        for warning in advisory_warnings:
            assert warning_generator.is_critical_warning(warning) is False
    
    def test_categorize_warnings(self, warning_generator):
        """Test warning categorization"""
        warnings = [
            "Essay is too short for grading",  # Critical
            "Consider adding more evidence",   # Advisory
            "Essay is too long",              # Critical
            "Use more formal language"        # Advisory
        ]
        
        categorized = warning_generator.categorize_warnings(warnings)
        
        assert "critical" in categorized
        assert "advisory" in categorized
        assert "total_count" in categorized
        
        assert len(categorized["critical"]) == 2
        assert len(categorized["advisory"]) == 2
        assert categorized["total_count"] == 4
        
        # Check specific warnings are in correct categories
        assert "too short" in categorized["critical"][0]
        assert "too long" in categorized["critical"][1]
        assert "evidence" in categorized["advisory"][0]
        assert "formal" in categorized["advisory"][1]
    
    def test_warning_generation_all_essay_types(self, warning_generator, real_service_locator):
        """Test warning generation for all essay types"""
        analyzer = self.create_mock_text_analyzer()
        from app.services.base.protocols import TextAnalyzerProtocol
        real_service_locator.register_singleton(TextAnalyzerProtocol, analyzer)
        
        text = "Sample essay text"
        word_count = 300
        paragraph_count = 3
        
        for essay_type in [EssayType.DBQ, EssayType.LEQ, EssayType.SAQ]:
            warnings = warning_generator.generate_warnings(text, word_count, paragraph_count, essay_type)
            assert isinstance(warnings, list)
            # Each essay type should be able to generate warnings without errors
    
    def test_length_warnings_boundary_conditions(self, warning_generator, real_service_locator):
        """Test length warnings at boundary conditions"""
        test_cases = [
            # (essay_type, word_count, should_have_critical_warning)
            (EssayType.SAQ, 24, True),   # Just below critical threshold
            (EssayType.SAQ, 25, False),  # Exactly at critical threshold
            (EssayType.SAQ, 600, False), # Exactly at max limit
            (EssayType.SAQ, 601, True),  # Just above max limit
        ]
        
        for essay_type, word_count, should_have_critical in test_cases:
            warnings = warning_generator.generate_warnings("text", word_count, 1, essay_type)
            critical_warnings = [w for w in warnings if warning_generator.is_critical_warning(w)]
            
            if should_have_critical:
                assert len(critical_warnings) > 0, f"Expected critical warning for {essay_type} with {word_count} words"
            else:
                # Check if warning is critical (length-based) or just advisory
                length_critical = any("too short" in w.lower() or "too long" in w.lower() for w in warnings)
                assert not length_critical, f"Unexpected critical length warning for {essay_type} with {word_count} words"