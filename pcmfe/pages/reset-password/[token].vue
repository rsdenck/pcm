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

      <!-- Reset Password Card -->
      <UCard class="shadow-xl border-0">
        <template #header>
          <div class="text-center">
            <h2 class="text-2xl font-bold text-gray-900">Reset Password</h2>
            <p class="text-sm text-gray-600 mt-1">Enter your new password</p>
          </div>
        </template>

        <!-- Success Alert -->
        <div v-if="resetSuccess" class="mb-6">
          <UAlert
            icon="i-heroicons-check-circle"
            color="green"
            variant="soft"
            title="Password Reset Successful"
            description="Your password has been reset. Redirecting to login..."
          />
        </div>

        <!-- Error Alert -->
        <div v-if="auth.error && !resetSuccess" class="mb-6">
          <UAlert
            icon="i-heroicons-exclamation-circle"
            color="red"
            variant="soft"
            :title="'Reset Failed'"
            :description="auth.error"
            @close="auth.error = null"
          />
        </div>

        <!-- Reset Form -->
        <form v-if="!resetSuccess" @submit.prevent="handleResetPassword" class="space-y-4">
          <!-- Password Field -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              New Password
            </label>
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
            <p class="mt-2 text-xs text-gray-500">
              Password must be at least 8 characters long
            </p>
          </div>

          <!-- Confirm Password Field -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password
            </label>
            <UInput
              v-model="formData.confirmPassword"
              type="password"
              placeholder="••••••••"
              icon="i-heroicons-lock-closed"
              :error="validation.hasFieldError('confirmPassword') && validation.isFieldTouched('confirmPassword')"
              @blur="validation.markTouched('confirmPassword')"
              @input="() => validation.clearFieldError('confirmPassword')"
              :ui="{
                base: 'relative block w-full disabled:cursor-not-allowed disabled:opacity-75 focus:outline-none border-0',
                rounded: 'rounded-lg',
                size: { md: 'text-sm px-3 py-2.5' },
                color: { white: 'bg-gray-50 shadow-sm ring-1 ring-gray-200 focus:ring-2 focus:ring-[#E57000] focus:ring-opacity-20' }
              }"
            />
            <p v-if="validation.hasFieldError('confirmPassword') && validation.isFieldTouched('confirmPassword')" class="mt-1 text-sm text-red-600">
              {{ validation.getFieldError('confirmPassword') }}
            </p>
          </div>

          <!-- Password Requirements -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p class="text-xs font-medium text-blue-900 mb-2">Password Requirements:</p>
            <ul class="text-xs text-blue-800 space-y-1">
              <li class="flex items-center gap-2">
                <UIcon :name="formData.password.length >= 8 ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="formData.password.length >= 8 ? 'text-green-600' : 'text-gray-400'" class="w-4 h-4" />
                At least 8 characters
              </li>
              <li class="flex items-center gap-2">
                <UIcon :name="/[A-Z]/.test(formData.password) ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="/[A-Z]/.test(formData.password) ? 'text-green-600' : 'text-gray-400'" class="w-4 h-4" />
                One uppercase letter
              </li>
              <li class="flex items-center gap-2">
                <UIcon :name="/[a-z]/.test(formData.password) ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="/[a-z]/.test(formData.password) ? 'text-green-600' : 'text-gray-400'" class="w-4 h-4" />
                One lowercase letter
              </li>
              <li class="flex items-center gap-2">
                <UIcon :name="/[0-9]/.test(formData.password) ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" :class="/[0-9]/.test(formData.password) ? 'text-green-600' : 'text-gray-400'" class="w-4 h-4" />
                One number
              </li>
            </ul>
          </div>

          <!-- Submit Button -->
          <UButton
            type="submit"
            :loading="auth.isLoading"
            :disabled="auth.isLoading"
            class="w-full bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white font-medium shadow-md hover:shadow-lg transition-all"
            size="lg"
          >
            <span v-if="!auth.isLoading">Reset Password</span>
            <span v-else class="flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="animate-spin" />
              Resetting...
            </span>
          </UButton>

          <!-- Back to Login -->
          <div class="text-center">
            <NuxtLink
              to="/login"
              class="text-sm text-[#E57000] hover:text-[#FF8C00] font-medium transition-colors"
            >
              Back to Login
            </NuxtLink>
          </div>
        </form>
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
import { useRoute } from 'vue-router'
import { useAuth } from '~/composables/useAuth'
import { useFormValidation } from '~/composables/useFormValidation'
import { useDebounce } from '~/composables/useDebounce'

definePageMeta({
  layout: 'blank'
})

useHead({
  title: 'Reset Password - PCM',
  meta: [
    { name: 'description', content: 'Reset your PCM password' }
  ]
})

const route = useRoute()
const auth = useAuth()
const validation = useFormValidation()
const { debounce } = useDebounce()
const resetSuccess = ref(false)

const formData = ref({
  password: '',
  confirmPassword: ''
})

/**
 * Validate password strength
 */
const validatePasswordStrength = (password: string): boolean => {
  const hasUpperCase = /[A-Z]/.test(password)
  const hasLowerCase = /[a-z]/.test(password)
  const hasNumbers = /[0-9]/.test(password)
  const isLongEnough = password.length >= 8

  return hasUpperCase && hasLowerCase && hasNumbers && isLongEnough
}

/**
 * Handle password reset
 */
const handleResetPassword = async () => {
  // Validate form
  const isValid = validation.validateFields({
    password: {
      value: formData.value.password,
      rules: [
        validation.requiredRule,
        {
          validate: (value: string) => validatePasswordStrength(value),
          message: 'Password must contain uppercase, lowercase, number, and be at least 8 characters'
        }
      ]
    },
    confirmPassword: {
      value: formData.value.confirmPassword,
      rules: [
        validation.requiredRule,
        {
          validate: (value: string) => value === formData.value.password,
          message: 'Passwords do not match'
        }
      ]
    }
  })

  if (!isValid) {
    validation.markAllTouched()
    return
  }

  // Attempt password reset with debounce
  const token = route.params.token as string
  const success = await debounce(() => auth.confirmPasswordReset(token, formData.value.password), 500, 'reset-password')

  if (success) {
    resetSuccess.value = true
    // Redirect to login after 3 seconds
    setTimeout(() => {
      navigateTo('/login')
    }, 3000)
  }
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

