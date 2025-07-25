/**
 * Services index - Central export for all service modules
 * APUSH Grader Web Frontend
 */

// API Service exports
export {
  ApiService,
  apiService,
  createApiService,
  configureApiForEnvironment,
  ApiError,
  ApiErrorType
} from './api';

// Configuration exports
export {
  ConfigManager,
  getConfig,
  getApiConfig,
  getCurrentEnvironment,
  checkApiConnection,
  updateConfig,
  getApiEndpoint,
  isDevelopment,
  isProduction,
  devLog,
  devError
} from './config';

// Type exports for services
export type {
  ApiConfig,
  RequestOptions,
  Environment,
  EnvironmentConfig
} from './api';

export type { Environment as EnvironmentInfo } from './config';

// ============================================================================
// Service Initialization
// ============================================================================

/**
 * Initialize all services for the application
 * Call this early in the application lifecycle
 */
export function initializeServices(): void {
  // API service auto-configures on import
  // Configuration is loaded on demand
  
  if (isDevelopment()) {
    console.log('🚀 APUSH Grader services initialized in development mode');
  }
}

/**
 * Check if all services are healthy
 */
export async function checkServicesHealth(): Promise<{
  api: boolean;
  overall: boolean;
}> {
  const apiHealthy = await checkApiConnection();
  
  return {
    api: apiHealthy,
    overall: apiHealthy
  };
}