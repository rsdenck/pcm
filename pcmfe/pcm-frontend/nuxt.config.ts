export default defineNuxtConfig({
  devtools: { enabled: true },
  
  modules: ['@nuxt/ui'],
  
  css: ['~/assets/css/main.css'],
  
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://192.168.130.10:8000/api/v1'
    }
  },
  
  app: {
    head: {
      title: 'PCM - Proxmox Center Manager',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Cloud Control Plane for Proxmox Infrastructure' }
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }
      ]
    }
  },
  
  compatibilityDate: '2024-01-01'
})
