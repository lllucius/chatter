import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'build',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor libraries
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@mui/material', '@mui/icons-material'],
          charts: ['recharts'],
          utils: ['date-fns', 'axios'],
        },
      },
    },
  },
  define: {
    global: 'globalThis',
  },
  root: '.',
  publicDir: 'public'
})