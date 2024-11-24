export const API_CONFIG = {
  baseUrl: 'http://localhost:4000/api',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
} as const;

export function getAuthHeaders() {
  return {
    ...API_CONFIG.headers,
  };
}