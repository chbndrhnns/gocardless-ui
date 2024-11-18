export const API_CONFIG = {
  baseUrl: `/api`,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
} as const;

export function getAuthHeaders(token?: string) {
  return {
    ...API_CONFIG.headers,
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
}