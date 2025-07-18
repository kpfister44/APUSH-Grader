import Foundation
import SwiftUI

// MARK: - Essay Type

enum EssayType: String, CaseIterable {
    case dbq = "DBQ"
    case leq = "LEQ"
    case saq = "SAQ"
    
    var displayName: String {
        switch self {
        case .dbq: return "DBQ (Document-Based Question)"
        case .leq: return "LEQ (Long Essay Question)"
        case .saq: return "SAQ (Short Answer Question)"
        }
    }
    
    var maxScore: Int {
        switch self {
        case .dbq, .leq: return 6
        case .saq: return 3
        }
    }
    
    var promptPlaceholderText: String {
        switch self {
        case .dbq:
            return "Enter the DBQ prompt and document descriptions..."
        case .leq:
            return "Enter the Long Essay Question prompt..."
        case .saq:
            return "Enter the Short Answer Question prompt..."
        }
    }
    
    var placeholderText: String {
        switch self {
        case .dbq:
            return "Enter your DBQ essay response here. Use the documents provided to support your argument..."
        case .leq:
            return "Enter your Long Essay Question response here. Develop a clear thesis and support it with historical evidence..."
        case .saq:
            return "Enter your Short Answer Question response here. Be concise and specific..."
        }
    }
    
    var minHeight: CGFloat {
        switch self {
        case .dbq, .leq: return 200
        case .saq: return 120
        }
    }
}

// MARK: - SAQ Type

enum SAQType: String, CaseIterable {
    case stimulus = "stimulus"
    case nonStimulus = "non_stimulus"
    case secondaryComparison = "secondary_comparison"
    
    var displayName: String {
        switch self {
        case .stimulus:
            return "Source Analysis"
        case .nonStimulus:
            return "Content Question"
        case .secondaryComparison:
            return "Historical Comparison"
        }
    }
    
    var description: String {
        switch self {
        case .stimulus:
            return "Analyzes primary or secondary source documents"
        case .nonStimulus:
            return "Tests historical content knowledge without sources"
        case .secondaryComparison:
            return "Compares different historical interpretations"
        }
    }
}

// MARK: - SAQ Multi-Part Support

struct SAQParts: Codable {
    let partA: String
    let partB: String
    let partC: String
    
    enum CodingKeys: String, CodingKey {
        case partA = "part_a"
        case partB = "part_b"
        case partC = "part_c"
    }
    
    init(partA: String, partB: String, partC: String) {
        self.partA = partA.trimmingCharacters(in: .whitespacesAndNewlines)
        self.partB = partB.trimmingCharacters(in: .whitespacesAndNewlines)
        self.partC = partC.trimmingCharacters(in: .whitespacesAndNewlines)
    }
    
    var isEmpty: Bool {
        return partA.isEmpty || partB.isEmpty || partC.isEmpty
    }
    
    var combinedText: String {
        return """
        A) \(partA)

        B) \(partB)

        C) \(partC)
        """
    }
}

// MARK: - Simple Response Models

struct APIGradingResult {
    let score: Int
    let maxScore: Int
    let percentage: Double
    let letterGrade: String
    let performanceLevel: String
    let breakdown: [String: APIRubricItem]
    let overallFeedback: String
    let suggestions: [String]
    let warnings: [String]
    let wordCount: Int
    let paragraphCount: Int
    
    // Convert from NetworkService response
    init(from response: GradingResponse) {
        self.score = response.score
        self.maxScore = response.maxScore
        self.percentage = response.percentage
        self.letterGrade = response.letterGrade
        self.performanceLevel = response.performanceLevel
        self.breakdown = response.breakdown.mapValues { APIRubricItem(from: $0) }
        self.overallFeedback = response.overallFeedback
        self.suggestions = response.suggestions
        self.warnings = response.warnings
        self.wordCount = response.wordCount
        self.paragraphCount = response.paragraphCount
    }
}

struct APIRubricItem {
    let score: Int
    let maxScore: Int
    let feedback: String
    
    var isFullCredit: Bool {
        return score == maxScore
    }
    
