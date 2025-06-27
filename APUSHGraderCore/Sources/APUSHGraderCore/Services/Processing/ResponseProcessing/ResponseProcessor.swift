import Foundation
import SwiftUI

// MARK: - Response Processing Coordinator

public class ResponseProcessor {
    
    // MARK: - Main Processing Function
    
    public static func processGradingResponse(_ response: GradeResponse, for essayType: EssayType) -> ProcessedGradingResult {
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

public struct ProcessedGradingResult {
    public let originalResponse: GradeResponse
    public let formattedText: String
    public let insights: [GradingInsight]
    public let validationIssues: [String]
    public let displayData: GradeDisplayData
    
    public init(originalResponse: GradeResponse, formattedText: String, insights: [GradingInsight], validationIssues: [String], displayData: GradeDisplayData) {
        self.originalResponse = originalResponse
        self.formattedText = formattedText
        self.insights = insights
        self.validationIssues = validationIssues
        self.displayData = displayData
    }
}