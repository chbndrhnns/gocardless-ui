import { API_CONFIG, getAuthHeaders } from '../config/api';
import { authService } from './auth';
import type { RequisitionsResponse, Institution, InstitutionsResponse } from '../types/gocardless';

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

export async function fetchInstitutions(country: string): Promise<Institution[]> {
  try {
    const accessToken = await authService.getAccessToken();
    const response = await fetch(`${API_CONFIG.baseUrl}/institutions/?country=${country}`, {
      headers: getAuthHeaders(accessToken),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.message || `API error: ${response.status} ${response.statusText}`
      );
    }

    const data: InstitutionsResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching institutions:', error);
    throw error;
  }
}