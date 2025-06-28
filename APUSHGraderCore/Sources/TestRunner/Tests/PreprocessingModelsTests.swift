import Foundation
import APUSHGraderCore

public struct PreprocessingModelsTests: TestRunnable {
    public init() {}
    
    public func runTests() -> TestSuite {
        let suite = TestSuite("PreprocessingModels")
        
        // Basic Properties Tests
        suite.addTest("Preprocessing Result Initialization") {
            let result = PreprocessingResult(
                cleanedText: "This is a test essay with multiple words.",
                wordCount: 8,
                paragraphCount: 1,
                warnings: ["Warning message"]
            )
            
            suite.assertEqual(result.cleanedText, "This is a test essay with multiple words.", "Cleaned text stored correctly")
            suite.assertEqual(result.wordCount, 8, "Word count stored correctly")
            suite.assertEqual(result.paragraphCount, 1, "Paragraph count stored correctly")
            suite.assertEqual(result.warnings.count, 1, "Warnings stored correctly")
            suite.assertEqual(result.warnings.first, "Warning message", "Warning message correct")
        }
        
        // Validation Logic Tests - No Warnings
        suite.addTest("Valid Result With No Warnings") {
            let validResult = PreprocessingResult(
                cleanedText: "A well-written essay with sufficient content.",
                wordCount: 7,
                paragraphCount: 1,
                warnings: []
            )
            
            suite.assert(validResult.isValid, "Result with no warnings should be valid")
        }
        
        // Validation Logic Tests - Non-Critical Warnings
        suite.addTest("Valid Result With Non-Critical Warnings") {
            let resultWithMinorWarnings = PreprocessingResult(
                cleanedText: "Essay text here.",
                wordCount: 3,
                paragraphCount: 1,
                warnings: ["Minor formatting issue", "Consider adding more details"]
            )
            
            suite.assert(resultWithMinorWarnings.isValid, "Result with non-critical warnings should be valid")
        }
        
        // Validation Logic Tests - "Too Short" Critical Warnings
        suite.addTest("Invalid Result With Too Short Warning") {
            let tooShortResult = PreprocessingResult(
                cleanedText: "Short",
                wordCount: 1,
                paragraphCount: 1,
                warnings: ["Essay is too short for accurate grading"]
            )
            
            suite.assert(!tooShortResult.isValid, "Result with 'too short' warning should be invalid")
        }
        
        suite.addTest("Invalid Result With Too Short Substring") {
            let tooShortResult = PreprocessingResult(
                cleanedText: "Brief essay",
                wordCount: 2,
                paragraphCount: 1,
                warnings: ["Content too short", "Add more evidence"]
            )
            
            suite.assert(!tooShortResult.isValid, "Result with 'too short' substring should be invalid")
        }
        
        // Validation Logic Tests - "Too Long" Critical Warnings
        suite.addTest("Invalid Result With Too Long Warning") {
            let tooLongResult = PreprocessingResult(
                cleanedText: "Very long essay content...",
                wordCount: 5000,
                paragraphCount: 20,
                warnings: ["Essay is too long and exceeds limits"]
            )
            
            suite.assert(!tooLongResult.isValid, "Result with 'too long' warning should be invalid")
        }
        
        suite.addTest("Invalid Result With Too Long Substring") {
            let tooLongResult = PreprocessingResult(
                cleanedText: "Extremely lengthy essay...",
                wordCount: 3000,
                paragraphCount: 15,
                warnings: ["Content too long for processing"]
            )
            
            suite.assert(!tooLongResult.isValid, "Result with 'too long' substring should be invalid")
        }
        
        // Validation Logic Tests - Mixed Warnings
        suite.addTest("Invalid Result With Mixed Critical And Non-Critical Warnings") {
            let mixedResult = PreprocessingResult(
                cleanedText: "Essay",
                wordCount: 1,
                paragraphCount: 1,
                warnings: ["Formatting issue", "Essay too short", "Consider revision"]
            )
            
            suite.assert(!mixedResult.isValid, "Result with any critical warning should be invalid")
        }
        
        suite.addTest("Valid Result With Multiple Non-Critical Warnings") {
            let multipleWarningsResult = PreprocessingResult(
                cleanedText: "A decent essay with some issues.",
                wordCount: 7,
                paragraphCount: 1,
                warnings: ["Minor grammar issue", "Consider stronger thesis", "Add more evidence"]
            )
            
            suite.assert(multipleWarningsResult.isValid, "Result with multiple non-critical warnings should be valid")
        }
        
        // Edge Cases Tests
        suite.addTest("Empty Text Edge Case") {
            let emptyResult = PreprocessingResult(
                cleanedText: "",
                wordCount: 0,
                paragraphCount: 0,
                warnings: ["No content provided"]
            )
            
            suite.assertEqual(emptyResult.cleanedText, "", "Empty text handled correctly")
            suite.assertEqual(emptyResult.wordCount, 0, "Zero word count handled correctly")
            suite.assertEqual(emptyResult.paragraphCount, 0, "Zero paragraph count handled correctly")
            suite.assert(emptyResult.isValid, "Empty text with non-critical warning should be valid")
        }
        
        suite.addTest("Zero Counts With Valid Text") {
            let zeroCountResult = PreprocessingResult(
                cleanedText: "Some text that was processed",
                wordCount: 0,
                paragraphCount: 0,
                warnings: []
            )
            
            suite.assert(!zeroCountResult.cleanedText.isEmpty, "Has cleaned text")
            suite.assertEqual(zeroCountResult.wordCount, 0, "Zero word count set correctly")
            suite.assertEqual(zeroCountResult.paragraphCount, 0, "Zero paragraph count set correctly")
            suite.assert(zeroCountResult.isValid, "Valid with no warnings")
        }
        
        // Case Sensitivity Tests
        suite.addTest("Case Sensitive Critical Warning Detection") {
            let upperCaseResult = PreprocessingResult(
                cleanedText: "Text",
                wordCount: 1,
                paragraphCount: 1,
                warnings: ["Essay TOO SHORT for processing"]
            )
            
            suite.assert(upperCaseResult.isValid, "Should NOT detect 'TOO SHORT' in uppercase (case sensitive)")
            
            let mixedCaseResult = PreprocessingResult(
                cleanedText: "Text",
                wordCount: 1000,
                paragraphCount: 50,
                warnings: ["Content Too Long for system"]
            )
            
            suite.assert(mixedCaseResult.isValid, "Should NOT detect 'Too Long' in mixed case (case sensitive)")
            
            // Test exact case matches
            let exactShortResult = PreprocessingResult(
                cleanedText: "Text",
                wordCount: 1,
                paragraphCount: 1,
                warnings: ["Essay too short for processing"]
            )
            
            suite.assert(!exactShortResult.isValid, "Should detect exact 'too short' in lowercase")
            
            let exactLongResult = PreprocessingResult(
                cleanedText: "Text",
                wordCount: 1000,
                paragraphCount: 50,
                warnings: ["Content too long for system"]
            )
            
            suite.assert(!exactLongResult.isValid, "Should detect exact 'too long' in lowercase")
        }
        
        // Boundary Tests
        suite.addTest("Warning Substring Boundary Cases") {
            let shortSubstringResult = PreprocessingResult(
                cleanedText: "Essay about shortage of time",
                wordCount: 6,
                paragraphCount: 1,
                warnings: ["Time shortage affected writing"]
            )
            
            suite.assert(shortSubstringResult.isValid, "Should not trigger on 'shortage' substring")
            
            let longSubstringResult = PreprocessingResult(
                cleanedText: "Essay about longevity",
                wordCount: 3,
                paragraphCount: 1,
                warnings: ["Discussion of longevity needs expansion"]
            )
            
            suite.assert(longSubstringResult.isValid, "Should not trigger on 'long' in 'longevity'")
        }
        
        // Multiple Critical Warnings Test
        suite.addTest("Multiple Critical Warnings") {
            let multipleCriticalResult = PreprocessingResult(
                cleanedText: "Bad essay",
                wordCount: 2,
                paragraphCount: 1,
                warnings: ["Essay too short", "Content too long somehow", "Also has issues"]
            )
            
            suite.assert(!multipleCriticalResult.isValid, "Should be invalid with multiple critical warnings")
        }
        
        // Large Data Tests
        suite.addTest("Large Counts And Multiple Warnings") {
            let largeDataResult = PreprocessingResult(
                cleanedText: "Very long essay content that goes on and on...",
                wordCount: 9999,
                paragraphCount: 999,
                warnings: Array(1...10).map { "Warning \($0)" }
            )
            
            suite.assertEqual(largeDataResult.wordCount, 9999, "Large word count handled correctly")
            suite.assertEqual(largeDataResult.paragraphCount, 999, "Large paragraph count handled correctly")
            suite.assertEqual(largeDataResult.warnings.count, 10, "Multiple warnings stored correctly")
            suite.assert(largeDataResult.isValid, "Valid with many non-critical warnings")
        }
        
        suite.run()
        return suite
    }
}