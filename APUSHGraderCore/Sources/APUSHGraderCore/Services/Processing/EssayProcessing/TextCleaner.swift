import Foundation

// MARK: - Text Cleaning

public class TextCleaner {
    
    public static func cleanText(_ text: String) -> String {
        var cleaned = text
        
        // Remove excessive whitespace while preserving paragraph breaks
        cleaned = cleaned.replacingOccurrences(of: "\\s+", with: " ", options: .regularExpression)
        cleaned = cleaned.replacingOccurrences(of: "\\n\\s*\\n", with: "\n\n", options: .regularExpression)
        
        // Trim leading and trailing whitespace
        cleaned = cleaned.trimmingCharacters(in: .whitespacesAndNewlines)
        
        // Remove common artifacts from copy-paste
        cleaned = cleaned.replacingOccurrences(of: "\u{201C}", with: "\"") // Left double quote
        cleaned = cleaned.replacingOccurrences(of: "\u{201D}", with: "\"") // Right double quote
        cleaned = cleaned.replacingOccurrences(of: "\u{2018}", with: "'")  // Left single quote
        cleaned = cleaned.replacingOccurrences(of: "\u{2019}", with: "'")  // Right single quote
        cleaned = cleaned.replacingOccurrences(of: "\u{2013}", with: "-")  // En dash
        cleaned = cleaned.replacingOccurrences(of: "\u{2014}", with: "-")  // Em dash
        
        return cleaned
    }
}