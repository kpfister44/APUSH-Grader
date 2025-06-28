import Foundation
import APUSHGraderCore

// MARK: - Test Runner Coordinator
func main() {
    TestFramework.printHeader()
    
    // Initialize test suites
    let testSuites: [TestRunnable] = [
        EssayTypeTests(),
        GradeModelsTests(),
        APIModelsTests(),
        PreprocessingModelsTests(),
        EssayProcessingTests()
    ]
    
    var totalPassed = 0
    var totalFailed = 0
    var results: [(String, TestSuite)] = []
    
    // Run all test suites
    for testRunner in testSuites {
        let suite = testRunner.runTests()
        results.append((suite.name, suite))
        totalPassed += suite.passedTests
        totalFailed += suite.failedTests
    }
    
    // Print detailed results by suite
    if !results.isEmpty {
        print("\n📋 Results by Test Suite:")
        for (name, suite) in results {
            let icon = TestFramework.sectionIcon(for: name)
            let status = suite.failedTests == 0 ? "✅" : "❌"
            print("\(status) \(icon) \(name): \(suite.passedTests) passed, \(suite.failedTests) failed")
        }
    }
    
    // Print summary and exit
    TestFramework.printSummary(totalPassed: totalPassed, totalFailed: totalFailed)
    
    if totalFailed == 0 {
        exit(0)
    } else {
        exit(1)
    }
}

// Run the test coordinator
main()