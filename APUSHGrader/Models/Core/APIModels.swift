import Foundation

// MARK: - API Configuration

struct APIConfig {
    static let temperature: Double = 0.3
    static let maxTokens: Int = 1500
    static let timeoutInterval: TimeInterval = 30.0
    
    // Model selection
    enum Provider {
        case openai
        case anthropic
    }
    
    enum Model {
        case gpt4o
        case gpt4oMini
        case claude35Sonnet
        case claude3Haiku
        
        var name: String {
            switch self {
            case .gpt4o: return "gpt-4o"
            case .gpt4oMini: return "gpt-4o-mini"
            case .claude35Sonnet: return "claude-3-5-sonnet-20241022"
            case .claude3Haiku: return "claude-3-haiku-20240307"
            }
        }
        
        var provider: Provider {
            switch self {
            case .gpt4o, .gpt4oMini: return .openai
            case .claude35Sonnet, .claude3Haiku: return .anthropic
            }
        }
    }
    
    static let preferredModel: Model = .claude35Sonnet
}