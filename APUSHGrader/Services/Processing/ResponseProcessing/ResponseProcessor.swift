import Foundation
import SwiftUI

// MARK: - Response Processing Coordinator

class ResponseProcessor {
    
    // MARK: - Main Processing Function
    
    static func processGradingResponse(_ response: GradeResponse, for essayType: EssayType) -> ProcessedGradingResult {
        // Validate the response
        let validationResults = ResponseValidator.validateResponse(response, for: essayType)
        
        // Format for display
        let formattedResult = ResponseFormatter.formatForDisplay(response, validationResults: validationResults)
        
        // Generate insights
        let insights = InsightsGenerator.generateInsights(from: response, essayType: essayType)
        
        return ProcessedGradingResult(
            originalResponse: response,
            formattedText: formattedResult,
            insights: insights,
            validationIssues: validationResults.issues,
            displayData: ResponseFormatter.createDisplayData(from: response, insights: insights)
        )
    }
}

// MARK: - Supporting Data Structures

struct ProcessedGradingResult {
    let originalResponse: GradeResponse
    let formattedText: String
    let insights: [GradingInsight]
    let validationIssues: [String]
    let displayData: GradeDisplayData
}