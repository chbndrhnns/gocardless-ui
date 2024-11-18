interface EnvConfig {
  secretId: string;
  secretKey: string;
  apiBaseUrl: string;
}

export const env: EnvConfig = {
  secretId: import.meta.env.VITE_SECRET_ID,
  secretKey: import.meta.env.VITE_SECRET_KEY,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
} as const;

// Validate environment variables
const requiredEnvVars: (keyof EnvConfig)[] = ['secretId', 'secretKey', 'apiBaseUrl'];

requiredEnvVars.forEach((key) => {
  if (!env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
});