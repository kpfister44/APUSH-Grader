import Foundation

// MARK: - Models

struct GradingRequest: Codable {
    let essayText: String?
    let essayType: String
    let prompt: String
    let saqParts: SAQParts?
    let saqType: String?
    
    enum CodingKeys: String, CodingKey {
        case essayText = "essay_text"
        case essayType = "essay_type"
        case prompt
        case saqParts = "saq_parts"
        case saqType = "saq_type"
    }
    
    // Legacy initializer for DBQ/LEQ
    init(essayText: String, essayType: String, prompt: String, saqType: String? = nil) {
        self.essayText = essayText
        self.essayType = essayType
        self.prompt = prompt
        self.saqParts = nil
        self.saqType = saqType
    }
    
    // New initializer for SAQ with parts
    init(saqParts: SAQParts, essayType: String, prompt: String, saqType: String? = nil) {
        self.essayText = ""  // Backend will use saq_parts instead
        self.essayType = essayType
        self.prompt = prompt
        self.saqParts = saqParts
        self.saqType = saqType
    }
}

struct GradingResponse: Codable {
    let score: Int
    let maxScore: Int
    let percentage: Double
    let letterGrade: String
    let performanceLevel: String
    let breakdown: [String: RubricItemResponse]
    let overallFeedback: String
    let suggestions: [String]
    let warnings: [String]
    let wordCount: Int
    let paragraphCount: Int
    let processingTimeMs: Int?
    
    enum CodingKeys: String, CodingKey {
        case score
        case maxScore = "max_score"
        case percentage
        case letterGrade = "letter_grade"
        case performanceLevel = "performance_level"
        case breakdown
        case overallFeedback = "overall_feedback"
        case suggestions
        case warnings
        case wordCount = "word_count"
        case paragraphCount = "paragraph_count"
        case processingTimeMs = "processing_time_ms"
    }
}

struct RubricItemResponse: Codable {
    let score: Int
    let maxScore: Int
    let feedback: String
    
    enum CodingKeys: String, CodingKey {
        case score
        case maxScore = "maxScore"
        case feedback
    }
}

struct ErrorResponse: Codable {
    let error: String
    let message: String
    let details: [String: String]?
}

struct BackendErrorResponse: Codable {
    let detail: ErrorResponse
}

// MARK: - Network Errors

enum NetworkError: Error, LocalizedError {
    case invalidURL
    case noData
    case invalidResponse
    case decodingError(String)
    case serverError(String)
    case networkUnavailable
    case rateLimited
    case requestTimeout
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid server URL"
        case .noData:
            return "No data received from server"
        case .invalidResponse:
            return "Invalid response from server"
        case .decodingError(let message):
            return "Failed to process response: \(message)"
        case .serverError(let message):
            return "Server error: \(message)"
        case .networkUnavailable:
            return "Network unavailable. Please check your connection."
        case .rateLimited:
            return "Too many requests. Please wait a moment and try again."
        case .requestTimeout:
            return "Request timed out. Please try again."
        }
    }
}

// MARK: - NetworkService

class NetworkService {
    static let shared = NetworkService()
    
