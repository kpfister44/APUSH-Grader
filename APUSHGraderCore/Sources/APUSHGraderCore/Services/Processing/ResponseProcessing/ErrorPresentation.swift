import Foundation

// MARK: - Error Presentation Helper

public class ErrorPresentation {
    
    public static func getUserFriendlyMessage(for error: Error) -> String {
        if let gradingError = error as? GradingError {
            switch gradingError {
            case .networkError(let message):
                return "Network connection issue: \(message). Please check your internet connection and try again."
            case .apiKeyMissing:
                return "API configuration missing. Please contact support or check your app settings."
            case .rateLimitExceeded:
                return "Service temporarily busy. Please wait a moment and try again."
            case .essayTooShort:
                return "Your essay appears to be too short for accurate grading. Please expand your response."
            case .essayTooLong:
                return "Your essay is quite long and may exceed processing limits. Consider shortening it."
            case .invalidResponse, .parseError:
                return "Received an unexpected response from the grading service. Please try again."
            case .invalidScore:
                return "Received invalid scoring data. Please try grading again."
            }
        }
        
        return "An unexpected error occurred: \(error.localizedDescription). Please try again."
    }
    
    static func getErrorIcon(for error: Error) -> String {
        if let gradingError = error as? GradingError {
            switch gradingError {
            case .networkError, .rateLimitExceeded:
                return "wifi.exclamationmark"
            case .apiKeyMissing:
                return "key.slash"
            case .essayTooShort, .essayTooLong:
                return "doc.text.magnifyingglass"
            case .invalidResponse, .parseError, .invalidScore:
                return "exclamationmark.triangle"
            }
        }
        return "exclamationmark.circle"
    }
}