/**
 * Environment configuration for APUSH Grader web frontend
 * Handles development vs production API URLs and settings
 */

import { ApiConfig } from '../types';

// ============================================================================
// Environment Detection
// ============================================================================

export interface Environment {
  name: string;
  isDevelopment: boolean;
  isProduction: boolean;
  isTest: boolean;
}

export function getEnvironment(): Environment {
  const nodeEnv = process.env.NODE_ENV || 'development';
  
  return {
    name: nodeEnv,
    isDevelopment: nodeEnv === 'development',
    isProduction: nodeEnv === 'production',
    isTest: nodeEnv === 'test'
  };
}

// ============================================================================
// API Configuration per Environment
// ============================================================================

export interface EnvironmentConfig extends ApiConfig {
  apiVersion: string;
  enableLogging: boolean;
  enableRetries: boolean;
  cors: {
    credentials: boolean;
  };
}

const DEVELOPMENT_CONFIG: EnvironmentConfig = {
  baseUrl: 'http://localhost:8000',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
  apiVersion: 'v1',
  enableLogging: true,
  enableRetries: true,
  cors: {
    credentials: false // No credentials needed for localhost
  }
};

const PRODUCTION_CONFIG: EnvironmentConfig = {
  baseUrl: '', // Will be set to window.location.origin
  timeout: 45000, // Longer timeout for production
  retryAttempts: 2,
  retryDelay: 1500,
  apiVersion: 'v1',
  enableLogging: false,
  enableRetries: true,
  cors: {
    credentials: true // May need credentials in production
  }
};

const TEST_CONFIG: EnvironmentConfig = {
  baseUrl: 'http://localhost:8000',
  timeout: 10000, // Shorter timeout for tests
  retryAttempts: 1,
  retryDelay: 500,
  apiVersion: 'v1',
  enableLogging: false,
  enableRetries: false, // No retries in tests
  cors: {
    credentials: false
  }
};

// ============================================================================
// Configuration Manager
// ============================================================================

export class ConfigManager {
  private static instance: ConfigManager;
  private config: EnvironmentConfig;
  private environment: Environment;

  private constructor() {
    this.environment = getEnvironment();
    this.config = this.getConfigForEnvironment();
    this.applyRuntimeConfiguration();
  }

  public static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  /**
   * Get configuration for current environment
   */
  private getConfigForEnvironment(): EnvironmentConfig {
    if (this.environment.isProduction) {
      return { ...PRODUCTION_CONFIG };
    } else if (this.environment.isTest) {
      return { ...TEST_CONFIG };
    } else {
      return { ...DEVELOPMENT_CONFIG };
    }
  }

  /**
   * Apply runtime-specific configuration
   */
  private applyRuntimeConfiguration(): void {
    // Set production base URL to current origin if in production
    if (this.environment.isProduction && typeof window !== 'undefined') {
      this.config.baseUrl = window.location.origin;
    }

    // Override with environment variables if available
    if (typeof process !== 'undefined' && process.env) {
      if (process.env.REACT_APP_API_BASE_URL) {
        this.config.baseUrl = process.env.REACT_APP_API_BASE_URL;
      }
      if (process.env.REACT_APP_API_TIMEOUT) {
        this.config.timeout = parseInt(process.env.REACT_APP_API_TIMEOUT, 10) || this.config.timeout;
      }
    }

    // Log configuration in development
    if (this.config.enableLogging) {
      console.log('🔧 API Configuration:', {
        environment: this.environment.name,
        baseUrl: this.config.baseUrl,
        timeout: this.config.timeout,
        retryAttempts: this.config.retryAttempts
      });
    }
  }

  /**
   * Get current configuration
   */
  public getConfig(): EnvironmentConfig {
    return { ...this.config };
  }

  /**
   * Get API configuration for ApiService
   */
  public getApiConfig(): ApiConfig {
    return {
      baseUrl: this.config.baseUrl,
      timeout: this.config.timeout,
      retryAttempts: this.config.retryAttempts,
      retryDelay: this.config.retryDelay
    };
  }

  /**
   * Get environment information
   */
  public getEnvironment(): Environment {
    return { ...this.environment };
  }

  /**
   * Update configuration at runtime
   */
  public updateConfig(updates: Partial<EnvironmentConfig>): void {
    this.config = { ...this.config, ...updates };
    
    if (this.config.enableLogging) {
      console.log('🔄 Configuration updated:', updates);
    }
  }

  /**
   * Check if API is accessible
   */
  public async checkApiConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.baseUrl}/health`, {
        method: 'GET',
        timeout: 5000,
        signal: AbortSignal.timeout(5000)
      });
      return response.ok;
    } catch (error) {
      if (this.config.enableLogging) {
        console.warn('🚨 API connection check failed:', error);
      }
      return false;
    }
  }
}

// ============================================================================
// Convenience Functions
// ============================================================================

/**
 * Get current environment configuration
 */
export function getConfig(): EnvironmentConfig {
  return ConfigManager.getInstance().getConfig();
}

/**
 * Get API configuration for ApiService
 */
export function getApiConfig(): ApiConfig {
  return ConfigManager.getInstance().getApiConfig();
}

/**
 * Get current environment info
 */
export function getCurrentEnvironment(): Environment {
  return ConfigManager.getInstance().getEnvironment();
}

/**
 * Check if API is reachable
 */
export function checkApiConnection(): Promise<boolean> {
  return ConfigManager.getInstance().checkApiConnection();
}

/**
 * Update configuration at runtime
 */
export function updateConfig(updates: Partial<EnvironmentConfig>): void {
  ConfigManager.getInstance().updateConfig(updates);
}

// ============================================================================
// Environment-Specific Utilities
// ============================================================================

/**
 * Get full API endpoint URL
 */
export function getApiEndpoint(path: string): string {
  const config = getConfig();
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${config.baseUrl}/api/${config.apiVersion}${cleanPath}`;
}

/**
 * Check if we're running in development
 */
export function isDevelopment(): boolean {
  return getCurrentEnvironment().isDevelopment;
}

/**
 * Check if we're running in production
 */
export function isProduction(): boolean {
  return getCurrentEnvironment().isProduction;
}

/**
 * Log message only in development
 */
export function devLog(message: string, ...args: any[]): void {
  if (isDevelopment() && getConfig().enableLogging) {
    console.log(`🔧 [DEV] ${message}`, ...args);
  }
}

/**
 * Log error only in development
 */
export function devError(message: string, error?: any): void {
  if (isDevelopment() && getConfig().enableLogging) {
    console.error(`🚨 [DEV] ${message}`, error);
  }
}

// ============================================================================
// Export Default Instance
// ============================================================================

export default ConfigManager.getInstance();