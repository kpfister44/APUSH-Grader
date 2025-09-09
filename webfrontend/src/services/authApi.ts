/**
 * Authenticated API Service that automatically includes session tokens
 */

import { ApiService, ApiConfig } from './api';
import { getConfig } from './config';

class AuthenticatedApiService extends ApiService {
  private getSessionToken(): string | null {
    return sessionStorage.getItem('session_token');
  }

  /**
   * Override the constructor to inject auth headers
   */
  constructor(config?: Partial<ApiConfig>) {
    super(config);
  }

  /**
   * Create authenticated request headers
   */
  private createAuthHeaders(): Record<string, string> {
    const token = this.getSessionToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  /**
   * Override gradeEssay to include auth headers
   */
  public async gradeEssay(request: any): Promise<any> {
    const token = this.getSessionToken();
    if (!token) {
      throw new Error('Authentication required');
    }

    const config = getConfig();
    const response = await fetch(`${config.baseUrl}/api/v1/grade`, {
      method: 'POST',
      headers: this.createAuthHeaders(),
      body: JSON.stringify(request),
    });

    if (response.status === 401) {
      // Session expired
      sessionStorage.removeItem('session_token');
      throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || errorData.detail || 'Request failed');
    }

    return response.json();
  }

  /**
   * Override checkHealth to include auth headers
   */
  public async checkHealth(): Promise<any> {
    const config = getConfig();
    const response = await fetch(`${config.baseUrl}/health`, {
      headers: this.createAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }

  /**
   * Get grading status (protected endpoint)
   */
  public async getGradingStatus(): Promise<any> {
    const token = this.getSessionToken();
    if (!token) {
      throw new Error('Authentication required');
    }

    const config = getConfig();
    const response = await fetch(`${config.baseUrl}/api/v1/grade/status`, {
      headers: this.createAuthHeaders(),
    });

    if (response.status === 401) {
      sessionStorage.removeItem('session_token');
      throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
      throw new Error('Failed to get grading status');
    }

    return response.json();
  }
}

// Create authenticated instance
export const authenticatedApiService = new AuthenticatedApiService();