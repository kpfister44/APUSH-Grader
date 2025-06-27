import Foundation

// MARK: - Core Grading Models

public struct GradeResponse: Codable {
    public let score: Int
    public let maxScore: Int
    public let breakdown: GradeBreakdown
    public let overallFeedback: String
    public let suggestions: [String]
    public let warnings: [String]?
    
    public init(score: Int, maxScore: Int, breakdown: GradeBreakdown, overallFeedback: String, suggestions: [String], warnings: [String]? = nil) {
        self.score = score
        self.maxScore = maxScore
        self.breakdown = breakdown
        self.overallFeedback = overallFeedback
        self.suggestions = suggestions
        self.warnings = warnings
    }
    
    public var percentageScore: Double {
        return Double(score) / Double(maxScore) * 100
    }
    
    public var letterGrade: String {
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

public struct GradeBreakdown: Codable {
    public let thesis: RubricItem
    public let contextualization: RubricItem
    public let evidence: RubricItem
    public let analysis: RubricItem
    public let complexity: RubricItem?  // Optional for SAQ
    
    public init(thesis: RubricItem, contextualization: RubricItem, evidence: RubricItem, analysis: RubricItem, complexity: RubricItem? = nil) {
        self.thesis = thesis
        self.contextualization = contextualization
        self.evidence = evidence
        self.analysis = analysis
        self.complexity = complexity
    }
}

public struct RubricItem: Codable {
    public let score: Int
    public let maxScore: Int
    public let feedback: String
    
    public init(score: Int, maxScore: Int, feedback: String) {
        self.score = score
        self.maxScore = maxScore
        self.feedback = feedback
    }
    
    public var isFullCredit: Bool {
        return score == maxScore
    }
    
    public var performanceLevel: String {
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

public enum GradingError: LocalizedError {
    case invalidResponse
    case invalidScore
    case networkError(String)
    case apiKeyMissing
    case rateLimitExceeded
    case essayTooShort
    case essayTooLong
    case parseError(String)
    
    public var errorDescription: String? {
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