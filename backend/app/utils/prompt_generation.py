"""
Simplified prompt generation for AI grading.
Replaces complex service with direct functions.
"""

import logging
from app.models.core import EssayType, SAQType, RubricType
from app.models.processing import PreprocessingResult

logger = logging.getLogger(__name__)


def generate_grading_prompt(essay_text: str, essay_type: EssayType, prompt: str, preprocessing_result: PreprocessingResult, saq_type: SAQType = None, rubric_type: RubricType = RubricType.COLLEGE_BOARD) -> tuple[str, str]:
    """
    Generate system prompt and user message for AI grading.
    
    Args:
        essay_text: The essay text to grade
        essay_type: Type of essay (DBQ, LEQ, SAQ)
        prompt: The original prompt/question
        preprocessing_result: Essay preprocessing results
        saq_type: SAQ subtype (only used when essay_type is SAQ)
        rubric_type: Rubric type for SAQ essays (defaults to College Board)
    
    Returns:
        Tuple of (system_prompt, user_message)
    """
    system_prompt = _get_system_prompt(essay_type, saq_type, rubric_type)
    user_message = _build_user_message(essay_text, essay_type, prompt, preprocessing_result)
    
    rubric_info = f" ({rubric_type.value})" if essay_type == EssayType.SAQ and rubric_type != RubricType.COLLEGE_BOARD else ""
    logger.info(f"Generated prompts for {essay_type.value} grading" + (f" ({saq_type.value})" if saq_type else "") + rubric_info)
    return system_prompt, user_message


def _get_system_prompt(essay_type: EssayType, saq_type: SAQType = None, rubric_type: RubricType = RubricType.COLLEGE_BOARD) -> str:
    """Get system prompt for essay type, SAQ subtype, and rubric type"""
    
    base_prompt = """You are an expert AP US History teacher grading student essays. Provide detailed, constructive feedback following the official College Board rubrics.

IMPORTANT: Return your response as valid JSON with this exact structure:
{
    "score": <total_score_number>,
    "max_score": <maximum_possible_score>,
    "letter_grade": "<A/B/C/D/F>",
    "overall_feedback": "<encouraging, student-friendly comprehensive feedback that starts with strengths, uses accessible language, and provides specific actionable suggestions for improvement>",
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

FEEDBACK TONE GUIDELINES:
- Begin overall feedback by acknowledging student efforts and identifying strengths
- Use encouraging, supportive language appropriate for high school students
- Avoid overly academic jargon; use clear, accessible terminology
- Frame criticism constructively with specific examples and suggestions
- End with actionable next steps for improvement
- Balance honesty about areas needing work with motivation to continue learning

Grade strictly but fairly. Provide specific, actionable feedback."""

    elif essay_type == EssayType.LEQ:
        return base_prompt + """

LEQ RUBRIC (6 points total):
- Thesis (1 point): Clear, historically defensible thesis
- Contextualization (1 point): Broader historical context  
- Evidence (2 points): Specific historical evidence
- Analysis (2 points): Historical reasoning + complex understanding

FEEDBACK TONE GUIDELINES:
- Begin overall feedback by acknowledging student efforts and identifying strengths
- Use encouraging, supportive language appropriate for high school students
- Avoid overly academic jargon; use clear, accessible terminology
- Frame criticism constructively with specific examples and suggestions
- End with actionable next steps for improvement
- Balance honesty about areas needing work with motivation to continue learning

Grade strictly but fairly. Provide specific, actionable feedback."""

    elif essay_type == EssayType.SAQ:
        return _get_saq_system_prompt(saq_type, rubric_type)


