import Foundation

// MARK: - Essay Processing Coordinator

class EssayProcessor {
    
    // MARK: - Main Processing Function
    
    static func preprocessEssay(_ text: String, for essayType: EssayType) -> PreprocessingResult {
        return TextAnalyzer.analyzeText(text, for: essayType)
    }
    
    // MARK: - Validation
    
    static func validateEssay(_ text: String, for essayType: EssayType) throws {
        try EssayValidator.validateEssay(text, for: essayType)
    }
}