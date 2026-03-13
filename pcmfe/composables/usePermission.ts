/**
 * usePermission Composable
 * Provides permission and role checking utilities
 */

import { computed } from 'vue'
import { useAuth } from '~/composables/useAuth'

export const usePermission = () => {
  const auth = useAuth()

  /**
   * Check if user has a specific permission
   */
  const hasPermission = (permission: string): boolean => {
    if (!auth.user?.value) return false
    return auth.user.value.permissions?.includes(permission) ?? false
  }

  /**
   * Check if user has any of the given permissions
   */
  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(permission => hasPermission(permission))
  }

  /**
   * Check if user has all of the given permissions
   */
  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissions.every(permission => hasPermission(permission))
  }

  /**
   * Check if user has a specific role
   */
  const hasRole = (role: string): boolean => {
    return auth.hasRole(role)
  }

  /**
   * Check if user has any of the given roles
   */
  const hasAnyRole = (roles: string[]): boolean => {
    return auth.hasAnyRole(roles)
  }

  /**
   * Check if user has all of the given roles
   */
  const hasAllRoles = (roles: string[]): boolean => {
    return auth.hasAllRoles(roles)
  }

  /**
   * Check if user is admin
   */
  const isAdmin = computed(() => auth.isAdmin.value)

  /**
   * Check if user is tenant manager
   */
  const isTenantManager = computed(() => auth.isTenantManager.value)

  /**
   * Check if user is tenant user
   */
  const isTenantUser = computed(() => auth.isTenantUser.value)

  /**
   * Check if user can perform action on resource
   */
  const canAccess = (resource: string, action: string): boolean => {
    const permission = `${resource}:${action}`
    return hasPermission(permission)
  }

  /**
   * Check if user can create resource
   */
  const canCreate = (resource: string): boolean => {
    return canAccess(resource, 'create')
  }

  /**
   * Check if user can read resource
   */
  const canRead = (resource: string): boolean => {
    return canAccess(resource, 'read')
  }

  /**
   * Check if user can update resource
   */
  const canUpdate = (resource: string): boolean => {
    return canAccess(resource, 'update')
  }

  /**
   * Check if user can delete resource
   */
  const canDelete = (resource: string): boolean => {
    return canAccess(resource, 'delete')
  }

  return {
    // Permission checks
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,

    // Role checks
    hasRole,
    hasAnyRole,
    hasAllRoles,

    // Computed properties
    isAdmin,
    isTenantManager,
    isTenantUser,

    // Resource access checks
    canAccess,
    canCreate,
    canRead,
    canUpdate,
    canDelete
  }
}

