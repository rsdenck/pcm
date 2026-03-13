<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo & Brand -->
      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <div class="w-16 h-16 rounded-lg bg-gradient-to-r from-[#E57000] to-[#FF8C00] flex items-center justify-center shadow-lg">
            <img src="/favicon.svg" alt="PCM Logo" class="w-10 h-10" />
          </div>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Proxmox Center Manager</h1>
        <p class="text-gray-600">Enterprise Cloud Control Plane</p>
      </div>

      <!-- Login Card -->
      <UCard class="shadow-xl border-0">
        <template #header>
          <div class="text-center">
            <h2 class="text-2xl font-bold text-gray-900">Sign In</h2>
            <p class="text-sm text-gray-600 mt-1">Enter your credentials to access PCM</p>
          </div>
        </template>

        <!-- Error Alert -->
        <div v-if="auth.error" class="mb-6">
          <UAlert
            icon="i-heroicons-exclamation-circle"
            color="red"
            variant="soft"
            :title="'Login Failed'"
            :description="auth.error"
            @close="auth.error = null"
          />
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Email Field -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <UInput
              v-model="formData.email"
              type="email"
              placeholder="user@example.com"
              icon="i-heroicons-envelope"
              :error="validation.hasFieldError('email') && validation.isFieldTouched('email')"
              @blur="validation.markTouched('email')"
              @input="() => validation.clearFieldError('email')"
              :ui="{
                base: 'relative block w-full disabled:cursor-not-allowed disabled:opacity-75 focus:outline-none border-0',
                rounded: 'rounded-lg',
                size: { md: 'text-sm px-3 py-2.5' },
                color: { white: 'bg-gray-50 shadow-sm ring-1 ring-gray-200 focus:ring-2 focus:ring-[#E57000] focus:ring-opacity-20' }
              }"
            />
            <p v-if="validation.hasFieldError('email') && validation.isFieldTouched('email')" class="mt-1 text-sm text-red-600">
              {{ validation.getFieldError('email') }}
            </p>
          </div>

          <!-- Password Field -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="block text-sm font-medium text-gray-700">
                Password
              </label>
              <NuxtLink
                to="/forgot-password"
                class="text-sm text-[#E57000] hover:text-[#FF8C00] font-medium transition-colors"
              >
                Forgot?
              </NuxtLink>
            </div>
            <UInput
              v-model="formData.password"
              type="password"
              placeholder="••••••••"
              icon="i-heroicons-lock-closed"
              :error="validation.hasFieldError('password') && validation.isFieldTouched('password')"
              @blur="validation.markTouched('password')"
              @input="() => validation.clearFieldError('password')"
              :ui="{
                base: 'relative block w-full disabled:cursor-not-allowed disabled:opacity-75 focus:outline-none border-0',
                rounded: 'rounded-lg',
                size: { md: 'text-sm px-3 py-2.5' },
                color: { white: 'bg-gray-50 shadow-sm ring-1 ring-gray-200 focus:ring-2 focus:ring-[#E57000] focus:ring-opacity-20' }
              }"
            />
            <p v-if="validation.hasFieldError('password') && validation.isFieldTouched('password')" class="mt-1 text-sm text-red-600">
              {{ validation.getFieldError('password') }}
            </p>
          </div>

          <!-- Remember Me -->
          <div class="flex items-center">
            <UCheckbox
              v-model="formData.rememberMe"
              label="Remember me"
              class="text-sm"
            />
          </div>

          <!-- Submit Button -->
          <UButton
            type="submit"
            :loading="auth.isLoading"
            :disabled="auth.isLoading"
            class="w-full bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white font-medium shadow-md hover:shadow-lg transition-all"
            size="lg"
          >
            <span v-if="!auth.isLoading">Sign In</span>
            <span v-else class="flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="animate-spin" />
              Signing in...
            </span>
          </UButton>
        </form>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500">Or continue with</span>
          </div>
        </div>

        <!-- Demo Credentials -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <p class="text-xs font-medium text-blue-900 mb-2">Demo Credentials:</p>
          <p class="text-xs text-blue-800">
            <strong>Email:</strong> admin@pcm.local<br>
            <strong>Password:</strong> Admin@123456
          </p>
        </div>
      </UCard>

      <!-- Footer -->
      <div class="mt-8 text-center text-sm text-gray-600">
        <p>
          PCM v0.1.0 • 
          <a href="#" class="text-[#E57000] hover:text-[#FF8C00] font-medium">Documentation</a> •
          <a href="#" class="text-[#E57000] hover:text-[#FF8C00] font-medium">Support</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useFormValidation } from '~/composables/useFormValidation'

definePageMeta({
  layout: 'blank'
})

useHead({
  title: 'Sign In - PCM',
  meta: [
    { name: 'description', content: 'Sign in to Proxmox Center Manager' }
  ]
})

const auth = useAuth()
const validation = useFormValidation()

const formData = ref({
  email: '',
  password: '',
  rememberMe: false
})

/**
 * Handle login form submission
 */
const handleLogin = async () => {
  // Validate form
  const isValid = validation.validateFields({
    email: {
      value: formData.value.email,
      rules: [validation.requiredRule, validation.emailRule]
    },
    password: {
      value: formData.value.password,
      rules: [validation.requiredRule, validation.minLengthRule(8)]
    }
  })

  if (!isValid) {
    validation.markAllTouched()
    return
  }

  // Attempt login
  await auth.login(formData.value.email, formData.value.password)
}

/**
 * Initialize page
 */
onMounted(() => {
  // If already authenticated, redirect to dashboard
  if (auth.isAuthenticated.value) {
    navigateTo('/dashboard')
  }
})
</script>
