/**
 * Authentication Middleware
 * Protects routes and enforces authentication/authorization
 */

import { useAuth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware((to, from) => {
  // Skip middleware on server side
  if (process.server) {
    return
  }

  const auth = useAuth()

  // Initialize auth on first load
  auth.initializeAuth()

  // Define public routes
  const publicRoutes = ['/', '/forgot-password']
  const isPublicRoute = publicRoutes.includes(to.path) || to.path.startsWith('/reset-password')

  // If authenticated and trying to access root, redirect to dashboard
  if (auth.isAuthenticated.value && to.path === '/') {
    return navigateTo('/dashboard', { replace: true })
  }

  // Check if route requires authentication (default is true unless explicitly set to false)
  const requiresAuth = to.meta.requiresAuth !== false

  // If not authenticated and trying to access protected route, redirect to root (login page)
  if (requiresAuth && !auth.isAuthenticated.value && !isPublicRoute) {
    return navigateTo('/', { replace: true })
  }

  // Check role-based access
  const requiredRole = to.meta.requiredRole as string | undefined
  if (requiredRole && !auth.hasRole(requiredRole)) {
    return navigateTo('/dashboard', { replace: true })
  }

  // Check permission-based access
  const requiredPermission = to.meta.requiredPermission as string | undefined
  if (requiredPermission && !auth.hasPermission(requiredPermission)) {
    return navigateTo('/dashboard', { replace: true })
  }

  // Check if route requires any of multiple roles
  const requiredRoles = to.meta.requiredRoles as string[] | undefined
  if (requiredRoles && !auth.hasAnyRole(requiredRoles)) {
    return navigateTo('/dashboard', { replace: true })
  }

  // Check if route requires all of multiple roles
  const requiredAllRoles = to.meta.requiredAllRoles as string[] | undefined
  if (requiredAllRoles && !auth.hasAllRoles(requiredAllRoles)) {
    return navigateTo('/dashboard', { replace: true })
  }
})

