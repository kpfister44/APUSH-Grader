import Foundation

// MARK: - Preprocessing Models

struct PreprocessingResult {
    let cleanedText: String
    let wordCount: Int
    let paragraphCount: Int
    let warnings: [String]
    let isValid: Bool
    
    init(cleanedText: String, wordCount: Int, paragraphCount: Int, warnings: [String]) {
        self.cleanedText = cleanedText
        self.wordCount = wordCount
        self.paragraphCount = paragraphCount
        self.warnings = warnings
        self.isValid = warnings.isEmpty || warnings.allSatisfy { !$0.contains("too short") && !$0.contains("too long") }
    }
}