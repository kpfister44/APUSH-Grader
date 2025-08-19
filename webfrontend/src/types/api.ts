/**
 * TypeScript interface definitions for APUSH Grader API
 * Matches Python FastAPI backend models exactly
 */

// ============================================================================
// API Request Models
// ============================================================================

export interface GradingRequest {
  essay_text?: string;           // For DBQ/LEQ or legacy SAQ
  essay_type: "DBQ" | "LEQ" | "SAQ";
  prompt: string;                // Essay question/prompt
  saq_parts?: {                  // For multi-part SAQ format
    part_a: string;
    part_b: string; 
    part_c: string;
  };
  saq_type?: "stimulus" | "non_stimulus" | "secondary_comparison";
  rubric_type?: "college_board" | "eg";  // Rubric type for SAQ essays
}

export interface HealthRequest {
  // No body needed for health check
}

export interface UsageSummaryRequest {
  // No body needed for usage summary
}

// ============================================================================
// API Response Models
// ============================================================================

export interface GradingResponse {
  score: number;                 // Achieved score
  max_score: number;            // Maximum possible (6 for DBQ/LEQ, 3 for College Board SAQ, 10 for EG SAQ)
  percentage: number;           // Score as percentage (0-100)
  letter_grade: string;         // A, B, C, D, F (with +/- modifiers)
  performance_level: string;    // Advanced, Proficient, Developing, etc.
  breakdown: {                  // Detailed rubric breakdown
    [section: string]: {
      score: number;
      max_score: number;
      feedback: string;
    }
  };
  overall_feedback: string;     // AI-generated overall feedback
  suggestions: string[];        // Specific improvement suggestions
  warnings: string[];           // Processing warnings
  word_count: number;          // Essay word count
  paragraph_count: number;     // Essay paragraph count
  processing_time_ms?: number; // Processing time
}

export interface HealthResponse {
  status: "healthy" | "unhealthy";
  timestamp: string;
  environment: string;
  version?: string;
}

export interface UsageSummaryResponse {
  essays_processed_today: number;
  daily_limit: number;
  essays_remaining: number;
  reset_time: string;
}

export interface ErrorResponse {
  error: string;               // Error type (VALIDATION_ERROR, RATE_LIMIT_ERROR, etc.)
  message: string;            // Human-readable message
  details?: Record<string, any>; // Additional error context
}

// ============================================================================
// HTTP Response Wrapper Types
// ============================================================================

export interface ApiResponse<T> {
  data?: T;
  error?: ErrorResponse;
  status: number;
  statusText: string;
}

export interface ApiSuccessResponse<T> extends ApiResponse<T> {
  data: T;
  error?: never;
}

export interface ApiErrorResponse extends ApiResponse<never> {
  data?: never;
  error: ErrorResponse;
}

// ============================================================================
// API Configuration Types
// ============================================================================

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

export interface RequestOptions {
  timeout?: number;
  retryAttempts?: number;
  headers?: Record<string, string>;
}

// ============================================================================
// Essay Type Enums and Utilities
// ============================================================================

export type EssayType = "DBQ" | "LEQ" | "SAQ";
export type SAQType = "stimulus" | "non_stimulus" | "secondary_comparison";
export type RubricType = "college_board" | "eg";

export const ESSAY_TYPES: Record<EssayType, { 
  label: string; 
  maxScore: number; 
  description: string;
}> = {
  DBQ: {
    label: "Document-Based Question",
    maxScore: 6,
    description: "Essay using provided historical documents"
  },
  LEQ: {
    label: "Long Essay Question", 
    maxScore: 6,
    description: "Extended analytical essay"
  },
  SAQ: {
    label: "Short Answer Question",
    maxScore: 3, // Note: actual max score depends on rubric type
    description: "Brief response question"
  }
};

export const SAQ_TYPES: Record<SAQType, {
  label: string;
  description: string;
}> = {
  stimulus: {
    label: "Source Analysis",
    description: "Uses primary/secondary source document"
  },
  non_stimulus: {
    label: "Content Question", 
    description: "Pure text-based questions without sources"
  },
  secondary_comparison: {
    label: "Historical Comparison",
    description: "Compares contrasting historical interpretations"
  }
};

export const RUBRIC_TYPES: Record<RubricType, {
  label: string;
  maxScore: number;
  description: string;
}> = {
  college_board: {
    label: "College Board Rubric",
    maxScore: 3,
    description: "Official 3-point rubric (Part A, B, C)"
  },
  eg: {
    label: "EG Rubric", 
    maxScore: 10,
    description: "Custom 10-point A/C/E criteria rubric"
  }
};

// ============================================================================
// Error Types
// ============================================================================

export enum ApiErrorType {
  NETWORK_ERROR = "NETWORK_ERROR",
  VALIDATION_ERROR = "VALIDATION_ERROR", 
  RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR",
  SERVER_ERROR = "SERVER_ERROR",
  TIMEOUT_ERROR = "TIMEOUT_ERROR",
  UNKNOWN_ERROR = "UNKNOWN_ERROR"
}

export class ApiError extends Error {
  public readonly type: ApiErrorType;
  public readonly status?: number;
  public readonly details?: Record<string, any>;

  constructor(
    message: string, 
    type: ApiErrorType = ApiErrorType.UNKNOWN_ERROR,
    status?: number,
    details?: Record<string, any>
  ) {
    super(message);
    this.name = "ApiError";
    this.type = type;
    this.status = status;
    this.details = details;
  }
}