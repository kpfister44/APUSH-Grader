import Foundation

// MARK: - API Configuration

public struct APIConfig {
    public static let temperature: Double = 0.3
    public static let maxTokens: Int = 1500
    public static let timeoutInterval: TimeInterval = 30.0
    
    // Model selection
    public enum Provider {
        case openai
        case anthropic
    }
    
    public enum Model {
        case gpt4o
        case gpt4oMini
        case claude35Sonnet
        case claude3Haiku
        
        public var name: String {
            switch self {
            case .gpt4o: return "gpt-4o"
            case .gpt4oMini: return "gpt-4o-mini"
            case .claude35Sonnet: return "claude-3-5-sonnet-20241022"
            case .claude3Haiku: return "claude-3-haiku-20240307"
            }
        }
        
        public var provider: Provider {
            switch self {
            case .gpt4o, .gpt4oMini: return .openai
            case .claude35Sonnet, .claude3Haiku: return .anthropic
            }
        }
    }
    
    public static let preferredModel: Model = .claude35Sonnet
}