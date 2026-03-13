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

      <!-- Password Reset Card -->
      <UCard class="shadow-xl border-0">
        <template #header>
          <div class="text-center">
            <h2 class="text-2xl font-bold text-gray-900">Reset Password</h2>
            <p class="text-sm text-gray-600 mt-1">Enter your email to receive a reset link</p>
          </div>
        </template>

        <!-- Success Message -->
        <div v-if="resetSent" class="mb-6">
          <UAlert
            icon="i-heroicons-check-circle"
            color="green"
            variant="soft"
            title="Email Sent"
            description="Check your email for password reset instructions"
          />
        </div>

        <!-- Error Alert -->
        <div v-if="auth.error" class="mb-6">
          <UAlert
            icon="i-heroicons-exclamation-circle"
            color="red"
            variant="soft"
            :title="'Error'"
            :description="auth.error"
            @close="auth.error = null"
          />
        </div>

        <!-- Reset Form -->
        <form v-if="!resetSent" @submit.prevent="handleResetRequest" class="space-y-4">
          <!-- Email Field -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <UInput
              v-model="email"
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

          <!-- Submit Button -->
          <UButton
            type="submit"
            :loading="auth.isLoading"
            :disabled="auth.isLoading"
            class="w-full bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000] text-white font-medium shadow-md hover:shadow-lg transition-all"
            size="lg"
          >
            <span v-if="!auth.isLoading">Send Reset Link</span>
            <span v-else class="flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="animate-spin" />
              Sending...
            </span>
          </UButton>
        </form>

        <!-- Back to Login -->
        <div class="mt-6 text-center">
          <NuxtLink
            to="/login"
            class="text-sm text-[#E57000] hover:text-[#FF8C00] font-medium transition-colors flex items-center justify-center gap-2"
          >
            <UIcon name="i-heroicons-arrow-left" />
            Back to Sign In
          </NuxtLink>
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
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useFormValidation } from '~/composables/useFormValidation'

definePageMeta({
  layout: 'blank'
})

useHead({
  title: 'Forgot Password - PCM',
  meta: [
    { name: 'description', content: 'Reset your PCM password' }
  ]
})

const auth = useAuth()
const validation = useFormValidation()

const email = ref('')
const resetSent = ref(false)

/**
 * Handle password reset request
 */
const handleResetRequest = async () => {
  // Validate email
  const isValid = validation.validateFields({
    email: {
      value: email.value,
      rules: [validation.requiredRule, validation.emailRule]
    }
  })

  if (!isValid) {
    validation.markAllTouched()
    return
  }

  // Request password reset
  const success = await auth.requestPasswordReset(email.value)
  if (success) {
    resetSent.value = true
  }
}
</script>
