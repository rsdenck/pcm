<template>
  <div class="relative">
    <!-- User Menu Button -->
    <UButton
      color="gray"
      variant="ghost"
      icon="i-heroicons-user-circle"
      :trailing="true"
      @click="isOpen = !isOpen"
      class="flex items-center gap-2"
    >
      <span class="hidden sm:inline text-sm font-medium">{{ userDisplayName }}</span>
      <UIcon name="i-heroicons-chevron-down" class="w-4 h-4" />
    </UButton>

    <!-- Dropdown Menu -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
      >
        <!-- User Info Section -->
        <div class="px-4 py-3 border-b border-gray-100">
          <p class="text-sm font-medium text-gray-900">{{ auth.user?.name }}</p>
          <p class="text-xs text-gray-500">{{ auth.user?.email }}</p>
        </div>

        <!-- Menu Items -->
        <div class="py-2">
          <!-- Profile -->
          <NuxtLink
            to="/dashboard/profile"
            class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            @click="isOpen = false"
          >
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-user" class="w-4 h-4" />
              <span>Profile</span>
            </div>
          </NuxtLink>

          <!-- Settings -->
          <NuxtLink
            to="/dashboard/settings"
            class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            @click="isOpen = false"
          >
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" />
              <span>Settings</span>
            </div>
          </NuxtLink>

          <!-- Change Password -->
          <button
            @click="handleChangePassword"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-lock-closed" class="w-4 h-4" />
              <span>Change Password</span>
            </div>
          </button>

          <!-- Divider -->
          <div class="my-2 border-t border-gray-100"></div>

          <!-- Logout -->
          <button
            @click="handleLogout"
            class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-left-on-rectangle" class="w-4 h-4" />
              <span>Logout</span>
            </div>
          </button>
        </div>
      </div>
    </Transition>

    <!-- Click outside to close -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40"
      @click="isOpen = false"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuth } from '~/composables/useAuth'

const auth = useAuth()
const isOpen = ref(false)

const userDisplayName = computed(() => {
  if (!auth.user?.name) return 'User'
  const name = auth.user.name
  return name.length > 15 ? name.substring(0, 12) + '...' : name
})

/**
 * Handle change password
 */
const handleChangePassword = () => {
  isOpen.value = false
  navigateTo('/dashboard/change-password')
}

/**
 * Handle logout
 */
const handleLogout = async () => {
  isOpen.value = false
  await auth.logout()
}
</script>

