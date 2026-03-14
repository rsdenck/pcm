<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">
      <!-- Logo & Brand -->
      <div class="text-center mb-6">
        <div class="flex justify-center mb-3">
          <div class="w-20 h-20 rounded-xl bg-white border-2 border-gray-200 flex items-center justify-center shadow-lg p-3">
            <img src="https://cdn.iconscout.com/icon/premium/png-256-thumb/proxmox-logo-icon-svg-download-png-7196884.png?f=webp" alt="Proxmox Logo" class="w-full h-full object-contain" />
          </div>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">Proxmox Center Manager</h1>
      </div>

      <!-- Login Card -->
      <UCard class="shadow-lg border border-gray-200">
        <template #header>
          <div class="text-center py-2">
            <h2 class="text-xl font-bold text-gray-900">Sign In</h2>
            <p class="text-xs text-gray-600 mt-1">Enter your credentials to access PCM</p>
          </div>
        </template>

        <!-- Error Alert - Only show after login attempt -->
        <div v-if="auth.error && hasAttemptedLogin" class="mb-4">
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
        <form @submit.prevent="handleLogin" class="space-y-3">
          <!-- Email Field -->
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1.5">
              Email Address
            </label>
            <UInput
              v-model="formData.email"
              type="email"
              placeholder="E-mail"
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
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-medium text-gray-700">
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
              placeholder="Password"
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
          <div class="flex items-center gap-2">
            <input
              type="checkbox"
              id="remember-me"
              v-model="formData.rememberMe"
              class="w-4 h-4 text-[#E57000] bg-gray-100 border-gray-300 rounded focus:ring-[#E57000] focus:ring-2"
            />
            <label for="remember-me" class="text-sm text-gray-700 cursor-pointer select-none">
              Remember me
            </label>
          </div>

          <!-- Submit Button -->
          <UButton
            type="submit"
            :disabled="isSubmitting"
            :loading="isSubmitting"
            class="w-full bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white font-medium shadow-md hover:shadow-lg transition-all"
            size="md"
          >
            <span v-if="!isSubmitting">Sign In</span>
            <span v-else>Signing in...</span>
          </UButton>
        </form>

        <!-- Demo Credentials -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-4">
          <p class="text-xs font-medium text-blue-900 mb-2">Demo Credentials:</p>
          <p class="text-xs text-blue-800">
            <strong>Email:</strong> admin@pcm.local<br>
            <strong>Password:</strong> Admin@123456
          </p>
        </div>
      </UCard>

      <!-- Footer -->
      <div class="mt-6 text-center text-xs text-gray-500">
        <p>PCM v0.1.0</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useFormValidation } from '~/composables/useFormValidation'

definePageMeta({
  layout: 'blank',
  requiresAuth: false
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

const hasAttemptedLogin = ref(false)
const isSubmitting = ref(false)

/**
 * Handle login form submission
 */
const handleLogin = async () => {
  console.log('Login button clicked!')
  console.log('Form data:', formData.value)
  
  // Prevent double submission
  if (isSubmitting.value) {
    console.log('Already submitting, ignoring...')
    return
  }
  
  // Mark that user has attempted to login
  hasAttemptedLogin.value = true
  
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
    console.log('Validation failed')
    validation.markAllTouched()
    return
  }

  console.log('Validation passed, attempting login...')
  
  // Set submitting flag
  isSubmitting.value = true
  
  try {
    await auth.login(formData.value.email, formData.value.password)
    console.log('Login successful!')
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    isSubmitting.value = false
  }
}

/**
 * Initialize page
 */
onMounted(() => {
  console.log('Login page mounted')
  // If already authenticated, redirect to dashboard
  if (auth.isAuthenticated.value) {
    console.log('Already authenticated, redirecting...')
    navigateTo('/dashboard')
  }
})
</script>
