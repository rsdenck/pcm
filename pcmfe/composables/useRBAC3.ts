/**
 * RBAC3 Hybrid Authentication & Authorization Composable
 * 
 * Provides reactive access to user roles, permissions, and authorization checks
 * for both local and LDAP-authenticated users.
 */

import { ref, computed, watch } from 'vue'
import { useAuth } from './useAuth'
import { authService } from '~/services/auth/authService'

export interface UserPermission {
  id: string
  name: string
  resource: string
  action: string
  description?: string
}

export interface UserRole {
  id: string
  name: string
  description?: string
  permissions: UserPermission[]
}

export interface RBACUser {
  id: string
  email: string
  username: string
  full_name?: string
  roles: UserRole[]
  permissions: UserPermission[]
  is_ldap_user: boolean
  ldap_groups?: string[]
}

export const useRBAC3 = () => {
  const { user: authUser } = useAuth()
  
  // State
  const rbacUser = ref<RBACUser | null>(null)
  const userRoles = ref<UserRole[]>([])
  const userPermissions = ref<UserPermission[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Computed properties
  const hasRole = computed(() => {
    return (roleName: string): boolean => {
      return userRoles.value.some(r => r.name === roleName)
    }
  })
  
  const hasPermission = computed(() => {
    return (permissionName: string): boolean => {
      return userPermissions.value.some(p => p.name === permissionName)
    }
  })
  
  const hasAnyPermission = computed(() => {
    return (permissionNames: string[]): boolean => {
      return permissionNames.some(p => 
        userPermissions.value.some(up => up.name === p)
      )
    }
  })
  
  const hasAllPermissions = computed(() => {
    return (permissionNames: string[]): boolean => {
      return permissionNames.every(p => 
        userPermissions.value.some(up => up.name === p)
      )
    }
  })
  
  const isAdmin = computed(() => {
    return hasRole.value('admin')
  })
  
  const isTenantAdmin = computed(() => {
    return hasRole.value('tenant_admin')
  })
  
  const isTenantManager = computed(() => {
    return hasRole.value('tenant_manager')
  })
  
  const isTenantUser = computed(() => {
    return hasRole.value('tenant_user')
  })
  
  const isLDAPUser = computed(() => {
    return rbacUser.value?.is_ldap_user ?? false
  })
  
  const ldapGroups = computed(() => {
    return rbacUser.value?.ldap_groups ?? []
  })
  
  // Methods
  const loadUserRBAC = async () => {
    if (!authUser.value) {
      error.value = 'User not authenticated'
      return
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      const config = useRuntimeConfig()
      const token = authService.getAccessToken()
      
      if (!token) {
        error.value = 'No authentication token available'
        return
      }
      
      const response = await $fetch<{
        id: string
        email: string
        username: string
        full_name?: string
        roles: UserRole[]
        permissions: UserPermission[]
        is_ldap_user: boolean
        ldap_groups?: string[]
      }>(`${config.public.apiBase}/users/${authUser.value.id}/rbac`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response) {
        rbacUser.value = response
        userRoles.value = response.roles || []
        userPermissions.value = response.permissions || []
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to load RBAC information'
      console.error('Error loading RBAC:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  const checkPermission = (permissionName: string): boolean => {
    return hasPermission.value(permissionName)
  }
  
  const checkRole = (roleName: string): boolean => {
    return hasRole.value(roleName)
  }
  
  const checkResourceAccess = (resource: string, action: string): boolean => {
    // PROVIDER_ADMIN tem acesso total a todos os recursos
    const userRoles = authUser.value?.roles || []
    if (userRoles.includes('PROVIDER_ADMIN') || userRoles.includes('provider_admin')) {
      return true
    }
    
    const permissionName = `${resource}:${action}`
    return hasPermission.value(permissionName)
  }
  
  const canCreate = (resource: string): boolean => {
    // PROVIDER_ADMIN tem acesso total
    const userRoles = authUser.value?.roles || []
    if (userRoles.includes('PROVIDER_ADMIN') || userRoles.includes('provider_admin')) {
      return true
    }
    return checkResourceAccess(resource, 'create')
  }
  
  const canRead = (resource: string): boolean => {
    // PROVIDER_ADMIN tem acesso total
    const userRoles = authUser.value?.roles || []
    if (userRoles.includes('PROVIDER_ADMIN') || userRoles.includes('provider_admin')) {
      return true
    }
    return checkResourceAccess(resource, 'read')
  }
  
  const canUpdate = (resource: string): boolean => {
    // PROVIDER_ADMIN tem acesso total
    const userRoles = authUser.value?.roles || []
    if (userRoles.includes('PROVIDER_ADMIN') || userRoles.includes('provider_admin')) {
      return true
    }
    return checkResourceAccess(resource, 'update')
  }
  
  const canDelete = (resource: string): boolean => {
    // PROVIDER_ADMIN tem acesso total
    const userRoles = authUser.value?.roles || []
    if (userRoles.includes('PROVIDER_ADMIN') || userRoles.includes('provider_admin')) {
      return true
    }
    return checkResourceAccess(resource, 'delete')
  }
  
  const canManage = (resource: string): boolean => {
    // PROVIDER_ADMIN tem acesso total
    const userRoles = authUser.value?.roles || []
    if (userRoles.includes('PROVIDER_ADMIN') || userRoles.includes('provider_admin')) {
      return true
    }
    return checkResourceAccess(resource, 'manage')
  }
  
  const requirePermission = (permissionName: string): void => {
    if (!hasPermission.value(permissionName)) {
      throw new Error(`Permission denied: ${permissionName}`)
    }
  }
  
  const requireRole = (roleName: string): void => {
    if (!hasRole.value(roleName)) {
      throw new Error(`Role required: ${roleName}`)
    }
  }
  
  const requireAnyRole = (roleNames: string[]): void => {
    if (!roleNames.some(r => hasRole.value(r))) {
      throw new Error(`One of these roles required: ${roleNames.join(', ')}`)
    }
  }
  
  const requireAllRoles = (roleNames: string[]): void => {
    if (!roleNames.every(r => hasRole.value(r))) {
      throw new Error(`All of these roles required: ${roleNames.join(', ')}`)
    }
  }
  
  // Watch for auth user changes
  watch(authUser, async (newUser) => {
    if (newUser) {
      await loadUserRBAC()
    } else {
      rbacUser.value = null
      userRoles.value = []
      userPermissions.value = []
    }
  }, { immediate: true })
  
  return {
    // State
    rbacUser,
    userRoles,
    userPermissions,
    isLoading,
    error,
    
    // Computed
    hasRole,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isAdmin,
    isTenantAdmin,
    isTenantManager,
    isTenantUser,
    isLDAPUser,
    ldapGroups,
    
    // Methods
    loadUserRBAC,
    checkPermission,
    checkRole,
    checkResourceAccess,
    canCreate,
    canRead,
    canUpdate,
    canDelete,
    canManage,
    requirePermission,
    requireRole,
    requireAnyRole,
    requireAllRoles
  }
}
