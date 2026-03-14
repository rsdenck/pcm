/**
 * useAuth Composable
 * Provides reactive authentication state and methods
 */

import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '~/services/auth/authService'
import { sessionManager } from '~/services/auth/sessionManager'

interface User {
  id: string
  email: string
  name: string
  roles: string[]
  permissions: string[]
  tenant_id: string
}

export const useAuth = () => {
  const router = useRouter()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)

  // Computed properties
  const isAdmin = computed(() => user.value?.roles.includes('admin') ?? false)
  const isTenantManager = computed(() => user.value?.roles.includes('tenant_manager') ?? false)
  const isTenantUser = computed(() => user.value?.roles.includes('tenant_user') ?? false)

  /**
   * Initialize authentication state
   */
  const initializeAuth = () => {
    const tokenInfo = authService.getCurrentUser()
    if (tokenInfo && authService.isAuthenticated()) {
      user.value = {
        id: tokenInfo.sub,
        email: tokenInfo.email,
        name: tokenInfo.email.split('@')[0],
        roles: tokenInfo.roles || [],
        permissions: tokenInfo.permissions || [],
        tenant_id: tokenInfo.tenant_id
      }
      isAuthenticated.value = true
      sessionManager.start()
    } else {
      isAuthenticated.value = false
    }
  }

  /**
   * Login with email and password
   */
  const login = async (email: string, password: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authService.login({ email, password })

      user.value = {
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        roles: response.user.roles,
        permissions: response.user.permissions,
        tenant_id: response.user.tenant_id
      }

      isAuthenticated.value = true
      sessionManager.start()

      // Redirect to dashboard
      await router.push('/dashboard')
    } catch (err: any) {
      error.value = err.message || 'Login failed'
      isAuthenticated.value = false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout user
   */
  const logout = async () => {
    isLoading.value = true
    error.value = null

    try {
      await authService.logout()
      user.value = null
      isAuthenticated.value = false
      sessionManager.stop()

      // Redirect to login
      await router.push('/login')
    } catch (err: any) {
      error.value = err.message || 'Logout failed'
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Refresh authentication token
   */
  const refreshAuth = async () => {
    try {
      await authService.refreshToken()
      const tokenInfo = authService.getCurrentUser()
      if (tokenInfo) {
        user.value = {
          id: tokenInfo.sub,
          email: tokenInfo.email,
          name: tokenInfo.email.split('@')[0],
          roles: tokenInfo.roles || [],
          permissions: tokenInfo.permissions || [],
          tenant_id: tokenInfo.tenant_id
        }
      }
    } catch (err: any) {
      console.error('Token refresh failed:', err)
      await logout()
    }
  }

  /**
   * Request password reset
   */
  const requestPasswordReset = async (email: string) => {
    isLoading.value = true
    error.value = null

    try {
      await authService.requestPasswordReset(email)
      return true
    } catch (err: any) {
      error.value = err.message || 'Password reset request failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Confirm password reset
   */
  const confirmPasswordReset = async (token: string, newPassword: string) => {
    isLoading.value = true
    error.value = null

    try {
      await authService.confirmPasswordReset(token, newPassword)
      return true
    } catch (err: any) {
      error.value = err.message || 'Password reset failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Check if user has permission
   */
  const hasPermission = (permission: string): boolean => {
    return user.value?.permissions.includes(permission) ?? false
  }

  /**
   * Check if user has role
   */
  const hasRole = (role: string): boolean => {
    return user.value?.roles.includes(role) ?? false
  }

  /**
   * Check if user has any of the given roles
   */
  const hasAnyRole = (roles: string[]): boolean => {
    return roles.some(role => hasRole(role))
  }

  /**
   * Check if user has all of the given roles
   */
  const hasAllRoles = (roles: string[]): boolean => {
    return roles.every(role => hasRole(role))
  }

  // Setup session event listeners
  if (typeof window !== 'undefined') {
    sessionManager.on('session-warning', () => {
      // Emit event for session warning modal
      window.dispatchEvent(new CustomEvent('auth-session-warning'))
    })

    sessionManager.on('session-expired', () => {
      // Logout on session expiration
      logout()
    })
  }

  return {
    // State
    isLoading,
    error,
    user,
    isAuthenticated,

    // Computed
    isAdmin,
    isTenantManager,
    isTenantUser,

    // Methods
    initializeAuth,
    login,
    logout,
    refreshAuth,
    requestPasswordReset,
    confirmPasswordReset,
    hasPermission,
    hasRole,
    hasAnyRole,
    hasAllRoles
  }
}
