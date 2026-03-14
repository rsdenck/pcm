export default defineNuxtConfig({
  devtools: { enabled: true },
  
  // Configuração do servidor de desenvolvimento
  devServer: {
    host: '192.168.130.10',
    port: 9000
  },
  
  modules: ['@nuxt/ui'],
  
  css: ['~/assets/css/main.css'],
  
  colorMode: {
    preference: 'light',
    fallback: 'light'
  },
  
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://192.168.130.10:9001/api/v1'
    }
  },
  
  // Register RBAC directives
  plugins: [
    '~/plugins/rbac-directives.ts'
  ],
  
  app: {
    head: {
      title: 'PCM - Proxmox Center Manager',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Cloud Control Plane for Proxmox Infrastructure' }
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: 'https://cdn.iconscout.com/icon/premium/png-256-thumb/proxmox-logo-icon-svg-download-png-7196884.png?f=webp' }
      ]
    }
  },
  
  // Redirect root to login
  router: {
    options: {
      strict: true
    }
  },
  
  compatibilityDate: '2024-01-01'
})
