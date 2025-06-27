import Foundation

// MARK: - Warning Generation

class WarningGenerator {
    
    static func generateWarnings(
        text: String,
        wordCount: Int,
        paragraphCount: Int,
        essayType: EssayType
    ) -> [String] {
        var warnings: [String] = []
        
        // Word count warnings
        let minWords = essayType.minWordCount
        let maxWords = getMaxWordCount(for: essayType)
        
        if wordCount < minWords {
            warnings.append("Essay may be too short (\(wordCount)/\(minWords)+ words)")
        } else if wordCount > maxWords {
            warnings.append("Essay may be too long (\(wordCount)/\(maxWords) words max)")
        }
        
        // Structure warnings
        switch essayType {
        case .dbq, .leq:
            if paragraphCount < 3 {
                warnings.append("Consider adding more paragraphs (introduction, body, conclusion)")
            }
            
            // Check for thesis-like statement in first paragraph
            let firstParagraph = TextAnalyzer.getFirstParagraph(from: text)
            if !TextAnalyzer.containsThesisIndicators(firstParagraph) {
                warnings.append("Consider adding a clear thesis statement in your introduction")
            }
            
            // Check for evidence keywords
            if !TextAnalyzer.containsEvidenceKeywords(text, for: essayType) {
                warnings.append("Consider including more specific historical evidence")
            }
            
        case .saq:
            if paragraphCount > 3 && wordCount > 200 {
                warnings.append("SAQ responses should be concise - consider shortening")
            }
        }
        
        if TextAnalyzer.containsInformalLanguage(text) {
            warnings.append("Consider using more formal academic language")
        }
        
        return warnings
    }
    
    // MARK: - Helper Functions
    
    private static func getMaxWordCount(for essayType: EssayType) -> Int {
        switch essayType {
        case .dbq: return 1200
        case .leq: return 1000
        case .saq: return 300
        }
    }
}
