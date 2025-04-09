import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    host: true, // 允许外部访问
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        secure: false
      }
    },
    watch: {
      usePolling: true
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true, // 开发环境启用 sourcemap
    minify: false, // 开发环境不压缩代码
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'axios', '@vueuse/core']
        }
      }
    }
  }
}) 