import Foundation

// MARK: - API Service Protocol

public protocol APIServiceProtocol {
    func gradeEssay(_ essay: String, type: EssayType, prompt: String) async throws -> GradeResponse
}

// MARK: - Provider-Specific Protocols

public protocol OpenAIServiceProtocol {
    func gradeEssay(_ essay: String, type: EssayType, prompt: String, preprocessingResult: PreprocessingResult) async throws -> GradeResponse
}

public protocol AnthropicServiceProtocol {
    func gradeEssay(_ essay: String, type: EssayType, prompt: String, preprocessingResult: PreprocessingResult) async throws -> GradeResponse
}