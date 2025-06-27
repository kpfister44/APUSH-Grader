import Foundation

// MARK: - API Service Protocol

protocol APIServiceProtocol {
    func gradeEssay(_ essay: String, type: EssayType, prompt: String) async throws -> GradeResponse
}

// MARK: - Provider-Specific Protocols

protocol OpenAIServiceProtocol {
    func gradeEssay(_ essay: String, type: EssayType, prompt: String, preprocessingResult: PreprocessingResult) async throws -> GradeResponse
}

protocol AnthropicServiceProtocol {
    func gradeEssay(_ essay: String, type: EssayType, prompt: String, preprocessingResult: PreprocessingResult) async throws -> GradeResponse
}