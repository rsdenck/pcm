/**
 * Authentication Middleware
 * Protects routes and enforces authentication/authorization
 */

import { useAuth } from '~/composables/useAuth'

export default defineRouteMiddleware(async (to, from) => {
  const auth = useAuth()

  // Initialize auth on first load
  if (!auth.isAuthenticated.value && process.client) {
    auth.initializeAuth()
  }

  // Check if route requires authentication
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !auth.isAuthenticated.value) {
    // Redirect to login if not authenticated
    return navigateTo('/login')
  }

  // Check if route requires specific role
  const requiredRole = to.meta.requiredRole as string | undefined
  if (requiredRole && !auth.hasRole(requiredRole)) {
    // Redirect to dashboard if role not met
    return navigateTo('/dashboard')
  }

  // Check if route requires specific permission
  const requiredPermission = to.meta.requiredPermission as string | undefined
  if (requiredPermission && !auth.hasPermission(requiredPermission)) {
    // Redirect to dashboard if permission not met
    return navigateTo('/dashboard')
  }

  // Check if route requires any of multiple roles
  const requiredRoles = to.meta.requiredRoles as string[] | undefined
  if (requiredRoles && !auth.hasAnyRole(requiredRoles)) {
    // Redirect to dashboard if none of the roles match
    return navigateTo('/dashboard')
  }

  // Check if route requires any of multiple permissions
  const requiredPermissions = to.meta.requiredPermissions as string[] | undefined
  if (requiredPermissions && !auth.hasAnyPermission(requiredPermissions)) {
    // Redirect to dashboard if none of the permissions match
    return navigateTo('/dashboard')
  }

  // Check if route requires all of multiple roles
  const requiredAllRoles = to.meta.requiredAllRoles as string[] | undefined
  if (requiredAllRoles && !auth.hasAllRoles(requiredAllRoles)) {
    // Redirect to dashboard if not all roles match
    return navigateTo('/dashboard')
  }

  // Check if route requires all of multiple permissions
  const requiredAllPermissions = to.meta.requiredAllPermissions as string[] | undefined
  if (requiredAllPermissions && !auth.hasAllPermissions(requiredAllPermissions)) {
    // Redirect to dashboard if not all permissions match
    return navigateTo('/dashboard')
  }

  // If authenticated and trying to access login page, redirect to dashboard
  if (auth.isAuthenticated.value && (to.path === '/login' || to.path === '/forgot-password')) {
    return navigateTo('/dashboard')
  }
})

