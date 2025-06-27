import Foundation

// MARK: - Essay Validation

class EssayValidator {
    
    static func validateEssay(_ text: String, for essayType: EssayType) throws {
        let result = TextAnalyzer.analyzeText(text, for: essayType)
        
        if result.cleanedText.isEmpty {
            throw GradingError.essayTooShort
        }
        
        if result.wordCount < essayType.minWordCount / 2 {
            throw GradingError.essayTooShort
        }
        
        let maxWords = getMaxWordCount(for: essayType)
        if result.wordCount > maxWords * 2 {
            throw GradingError.essayTooLong
        }
    }
    
    private static func getMaxWordCount(for essayType: EssayType) -> Int {
        switch essayType {
        case .dbq: return 1200
        case .leq: return 1000
        case .saq: return 300
        }
    }
}