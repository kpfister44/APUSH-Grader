import Foundation

// MARK: - Core Grading Models

struct GradeResponse: Codable {
    let score: Int
    let maxScore: Int
    let breakdown: GradeBreakdown
    let overallFeedback: String
    let suggestions: [String]
    let warnings: [String]?
    
    var percentageScore: Double {
        return Double(score) / Double(maxScore) * 100
    }
    
    var letterGrade: String {
        let percentage = percentageScore
        switch percentage {
        case 90...100: return "A"
        case 80..<90: return "B"
        case 70..<80: return "C"
        case 60..<70: return "D"
        default: return "F"
        }
    }
}

struct GradeBreakdown: Codable {
    let thesis: RubricItem
    let contextualization: RubricItem
    let evidence: RubricItem
    let analysis: RubricItem
    let complexity: RubricItem?  // Optional for SAQ
    
    init(thesis: RubricItem, contextualization: RubricItem, evidence: RubricItem, analysis: RubricItem, complexity: RubricItem? = nil) {
        self.thesis = thesis
        self.contextualization = contextualization
        self.evidence = evidence
        self.analysis = analysis
        self.complexity = complexity
    }
}

struct RubricItem: Codable {
    let score: Int
    let maxScore: Int
    let feedback: String
    
    var isFullCredit: Bool {
        return score == maxScore
    }
    
    var performanceLevel: String {
        let percentage = Double(score) / Double(maxScore)
        switch percentage {
        case 1.0: return "Excellent"
        case 0.8..<1.0: return "Proficient"
        case 0.5..<0.8: return "Developing"
        default: return "Needs Improvement"
        }
    }
}

// MARK: - Error Types

enum GradingError: LocalizedError {
    case invalidResponse
    case invalidScore
    case networkError(String)
    case apiKeyMissing
    case rateLimitExceeded
    case essayTooShort
    case essayTooLong
    case parseError(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Received invalid response from grading service"
        case .invalidScore:
            return "Received invalid score from grading service"
        case .networkError(let message):
            return "Network error: \(message)"
        case .apiKeyMissing:
            return "API key is missing. Please check your configuration"
        case .rateLimitExceeded:
            return "Rate limit exceeded. Please try again later"
        case .essayTooShort:
            return "Essay is too short for accurate grading"
        case .essayTooLong:
            return "Essay exceeds maximum length"
        case .parseError(let message):
            return "Failed to parse response: \(message)"
        }
    }
}