    // Convert from NetworkService response
    init(from response: RubricItemResponse) {
        self.score = response.score
        self.maxScore = response.maxScore
        self.feedback = response.feedback
    }
}

// MARK: - Display Data

struct APIGradeDisplayData {
    let scoreText: String
    let percentageText: String
    let letterGrade: String
    let performanceColor: Color
    
    init(from result: APIGradingResult) {
        self.scoreText = "\(result.score)/\(result.maxScore)"
        self.percentageText = String(format: "%.1f%%", result.percentage)
        self.letterGrade = result.letterGrade
        
        // Color based on performance level
        switch result.performanceLevel.lowercased() {
        case "excellent":
            self.performanceColor = .green
        case "proficient":
            self.performanceColor = .blue
        case "developing":
            self.performanceColor = .orange
        case "inadequate":
            self.performanceColor = .red
        default:
            self.performanceColor = .gray
        }
    }
}

// MARK: - Insights (simplified)

enum APIInsightType {
    case performance
    case strength
    case improvement
    case tip
    case warning
}

enum APIInsightSeverity {
    case info
    case warning
    case error
    case success
}

struct APIGradingInsight {
    let type: APIInsightType
    let title: String
    let message: String
    let severity: APIInsightSeverity
    
    // Generate insights from API response
    static func generateInsights(from result: APIGradingResult) -> [APIGradingInsight] {
        var insights: [APIGradingInsight] = []
        
        // Performance insight
        let performanceInsight = APIGradingInsight(
            type: .performance,
            title: "Overall Performance",
            message: "Scored \(result.score)/\(result.maxScore) (\(result.performanceLevel))",
            severity: result.percentage >= 80 ? .success : (result.percentage >= 60 ? .info : .warning)
        )
        insights.append(performanceInsight)
        
        // Strength insights from high-scoring rubric items
        for (rubricName, item) in result.breakdown {
            if item.isFullCredit {
                let strengthInsight = APIGradingInsight(
                    type: .strength,
                    title: "\(rubricName.capitalized) Strength",
                    message: "Full credit achieved",
                    severity: .success
                )
                insights.append(strengthInsight)
            }
        }
        
        // Improvement insights from low-scoring rubric items
        for (rubricName, item) in result.breakdown {
            if item.score < item.maxScore {
                let improvementInsight = APIGradingInsight(
                    type: .improvement,
                    title: "\(rubricName.capitalized) Improvement",
                    message: "Consider strengthening this area",
                    severity: .warning
                )
                insights.append(improvementInsight)
            }
        }
        
        // Warning insights
        for warning in result.warnings {
            let warningInsight = APIGradingInsight(
                type: .warning,
                title: "Warning",
                message: warning,
                severity: .warning
            )
            insights.append(warningInsight)
        }
        
        return insights
    }
}

// MARK: - Processed Result (for UI compatibility)

struct APIProcessedGradingResult {
    let originalResponse: APIGradingResult
    let formattedText: String
    let insights: [APIGradingInsight]
    let validationIssues: [String]
    let displayData: APIGradeDisplayData
    
    init(from apiResult: APIGradingResult) {
        self.originalResponse = apiResult
        self.formattedText = Self.formatResult(apiResult)
        self.insights = APIGradingInsight.generateInsights(from: apiResult)
        self.validationIssues = apiResult.warnings
        self.displayData = APIGradeDisplayData(from: apiResult)
    }
    
    private static func formatResult(_ result: APIGradingResult) -> String {
        var formatted = "Score: \(result.score)/\(result.maxScore) (\(result.letterGrade))\n"
        formatted += "Performance Level: \(result.performanceLevel)\n\n"
        formatted += "Overall Feedback:\n\(result.overallFeedback)\n\n"
        
        if !result.suggestions.isEmpty {
            formatted += "Suggestions:\n"
            for (index, suggestion) in result.suggestions.enumerated() {
                formatted += "\(index + 1). \(suggestion)\n"
            }
        }
        
        return formatted
    }
}