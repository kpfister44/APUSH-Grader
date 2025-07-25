/**
 * API Service Client for APUSH Grader Backend
 * Handles all HTTP communication with Python FastAPI backend
 */

import {
  GradingRequest,
  GradingResponse,
  HealthResponse,
  UsageSummaryResponse,
  ApiConfig,
  RequestOptions,
  ApiSuccessResponse,
  ApiErrorResponse,
  ApiError,
  ApiErrorType
} from '../types';
import { getApiConfig, devLog, devError } from './config';

// ============================================================================
// Configuration and Constants
// ============================================================================

// Get default configuration from environment config
const DEFAULT_CONFIG: ApiConfig = getApiConfig();

const DEFAULT_REQUEST_OPTIONS: RequestOptions = {
  timeout: DEFAULT_CONFIG.timeout,
  retryAttempts: DEFAULT_CONFIG.retryAttempts,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Sleep function for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Calculate exponential backoff delay
 */
function calculateRetryDelay(attempt: number, baseDelay: number): number {
  return baseDelay * Math.pow(2, attempt - 1) + Math.random() * 1000;
}

/**
 * Determine API error type from HTTP status and response
 */
function determineErrorType(status: number, errorCode?: string): ApiErrorType {
  if (status === 0 || status >= 500) {
    return ApiErrorType.NETWORK_ERROR;
  }
  
  switch (status) {
    case 400:
      return errorCode === 'VALIDATION_ERROR' 
        ? ApiErrorType.VALIDATION_ERROR 
        : ApiErrorType.SERVER_ERROR;
    case 429:
      return ApiErrorType.RATE_LIMIT_ERROR;
    case 408:
      return ApiErrorType.TIMEOUT_ERROR;
    default:
      return ApiErrorType.SERVER_ERROR;
  }
}

/**
 * Parse error response from backend
 */
function parseErrorResponse(response: any, status: number): ApiError {
  try {
    if (response && typeof response === 'object') {
      const errorType = determineErrorType(status, response.error);
      return new ApiError(
        response.message || 'An error occurred',
        errorType,
        status,
        response.details
      );
    }
  } catch (e) {
    // Failed to parse error response
  }
  
  // Fallback error
  return new ApiError(
    `HTTP ${status}: Request failed`,
    determineErrorType(status),
    status
  );
}

// ============================================================================
// Core HTTP Client
// ============================================================================

class HttpClient {
  private config: ApiConfig;

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Make HTTP request with retry logic and error handling
   */
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit & { retryAttempts?: number } = {}
  ): Promise<ApiSuccessResponse<T>> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const maxRetries = options.retryAttempts ?? this.config.retryAttempts;
    
    let lastError: ApiError | null = null;

    for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
      try {
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(
          () => controller.abort(),
          options.timeout ?? this.config.timeout
        );

        const fetchOptions: RequestInit = {
          ...options,
          signal: controller.signal,
          headers: {
            ...DEFAULT_REQUEST_OPTIONS.headers,
            ...options.headers
          }
        };

        const response = await fetch(url, fetchOptions);
        clearTimeout(timeoutId);

        devLog(`HTTP ${fetchOptions.method} ${url} - ${response.status}`);

        // Handle successful response
        if (response.ok) {
          const data = await response.json();
          return {
            data,
            status: response.status,
            statusText: response.statusText
          };
        }

        // Handle error response
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { message: response.statusText };
        }

        const apiError = parseErrorResponse(errorData, response.status);
        
        // Don't retry validation errors or rate limit errors after first attempt
        if (apiError.type === ApiErrorType.VALIDATION_ERROR || 
            (apiError.type === ApiErrorType.RATE_LIMIT_ERROR && attempt > 1)) {
          throw apiError;
        }

        lastError = apiError;

      } catch (error) {
        if (error instanceof ApiError) {
          lastError = error;
        } else if (error instanceof DOMException && error.name === 'AbortError') {
          lastError = new ApiError(
            'Request timeout',
            ApiErrorType.TIMEOUT_ERROR,
            408
          );
        } else if (error instanceof TypeError && error.message.includes('fetch')) {
          lastError = new ApiError(
            'Network connection failed',
            ApiErrorType.NETWORK_ERROR,
            0
          );
        } else {
          lastError = new ApiError(
            error instanceof Error ? error.message : 'Unknown error',
            ApiErrorType.UNKNOWN_ERROR
          );
        }
        
        devError(`Request failed (attempt ${attempt}/${maxRetries + 1}):`, lastError);
      }

      // If this was the last attempt, break
      if (attempt > maxRetries) {
        break;
      }

      // Wait before retrying (exponential backoff)
      const delay = calculateRetryDelay(attempt, this.config.retryDelay);
      await sleep(delay);
    }

    // All retries failed, throw the last error
    throw lastError || new ApiError('Request failed', ApiErrorType.UNKNOWN_ERROR);
  }

  /**
   * GET request
   */
  public async get<T>(endpoint: string, options?: RequestOptions): Promise<ApiSuccessResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'GET',
      ...options
    });
  }

  /**
   * POST request
   */
  public async post<T>(
    endpoint: string, 
    data?: any, 
    options?: RequestOptions
  ): Promise<ApiSuccessResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      ...options
    });
  }
}

