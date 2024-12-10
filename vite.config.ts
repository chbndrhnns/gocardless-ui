import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(() => ({
    plugins: [react()],
    preview: {
        port: 5173,
        host: "0.0.0.0"
    },
    server: {
        port: 5173,
        host: "0.0.0.0"
    },
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/test/setup.ts',
        css: true
    }
}));