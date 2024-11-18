import {API_CONFIG, getAuthHeaders} from '../config/api';
import {env} from '../config/env';
import type {TokenResponse} from '../types/gocardless';

class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private accessExpires: number | null = null;
  private refreshExpires: number | null = null;

  async getAccessToken(): Promise<string> {
    if (this.accessToken && this.accessExpires && Date.now() < this.accessExpires) {
      return this.accessToken;
    }

    if (this.refreshToken && this.refreshExpires && Date.now() < this.refreshExpires) {
      return this.refreshAccessToken();
    }

    return this.createNewToken();
  }

  private async createNewToken(): Promise<string> {
    try {
      const authHeaders = getAuthHeaders();
      const response = await fetch(`${API_CONFIG.baseUrl}/token/new/`, {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({
          secret_id: env.secretId,
          secret_key: env.secretKey,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.message || `Failed to create token: ${response.status} ${response.statusText}`
        );
      }

      const data: TokenResponse = await response.json();
      this.updateTokens(data);
      return data.access;
    } catch (error) {
      console.error('Error creating new token:', error);
      throw error;
    }
  }

  private async refreshAccessToken(): Promise<string> {
    if (!this.refreshToken) {
      return this.createNewToken();
    }

    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/token/refresh/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          refresh: this.refreshToken,
        }),
      });

      if (!response.ok) {
        // If refresh fails, create a new token
        return this.createNewToken();
      }

      const data: TokenResponse = await response.json();
      this.updateTokens(data);
      return data.access;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return this.createNewToken();
    }
  }

  private updateTokens(data: TokenResponse) {
    this.accessToken = data.access;
    this.refreshToken = data.refresh;
    this.accessExpires = Date.now() + (data.access_expires * 1000);
    this.refreshExpires = Date.now() + (data.refresh_expires * 1000);
  }
}

export const authService = new AuthService();