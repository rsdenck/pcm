<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

const auth = useAuth()
const router = useRouter()

// Initialize auth and redirect
onMounted(async () => {
  // Initialize auth
  await auth.initializeAuth()
  
  // Wait a tick for auth state to update
  await nextTick()
  
  // Redirect based on authentication status
  if (auth.isAuthenticated.value) {
    await navigateTo('/dashboard', { replace: true })
  } else {
    await navigateTo('/login', { replace: true })
  }
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
    <div class="text-center">
      <div class="w-12 h-12 rounded-full bg-gradient-to-r from-[#E57000] to-[#FF8C00] mx-auto mb-4 animate-spin"></div>
      <p class="text-gray-600">Carregando...</p>
    </div>
  </div>
</template>
