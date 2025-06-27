import Foundation

// MARK: - Response Validation

class ResponseValidator {
    
    static func validateResponse(_ response: GradeResponse, for essayType: EssayType) -> ValidationResult {
        var issues: [String] = []
        var warnings: [String] = []
        
        // Validate score ranges
        if response.score < 0 || response.score > response.maxScore {
            issues.append("Invalid total score: \(response.score)/\(response.maxScore)")
        }
        
        if response.maxScore != essayType.maxScore {
            issues.append("Incorrect maximum score for \(essayType.rawValue)")
        }
        
        // Validate breakdown scores
        let breakdown = response.breakdown
        
        switch essayType {
        case .dbq, .leq:
            validateRubricItem(breakdown.thesis, expected: 1, name: "thesis", issues: &issues)
            validateRubricItem(breakdown.contextualization, expected: 1, name: "contextualization", issues: &issues)
            validateRubricItem(breakdown.evidence, expected: 2, name: "evidence", issues: &issues)
            validateRubricItem(breakdown.analysis, expected: 2, name: "analysis", issues: &issues)
            
        case .saq:
            // For SAQ, the structure is different but mapped to same fields
            validateRubricItem(breakdown.thesis, expected: 1, name: "partA", issues: &issues)
            validateRubricItem(breakdown.contextualization, expected: 1, name: "partB", issues: &issues)
            validateRubricItem(breakdown.evidence, expected: 1, name: "partC", issues: &issues)
        }
        
        // Validate feedback quality
        if response.overallFeedback.count < 50 {
            warnings.append("Overall feedback is quite brief")
        }
        
        if response.suggestions.count < 2 {
            warnings.append("Limited suggestions provided")
        }
        
        // Check for consistency
        let calculatedTotal = calculateTotalScore(from: response.breakdown, essayType: essayType)
        if calculatedTotal != response.score {
            issues.append("Score mismatch: reported \(response.score), calculated \(calculatedTotal)")
        }
        
        return ValidationResult(issues: issues, warnings: warnings)
    }
    
    private static func validateRubricItem(_ item: RubricItem, expected: Int, name: String, issues: inout [String]) {
        if item.maxScore != expected {
            issues.append("\(name): incorrect max score (\(item.maxScore), expected \(expected))")
        }
        if item.score < 0 || item.score > item.maxScore {
            issues.append("\(name): invalid score (\(item.score)/\(item.maxScore))")
        }
        if item.feedback.isEmpty {
            issues.append("\(name): missing feedback")
        }
    }
    
    private static func calculateTotalScore(from breakdown: GradeBreakdown, essayType: EssayType) -> Int {
        switch essayType {
        case .dbq, .leq:
            return breakdown.thesis.score + breakdown.contextualization.score + 
                   breakdown.evidence.score + breakdown.analysis.score
        case .saq:
            return breakdown.thesis.score + breakdown.contextualization.score + breakdown.evidence.score
        }
    }
}

// MARK: - Supporting Models

struct ValidationResult {
    let issues: [String]
    let warnings: [String]
}