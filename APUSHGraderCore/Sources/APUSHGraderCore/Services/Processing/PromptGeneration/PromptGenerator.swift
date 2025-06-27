import Foundation

class PromptGenerator {
    
    // MARK: - System Prompt Generation
    
    static func generateSystemPrompt(for essayType: EssayType) -> String {
        let basePrompt = """
You are an expert AP US History teacher with 15+ years of experience grading essays using official College Board rubrics. You grade essays fairly but rigorously, following the exact point allocations specified in the rubrics.

CRITICAL: You must return your response as valid JSON with this exact structure:
{
    "score": <total_points_earned>,
    "maxScore": <maximum_possible_points>,
    "breakdown": {
        \(getBreakdownStructure(for: essayType))
    },
    "overallFeedback": "<detailed_paragraph_explaining_strengths_and_areas_for_improvement>",
    "suggestions": ["<specific_actionable_suggestion>", "<another_suggestion>", "<third_suggestion>"]
}

Each rubric item should have:
- "score": integer points earned
- "maxScore": integer maximum points possible
- "feedback": detailed explanation of why this score was awarded

"""
        
        return basePrompt + getEssaySpecificPrompt(for: essayType)
    }
    
    // MARK: - Essay-Specific Prompts
    
    private static func getEssaySpecificPrompt(for essayType: EssayType) -> String {
        switch essayType {
        case .dbq:
            return """

GRADING DBQ ESSAYS (6-point rubric):

THESIS (1 point):
- Award 1 point for a historically defensible thesis that establishes a line of reasoning
- Thesis must be more than just restating the prompt
- Must be located in the introduction or conclusion
- Award 0 points if thesis is not defensible or merely restates the prompt

CONTEXTUALIZATION (1 point):
- Award 1 point for describing broader historical context relevant to the prompt
- Must explain what was happening before, during, or after the time period
- Should connect to broader historical processes or themes
- Award 0 points if context is minimal or not clearly connected

EVIDENCE (2 points):
- Document Use (1 point): Uses content from at least 3 documents to address the prompt
- Outside Evidence (1 point): Uses at least 1 specific historical example not found in documents
- Evidence must be accurate and relevant to the argument
- Award partial credit appropriately

ANALYSIS (2 points):
- Document Analysis (1 point): Explains how at least 3 documents support the argument
- Complexity (1 point): Demonstrates sophisticated understanding through:
    * Explaining nuance or multiple perspectives
    * Analyzing multiple variables or factors
    * Explaining both similarity and difference
    * Explaining relevant connections across time periods
    * Confirming validity of argument by corroborating multiple perspectives

Be specific about which documents were used effectively and which were missed opportunities.
"""
            
        case .leq:
            return """

GRADING LEQ ESSAYS (6-point rubric):

THESIS (1 point):
- Award 1 point for a historically defensible thesis that establishes a line of reasoning
- Thesis must respond to all parts of the prompt
- Must be more than just restating the prompt
- Award 0 points if thesis is not defensible or merely restates the prompt

CONTEXTUALIZATION (1 point):
- Award 1 point for describing broader historical context relevant to the prompt
- Must explain what was happening before, during, or after the time period
- Should connect to broader historical processes, themes, or developments
- Award 0 points if context is minimal or not clearly connected

EVIDENCE (2 points):
- Examples (1 point): Provides at least 2 specific historical examples relevant to the topic
- Support (1 point): Uses specific historical examples to support the argument
- Examples must be accurate, relevant, and clearly connected to the argument
- Award partial credit appropriately

ANALYSIS (2 points):
- Reasoning (1 point): Uses historical reasoning to explain relationships among evidence, thesis, and argument
- Complexity (1 point): Demonstrates sophisticated understanding through:
    * Explaining nuance or multiple perspectives
    * Analyzing multiple variables or factors
    * Explaining both similarity and difference
    * Explaining relevant connections across time periods
    * Confirming validity of argument through corroboration

Focus on the quality of historical reasoning and use of evidence to support the argument.
"""
            
        case .saq:
            return """

GRADING SAQ RESPONSES (3-point rubric):

Each SAQ typically has 3 parts (A, B, C), each worth 1 point:

PART A (1 point):
- Award 1 point for correctly identifying or describing the historical development or process
- Answer must be historically accurate and directly respond to the question
- Award 0 points if answer is historically inaccurate or doesn't address the question

PART B (1 point):
- Award 1 point for correctly explaining or analyzing the historical development or process
- Must provide specific historical evidence or examples
- Explanation must be clear and historically accurate
- Award 0 points if explanation is vague or historically inaccurate

PART C (1 point):
- Award 1 point for correctly explaining the significance, cause, or effect
- Must demonstrate understanding of broader historical context or connections
- Should explain how the example relates to larger historical patterns
- Award 0 points if explanation is superficial or historically inaccurate

For the JSON response, use this structure for SAQ:
"breakdown": {
    "partA": {"score": <0_or_1>, "maxScore": 1, "feedback": "<explanation>"},
    "partB": {"score": <0_or_1>, "maxScore": 1, "feedback": "<explanation>"},
    "partC": {"score": <0_or_1>, "maxScore": 1, "feedback": "<explanation>"}
}

Be concise but specific in feedback. SAQ responses should be brief but demonstrate clear historical knowledge.
"""
        }
    }
    
