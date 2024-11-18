import { API_CONFIG, getAuthHeaders } from '../config/api';
import { authService } from './auth';
import type { RequisitionsResponse } from '../types/gocardless';

export async function fetchRequisitions(): Promise<RequisitionsResponse> {
  try {
    const accessToken = await authService.getAccessToken();
    const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/`, {
      headers: getAuthHeaders(accessToken),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.message || `API error: ${response.status} ${response.statusText}`
      );
    }

    return response.json();
  } catch (error) {
    console.error('Error fetching requisitions:', error);
    throw error;
  }
}