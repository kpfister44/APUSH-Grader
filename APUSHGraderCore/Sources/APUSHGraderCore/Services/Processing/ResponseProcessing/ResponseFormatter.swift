import Foundation
import SwiftUI

// MARK: - Response Display Formatting

class ResponseFormatter {
    
    static func formatForDisplay(_ response: GradeResponse, validationResults: ValidationResult) -> String {
        var formatted = ""
        
        // Header with score
        formatted += "📊 **Grade: \(response.score)/\(response.maxScore)** (\(Int(response.percentageScore))% - \(response.letterGrade))\n\n"
        
        // Validation issues (if any)
        if !validationResults.issues.isEmpty {
            formatted += "⚠️ **Validation Issues:**\n"
            for issue in validationResults.issues {
                formatted += "• \(issue)\n"
            }
            formatted += "\n"
        }
        
        // Warnings (preprocessing + validation)
        let allWarnings = (response.warnings ?? []) + validationResults.warnings
        if !allWarnings.isEmpty {
            formatted += "⚠️ **Notes:**\n"
            for warning in allWarnings {
                formatted += "• \(warning)\n"
            }
            formatted += "\n"
        }
        
        // Detailed breakdown
        formatted += "📋 **Detailed Breakdown:**\n\n"
        formatted += formatBreakdown(response.breakdown, for: determineEssayType(from: response))
        
        // Overall feedback
        formatted += "\n💬 **Overall Feedback:**\n\(response.overallFeedback)\n\n"
        
        // Suggestions
        if !response.suggestions.isEmpty {
            formatted += "💡 **Suggestions for Improvement:**\n"
            for (index, suggestion) in response.suggestions.enumerated() {
                formatted += "\(index + 1). \(suggestion)\n"
            }
        }
        
        return formatted
    }
    
    private static func formatBreakdown(_ breakdown: GradeBreakdown, for essayType: EssayType) -> String {
        var formatted = ""
        
        switch essayType {
        case .dbq, .leq:
            formatted += formatRubricItem("Thesis", breakdown.thesis)
            formatted += formatRubricItem("Contextualization", breakdown.contextualization)
            formatted += formatRubricItem("Evidence", breakdown.evidence)
            formatted += formatRubricItem("Analysis & Reasoning", breakdown.analysis)
            
        case .saq:
            formatted += formatRubricItem("Part A", breakdown.thesis)
            formatted += formatRubricItem("Part B", breakdown.contextualization)
            formatted += formatRubricItem("Part C", breakdown.evidence)
        }
        
        return formatted
    }
    
    private static func formatRubricItem(_ name: String, _ item: RubricItem) -> String {
        let emoji = item.isFullCredit ? "✅" : (item.score > 0 ? "🔶" : "❌")
        let performance = item.performanceLevel
        
        return """
\(emoji) **\(name): \(item.score)/\(item.maxScore)** (\(performance))
   \(item.feedback)

"""
    }
    
    // MARK: - Display Data Creation
    
    static func createDisplayData(from response: GradeResponse, insights: [GradingInsight]) -> GradeDisplayData {
        return GradeDisplayData(
            scoreText: "\(response.score)/\(response.maxScore)",
            percentageText: "\(Int(response.percentageScore))%",
            letterGrade: response.letterGrade,
            performanceColor: getPerformanceColor(response.percentageScore),
            breakdownItems: createBreakdownDisplayItems(response.breakdown),
            insights: insights
        )
    }
    
    private static func createBreakdownDisplayItems(_ breakdown: GradeBreakdown) -> [BreakdownDisplayItem] {
        return [
            BreakdownDisplayItem(breakdown.thesis, name: "Thesis"),
            BreakdownDisplayItem(breakdown.contextualization, name: "Context"),
            BreakdownDisplayItem(breakdown.evidence, name: "Evidence"),
            BreakdownDisplayItem(breakdown.analysis, name: "Analysis")
        ]
    }
    
    private static func getPerformanceColor(_ percentage: Double) -> Color {
        switch percentage {
        case 90...100: return .green
        case 80..<90: return .blue
        case 70..<80: return .orange
        case 60..<70: return .yellow
        default: return .red
        }
    }
    
    // MARK: - Helper Functions
    
    private static func determineEssayType(from response: GradeResponse) -> EssayType {
        // Determine based on max score and structure
        if response.maxScore == 6 {
            return .dbq // Could be LEQ too, but formatting is the same
        } else {
            return .saq
        }
    }
}

// MARK: - Supporting Models

public struct GradeDisplayData {
    public let scoreText: String
    public let percentageText: String
    public let letterGrade: String
    public let performanceColor: Color
    public let breakdownItems: [BreakdownDisplayItem]
    public let insights: [GradingInsight]
    
    public init(scoreText: String, percentageText: String, letterGrade: String, performanceColor: Color, breakdownItems: [BreakdownDisplayItem], insights: [GradingInsight]) {
        self.scoreText = scoreText
        self.percentageText = percentageText
        self.letterGrade = letterGrade
        self.performanceColor = performanceColor
        self.breakdownItems = breakdownItems
        self.insights = insights
    }
}

public struct BreakdownDisplayItem {
    public let name: String
    public let score: Int
    public let maxScore: Int
    public let feedback: String
    public let performanceLevel: String
    public let isFullCredit: Bool
    
    public init(_ rubricItem: RubricItem, name: String) {
        self.name = name
        self.score = rubricItem.score
        self.maxScore = rubricItem.maxScore
        self.feedback = rubricItem.feedback
        self.performanceLevel = rubricItem.performanceLevel
        self.isFullCredit = rubricItem.isFullCredit
    }
}