// ============================================================================
// API Service Class
// ============================================================================

export class ApiService {
  private client: HttpClient;

  constructor(config?: Partial<ApiConfig>) {
    this.client = new HttpClient(config);
  }

  /**
   * Grade an essay using the backend API
   * Main endpoint: POST /api/v1/grade
   */
  public async gradeEssay(request: GradingRequest): Promise<GradingResponse> {
    try {
      const response = await this.client.post<GradingResponse>('/api/v1/grade', request, {
        timeout: 45000, // Extended timeout for AI processing
        retryAttempts: 2 // Fewer retries for expensive operations
      });
      return response.data;
    } catch (error) {
      // Re-throw with enhanced context for grading errors
      if (error instanceof ApiError) {
        if (error.type === ApiErrorType.RATE_LIMIT_ERROR) {
          throw new ApiError(
            'Rate limit exceeded. Please wait before submitting another essay.',
            error.type,
            error.status,
            error.details
          );
        }
        throw error;
      }
      throw new ApiError('Failed to grade essay', ApiErrorType.UNKNOWN_ERROR);
    }
  }

  /**
   * Check backend health status
   * Endpoint: GET /health
   */
  public async checkHealth(): Promise<HealthResponse> {
    try {
      const response = await this.client.get<HealthResponse>('/health', {
        timeout: 5000, // Quick timeout for health checks
        retryAttempts: 1
      });
      return response.data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Health check failed', ApiErrorType.NETWORK_ERROR);
    }
  }

  /**
   * Get usage summary for rate limiting info
   * Endpoint: GET /usage/summary
   */
  public async getUsageSummary(): Promise<UsageSummaryResponse> {
    try {
      const response = await this.client.get<UsageSummaryResponse>('/usage/summary', {
        timeout: 5000,
        retryAttempts: 1
      });
      return response.data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Failed to get usage summary', ApiErrorType.NETWORK_ERROR);
    }
  }

  /**
   * Update API configuration
   */
  public updateConfig(config: Partial<ApiConfig>): void {
    this.client = new HttpClient({ ...DEFAULT_CONFIG, ...config });
  }
}

// ============================================================================
// Default Export and Singleton Instance
// ============================================================================

// Create default instance
export const apiService = new ApiService();

// Export types and utilities
export { ApiError, ApiErrorType };
export type { ApiConfig, RequestOptions };

// Export factory function for custom instances
export function createApiService(config?: Partial<ApiConfig>): ApiService {
  return new ApiService(config);
}

// ============================================================================
// Environment Detection and Configuration
// ============================================================================

/**
 * Auto-configure API based on environment
 * Now handled by the config service, but keeping for backward compatibility
 */
export function configureApiForEnvironment(): void {
  const config = getApiConfig();
  apiService.updateConfig(config);
  devLog('API service configured automatically');
}

// Auto-configure on module load
if (typeof window !== 'undefined') {
  configureApiForEnvironment();
}