import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import ViteAutoImport from 'unplugin-auto-import/vite'
import { VitePWA } from 'vite-plugin-pwa'

// configure for the production build, see https://vitejs.dev/config/

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  base: mode === 'development' ? '/' : 'http://localhost:9265',
  build: {
    // Configure build options
    rollupOptions: {
      output: {
        manualChunks: {

        }
      }
    }
  },

  plugins: [
    vue(),
    ViteAutoImport({
      imports: ['vue', 'vue-router'],
      dts: './src/auto-imports.d.ts',
    }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      manifest: {
        name: 'Mathano',
        short_name: 'Mathano',
        description: 'Mathano is a course platform',
        theme_color: '#ffffff',
        icons: [
          {
            "src": "/pwa-192x192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any"
          },
          {
            "src": "/pwa-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any"
          },
          {
            "src": "/pwa-maskable-192x192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "maskable"
          },
          {
            "src": "/pwa-maskable-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable"
          }
        ]
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
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
})
)