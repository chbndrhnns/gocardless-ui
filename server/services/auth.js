import { env } from '../config/env.js';
import { API_CONFIG } from '../config/api.js';

let accessToken = null;
let refreshToken = null;
let accessExpires = null;
let refreshExpires = null;

export async function getAccessToken() {
  if (accessToken && accessExpires && Date.now() < accessExpires) {
    return accessToken;
  }

  if (refreshToken && refreshExpires && Date.now() < refreshExpires) {
    return refreshAccessToken();
  }

  return createNewToken();
}

async function createNewToken() {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/token/new/`, {
      method: 'POST',
      headers: API_CONFIG.headers,
      body: JSON.stringify({
        secret_id: env.secretId,
        secret_key: env.secretKey,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create token: ${response.status}`);
    }

    const data = await response.json();
    updateTokens(data);
    return data.access;
  } catch (error) {
    throw new Error(`Error creating token: ${error.message}`);
  }
}

async function refreshAccessToken() {
  if (!refreshToken) {
    return createNewToken();
  }

  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/token/refresh/`, {
      method: 'POST',
      headers: API_CONFIG.headers,
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      return createNewToken();
    }

    const data = await response.json();
    updateTokens(data);
    return data.access;
  } catch (error) {
    return createNewToken();
  }
}

function updateTokens(data) {
  accessToken = data.access;
  refreshToken = data.refresh;
  accessExpires = Date.now() + (data.access_expires * 1000);
  refreshExpires = Date.now() + (data.refresh_expires * 1000);
}