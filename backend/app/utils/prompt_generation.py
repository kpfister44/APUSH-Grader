"""
Simplified prompt generation for AI grading.
Replaces complex service with direct functions.
"""

import logging
from app.models.core import EssayType
from app.models.processing import PreprocessingResult

logger = logging.getLogger(__name__)


def generate_grading_prompt(essay_text: str, essay_type: EssayType, prompt: str, preprocessing_result: PreprocessingResult) -> tuple[str, str]:
    """
    Generate system prompt and user message for AI grading.
    
    Returns:
        Tuple of (system_prompt, user_message)
    """
    system_prompt = _get_system_prompt(essay_type)
    user_message = _build_user_message(essay_text, essay_type, prompt, preprocessing_result)
    
    logger.info(f"Generated prompts for {essay_type.value} grading")
    return system_prompt, user_message


def _get_system_prompt(essay_type: EssayType) -> str:
    """Get system prompt for essay type"""
    
    base_prompt = """You are an expert AP US History teacher grading student essays. Provide detailed, constructive feedback following the official College Board rubrics.

IMPORTANT: Return your response as valid JSON with this exact structure:
{
    "score": <total_score_number>,
    "max_score": <maximum_possible_score>,
    "letter_grade": "<A/B/C/D/F>",
    "overall_feedback": "<comprehensive feedback>",
    "suggestions": ["<suggestion1>", "<suggestion2>", ...],
    "breakdown": {
        "thesis": {"score": <number>, "max_score": <number>, "feedback": "<feedback>"},
        "contextualization": {"score": <number>, "max_score": <number>, "feedback": "<feedback>"},
        "evidence": {"score": <number>, "max_score": <number>, "feedback": "<feedback>"},
        "analysis": {"score": <number>, "max_score": <number>, "feedback": "<feedback>"}
    }
}"""

    if essay_type == EssayType.DBQ:
        return base_prompt + """

DBQ RUBRIC (6 points total):
- Thesis (1 point): Clear, historically defensible thesis
- Contextualization (1 point): Broader historical context
- Evidence (2 points): Use of documents + outside evidence
- Analysis (2 points): Document analysis + complex understanding

Grade strictly but fairly. Provide specific, actionable feedback."""

    elif essay_type == EssayType.LEQ:
        return base_prompt + """

LEQ RUBRIC (6 points total):
- Thesis (1 point): Clear, historically defensible thesis
- Contextualization (1 point): Broader historical context  
- Evidence (2 points): Specific historical evidence
- Analysis (2 points): Historical reasoning + complex understanding

Grade strictly but fairly. Provide specific, actionable feedback."""

    elif essay_type == EssayType.SAQ:
        return """You are an expert AP US History teacher grading Short Answer Questions. 

IMPORTANT: Return your response as valid JSON with this exact structure:
{
    "score": <total_score_number>,
    "max_score": 3,
    "letter_grade": "<A/B/C/D/F>",
    "overall_feedback": "<comprehensive feedback>",
    "suggestions": ["<suggestion1>", "<suggestion2>", ...],
    "breakdown": {
        "thesis": {"score": <number>, "max_score": 1, "feedback": "<feedback>"},
        "contextualization": {"score": <number>, "max_score": 1, "feedback": "<feedback>"},
        "evidence": {"score": <number>, "max_score": 1, "feedback": "<feedback>"},
        "analysis": {"score": 0, "max_score": 0, "feedback": "Not applicable for SAQ"}
    }
}

SAQ RUBRIC (3 points total):
- Part A (1 point): Accurately answers the question
- Part B (1 point): Supports answer with specific evidence
- Part C (1 point): Explains how evidence supports the answer

Grade strictly but fairly. Provide specific, actionable feedback."""


def _build_user_message(essay_text: str, essay_type: EssayType, prompt: str, preprocessing_result: PreprocessingResult) -> str:
    """Build user message with essay content"""
    
    message = f"""ESSAY TYPE: {essay_type.value}

PROMPT: {prompt}

STUDENT ESSAY:
{essay_text}

ESSAY STATISTICS:
- Word count: {preprocessing_result.word_count}
- Paragraph count: {preprocessing_result.paragraph_count}"""

    if preprocessing_result.warnings:
        message += f"\n- Warnings: {len(preprocessing_result.warnings)} issues detected"

    message += f"""

Please grade this {essay_type.value} essay according to the rubric. Focus on:
1. Historical accuracy and evidence
2. Thesis clarity and argument strength
3. Use of specific examples
4. Writing quality and organization

Return ONLY valid JSON as specified in the system prompt."""

    return message