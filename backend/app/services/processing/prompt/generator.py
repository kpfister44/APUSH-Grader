"""
Prompt generation service for AI essay grading.

Generates essay-specific prompts for DBQ, LEQ, and SAQ grading based on AP US History rubrics.
Migrated from Swift APUSHGraderCore PromptGenerator implementation.
"""

from typing import List
from abc import ABC, abstractmethod

from app.models.core.essay_types import EssayType
from app.models.processing.preprocessing import PreprocessingResult
from app.services.base.base_service import BaseService
from app.services.base.protocols import PromptGeneratorProtocol


class PromptGenerator(BaseService, PromptGeneratorProtocol):
    """
    Generates AI prompts for essay grading with essay-type specific instructions.
    
    Produces system prompts with detailed rubric instructions and user messages
    containing essay content and grading criteria.
    """
    
    def generate_system_prompt(self, essay_type: EssayType) -> str:
        """
        Generate system prompt with essay-specific grading instructions.
        
        Args:
            essay_type: The type of essay (DBQ, LEQ, SAQ)
            
        Returns:
            Complete system prompt string with base instructions and essay-specific criteria
        """
        base_prompt = self._get_base_system_prompt()
        essay_specific_prompt = self._get_essay_specific_grading_prompt(essay_type)
        
        return f"{base_prompt}\n\n{essay_specific_prompt}"
    
    def generate_user_message(
        self,
        essay_text: str, 
        essay_type: EssayType,
        prompt: str,
        preprocessing_result: PreprocessingResult
    ) -> str:
        """
        Generate user message containing essay content and metadata.
        
        Args:
            essay_text: The student's essay text
            essay_type: The type of essay (DBQ, LEQ, SAQ)  
            prompt: The essay question/prompt
            preprocessing_result: Results from essay preprocessing
            
        Returns:
            Complete user message with essay metadata, prompt, and content
        """
        # Format warnings for display
        warnings_text = ""
        if preprocessing_result.warnings:
            warnings_list = "\n".join([f"- {warning}" for warning in preprocessing_result.warnings])
            warnings_text = f"\n\nWARNINGS:\n{warnings_list}"
        
        # Create user message with all required information
        user_message = f"""ESSAY TO GRADE:

Type: {essay_type.value}
Word Count: {preprocessing_result.word_count}
Paragraph Count: {preprocessing_result.paragraph_count}
Validation Status: {"Valid" if preprocessing_result.is_valid else "Invalid"}{warnings_text}

PROMPT/QUESTION:
{prompt}

ESSAY TEXT:
{preprocessing_result.cleaned_text}

{self._get_essay_specific_user_instructions(essay_type)}"""

        return user_message
    
    def _get_base_system_prompt(self) -> str:
        """Get base system prompt with general grading instructions."""
        return """You are an expert AP US History teacher with over 15 years of experience grading AP exams. You will grade student essays following the official College Board rubrics with precision and consistency.

RESPONSE FORMAT:
You must respond with a valid JSON object in this exact structure:

{
  "score": <number>,
  "maxScore": <number>,
  "breakdown": {
    // Essay-specific breakdown structure (see below)
  },
  "overallFeedback": "<string>",
  "suggestions": [
    "<string>",
    "<string>"
  ]
}

GRADING PRINCIPLES:
- Use official College Board rubrics exactly
- Be strict but fair in your assessment
- Provide specific, actionable feedback
- Focus on historical accuracy and argument quality
- Award partial credit where appropriate
- Explain your reasoning clearly"""
    
    def _get_essay_specific_grading_prompt(self, essay_type: EssayType) -> str:
        """Get essay-specific grading criteria and breakdown structure."""
        if essay_type == EssayType.DBQ:
            return self._get_dbq_grading_prompt()
        elif essay_type == EssayType.LEQ:
            return self._get_leq_grading_prompt()
        elif essay_type == EssayType.SAQ:
            return self._get_saq_grading_prompt()
        else:
            raise ValueError(f"Unknown essay type: {essay_type}")
    
    def _get_dbq_grading_prompt(self) -> str:
        """Get DBQ-specific grading instructions and breakdown structure."""
        return """DBQ GRADING RUBRIC (6 points total):

BREAKDOWN STRUCTURE for DBQ:
"breakdown": {
  "thesis": {
    "score": <0 or 1>,
    "maxScore": 1,
    "feedback": "<specific feedback>"
  },
  "contextualization": {
    "score": <0 or 1>,
    "maxScore": 1, 
    "feedback": "<specific feedback>"
  },
  "evidence": {
    "score": <0, 1, or 2>,
    "maxScore": 2,
    "feedback": "<specific feedback>"
  },
  "analysis": {
    "score": <0, 1, or 2>,
    "maxScore": 2,
    "feedback": "<specific feedback>"
  }
}

GRADING CRITERIA:

1. THESIS (1 point):
   - Must respond to the prompt with a historically defensible thesis/claim
   - Must establish a line of reasoning
   - Cannot simply restate the prompt or be too vague

2. CONTEXTUALIZATION (1 point):
   - Must describe broader historical context relevant to the prompt
   - Must be more than just a brief mention
   - Should connect to events/processes before, during, or after the time period

3. EVIDENCE (2 points):
   - 1 point: Uses content from at least 3 documents to address the topic
   - 1 point: Uses at least 1 additional piece of outside evidence beyond the documents
   - Evidence must be specific and relevant

4. ANALYSIS (2 points):
   - 1 point: Explains how or why at least 3 documents are relevant to the argument
   - 1 point: Demonstrates complex understanding through analysis, connection, or sophistication"""
    
    def _get_leq_grading_prompt(self) -> str:
        """Get LEQ-specific grading instructions and breakdown structure."""
        return """LEQ GRADING RUBRIC (6 points total):

BREAKDOWN STRUCTURE for LEQ:
"breakdown": {
  "thesis": {
    "score": <0 or 1>,
    "maxScore": 1,
    "feedback": "<specific feedback>"
  },
  "contextualization": {
    "score": <0 or 1>,
    "maxScore": 1,
    "feedback": "<specific feedback>"
  },
  "evidence": {
    "score": <0, 1, or 2>,
    "maxScore": 2,
    "feedback": "<specific feedback>"
  },
  "analysis": {
    "score": <0, 1, or 2>,
    "maxScore": 2,
    "feedback": "<specific feedback>"
  }
}

GRADING CRITERIA:

1. THESIS (1 point):
   - Must respond to all parts of the prompt
   - Must present a defensible thesis or claim
   - Must establish a line of reasoning

2. CONTEXTUALIZATION (1 point):
   - Must describe broader historical context relevant to the prompt
   - Must be more than just a brief mention
   - Should situate the argument within broader historical events/processes

3. EVIDENCE (2 points):
   - 1 point: Provides specific historical examples relevant to the argument
   - 1 point: Uses historical evidence to support the argument (at least 2 examples)
   - Evidence must be accurate and clearly connected to the argument

4. ANALYSIS (2 points):
   - 1 point: Uses historical reasoning (comparison, causation, continuity/change)
   - 1 point: Demonstrates complex understanding through sophisticated argument, connections, or analysis"""
    
    def _get_saq_grading_prompt(self) -> str:
        """Get SAQ-specific grading instructions and breakdown structure.""" 
        return """SAQ GRADING RUBRIC (3 points total):

BREAKDOWN STRUCTURE for SAQ:
"breakdown": {
  "partA": {
    "score": <0 or 1>,
    "maxScore": 1,
    "feedback": "<specific feedback>"
  },
  "partB": {
    "score": <0 or 1>,
    "maxScore": 1,
    "feedback": "<specific feedback>"
  },
  "partC": {
    "score": <0 or 1>,
    "maxScore": 1,
    "feedback": "<specific feedback>"
  }
}

GRADING CRITERIA:

SAQs typically have three parts (A, B, C), each worth 1 point:

1. PART A (1 point):
   - Usually asks to identify, describe, or explain a historical development
   - Requires specific, accurate historical information
   - Must directly address what is asked

2. PART B (1 point):
   - Often asks to explain with specific evidence
   - Requires both explanation and supporting evidence
   - Must connect evidence to the explanation

3. PART C (1 point):
   - Typically asks to explain significance, cause, effect, or broader context
   - Requires analysis beyond simple description
   - Must demonstrate understanding of historical connections"""
    
    def _get_essay_specific_user_instructions(self, essay_type: EssayType) -> str:
        """Get essay-specific instructions for the user message."""
        if essay_type == EssayType.DBQ:
            return """GRADING INSTRUCTIONS FOR THIS DBQ:
- Look for a clear thesis that establishes a line of reasoning
- Check for contextualization that connects to broader historical context
- Verify use of at least 3 documents and 1 piece of outside evidence
- Assess document analysis and demonstration of complexity
- Award points based on College Board DBQ rubric (6 points total)"""
        
        elif essay_type == EssayType.LEQ:
            return """GRADING INSTRUCTIONS FOR THIS LEQ:
- Look for a defensible thesis that responds to all parts of the prompt
- Check for contextualization within broader historical events
- Verify specific historical examples (at least 2 for full evidence points)
- Assess historical reasoning and complexity of argument
- Award points based on College Board LEQ rubric (6 points total)"""
        
        elif essay_type == EssayType.SAQ:
            return """GRADING INSTRUCTIONS FOR THIS SAQ:
- Grade each part (A, B, C) separately for 1 point each
- Look for specific, accurate historical information
- Check that explanations are supported with evidence where required
- Assess whether responses directly address what is asked
- Award points based on College Board SAQ rubric (3 points total)"""
        
        else:
            raise ValueError(f"Unknown essay type: {essay_type}")