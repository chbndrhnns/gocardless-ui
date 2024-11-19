import { API_CONFIG } from '../config/api';
import type { RequisitionsResponse, Institution, InstitutionsResponse, Requisition, RequisitionDetails, BankAccount } from '../types/gocardless';

export async function fetchRequisitions(): Promise<RequisitionsResponse> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/requisitions`);
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

export async function fetchAccountDetails(accountId: string): Promise<BankAccount> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/accounts/${accountId}`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
          errorData?.message || `API error: ${response.status} ${response.statusText}`
      );
    }
    return response.json();
  } catch (error) {
    console.error('Error fetching account details:', error);
    throw error;
  }
}

export async function deleteRequisition(id: string): Promise<void> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
          errorData?.message || `API error: ${response.status} ${response.statusText}`
      );
    }
  } catch (error) {
    console.error('Error deleting requisition:', error);
    throw error;
  }
}

export async function fetchRequisitionDetails(id: string): Promise<RequisitionDetails> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/${id}`);
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
    const response = await fetch(`${API_CONFIG.baseUrl}/institutions?country=${country}`);
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
    const response = await fetch(`${API_CONFIG.baseUrl}/requisitions`, {
      method: 'POST',
      headers: API_CONFIG.headers,
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