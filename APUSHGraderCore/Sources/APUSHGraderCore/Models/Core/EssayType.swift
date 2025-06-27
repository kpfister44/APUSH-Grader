import Foundation
import SwiftUI

public enum EssayType: String, CaseIterable {
    case dbq = "DBQ"
    case leq = "LEQ"
    case saq = "SAQ"
    
    public var description: String {
        switch self {
        case .dbq:
            return "Document Based Question"
        case .leq:
            return "Long Essay Question"
        case .saq:
            return "Short Answer Question"
        }
    }
    
    public var placeholderText: String {
        switch self {
        case .dbq:
            return "Enter your DBQ essay here. Remember to use the provided documents and include outside evidence..."
        case .leq:
            return "Enter your LEQ essay here. Focus on developing a clear thesis with supporting evidence..."
        case .saq:
            return "Enter your short answer response here. Be concise and address all parts of the question..."
        }
    }
    
    public var promptPlaceholderText: String {
        switch self {
        case .dbq:
            return "Enter the DBQ prompt/question here. Include the historical context and documents provided..."
        case .leq:
            return "Enter the LEQ prompt/question here. Include the time period and any specific requirements..."
        case .saq:
            return "Enter the SAQ prompt/question here. Include all parts (A, B, C) if applicable..."
        }
    }
    
    public var minHeight: CGFloat {
        switch self {
        case .saq:
            return 100
        case .dbq, .leq:
            return 200
        }
    }
    
    public var maxScore: Int {
        switch self {
        case .dbq, .leq: return 6
        case .saq: return 3
        }
    }
    
    public var minWordCount: Int {
        switch self {
        case .dbq: return 400
        case .leq: return 300
        case .saq: return 50
        }
    }
    
    public var rubricStructure: [String: Int] {
        switch self {
        case .dbq, .leq:
            return [
                "thesis": 1,
                "contextualization": 1,
                "evidence": 2,
                "analysis": 2
            ]
        case .saq:
            return [
                "partA": 1,
                "partB": 1,
                "partC": 1
            ]
        }
    }
}