import Foundation

// MARK: - Essay Processing Coordinator

public class EssayProcessor {
    
    // MARK: - Main Processing Function
    
    public static func preprocessEssay(_ text: String, for essayType: EssayType) -> PreprocessingResult {
        return TextAnalyzer.analyzeText(text, for: essayType)
    }
    
    // MARK: - Validation
    
    public static func validateEssay(_ text: String, for essayType: EssayType) throws {
        try EssayValidator.validateEssay(text, for: essayType)
    }
}