import Foundation

// MARK: - Anthropic API Service

class AnthropicService: AnthropicServiceProtocol {
    private let session: URLSession
    private let model: APIConfig.Model
    
    private var apiKey: String {
        return Bundle.main.object(forInfoDictionaryKey: "ANTHROPIC_API_KEY") as? String ?? ""
    }
    
    init(model: APIConfig.Model, session: URLSession = URLSession.shared) {
        self.model = model
        self.session = session
    }
    
    func gradeEssay(_ essay: String, type: EssayType, prompt: String, preprocessingResult: PreprocessingResult) async throws -> GradeResponse {
        guard !apiKey.isEmpty else {
            throw GradingError.apiKeyMissing
        }
        
        let url = URL(string: "https://api.anthropic.com/v1/messages")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
        
        let systemPrompt = PromptGenerator.generateSystemPrompt(for: type)
        let userMessage = PromptGenerator.generateUserMessage(
            essay: essay,
            essayType: type,
            prompt: prompt,
            preprocessingResult: preprocessingResult
        )
        
        let requestBody: [String: Any] = [
            "model": model.name,
            "max_tokens": APIConfig.maxTokens,
            "temperature": APIConfig.temperature,
            "system": systemPrompt,
            "messages": [
                ["role": "user", "content": userMessage]
            ]
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await session.data(for: request)
        
        try validateHTTPResponse(response)
        
        guard let jsonResponse = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let content = jsonResponse["content"] as? [[String: Any]],
              let firstContent = content.first,
              let text = firstContent["text"] as? String else {
            throw GradingError.invalidResponse
        }
        
        return try parseGradingResponse(text, warnings: preprocessingResult.warnings)
    }
    
    // MARK: - Response Validation
    
    private func validateHTTPResponse(_ response: URLResponse) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw GradingError.networkError("Invalid response type")
        }
        
        switch httpResponse.statusCode {
        case 200...299:
            return
        case 401:
            throw GradingError.apiKeyMissing
        case 429:
            throw GradingError.rateLimitExceeded
        case 400...499:
            throw GradingError.networkError("Client error: \(httpResponse.statusCode)")
        case 500...599:
            throw GradingError.networkError("Server error: \(httpResponse.statusCode)")
        default:
            throw GradingError.networkError("Unexpected status code: \(httpResponse.statusCode)")
        }
    }
    
    // MARK: - Response Parsing
    
    private func parseGradingResponse(_ responseText: String, warnings: [String]) throws -> GradeResponse {
        let cleanedResponse = extractJSON(from: responseText)
        
        guard let data = cleanedResponse.data(using: .utf8) else {
            throw GradingError.parseError("Could not convert response to data")
        }
        
        do {
            let decoder = JSONDecoder()
            var gradeResponse = try decoder.decode(GradeResponse.self, from: data)
            
            if !warnings.isEmpty {
                let existingWarnings = gradeResponse.warnings ?? []
                let updatedResponse = GradeResponse(
                    score: gradeResponse.score,
                    maxScore: gradeResponse.maxScore,
                    breakdown: gradeResponse.breakdown,
                    overallFeedback: gradeResponse.overallFeedback,
                    suggestions: gradeResponse.suggestions,
                    warnings: existingWarnings + warnings
                )
                return updatedResponse
            }
            
            return gradeResponse
        } catch {
            throw GradingError.parseError("JSON parsing failed: \(error.localizedDescription)")
        }
    }
    
    private func extractJSON(from text: String) -> String {
        if let startRange = text.range(of: "{"),
           let endRange = text.range(of: "}", options: .backwards) {
            let jsonString = String(text[startRange.lowerBound...endRange.upperBound])
            return jsonString
        }
        
        return text
    }
}