import Foundation

// MARK: - Text Analysis

public class TextAnalyzer {
    
    public static func analyzeText(_ text: String, for essayType: EssayType) -> PreprocessingResult {
        // Clean the text first
        let cleanedText = TextCleaner.cleanText(text)
        
        // Analyze the text
        let wordCount = countWords(in: cleanedText)
        let paragraphCount = countParagraphs(in: cleanedText)
        
        // Generate warnings using WarningGenerator
        let warnings = WarningGenerator.generateWarnings(
            text: cleanedText,
            wordCount: wordCount,
            paragraphCount: paragraphCount,
            essayType: essayType
        )
        
        return PreprocessingResult(
            cleanedText: cleanedText,
            wordCount: wordCount,
            paragraphCount: paragraphCount,
            warnings: warnings
        )
    }
    
    // MARK: - Basic Text Metrics
    
    public static func countWords(in text: String) -> Int {
        let words = text.components(separatedBy: .whitespacesAndNewlines)
        return words.filter { !$0.isEmpty }.count
    }
    
    public static func countParagraphs(in text: String) -> Int {
        let paragraphs = text.components(separatedBy: "\n\n")
        return paragraphs.filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }.count
    }
    
    public static func countSentences(in text: String) -> Int {
        let sentences = text.components(separatedBy: CharacterSet(charactersIn: ".!?"))
        return sentences.filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }.count
    }
    
    // MARK: - Content Analysis
    
    public static func getFirstParagraph(from text: String) -> String {
        let paragraphs = text.components(separatedBy: "\n\n")
        return paragraphs.first?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
    }
    
    public static func containsThesisIndicators(_ text: String) -> Bool {
        let thesisKeywords = [
            "argue", "argues", "argued", "thesis", "claim", "contend", "assert",
            "maintain", "demonstrate", "prove", "evidence suggests", "analysis reveals"
        ]
        let lowercaseText = text.lowercased()
        return thesisKeywords.contains { lowercaseText.contains($0) }
    }
    
    public static func containsEvidenceKeywords(_ text: String, for essayType: EssayType) -> Bool {
        let commonEvidence = [
            "document", "source", "evidence", "example", "instance", "case",
            "demonstrates", "illustrates", "shows", "reveals", "indicates"
        ]
        
        let historicalEvidence = [
            "act", "law", "treaty", "war", "battle", "president", "congress",
            "court", "amendment", "movement", "period", "era", "century"
        ]
        
        let lowercaseText = text.lowercased()
        let hasCommonEvidence = commonEvidence.contains { lowercaseText.contains($0) }
        let hasHistoricalEvidence = historicalEvidence.contains { lowercaseText.contains($0) }
        
        return hasCommonEvidence && hasHistoricalEvidence
    }
    
    public static func containsInformalLanguage(_ text: String) -> Bool {
        let informalWords = [
            "gonna", "wanna", "can't", "won't", "don't", "isn't", "aren't",
            "wasn't", "weren't", "hasn't", "haven't", "hadn't", "stuff", "things",
            "a lot of", "lots of", "tons of", "super", "really", "pretty much"
        ]
        let lowercaseText = text.lowercased()
        return informalWords.contains { lowercaseText.contains($0) }
    }
}
