import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import ViteAutoImport from 'unplugin-auto-import/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    ViteAutoImport({
      imports: ['vue', 'vue-router'],
      dts: './src/auto-imports.d.ts',
    }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      manifest: {
        name: 'Vite App',
        short_name: 'Vite App',
        theme_color: '#ffffff',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
      devOptions: {
        enabled: true, // Enable for testing in development
        type: 'module'
      }
    }),
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
