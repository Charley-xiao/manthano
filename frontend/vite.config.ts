import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import ViteAutoImport from 'unplugin-auto-import/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    ViteAutoImport({
      imports: ['vue', 'vue-router'],
      dts: './src/auto-imports.d.ts',
    })
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:9265',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