    private let baseURL = "http://localhost:8000"
    private let session: URLSession
    
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30.0
        config.timeoutIntervalForResource = 60.0
        self.session = URLSession(configuration: config)
    }
    
    func gradeEssay(
        essayText: String,
        essayType: String,
        prompt: String,
        saqType: String? = nil
    ) async throws -> GradingResponse {
        
        guard let url = URL(string: "\(baseURL)/api/v1/grade") else {
            throw NetworkError.invalidURL
        }
        
        let request = GradingRequest(
            essayText: essayText,
            essayType: essayType,
            prompt: prompt,
            saqType: saqType
        )
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let jsonData = try JSONEncoder().encode(request)
            urlRequest.httpBody = jsonData
            
            let (data, response) = try await session.data(for: urlRequest)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            // Handle different HTTP status codes
            switch httpResponse.statusCode {
            case 200...299:
                // Success - decode the response
                do {
                    let gradingResponse = try JSONDecoder().decode(GradingResponse.self, from: data)
                    return gradingResponse
                } catch {
                    throw NetworkError.decodingError(error.localizedDescription)
                }
                
            case 429:
                // Rate limited
                throw NetworkError.rateLimited
                
            case 400...499:
                // Client error - try to decode backend error response
                if let backendError = try? JSONDecoder().decode(BackendErrorResponse.self, from: data) {
                    throw NetworkError.serverError(backendError.detail.message)
                } else if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                    throw NetworkError.serverError(errorResponse.message)
                } else {
                    throw NetworkError.serverError("Client error: \(httpResponse.statusCode)")
                }
                
            case 500...599:
                // Server error
                if let backendError = try? JSONDecoder().decode(BackendErrorResponse.self, from: data) {
                    throw NetworkError.serverError(backendError.detail.message)
                } else if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                    throw NetworkError.serverError(errorResponse.message)
                } else {
                    throw NetworkError.serverError("Server error: \(httpResponse.statusCode)")
                }
                
            default:
                throw NetworkError.serverError("Unexpected response: \(httpResponse.statusCode)")
            }
            
        } catch let error as NetworkError {
            throw error
        } catch {
            // Handle URLSession errors
            if let urlError = error as? URLError {
                switch urlError.code {
                case .notConnectedToInternet, .networkConnectionLost:
                    throw NetworkError.networkUnavailable
                case .timedOut:
                    throw NetworkError.requestTimeout
                default:
                    throw NetworkError.serverError(urlError.localizedDescription)
                }
            } else {
                throw NetworkError.serverError(error.localizedDescription)
            }
        }
    }
    
    func gradeEssayWithSAQParts(
        saqParts: SAQParts,
        essayType: String,
        prompt: String,
        saqType: String? = nil
    ) async throws -> GradingResponse {
        
        guard let url = URL(string: "\(baseURL)/api/v1/grade") else {
            throw NetworkError.invalidURL
        }
        
        let request = GradingRequest(
            saqParts: saqParts,
            essayType: essayType,
            prompt: prompt,
            saqType: saqType
        )
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let jsonData = try JSONEncoder().encode(request)
            urlRequest.httpBody = jsonData
            
            let (data, response) = try await session.data(for: urlRequest)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            // Handle different HTTP status codes
            switch httpResponse.statusCode {
            case 200...299:
                // Success - decode the response
                do {
                    let gradingResponse = try JSONDecoder().decode(GradingResponse.self, from: data)
                    return gradingResponse
                } catch {
                    throw NetworkError.decodingError(error.localizedDescription)
                }
                
            case 429:
                // Rate limited
                throw NetworkError.rateLimited
                
            case 400...499:
                // Client error - try to decode backend error response
                if let backendError = try? JSONDecoder().decode(BackendErrorResponse.self, from: data) {
                    throw NetworkError.serverError(backendError.detail.message)
                } else if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                    throw NetworkError.serverError(errorResponse.message)
                } else {
                    throw NetworkError.serverError("Client error: \(httpResponse.statusCode)")
                }
                
            case 500...599:
                // Server error
                if let backendError = try? JSONDecoder().decode(BackendErrorResponse.self, from: data) {
                    throw NetworkError.serverError(backendError.detail.message)
                } else if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                    throw NetworkError.serverError(errorResponse.message)
                } else {
                    throw NetworkError.serverError("Server error: \(httpResponse.statusCode)")
                }
                
            default:
                throw NetworkError.serverError("Unexpected response: \(httpResponse.statusCode)")
            }
            
        } catch let error as NetworkError {
            throw error
        } catch {
            // Handle URLSession errors
            if let urlError = error as? URLError {
                switch urlError.code {
                case .notConnectedToInternet, .networkConnectionLost:
                    throw NetworkError.networkUnavailable
                case .timedOut:
                    throw NetworkError.requestTimeout
                default:
                    throw NetworkError.serverError(urlError.localizedDescription)
                }
            } else {
                throw NetworkError.serverError(error.localizedDescription)
            }
        }
    }
}