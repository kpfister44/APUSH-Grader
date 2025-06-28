import Foundation
import APUSHGraderCore

public struct GradeModelsTests: TestRunnable {
    public init() {}
    
    public func runTests() -> TestSuite {
        let suite = TestSuite("GradeModels")
        
        // Helper method for creating sample breakdown
        func createSampleBreakdown() -> GradeBreakdown {
            return GradeBreakdown(
                thesis: RubricItem(score: 1, maxScore: 1, feedback: "Clear thesis"),
                contextualization: RubricItem(score: 1, maxScore: 1, feedback: "Good context"),
                evidence: RubricItem(score: 1, maxScore: 2, feedback: "Some evidence"),
                analysis: RubricItem(score: 1, maxScore: 2, feedback: "Basic analysis"),
                complexity: nil
            )
        }
        
        // GradeResponse Tests
        suite.addTest("Grade Response Percentage Calculation") {
            let gradeResponse = GradeResponse(
                score: 4,
                maxScore: 6,
                breakdown: createSampleBreakdown(),
                overallFeedback: "Good work",
                suggestions: ["Improve thesis"]
            )
            
            let expectedPercentage = (4.0 / 6.0) * 100
            suite.assertApproxEqual(gradeResponse.percentageScore, expectedPercentage, "Percentage calculation")
        }
        
        suite.addTest("Grade Response Letter Grades") {
            // Test A grade (90-100%)
            let gradeA = GradeResponse(score: 6, maxScore: 6, breakdown: createSampleBreakdown(), overallFeedback: "", suggestions: [])
            suite.assertEqual(gradeA.letterGrade, "A", "Perfect score gets A")
            
            let gradeAMinus = GradeResponse(score: 27, maxScore: 30, breakdown: createSampleBreakdown(), overallFeedback: "", suggestions: [])
            suite.assertEqual(gradeAMinus.letterGrade, "A", "90% gets A")
            
            // Test B grade (80-89%)
            let gradeB = GradeResponse(score: 5, maxScore: 6, breakdown: createSampleBreakdown(), overallFeedback: "", suggestions: [])
            suite.assertEqual(gradeB.letterGrade, "B", "83% gets B")
            
            let gradeBEdge = GradeResponse(score: 24, maxScore: 30, breakdown: createSampleBreakdown(), overallFeedback: "", suggestions: [])
            suite.assertEqual(gradeBEdge.letterGrade, "B", "80% gets B")
            
            // Test C grade (70-79%)
            let gradeCActual = GradeResponse(score: 22, maxScore: 30, breakdown: createSampleBreakdown(), overallFeedback: "", suggestions: [])
            suite.assertEqual(gradeCActual.letterGrade, "C", "73% gets C")
            
            // Test D grade (60-69%) - 4/6 = 66.67%
            let gradeD = GradeResponse(score: 4, maxScore: 6, breakdown: createSampleBreakdown(), overallFeedback: "", suggestions: [])
            suite.assertEqual(gradeD.letterGrade, "D", "67% gets D")
            
            let gradeDEdge = GradeResponse(score: 18, maxScore: 30, breakdown: createSampleBreakdown(), overallFeedback: "", suggestions: [])
            suite.assertEqual(gradeDEdge.letterGrade, "D", "60% gets D")
            
            // Test F grade (<60%)
            let gradeF = GradeResponse(score: 2, maxScore: 6, breakdown: createSampleBreakdown(), overallFeedback: "", suggestions: [])
            suite.assertEqual(gradeF.letterGrade, "F", "33% gets F")
        }
        
        suite.addTest("Grade Response With Warnings") {
            let gradeWithWarnings = GradeResponse(
                score: 3,
                maxScore: 6,
                breakdown: createSampleBreakdown(),
                overallFeedback: "Needs work",
                suggestions: ["Add more evidence"],
                warnings: ["Essay too short", "Missing citations"]
            )
            
            suite.assert(gradeWithWarnings.warnings != nil, "Has warnings")
            suite.assertEqual(gradeWithWarnings.warnings?.count, 2, "Correct warning count")
            suite.assertEqual(gradeWithWarnings.warnings?.first, "Essay too short", "Correct first warning")
        }
        
        suite.addTest("Grade Response Without Warnings") {
            let gradeWithoutWarnings = GradeResponse(
                score: 5,
                maxScore: 6,
                breakdown: createSampleBreakdown(),
                overallFeedback: "Excellent work",
                suggestions: []
            )
            
            suite.assert(gradeWithoutWarnings.warnings == nil, "No warnings when not provided")
        }
        
        // RubricItem Tests
        suite.addTest("Rubric Item Full Credit") {
            let fullCreditItem = RubricItem(score: 2, maxScore: 2, feedback: "Perfect!")
            suite.assert(fullCreditItem.isFullCredit, "Full credit detection")
            
            let partialCreditItem = RubricItem(score: 1, maxScore: 2, feedback: "Good effort")
            suite.assert(!partialCreditItem.isFullCredit, "Partial credit detection")
            
            let noCreditItem = RubricItem(score: 0, maxScore: 2, feedback: "Missing")
            suite.assert(!noCreditItem.isFullCredit, "No credit detection")
        }
        
        suite.addTest("Rubric Item Performance Levels") {
            // Test Excellent (100%)
            let excellent = RubricItem(score: 2, maxScore: 2, feedback: "Perfect")
            suite.assertEqual(excellent.performanceLevel, "Excellent", "100% is Excellent")
            
            // Test Proficient (80-99%)
            let proficient = RubricItem(score: 4, maxScore: 5, feedback: "Very good")
            suite.assertEqual(proficient.performanceLevel, "Proficient", "80% is Proficient")
            
            let proficientHigh = RubricItem(score: 9, maxScore: 10, feedback: "Almost perfect")
            suite.assertEqual(proficientHigh.performanceLevel, "Proficient", "90% is Proficient")
            
            // Test Developing (50-79%)
            let developing = RubricItem(score: 3, maxScore: 5, feedback: "Getting there")
            suite.assertEqual(developing.performanceLevel, "Developing", "60% is Developing")
            
            let developingHigh = RubricItem(score: 7, maxScore: 10, feedback: "Making progress")
            suite.assertEqual(developingHigh.performanceLevel, "Developing", "70% is Developing")
            
            // Test Needs Improvement (<50%)
            let needsImprovement = RubricItem(score: 1, maxScore: 3, feedback: "Needs work")
            suite.assertEqual(needsImprovement.performanceLevel, "Needs Improvement", "33% is Needs Improvement")
            
            let needsImprovementZero = RubricItem(score: 0, maxScore: 2, feedback: "Missing")
            suite.assertEqual(needsImprovementZero.performanceLevel, "Needs Improvement", "0% is Needs Improvement")
        }
        
        // GradingError Tests
        suite.addTest("Grading Error Descriptions") {
            suite.assertEqual(GradingError.invalidResponse.errorDescription, "Received invalid response from grading service", "Invalid response error")
            suite.assertEqual(GradingError.invalidScore.errorDescription, "Received invalid score from grading service", "Invalid score error")
            suite.assertEqual(GradingError.networkError("Connection failed").errorDescription, "Network error: Connection failed", "Network error with message")
            suite.assertEqual(GradingError.apiKeyMissing.errorDescription, "API key is missing. Please check your configuration", "API key missing error")
            suite.assertEqual(GradingError.rateLimitExceeded.errorDescription, "Rate limit exceeded. Please try again later", "Rate limit error")
            suite.assertEqual(GradingError.essayTooShort.errorDescription, "Essay is too short for accurate grading", "Essay too short error")
            suite.assertEqual(GradingError.essayTooLong.errorDescription, "Essay exceeds maximum length", "Essay too long error")
            suite.assertEqual(GradingError.parseError("JSON error").errorDescription, "Failed to parse response: JSON error", "Parse error with message")
        }
        
        // Edge Case Tests
        suite.addTest("Edge Cases") {
            let zeroGrade = GradeResponse(
                score: 0,
                maxScore: 6,
                breakdown: createSampleBreakdown(),
                overallFeedback: "No points earned",
                suggestions: ["Start over"]
            )
            
            suite.assertEqual(zeroGrade.percentageScore, 0.0, "Zero score percentage")
            suite.assertEqual(zeroGrade.letterGrade, "F", "Zero score gets F")
            
            let perfectGrade = GradeResponse(
                score: 6,
                maxScore: 6,
                breakdown: createSampleBreakdown(),
                overallFeedback: "Perfect!",
                suggestions: []
            )
            
            suite.assertEqual(perfectGrade.percentageScore, 100.0, "Perfect score percentage")
            suite.assertEqual(perfectGrade.letterGrade, "A", "Perfect score gets A")
        }
        
        suite.run()
        return suite
    }
}