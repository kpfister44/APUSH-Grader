import Foundation

// MARK: - Preprocessing Models

public struct PreprocessingResult {
    public let cleanedText: String
    public let wordCount: Int
    public let paragraphCount: Int
    public let warnings: [String]
    public let isValid: Bool
    
    public init(cleanedText: String, wordCount: Int, paragraphCount: Int, warnings: [String]) {
        self.cleanedText = cleanedText
        self.wordCount = wordCount
        self.paragraphCount = paragraphCount
        self.warnings = warnings
        self.isValid = warnings.isEmpty || warnings.allSatisfy { !$0.contains("too short") && !$0.contains("too long") }
    }
}