/**
 * Central type definitions export for APUSH Grader web frontend
 * Re-exports all types for convenient importing
 */

// API Types
export type {
  // Request types
  GradingRequest,
  HealthRequest,
  UsageSummaryRequest,
  
  // Response types
  GradingResponse,
  HealthResponse,
  UsageSummaryResponse,
  ErrorResponse,
  
  // HTTP wrapper types
  ApiResponse,
  ApiSuccessResponse,
  ApiErrorResponse,
  
  // Configuration types
  ApiConfig,
  RequestOptions,
  
  // Enum types
  EssayType,
  SAQType
} from './api';

export {
  // Constants and utilities
  ESSAY_TYPES,
  SAQ_TYPES,
  ApiErrorType,
  ApiError
} from './api';

// UI Types
export type {
  // Form validation
  FormValidationState,
  FormFieldValidation,
  ValidationRule,
  FormValidationRules,
  
  // Insights and performance
  InsightCategory,
  CategorizedInsight,
  PerformanceLevel,
  PerformanceLevelConfig,
  
  // Processed results
  FormattedBreakdownItem,
  ProcessedGradingResult,
  
  // UI state
  LoadingState,
  UINotification,
  ModalState,
  
  // Component props
  BaseComponentProps,
  InteractiveComponentProps,
  FormFieldProps,
  
  // Animation and responsive
  AnimationConfig,
  TransitionState,
  BreakpointSize,
  ResponsiveConfig
} from './ui';

export {
  // Constants and utilities
  PERFORMANCE_LEVELS,
  getPerformanceLevel,
  formatPercentage,
  formatScore,
  generateNotificationId
} from './ui';