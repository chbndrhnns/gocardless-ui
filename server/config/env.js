import dotenv from 'dotenv';

dotenv.config();

export const env = {
  secretId: process.env.VITE_SECRET_ID,
  secretKey: process.env.VITE_SECRET_KEY,
  lunchmoney_token: process.env.LUNCHMONEY_ACCESS_TOKEN,
};