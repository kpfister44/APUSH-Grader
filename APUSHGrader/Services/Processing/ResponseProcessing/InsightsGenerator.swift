import Foundation

// MARK: - Insights Generation

class InsightsGenerator {
    
    static func generateInsights(from response: GradeResponse, essayType: EssayType) -> [GradingInsight] {
        var insights: [GradingInsight] = []
        
        // Performance level insight
        let performanceLevel = getOverallPerformanceLevel(response.percentageScore)
        insights.append(GradingInsight(
            type: .performance,
            title: "Overall Performance",
            message: "This essay demonstrates \(performanceLevel.lowercased()) understanding of APUSH concepts.",
            severity: getSeverityForPerformance(response.percentageScore)
        ))
        
        // Strength analysis
        let strengths = identifyStrengths(from: response.breakdown, essayType: essayType)
        if !strengths.isEmpty {
            insights.append(GradingInsight(
                type: .strength,
                title: "Key Strengths",
                message: "Strong performance in: \(strengths.joined(separator: ", "))",
                severity: .info
            ))
        }
        
        // Areas for improvement
        let improvements = identifyImprovements(from: response.breakdown, essayType: essayType)
        if !improvements.isEmpty {
            insights.append(GradingInsight(
                type: .improvement,
                title: "Focus Areas",
                message: "Consider improving: \(improvements.joined(separator: ", "))",
                severity: .warning
            ))
        }
        
        // Essay type specific insights
        insights.append(contentsOf: generateEssayTypeInsights(response, essayType: essayType))
        
        return insights
    }
    
    private static func identifyStrengths(from breakdown: GradeBreakdown, essayType: EssayType) -> [String] {
        var strengths: [String] = []
        
        switch essayType {
        case .dbq, .leq:
            if breakdown.thesis.isFullCredit { strengths.append("thesis development") }
            if breakdown.contextualization.isFullCredit { strengths.append("historical contextualization") }
            if breakdown.evidence.score >= breakdown.evidence.maxScore - 1 { strengths.append("use of evidence") }
            if breakdown.analysis.score >= breakdown.analysis.maxScore - 1 { strengths.append("historical analysis") }
            
        case .saq:
            if breakdown.thesis.isFullCredit { strengths.append("Part A response") }
            if breakdown.contextualization.isFullCredit { strengths.append("Part B response") }
            if breakdown.evidence.isFullCredit { strengths.append("Part C response") }
        }
        
        return strengths
    }
    
    private static func identifyImprovements(from breakdown: GradeBreakdown, essayType: EssayType) -> [String] {
        var improvements: [String] = []
        
        switch essayType {
        case .dbq, .leq:
            if breakdown.thesis.score < breakdown.thesis.maxScore { improvements.append("thesis clarity") }
            if breakdown.contextualization.score < breakdown.contextualization.maxScore { improvements.append("historical context") }
            if breakdown.evidence.score < breakdown.evidence.maxScore { improvements.append("evidence usage") }
            if breakdown.analysis.score < breakdown.analysis.maxScore { improvements.append("analytical complexity") }
            
        case .saq:
            if breakdown.thesis.score < breakdown.thesis.maxScore { improvements.append("Part A completeness") }
            if breakdown.contextualization.score < breakdown.contextualization.maxScore { improvements.append("Part B accuracy") }
            if breakdown.evidence.score < breakdown.evidence.maxScore { improvements.append("Part C development") }
        }
        
        return improvements
    }
    
    private static func generateEssayTypeInsights(_ response: GradeResponse, essayType: EssayType) -> [GradingInsight] {
        var insights: [GradingInsight] = []
        
        switch essayType {
        case .dbq:
            if response.breakdown.evidence.score < 2 {
                insights.append(GradingInsight(
                    type: .tip,
                    title: "DBQ Strategy",
                    message: "Remember to use at least 3 documents AND include outside historical evidence.",
                    severity: .info
                ))
            }
            
        case .leq:
            if response.breakdown.analysis.score < 2 {
                insights.append(GradingInsight(
                    type: .tip,
                    title: "LEQ Strategy", 
                    message: "Focus on sophisticated analysis - compare multiple perspectives or explain change over time.",
                    severity: .info
                ))
            }
            
        case .saq:
            if response.score < 3 {
                insights.append(GradingInsight(
                    type: .tip,
                    title: "SAQ Strategy",
                    message: "Ensure each part directly answers the question with specific historical evidence.",
                    severity: .info
                ))
            }
        }
        
        return insights
    }
    
    // MARK: - Helper Functions
    
    private static func getOverallPerformanceLevel(_ percentage: Double) -> String {
        switch percentage {
        case 90...100: return "Excellent"
        case 80..<90: return "Proficient"
        case 70..<80: return "Developing" 
        case 60..<70: return "Approaching"
        default: return "Beginning"
        }
    }
    
    private static func getSeverityForPerformance(_ percentage: Double) -> InsightSeverity {
        switch percentage {
        case 80...100: return .success
        case 60..<80: return .warning
        default: return .error
        }
    }
}

// MARK: - Supporting Models

struct GradingInsight {
    let type: InsightType
    let title: String
    let message: String
    let severity: InsightSeverity
}

enum InsightType {
    case performance, strength, improvement, tip, warning
}

enum InsightSeverity {
    case info, warning, error, success
}