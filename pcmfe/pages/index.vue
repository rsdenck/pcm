<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

const auth = useAuth()

// Initialize auth
if (process.client) {
  auth.initializeAuth()
}

// Redirect based on authentication status
if (auth.isAuthenticated.value) {
  navigateTo('/dashboard', { replace: true })
} else {
  navigateTo('/login', { replace: true })
}
</script>

<template>
  <div></div>
</template>
