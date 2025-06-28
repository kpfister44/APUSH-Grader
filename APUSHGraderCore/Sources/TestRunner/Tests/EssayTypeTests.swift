import Foundation
import APUSHGraderCore

public struct EssayTypeTests: TestRunnable {
    public init() {}
    
    public func runTests() -> TestSuite {
        let suite = TestSuite("EssayType")
        
        // Basic Properties Tests
        suite.addTest("Essay Type Descriptions") {
            suite.assertEqual(EssayType.dbq.description, "Document Based Question", "DBQ description")
            suite.assertEqual(EssayType.leq.description, "Long Essay Question", "LEQ description")
            suite.assertEqual(EssayType.saq.description, "Short Answer Question", "SAQ description")
        }
        
        suite.addTest("Max Scores") {
            suite.assertEqual(EssayType.dbq.maxScore, 6, "DBQ max score")
            suite.assertEqual(EssayType.leq.maxScore, 6, "LEQ max score")
            suite.assertEqual(EssayType.saq.maxScore, 3, "SAQ max score")
        }
        
        suite.addTest("Min Word Counts") {
            suite.assertEqual(EssayType.dbq.minWordCount, 400, "DBQ min word count")
            suite.assertEqual(EssayType.leq.minWordCount, 300, "LEQ min word count")
            suite.assertEqual(EssayType.saq.minWordCount, 50, "SAQ min word count")
        }
        
        suite.addTest("Min Heights") {
            suite.assertEqual(EssayType.dbq.minHeight, 200, "DBQ min height")
            suite.assertEqual(EssayType.leq.minHeight, 200, "LEQ min height")
            suite.assertEqual(EssayType.saq.minHeight, 100, "SAQ min height")
        }
        
        // Rubric Structure Tests
        suite.addTest("DBQ Rubric Structure") {
            let dbqRubric = EssayType.dbq.rubricStructure
            suite.assertEqual(dbqRubric["thesis"], 1, "DBQ thesis score")
            suite.assertEqual(dbqRubric["contextualization"], 1, "DBQ contextualization score")
            suite.assertEqual(dbqRubric["evidence"], 2, "DBQ evidence score")
            suite.assertEqual(dbqRubric["analysis"], 2, "DBQ analysis score")
            suite.assertEqual(dbqRubric.count, 4, "DBQ rubric item count")
        }
        
        suite.addTest("LEQ Rubric Structure") {
            let leqRubric = EssayType.leq.rubricStructure
            suite.assertEqual(leqRubric["thesis"], 1, "LEQ thesis score")
            suite.assertEqual(leqRubric["contextualization"], 1, "LEQ contextualization score")
            suite.assertEqual(leqRubric["evidence"], 2, "LEQ evidence score")
            suite.assertEqual(leqRubric["analysis"], 2, "LEQ analysis score")
            suite.assertEqual(leqRubric.count, 4, "LEQ rubric item count")
        }
        
        suite.addTest("SAQ Rubric Structure") {
            let saqRubric = EssayType.saq.rubricStructure
            suite.assertEqual(saqRubric["partA"], 1, "SAQ part A score")
            suite.assertEqual(saqRubric["partB"], 1, "SAQ part B score")
            suite.assertEqual(saqRubric["partC"], 1, "SAQ part C score")
            suite.assertEqual(saqRubric.count, 3, "SAQ rubric item count")
        }
        
        // Rubric Score Validation Tests
        suite.addTest("Rubric Scores Match Max Scores") {
            let dbqTotal = EssayType.dbq.rubricStructure.values.reduce(0, +)
            suite.assertEqual(dbqTotal, EssayType.dbq.maxScore, "DBQ rubric total matches max score")
            
            let leqTotal = EssayType.leq.rubricStructure.values.reduce(0, +)
            suite.assertEqual(leqTotal, EssayType.leq.maxScore, "LEQ rubric total matches max score")
            
            let saqTotal = EssayType.saq.rubricStructure.values.reduce(0, +)
            suite.assertEqual(saqTotal, EssayType.saq.maxScore, "SAQ rubric total matches max score")
        }
        
        // Placeholder Text Tests
        suite.addTest("Placeholder Texts Are Not Empty") {
            suite.assert(!EssayType.dbq.placeholderText.isEmpty, "DBQ placeholder text not empty")
            suite.assert(!EssayType.leq.placeholderText.isEmpty, "LEQ placeholder text not empty")
            suite.assert(!EssayType.saq.placeholderText.isEmpty, "SAQ placeholder text not empty")
            
            suite.assert(!EssayType.dbq.promptPlaceholderText.isEmpty, "DBQ prompt placeholder text not empty")
            suite.assert(!EssayType.leq.promptPlaceholderText.isEmpty, "LEQ prompt placeholder text not empty")
            suite.assert(!EssayType.saq.promptPlaceholderText.isEmpty, "SAQ prompt placeholder text not empty")
        }
        
        suite.addTest("Placeholder Texts Contain Relevant Keywords") {
            suite.assert(EssayType.dbq.placeholderText.contains("DBQ"), "DBQ placeholder contains 'DBQ'")
            suite.assert(EssayType.dbq.placeholderText.contains("documents"), "DBQ placeholder mentions documents")
            
            suite.assert(EssayType.leq.placeholderText.contains("LEQ"), "LEQ placeholder contains 'LEQ'")
            suite.assert(EssayType.leq.placeholderText.contains("thesis"), "LEQ placeholder mentions thesis")
            
            suite.assert(EssayType.saq.placeholderText.contains("short answer"), "SAQ placeholder mentions short answer")
            suite.assert(EssayType.saq.placeholderText.contains("concise"), "SAQ placeholder mentions being concise")
        }
        
        // Case Iteration Tests
        suite.addTest("All Cases Included") {
            let allCases = EssayType.allCases
            suite.assertEqual(allCases.count, 3, "Correct number of essay types")
            suite.assert(allCases.contains(.dbq), "Contains DBQ case")
            suite.assert(allCases.contains(.leq), "Contains LEQ case")
            suite.assert(allCases.contains(.saq), "Contains SAQ case")
        }
        
        // Raw Value Tests
        suite.addTest("Raw Values") {
            suite.assertEqual(EssayType.dbq.rawValue, "DBQ", "DBQ raw value")
            suite.assertEqual(EssayType.leq.rawValue, "LEQ", "LEQ raw value")
            suite.assertEqual(EssayType.saq.rawValue, "SAQ", "SAQ raw value")
        }
        
        suite.run()
        return suite
    }
}