def _get_saq_system_prompt(saq_type: SAQType = None, rubric_type: RubricType = RubricType.COLLEGE_BOARD) -> str:
    """Get SAQ-specific system prompt based on SAQ type and rubric type"""
    
    # Handle EG rubric first
    if rubric_type == RubricType.EG:
        return _get_eg_rubric_prompt()
    
    # Default to College Board rubric
    
    base_saq_prompt = """You are an expert AP US History teacher grading Short Answer Questions. 

IMPORTANT: Return your response as valid JSON with this exact structure:
{
    "score": <total_score_number>,
    "max_score": 3,
    "letter_grade": "<A/B/C/D/F>",
    "overall_feedback": "<encouraging, student-friendly comprehensive feedback that starts with strengths, uses accessible language, and provides specific actionable suggestions for improvement>",
    "suggestions": ["<suggestion1>", "<suggestion2>", ...],
    "breakdown": {
        "part_a": {"score": <number>, "max_score": 1, "feedback": "<feedback>"},
        "part_b": {"score": <number>, "max_score": 1, "feedback": "<feedback>"},
        "part_c": {"score": <number>, "max_score": 1, "feedback": "<feedback>"}
    }
}

FEEDBACK TONE GUIDELINES:
- Use encouraging, student-friendly language
- Acknowledge what the student did well before addressing areas for improvement
- Provide specific, actionable suggestions rather than general criticism
- Use clear, accessible language appropriate for high school students
- Frame feedback as opportunities for growth rather than failures"""

    if saq_type == SAQType.STIMULUS:
        return base_saq_prompt + """

STIMULUS SAQ RUBRIC (3 points total):
- Part A (1 point): Accurately identifies or describes information from the provided source
- Part B (1 point): Explains using specific evidence, incorporating source material appropriately
- Part C (1 point): Analyzes significance or connections, demonstrating understanding of source context

GRADING FOCUS:
- Evaluate how well the student uses the provided source material
- Assess source analysis skills and historical contextualization
- Look for proper integration of source evidence with historical knowledge
- Reward accurate interpretation of primary/secondary source content

Grade strictly but fairly. Provide specific, actionable feedback."""

    elif saq_type == SAQType.NON_STIMULUS:
        return base_saq_prompt + """

NON-STIMULUS SAQ RUBRIC (3 points total):
- Part A (1 point): Accurately identifies or describes historical information
- Part B (1 point): Explains with specific historical evidence and examples
- Part C (1 point): Analyzes significance, causation, or historical connections

GRADING FOCUS:
- Evaluate depth of historical content knowledge
- Assess quality and specificity of historical evidence provided
- Look for accurate historical facts, dates, names, and events
- Reward demonstration of historical thinking skills without source material

Grade strictly but fairly. Provide specific, actionable feedback."""

    elif saq_type == SAQType.SECONDARY_COMPARISON:
        return base_saq_prompt + """

SECONDARY COMPARISON SAQ RUBRIC (3 points total):
- Part A (1 point): Accurately identifies differences/similarities between historical interpretations
- Part B (1 point): Provides specific evidence supporting one interpretation
- Part C (1 point): Provides specific evidence supporting the other interpretation or analyzes the debate

GRADING FOCUS:
- Evaluate understanding of historiographical perspectives and debates
- Assess ability to distinguish between different historical interpretations
- Look for specific evidence that supports each interpretation
- Reward analysis of how evidence can support different conclusions

Grade strictly but fairly. Provide specific, actionable feedback."""

    else:
        # Default SAQ prompt for backward compatibility
        return base_saq_prompt + """

SAQ RUBRIC (3 points total):
- Part A (1 point): Accurately answers the question
- Part B (1 point): Supports answer with specific evidence
- Part C (1 point): Explains how evidence supports the answer

Grade strictly but fairly. Provide specific, actionable feedback."""


def _get_eg_rubric_prompt() -> str:
    """Get EG rubric system prompt (10-point A/C/E criteria)"""
    
    return """You are an expert AP US History teacher grading Short Answer Questions using the EG Rubric.

IMPORTANT: Return your response as valid JSON with this exact structure:
{
    "score": <total_score_number>,
    "max_score": 10,
    "letter_grade": "<A/B/C/D/F>",
    "overall_feedback": "<encouraging, student-friendly comprehensive feedback that starts with strengths, uses accessible language, and provides specific actionable suggestions for improvement>",
    "suggestions": ["<suggestion1>", "<suggestion2>", ...],
    "breakdown": {
        "criterion_a": {"score": <number>, "max_score": 1, "feedback": "<feedback>"},
        "criterion_c": {"score": <number>, "max_score": 3, "feedback": "<feedback>"},
        "criterion_e": {"score": <number>, "max_score": 6, "feedback": "<feedback>"}
    }
}

FEEDBACK TONE GUIDELINES:
- Use encouraging, student-friendly language
- Acknowledge what the student did well before addressing areas for improvement
- Provide specific, actionable suggestions rather than general criticism
- Use clear, accessible language appropriate for high school students
- Frame feedback as opportunities for growth rather than failures

EG RUBRIC (10 points total):
- **Criterion A: Addresses the prompt, Written in complete sentences** (1 point total)
  - **PRIMARY FOCUS:** Student gets this 1 point if ALL THREE parts (a, b, c) directly address what the prompt is asking
  - **SECONDARY CONSIDERATION:** Writing should demonstrate clear communication (complete thoughts, understandable responses)
  - **LENIENT APPROACH:** Prioritize content over perfect grammar - students can earn this point even with minor sentence structure issues if they clearly address all parts of the prompt
  - If any part completely fails to address the prompt OR is completely incomprehensible, award 0 points for Criterion A
  - Focus on: "Did they answer what was asked?" rather than "Is every sentence grammatically perfect?"

- **Criterion C: Cites specific evidence** (3 points total)
  - 1 point each for questions #1A, #1B, #1C
  - **CRITICAL TIME PERIOD REQUIREMENT:** Evidence must be from the specific time period mentioned in the prompt
  - If evidence is from outside the prompt's time period, award 0 points for that part, even if evidence is otherwise accurate and relevant
  - Must provide specific historical facts, names, dates, events from the correct time period
  - Evidence must be relevant and accurate within the designated timeframe

- **Criterion E: Explains the evidence thoroughly, Proves you know history!** (6 points total)
  - 1-2 points each for questions #1A, #1B, #1C
  - Must thoroughly explain how evidence supports the answer
  - Must demonstrate deep understanding of historical context
  - Must show connections between evidence and historical significance

GRADING FOCUS:
- For Criterion A: Evaluate ALL THREE parts together - award point if all parts address the prompt, even with minor grammar issues
- For Criterion C: Strictly enforce time period requirements - no points for out-of-period evidence
- Evaluate depth of historical knowledge and explanation
- Assess quality and specificity of evidence provided within correct timeframe
- Look for thorough analysis that proves historical understanding
- Reward clear writing and direct addressing of prompts

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