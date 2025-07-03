"""
Tests for PromptGenerator service.

Validates essay-specific prompt generation, system prompts, and user message formatting.
"""

import pytest
from unittest.mock import Mock
import json

from app.services.processing.prompt.generator import PromptGenerator
from app.models.core.essay_types import EssayType
from app.models.processing.preprocessing import PreprocessingResult


class TestPromptGenerator:
    """Test suite for PromptGenerator service"""
    
    @pytest.fixture
    def prompt_generator(self):
        """Create PromptGenerator instance for testing"""
        return PromptGenerator()
    
    @pytest.fixture 
    def sample_preprocessing_result(self):
        """Create sample preprocessing result for testing"""
        return PreprocessingResult(
            cleaned_text="This is a cleaned essay text with proper formatting and analysis.",
            word_count=12,
            paragraph_count=1,
            warnings=["Warning: Essay may be too short"],
            is_valid=True
        )
    
    # System Prompt Generation Tests
    
    def test_generate_system_prompt_dbq(self, prompt_generator):
        """Test DBQ system prompt generation"""
        prompt = prompt_generator.generate_system_prompt(EssayType.DBQ)
        
        # Check base prompt components
        assert "expert AP US History teacher" in prompt
        assert "15 years of experience" in prompt
        assert "College Board rubrics" in prompt
        assert "JSON object" in prompt
        
        # Check DBQ-specific components
        assert "DBQ GRADING RUBRIC (6 points total)" in prompt
        assert "thesis" in prompt.lower()
        assert "contextualization" in prompt.lower()
        assert "evidence" in prompt.lower()
        assert "analysis" in prompt.lower()
        assert "Document-Based Question" in prompt or "documents" in prompt.lower()
        
        # Check breakdown structure
        assert '"thesis":' in prompt
        assert '"contextualization":' in prompt
        assert '"evidence":' in prompt
        assert '"analysis":' in prompt
        assert "maxScore" in prompt
        assert "feedback" in prompt
    
    def test_generate_system_prompt_leq(self, prompt_generator):
        """Test LEQ system prompt generation"""
        prompt = prompt_generator.generate_system_prompt(EssayType.LEQ)
        
        # Check base prompt components
        assert "expert AP US History teacher" in prompt
        assert "JSON object" in prompt
        
        # Check LEQ-specific components
        assert "LEQ GRADING RUBRIC (6 points total)" in prompt
        assert "Long Essay Question" in prompt or "historical reasoning" in prompt.lower()
        
        # Check 6-point structure
        assert '"thesis":' in prompt
        assert '"contextualization":' in prompt  
        assert '"evidence":' in prompt
        assert '"analysis":' in prompt
    
    def test_generate_system_prompt_saq(self, prompt_generator):
        """Test SAQ system prompt generation"""
        prompt = prompt_generator.generate_system_prompt(EssayType.SAQ)
        
        # Check base prompt components
        assert "expert AP US History teacher" in prompt
        assert "JSON object" in prompt
        
        # Check SAQ-specific components
        assert "SAQ GRADING RUBRIC (3 points total)" in prompt
        assert "Short Answer Question" in prompt or "three parts" in prompt.lower()
        
        # Check 3-point structure
        assert '"partA":' in prompt
        assert '"partB":' in prompt
        assert '"partC":' in prompt
    
    def test_system_prompt_json_structure(self, prompt_generator):
        """Test that system prompts define proper JSON response structure"""
        for essay_type in [EssayType.DBQ, EssayType.LEQ, EssayType.SAQ]:
            prompt = prompt_generator.generate_system_prompt(essay_type)
            
            # Check required JSON fields
            assert '"score":' in prompt
            assert '"maxScore":' in prompt
            assert '"breakdown":' in prompt
            assert '"overallFeedback":' in prompt
            assert '"suggestions":' in prompt
    
    # User Message Generation Tests
    
    def test_generate_user_message_basic(self, prompt_generator, sample_preprocessing_result):
        """Test basic user message generation"""
        essay_text = "Sample essay text for testing purposes."
        essay_type = EssayType.LEQ
        prompt = "Evaluate the impact of the American Revolution."
        
        user_message = prompt_generator.generate_user_message(
            essay_text, essay_type, prompt, sample_preprocessing_result
        )
        
        # Check message structure
        assert "ESSAY TO GRADE:" in user_message
        assert "Type:" in user_message
        assert "Word Count:" in user_message
        assert "Paragraph Count:" in user_message
        assert "Validation Status:" in user_message
        assert "PROMPT/QUESTION:" in user_message
        assert "ESSAY TEXT:" in user_message
        assert "GRADING INSTRUCTIONS" in user_message
        
        # Check content
        assert essay_type.value in user_message
        assert str(sample_preprocessing_result.word_count) in user_message
        assert str(sample_preprocessing_result.paragraph_count) in user_message
        assert prompt in user_message
        assert sample_preprocessing_result.cleaned_text in user_message
    
    def test_generate_user_message_with_warnings(self, prompt_generator):
        """Test user message generation with warnings"""
        preprocessing_result = PreprocessingResult(
            cleaned_text="Short essay text.",
            word_count=50,
            paragraph_count=1,
            warnings=["Essay is too short", "Missing thesis statement"],
            is_valid=False
        )
        
        user_message = prompt_generator.generate_user_message(
            "Essay text", EssayType.DBQ, "Test prompt", preprocessing_result
        )
        
        # Check warnings section
        assert "WARNINGS:" in user_message
        assert "- Essay is too short" in user_message
        assert "- Missing thesis statement" in user_message
        assert "Invalid" in user_message  # Validation status
    
    def test_generate_user_message_no_warnings(self, prompt_generator):
        """Test user message generation without warnings"""
        preprocessing_result = PreprocessingResult(
            cleaned_text="Valid essay text with sufficient length.",
            word_count=300,
            paragraph_count=3,
            warnings=[],
            is_valid=True
        )
        
        user_message = prompt_generator.generate_user_message(
            "Essay text", EssayType.LEQ, "Test prompt", preprocessing_result
        )
        
        # Should not have warnings section
        assert "WARNINGS:" not in user_message
        assert "Valid" in user_message  # Validation status
    
    def test_generate_user_message_essay_specific_instructions(self, prompt_generator, sample_preprocessing_result):
        """Test essay-specific grading instructions in user message"""
        
        # Test DBQ instructions
        dbq_message = prompt_generator.generate_user_message(
            "Essay", EssayType.DBQ, "Prompt", sample_preprocessing_result
        )
        assert "GRADING INSTRUCTIONS FOR THIS DBQ" in dbq_message
        assert "documents" in dbq_message.lower()
        assert "6 points total" in dbq_message
        
        # Test LEQ instructions
        leq_message = prompt_generator.generate_user_message(
            "Essay", EssayType.LEQ, "Prompt", sample_preprocessing_result
        )
        assert "GRADING INSTRUCTIONS FOR THIS LEQ" in leq_message
        assert "defensible thesis" in leq_message.lower()
        assert "6 points total" in leq_message
        
        # Test SAQ instructions
        saq_message = prompt_generator.generate_user_message(
            "Essay", EssayType.SAQ, "Prompt", sample_preprocessing_result
        )
        assert "GRADING INSTRUCTIONS FOR THIS SAQ" in saq_message
        assert "part A" in saq_message.lower() or "part (A" in saq_message
        assert "3 points total" in saq_message
    
    # Edge Cases and Validation Tests
    
    def test_generate_system_prompt_invalid_essay_type(self, prompt_generator):
        """Test system prompt generation with invalid essay type"""
        with pytest.raises(ValueError):
            prompt_generator.generate_system_prompt("INVALID")
    
    def test_generate_user_message_empty_text(self, prompt_generator, sample_preprocessing_result):
        """Test user message generation with empty essay text"""
        user_message = prompt_generator.generate_user_message(
            "", EssayType.DBQ, "Prompt", sample_preprocessing_result
        )
        
        # Should still generate valid message structure
        assert "ESSAY TO GRADE:" in user_message
        assert "ESSAY TEXT:" in user_message
        assert sample_preprocessing_result.cleaned_text in user_message
    
    def test_generate_user_message_long_prompt(self, prompt_generator, sample_preprocessing_result):
        """Test user message generation with very long prompt"""
        long_prompt = "This is a very long prompt " * 50  # 1400+ characters
        
        user_message = prompt_generator.generate_user_message(
            "Essay", EssayType.LEQ, long_prompt, sample_preprocessing_result
        )
        
        assert long_prompt in user_message
        assert "PROMPT/QUESTION:" in user_message
    
    # Content Validation Tests
    
    def test_dbq_prompt_contains_required_elements(self, prompt_generator):
        """Test DBQ prompt contains all required grading elements"""
        prompt = prompt_generator.generate_system_prompt(EssayType.DBQ)
        
        # Required DBQ elements
        required_elements = [
            "thesis",
            "contextualization", 
            "evidence",
            "analysis",
            "documents",
            "outside evidence",
            "line of reasoning",
            "historically defensible"
        ]
        
        prompt_lower = prompt.lower()
        for element in required_elements:
            assert element in prompt_lower, f"Missing required element: {element}"
    
    def test_leq_prompt_contains_required_elements(self, prompt_generator):
        """Test LEQ prompt contains all required grading elements"""
        prompt = prompt_generator.generate_system_prompt(EssayType.LEQ)
        
        # Required LEQ elements
        required_elements = [
            "thesis",
            "contextualization",
            "evidence", 
            "analysis",
            "historical reasoning",
            "defensible",
            "sophisticated"
        ]
        
        prompt_lower = prompt.lower()
        for element in required_elements:
            assert element in prompt_lower, f"Missing required element: {element}"
    
    def test_saq_prompt_contains_required_elements(self, prompt_generator):
        """Test SAQ prompt contains all required grading elements"""
        prompt = prompt_generator.generate_system_prompt(EssayType.SAQ)
        
        # Required SAQ elements
        required_elements = [
            "part a",
            "part b", 
            "part c",
            "identify",
            "explain",
            "significance"
        ]
        
        prompt_lower = prompt.lower()
        for element in required_elements:
            assert element in prompt_lower, f"Missing required element: {element}"
    
    # Integration Tests
    
    def test_prompt_generation_workflow(self, prompt_generator):
        """Test complete prompt generation workflow"""
        essay_text = "The American Revolution fundamentally transformed American society..."
        essay_type = EssayType.LEQ
        prompt = "Evaluate the extent to which the American Revolution changed American society."
        
        preprocessing_result = PreprocessingResult(
            cleaned_text=essay_text,
            word_count=len(essay_text.split()),
            paragraph_count=1,
            warnings=[],
            is_valid=True
        )
        
        # Generate both system and user prompts
        system_prompt = prompt_generator.generate_system_prompt(essay_type)
        user_message = prompt_generator.generate_user_message(
            essay_text, essay_type, prompt, preprocessing_result
        )
        
        # Validate both are non-empty and contain expected content
        assert len(system_prompt) > 500  # Should be substantial
        assert len(user_message) > 200   # Should contain all sections
        
        assert "LEQ" in system_prompt
        assert essay_type.value in user_message
        assert essay_text in user_message
        assert prompt in user_message
    
    def test_configuration_validation(self, prompt_generator):
        """Test prompt generator configuration validation"""
        # Should not raise exception for valid configuration
        prompt_generator._validate_configuration()
    
    # Performance and Memory Tests
    
    def test_multiple_prompt_generation_performance(self, prompt_generator, sample_preprocessing_result):
        """Test generating multiple prompts doesn't cause memory issues"""
        import time
        
        start_time = time.time()
        
        # Generate 100 prompts
        for i in range(100):
            essay_type = [EssayType.DBQ, EssayType.LEQ, EssayType.SAQ][i % 3]
            prompt_generator.generate_system_prompt(essay_type)
            prompt_generator.generate_user_message(
                f"Essay text {i}", essay_type, f"Prompt {i}", sample_preprocessing_result
            )
        
        elapsed = time.time() - start_time
        assert elapsed < 5.0  # Should complete quickly
    
    def test_prompt_consistency(self, prompt_generator):
        """Test that identical inputs produce identical outputs"""
        essay_type = EssayType.DBQ
        
        # Generate same prompt multiple times
        prompt1 = prompt_generator.generate_system_prompt(essay_type)
        prompt2 = prompt_generator.generate_system_prompt(essay_type)
        prompt3 = prompt_generator.generate_system_prompt(essay_type)
        
        # Should be identical
        assert prompt1 == prompt2 == prompt3
    
    def test_prompt_uniqueness_across_types(self, prompt_generator):
        """Test that different essay types produce different prompts"""
        dbq_prompt = prompt_generator.generate_system_prompt(EssayType.DBQ)
        leq_prompt = prompt_generator.generate_system_prompt(EssayType.LEQ)
        saq_prompt = prompt_generator.generate_system_prompt(EssayType.SAQ)
        
        # Should all be different
        assert dbq_prompt != leq_prompt
        assert leq_prompt != saq_prompt
        assert saq_prompt != dbq_prompt
        
        # But should share common base elements
        common_elements = ["expert AP US History teacher", "JSON object"]
        for element in common_elements:
            assert element in dbq_prompt
            assert element in leq_prompt
            assert element in saq_prompt