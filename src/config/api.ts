export const API_CONFIG = {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:4000/api',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    },
} as const;
