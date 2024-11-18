import { API_CONFIG, getAuthHeaders } from '../config/api';
import { authService } from './auth';
import type { RequisitionsResponse, Institution, InstitutionsResponse, Requisition, RequisitionDetails } from '../types/gocardless';

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

export async function fetchRequisitionDetails(id: string): Promise<RequisitionDetails> {
  try {
    const accessToken = await authService.getAccessToken();
    const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/${id}/`, {
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
    console.error('Error fetching requisition details:', error);
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

export async function createRequisition(params: {
  institutionId: string;
  redirectUrl: string;
  reference: string;
  userLanguage: string;
}): Promise<Requisition> {
  try {
    const accessToken = await authService.getAccessToken();
    const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/`, {
      method: 'POST',
      headers: getAuthHeaders(accessToken),
      body: JSON.stringify({
        institution_id: params.institutionId,
        redirect: params.redirectUrl,
        reference: params.reference,
        user_language: params.userLanguage,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.message || `API error: ${response.status} ${response.statusText}`
      );
    }

    return response.json();
  } catch (error) {
    console.error('Error creating requisition:', error);
    throw error;
  }
}