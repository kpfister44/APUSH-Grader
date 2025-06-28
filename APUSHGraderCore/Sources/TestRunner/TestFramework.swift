import Foundation

// MARK: - Test Framework
public class TestSuite {
    public let name: String
    private var tests: [(String, () -> Void)] = []
    public private(set) var passedTests = 0
    public private(set) var failedTests = 0
    
    public init(_ name: String) {
        self.name = name
    }
    
    public func addTest(_ name: String, _ test: @escaping () -> Void) {
        tests.append((name, test))
    }
    
    public func run() {
        print("\n\(TestFramework.sectionIcon(for: name)) Testing \(name)...")
        
        for (_, test) in tests {
            test()
        }
    }
    
    public func assert(_ condition: Bool, _ message: String, file: String = #file, line: Int = #line) {
        if condition {
            print("✅ PASS: \(message)")
            passedTests += 1
        } else {
            print("❌ FAIL: \(message) (at \(file):\(line))")
            failedTests += 1
        }
    }
    
    public func assertEqual<T: Equatable>(_ actual: T, _ expected: T, _ message: String, file: String = #file, line: Int = #line) {
        if actual == expected {
            print("✅ PASS: \(message)")
            passedTests += 1
        } else {
            print("❌ FAIL: \(message) - Expected: \(expected), Got: \(actual) (at \(file):\(line))")
            failedTests += 1
        }
    }
    
    public func assertApproxEqual(_ actual: Double, _ expected: Double, accuracy: Double = 0.01, _ message: String, file: String = #file, line: Int = #line) {
        if abs(actual - expected) <= accuracy {
            print("✅ PASS: \(message)")
            passedTests += 1
        } else {
            print("❌ FAIL: \(message) - Expected: \(expected), Got: \(actual) (at \(file):\(line))")
            failedTests += 1
        }
    }
}

// MARK: - Test Framework Utilities
public struct TestFramework {
    public static func sectionIcon(for testName: String) -> String {
        switch testName.lowercased() {
        case let name where name.contains("essay"): return "📝"
        case let name where name.contains("grade"): return "📊"
        case let name where name.contains("api"): return "🔧"
        case let name where name.contains("process"): return "⚙️"
        case let name where name.contains("prompt"): return "💭"
        default: return "🧪"
        }
    }
    
    public static func printHeader() {
        print("🧪 Running APUSHGraderCore Business Logic Tests...")
        print(String(repeating: "=", count: 50))
    }
    
    public static func printSummary(totalPassed: Int, totalFailed: Int) {
        print("\n" + String(repeating: "=", count: 50))
        print("🏁 Test Results Summary:")
        print("✅ Passed: \(totalPassed)")
        print("❌ Failed: \(totalFailed)")
        print("📊 Total: \(totalPassed + totalFailed)")
        
        if totalFailed == 0 {
            print("🎉 All tests passed!")
        } else {
            print("💥 Some tests failed!")
        }
    }
}

// MARK: - Test Protocol
public protocol TestRunnable {
    func runTests() -> TestSuite
}