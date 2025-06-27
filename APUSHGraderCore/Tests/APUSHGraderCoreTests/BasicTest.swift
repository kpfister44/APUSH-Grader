import XCTest
@testable import APUSHGraderCore

final class BasicTest: XCTestCase {
    func testEssayTypeProperties() {
        let dbq = EssayType.dbq
        XCTAssertEqual(dbq.maxScore, 6)
        XCTAssertEqual(dbq.minWordCount, 400)
        XCTAssertEqual(dbq.description, "Document Based Question")
    }
    
    func testMockAPIService() {
        let mockService = MockAPIService(delay: 0.1)
        XCTAssertNotNil(mockService)
    }
}