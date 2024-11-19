import dotenv from 'dotenv';

dotenv.config();

export const env = {
  secretId: process.env.VITE_SECRET_ID,
  secretKey: process.env.VITE_SECRET_KEY,
  apiBaseUrl: process.env.VITE_API_BASE_URL,
};