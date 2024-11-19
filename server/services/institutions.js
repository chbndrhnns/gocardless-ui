import { API_CONFIG } from '../config/api.js';
import { getAccessToken } from './auth.js';

export async function getInstitutions(country) {
  const token = await getAccessToken();
  const response = await fetch(`${API_CONFIG.baseUrl}/institutions/?country=${country}`, {
    headers: {
      ...API_CONFIG.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch institutions: ${response.status}`);
  }

  return response.json();
}