/**
 * v-permission Directive
 * Conditionally renders elements based on user permissions
 */

import { useAuth } from '~/composables/useAuth'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('permission', {
    mounted(el: HTMLElement, binding: any) {
      const auth = useAuth()
      const { value, modifiers } = binding

      if (!value) {
        return
      }

      let hasPermission = false

      // Check based on modifiers
      if (modifiers.any) {
        // Check if user has any of the permissions
        hasPermission = Array.isArray(value)
          ? value.some(p => auth.hasPermission(p))
          : auth.hasPermission(value)
      } else if (modifiers.all) {
        // Check if user has all of the permissions
        hasPermission = Array.isArray(value)
          ? value.every(p => auth.hasPermission(p))
          : auth.hasPermission(value)
      } else {
        // Default: check if user has the permission
        hasPermission = Array.isArray(value)
          ? value.some(p => auth.hasPermission(p))
          : auth.hasPermission(value)
      }

      // Hide element if permission check fails
      if (!hasPermission) {
        el.style.display = 'none'
      }
    },
    updated(el: HTMLElement, binding: any) {
      const auth = useAuth()
      const { value, modifiers } = binding

      if (!value) {
        return
      }

      let hasPermission = false

      if (modifiers.any) {
        hasPermission = Array.isArray(value)
          ? value.some(p => auth.hasPermission(p))
          : auth.hasPermission(value)
      } else if (modifiers.all) {
        hasPermission = Array.isArray(value)
          ? value.every(p => auth.hasPermission(p))
          : auth.hasPermission(value)
      } else {
        hasPermission = Array.isArray(value)
          ? value.some(p => auth.hasPermission(p))
          : auth.hasPermission(value)
      }

      el.style.display = hasPermission ? '' : 'none'
    }
  })

  nuxtApp.vueApp.directive('role', {
    mounted(el: HTMLElement, binding: any) {
      const auth = useAuth()
      const { value, modifiers } = binding

      if (!value) {
        return
      }

      let hasRole = false

      if (modifiers.any) {
        hasRole = Array.isArray(value)
          ? value.some(r => auth.hasRole(r))
          : auth.hasRole(value)
      } else if (modifiers.all) {
        hasRole = Array.isArray(value)
          ? value.every(r => auth.hasRole(r))
          : auth.hasRole(value)
      } else {
        hasRole = Array.isArray(value)
          ? value.some(r => auth.hasRole(r))
          : auth.hasRole(value)
      }

      if (!hasRole) {
        el.style.display = 'none'
      }
    },
    updated(el: HTMLElement, binding: any) {
      const auth = useAuth()
      const { value, modifiers } = binding

      if (!value) {
        return
      }

      let hasRole = false

      if (modifiers.any) {
        hasRole = Array.isArray(value)
          ? value.some(r => auth.hasRole(r))
          : auth.hasRole(value)
      } else if (modifiers.all) {
        hasRole = Array.isArray(value)
          ? value.every(r => auth.hasRole(r))
          : auth.hasRole(value)
      } else {
        hasRole = Array.isArray(value)
          ? value.some(r => auth.hasRole(r))
          : auth.hasRole(value)
      }

      el.style.display = hasRole ? '' : 'none'
    }
  })
})

