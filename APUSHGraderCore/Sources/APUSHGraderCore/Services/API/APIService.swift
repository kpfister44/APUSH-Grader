import Foundation

// MARK: - Main API Service Coordinator

public class APIService: APIServiceProtocol {
    private let openAIService: OpenAIServiceProtocol
    private let anthropicService: AnthropicServiceProtocol
    private let model: APIConfig.Model
    
    public init(model: APIConfig.Model = APIConfig.preferredModel) {
        self.model = model
        
        // Configure URLSession
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = APIConfig.timeoutInterval
        config.timeoutIntervalForResource = APIConfig.timeoutInterval * 2
        let session = URLSession(configuration: config)
        
        // Initialize provider services
        self.openAIService = OpenAIService(model: model, session: session)
        self.anthropicService = AnthropicService(model: model, session: session)
    }
    
    // MARK: - Main Grading Function
    
    public func gradeEssay(_ essay: String, type: EssayType, prompt: String) async throws -> GradeResponse {
        // Validate essay first
        try EssayProcessor.validateEssay(essay, for: type)
        
        // Preprocess the essay
        let preprocessingResult = EssayProcessor.preprocessEssay(essay, for: type)
        
        // Grade with retry logic
        return try await gradeWithRetry(
            essay: preprocessingResult.cleanedText,
            type: type,
            prompt: prompt,
            preprocessingResult: preprocessingResult,
            maxRetries: 3
        )
    }
    
    // MARK: - Retry Logic
    
    private func gradeWithRetry(
        essay: String,
        type: EssayType,
        prompt: String,
        preprocessingResult: PreprocessingResult,
        maxRetries: Int
    ) async throws -> GradeResponse {
        var lastError: Error?
        
        for attempt in 1...maxRetries {
            do {
                return try await performGrading(
                    essay: essay,
                    type: type,
                    prompt: prompt,
                    preprocessingResult: preprocessingResult
                )
            } catch let error as GradingError {
                lastError = error
                
                switch error {
                case .rateLimitExceeded:
                    // Exponential backoff for rate limits
                    let delay = Double(attempt * attempt) * 2.0
                    try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                case .networkError:
                    // Short delay for network errors
                    if attempt < maxRetries {
                        try await Task.sleep(nanoseconds: 1_000_000_000) // 1 second
                    }
                case .parseError:
                    // Don't retry parse errors immediately
                    if attempt < maxRetries {
                        try await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
                    }
                default:
                    // Don't retry other errors
                    throw error
                }
            } catch {
                lastError = error
                if attempt < maxRetries {
                    try await Task.sleep(nanoseconds: 1_000_000_000)
                }
            }
        }
        
        throw lastError ?? GradingError.networkError("Max retries exceeded")
    }
    
    // MARK: - Provider Routing
    
    private func performGrading(
        essay: String,
        type: EssayType,
        prompt: String,
        preprocessingResult: PreprocessingResult
    ) async throws -> GradeResponse {
        switch model.provider {
        case .openai:
            return try await openAIService.gradeEssay(essay, type: type, prompt: prompt, preprocessingResult: preprocessingResult)
        case .anthropic:
            return try await anthropicService.gradeEssay(essay, type: type, prompt: prompt, preprocessingResult: preprocessingResult)
        }
    }
}