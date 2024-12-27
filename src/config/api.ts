const getBaseUrl = () => {
    const {protocol, hostname} = window.location;
    const backendPort = import.meta.env.VITE_BACKEND_PORT || '4000';
    return `${protocol}//${hostname}:${backendPort}/api`;
};

export const API_CONFIG = {
    baseUrl: getBaseUrl(),
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    },
} as const;
