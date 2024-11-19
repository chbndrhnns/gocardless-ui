import { API_CONFIG } from '../config/api.js';
import { getAccessToken } from './auth.js';
import { getAccountDetails } from './accounts.js';

export async function getRequisitions() {
  const token = await getAccessToken();
  const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/`, {
    headers: {
      ...API_CONFIG.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch requisitions: ${response.status}`);
  }

  const data = await response.json();
  return {
    ...data,
    results: data.results.sort((a, b) => 
      new Date(a.created).getTime() - new Date(b.created).getTime()
    ),
  };
}

export async function getRequisitionDetails(id) {
  const token = await getAccessToken();
  const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/${id}/`, {
    headers: {
      ...API_CONFIG.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch requisition details: ${response.status}`);
  }

  const requisition = await response.json();
  const accountDetails = await Promise.all(
    requisition.accounts.map(accountId => getAccountDetails(accountId))
  );

  return {
    ...requisition,
    accounts: accountDetails,
  };
}

export async function createNewRequisition(params) {
  const token = await getAccessToken();
  const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/`, {
    method: 'POST',
    headers: {
      ...API_CONFIG.headers,
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      institution_id: params.institutionId,
      redirect: params.redirectUrl,
      reference: params.reference,
      user_language: params.userLanguage,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create requisition: ${response.status}`);
  }

  return response.json();
}

export async function removeRequisition(id) {
  const token = await getAccessToken();
  const response = await fetch(`${API_CONFIG.baseUrl}/requisitions/${id}/`, {
    method: 'DELETE',
    headers: {
      ...API_CONFIG.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete requisition: ${response.status}`);
  }
}