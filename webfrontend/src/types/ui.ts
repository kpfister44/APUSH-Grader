/**
 * UI-specific TypeScript interface definitions
 * For form validation, insights, and processed results
 */

import { GradingResponse } from './api';

// ============================================================================
// Form Validation Types
// ============================================================================

export interface FormValidationState {
  isValid: boolean;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
}

export interface FormFieldValidation {
  isValid: boolean;
  error?: string;
  touched: boolean;
}

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: string) => string | undefined;
}

export interface FormValidationRules {
  [fieldName: string]: ValidationRule;
}

// ============================================================================
// Insight Categorization Types
// ============================================================================

export interface InsightCategory {
  type: "strength" | "improvement" | "warning";
  icon: string;
  title: string;
  description: string;
}

export interface CategorizedInsight {
  category: InsightCategory;
  content: string;
  priority: "high" | "medium" | "low";
}

// ============================================================================
// Performance Level Types
// ============================================================================

export type PerformanceLevel = "excellent" | "proficient" | "developing" | "inadequate";

export interface PerformanceLevelConfig {
  label: string;
  color: string;
  bgColor: string;
  textColor: string;
  minPercentage: number;
  description: string;
}

export const PERFORMANCE_LEVELS: Record<PerformanceLevel, PerformanceLevelConfig> = {
  excellent: {
    label: "Excellent",
    color: "text-green-600",
    bgColor: "bg-green-100",
    textColor: "text-green-800",
    minPercentage: 90,
    description: "Outstanding work demonstrating mastery"
  },
  proficient: {
    label: "Proficient", 
    color: "text-blue-600",
    bgColor: "bg-blue-100",
    textColor: "text-blue-800",
    minPercentage: 70,
    description: "Good work meeting expectations"
  },
  developing: {
    label: "Developing",
    color: "text-orange-600", 
    bgColor: "bg-orange-100",
    textColor: "text-orange-800",
    minPercentage: 50,
    description: "Work shows progress but needs improvement"
  },
  inadequate: {
    label: "Inadequate",
    color: "text-red-600",
    bgColor: "bg-red-100", 
    textColor: "text-red-800",
    minPercentage: 0,
    description: "Work needs significant improvement"
  }
};

// ============================================================================
// Processed Results Types
// ============================================================================

export interface FormattedBreakdownItem {
  section: string;
  displayName: string;
  score: number;
  maxScore: number;
  feedback: string;
  percentage: number;
  performanceLevel: PerformanceLevel;
}

export interface ProcessedGradingResult extends GradingResponse {
  insights: CategorizedInsight[];
  formattedBreakdown: FormattedBreakdownItem[];
  performanceLevel: PerformanceLevel;
  performanceLevelConfig: PerformanceLevelConfig;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

export interface UINotification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
  duration?: number;
  dismissible?: boolean;
}

export interface ModalState {
  isOpen: boolean;
  title?: string;
  content?: React.ReactNode;
  onClose?: () => void;
  onConfirm?: () => void;
}

// ============================================================================
// Component Props Types  
// ============================================================================

export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface InteractiveComponentProps extends BaseComponentProps {
  disabled?: boolean;
  loading?: boolean;
}

export interface FormFieldProps extends InteractiveComponentProps {
  label?: string;
  placeholder?: string;
  error?: string;
  required?: boolean;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
}

// ============================================================================
// Animation and Transition Types
// ============================================================================

export interface AnimationConfig {
  duration: number;
  easing: string;
  delay?: number;
}

export interface TransitionState {
  isVisible: boolean;
  isAnimating: boolean;
  animationConfig?: AnimationConfig;
}

// ============================================================================
// Responsive Design Types
// ============================================================================

export type BreakpointSize = "sm" | "md" | "lg" | "xl" | "2xl";

export interface ResponsiveConfig<T> {
  default: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  "2xl"?: T;
}

// ============================================================================
// Utility Functions for UI Types
// ============================================================================

export function getPerformanceLevel(percentage: number): PerformanceLevel {
  if (percentage >= PERFORMANCE_LEVELS.excellent.minPercentage) return "excellent";
  if (percentage >= PERFORMANCE_LEVELS.proficient.minPercentage) return "proficient";
  if (percentage >= PERFORMANCE_LEVELS.developing.minPercentage) return "developing";
  return "inadequate";
}

export function formatPercentage(value: number): string {
  return `${Math.round(value)}%`;
}

export function formatScore(score: number, maxScore: number): string {
  return `${score}/${maxScore}`;
}

export function generateNotificationId(): string {
  return `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}