import Foundation

// MARK: - Mock API Service for Testing

public class MockAPIService: APIServiceProtocol {
    private let delay: TimeInterval
    
    public init(delay: TimeInterval = 2.0) {
        self.delay = delay
    }
    
    public func gradeEssay(_ essay: String, type: EssayType, prompt: String) async throws -> GradeResponse {
        // Simulate API delay
        try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
        
        // Return mock response with appropriate score for essay type
        let mockScore = type == .saq ? 2 : 4
        return GradeResponse(
            score: mockScore,
            maxScore: type.maxScore,
            breakdown: createMockBreakdown(for: type),
            overallFeedback: "This essay demonstrates good understanding of the topic with clear evidence and analysis. The thesis is well-developed and the argument is coherent throughout.",
            suggestions: [
                "Consider adding more specific historical examples",
                "Strengthen the conclusion by connecting to broader themes",
                "Improve transitions between paragraphs"
            ],
            warnings: nil
        )
    }
    
    private func createMockBreakdown(for type: EssayType) -> GradeBreakdown {
        switch type {
        case .dbq, .leq:
            return GradeBreakdown(
                thesis: RubricItem(score: 1, maxScore: 1, feedback: "Clear and defensible thesis"),
                contextualization: RubricItem(score: 1, maxScore: 1, feedback: "Good historical context"),
                evidence: RubricItem(score: 1, maxScore: 2, feedback: "Uses some evidence but could be stronger"),
                analysis: RubricItem(score: 1, maxScore: 2, feedback: "Shows analysis but lacks complexity")
            )
        case .saq:
            return GradeBreakdown(
                thesis: RubricItem(score: 1, maxScore: 1, feedback: "Part A answered correctly"),
                contextualization: RubricItem(score: 1, maxScore: 1, feedback: "Part B shows good understanding"),
                evidence: RubricItem(score: 0, maxScore: 1, feedback: "Part C needs more development"),
                analysis: RubricItem(score: 0, maxScore: 0, feedback: "")
            )
        }
    }
}