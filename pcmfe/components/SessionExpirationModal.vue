<template>
  <UModal v-model="isOpen" :ui="{ width: 'w-full sm:max-w-md' }">
    <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
      <template #header>
        <div class="flex items-center gap-3">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-yellow-500" />
          <h3 class="text-lg font-semibold text-gray-900">Session Expiring Soon</h3>
        </div>
      </template>

      <div class="space-y-4">
        <p class="text-gray-600">
          Your session will expire in <span class="font-bold text-red-600">{{ timeRemaining }}</span> seconds due to inactivity.
        </p>

        <!-- Countdown Progress Bar -->
        <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            class="bg-gradient-to-r from-yellow-500 to-red-500 h-full transition-all duration-1000"
            :style="{ width: `${(timeRemaining / warningDuration) * 100}%` }"
          ></div>
        </div>

        <p class="text-sm text-gray-500">
          Click "Continue Session" to stay logged in, or you will be automatically logged out.
        </p>
      </div>

      <template #footer>
        <div class="flex gap-3">
          <UButton
            color="gray"
            variant="ghost"
            @click="handleLogout"
            class="flex-1"
          >
            Logout Now
          </UButton>
          <UButton
            color="primary"
            @click="handleContinue"
            class="flex-1 bg-gradient-to-r from-[#E57000] to-[#FF8C00] hover:from-[#CC6600] hover:to-[#E57000]"
          >
            Continue Session
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useAuth } from '~/composables/useAuth'

const auth = useAuth()
const isOpen = ref(false)
const timeRemaining = ref(0)
const warningDuration = ref(60) // 60 seconds warning
let countdownInterval: NodeJS.Timeout | null = null

/**
 * Handle continue session
 */
const handleContinue = async () => {
  isOpen.value = false
  await auth.refreshAuth()
  // Reset session timeout
  window.dispatchEvent(new CustomEvent('auth-session-reset'))
}

/**
 * Handle logout
 */
const handleLogout = async () => {
  isOpen.value = false
  await auth.logout()
}

/**
 * Start countdown timer
 */
const startCountdown = () => {
  timeRemaining.value = warningDuration.value

  countdownInterval = setInterval(() => {
    timeRemaining.value--

    if (timeRemaining.value <= 0) {
      stopCountdown()
      handleLogout()
    }
  }, 1000)
}

/**
 * Stop countdown timer
 */
const stopCountdown = () => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
}

/**
 * Initialize modal
 */
onMounted(() => {
  if (process.client) {
    window.addEventListener('auth-session-warning', () => {
      isOpen.value = true
      startCountdown()
    })

    window.addEventListener('auth-session-reset', () => {
      stopCountdown()
    })
  }
})

/**
 * Cleanup
 */
onUnmounted(() => {
  stopCountdown()
  if (process.client) {
    window.removeEventListener('auth-session-warning', () => {})
    window.removeEventListener('auth-session-reset', () => {})
  }
})
</script>