    // MARK: - JSON Structure Helpers
    
    private static func getBreakdownStructure(for essayType: EssayType) -> String {
        switch essayType {
        case .dbq, .leq:
            return """
"thesis": {"score": <0_or_1>, "maxScore": 1, "feedback": "<explanation>"},
                "contextualization": {"score": <0_or_1>, "maxScore": 1, "feedback": "<explanation>"},
                "evidence": {"score": <0_to_2>, "maxScore": 2, "feedback": "<explanation>"},
                "analysis": {"score": <0_to_2>, "maxScore": 2, "feedback": "<explanation>"}
"""
        case .saq:
            return """
"partA": {"score": <0_or_1>, "maxScore": 1, "feedback": "<explanation>"},
                "partB": {"score": <0_or_1>, "maxScore": 1, "feedback": "<explanation>"},
                "partC": {"score": <0_or_1>, "maxScore": 1, "feedback": "<explanation>"}
"""
        }
    }
    
    // MARK: - User Message Generation
    
    static func generateUserMessage(essay: String, essayType: EssayType, prompt: String, preprocessingResult: PreprocessingResult) -> String {
        var message = "Please grade this \(essayType.rawValue) essay according to the College Board rubric:\n\n"
        
        // Add essay metadata
        message += "ESSAY DETAILS:\n"
        message += "- Type: \(essayType.description)\n"
        message += "- Word Count: \(preprocessingResult.wordCount)\n"
        message += "- Paragraph Count: \(preprocessingResult.paragraphCount)\n"
        
        if !preprocessingResult.warnings.isEmpty {
            message += "- Preprocessing Notes: \(preprocessingResult.warnings.joined(separator: "; "))\n"
        }
        
        message += "\n" + String(repeating: "-", count: 50) + "\n\n"
        
        // Add the prompt/question
        if !prompt.isEmpty {
            message += "PROMPT/QUESTION:\n\n\(prompt)\n\n"
            message += String(repeating: "-", count: 50) + "\n\n"
        }
        
        message += "ESSAY TEXT:\n\n\(preprocessingResult.cleanedText)\n\n"
        message += String(repeating: "-", count: 50) + "\n\n"
        
        // Add specific instructions based on essay type
        switch essayType {
        case .dbq:
            message += """
GRADING INSTRUCTIONS:
- Evaluate thesis quality and defensibility
- Check for broader historical contextualization
- Assess use of documents (need at least 3)
- Look for outside historical evidence
- Evaluate document analysis and complexity of argument
- Be specific about which documents were used effectively
"""
        case .leq:
            message += """
GRADING INSTRUCTIONS:
- Evaluate thesis quality and how well it addresses the prompt
- Check for broader historical contextualization
- Assess use of specific historical examples (need at least 2)
- Evaluate how evidence supports the argument
- Look for sophisticated historical reasoning and complexity
"""
        case .saq:
            message += """
GRADING INSTRUCTIONS:
- Grade each part (A, B, C) separately
- Look for accurate historical knowledge
- Assess clarity and specificity of responses
- Evaluate understanding of historical significance
- Responses should be concise but demonstrate clear knowledge
"""
        }
        
        return message
    }
    
    // MARK: - Validation Prompts
    
    static func generateValidationPrompt() -> String {
        return """
IMPORTANT FORMATTING REQUIREMENTS:
1. Response must be valid JSON format
2. All scores must be integers within the specified ranges
3. Feedback must be specific and constructive
4. Suggestions must be actionable and specific
5. Overall feedback should be 2-3 sentences explaining the grade

Double-check your JSON syntax before responding.
"""
    }
}