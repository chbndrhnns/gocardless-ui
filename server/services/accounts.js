import { API_CONFIG } from '../config/api.js';
import { getAccessToken } from './auth.js';

export async function getAccountDetails(accountId) {
  const token = await getAccessToken();
  const response = await fetch(`${API_CONFIG.baseUrl}/accounts/${accountId}/`, {
    headers: {
      ...API_CONFIG.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch account details: ${response.status}`);
  }

  return response.json();
}