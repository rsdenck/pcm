/**
 * RBAC3 Directives for Vue 3
 * 
 * Provides v-rbac-permission, v-rbac-role, and v-rbac-resource directives
 * for conditional rendering based on user permissions and roles.
 */

import { DirectiveBinding, VNode } from 'vue'
import { useRBAC3 } from '~/composables/useRBAC3'

/**
 * v-rbac-permission directive
 * 
 * Usage:
 *   v-rbac-permission="'vm:create'"
 *   v-rbac-permission="['vm:create', 'vm:delete']"
 *   v-rbac-permission.any="['vm:create', 'vm:delete']"
 *   v-rbac-permission.all="['vm:create', 'vm:delete']"
 */
export const vRBACPermission = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const { hasPermission, hasAnyPermission, hasAllPermissions } = useRBAC3()
    
    let hasAccess = false
    const permissions = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (binding.modifiers.any) {
      hasAccess = hasAnyPermission.value(permissions)
    } else if (binding.modifiers.all) {
      hasAccess = hasAllPermissions.value(permissions)
    } else {
      // Default: check if user has all permissions
      hasAccess = hasAllPermissions.value(permissions)
    }
    
    if (!hasAccess) {
      el.style.display = 'none'
      el.setAttribute('data-rbac-hidden', 'true')
    }
  },
  updated(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const { hasPermission, hasAnyPermission, hasAllPermissions } = useRBAC3()
    
    let hasAccess = false
    const permissions = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (binding.modifiers.any) {
      hasAccess = hasAnyPermission.value(permissions)
    } else if (binding.modifiers.all) {
      hasAccess = hasAllPermissions.value(permissions)
    } else {
      hasAccess = hasAllPermissions.value(permissions)
    }
    
    if (!hasAccess) {
      el.style.display = 'none'
      el.setAttribute('data-rbac-hidden', 'true')
    } else {
      el.style.display = ''
      el.removeAttribute('data-rbac-hidden')
    }
  }
}

/**
 * v-rbac-role directive
 * 
 * Usage:
 *   v-rbac-role="'admin'"
 *   v-rbac-role="['admin', 'tenant_admin']"
 *   v-rbac-role.any="['admin', 'tenant_admin']"
 *   v-rbac-role.all="['admin', 'tenant_admin']"
 */
export const vRBACRole = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const { hasRole } = useRBAC3()
    
    let hasAccess = false
    const roles = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (binding.modifiers.any) {
      hasAccess = roles.some(r => hasRole.value(r))
    } else if (binding.modifiers.all) {
      hasAccess = roles.every(r => hasRole.value(r))
    } else {
      // Default: check if user has any of the roles
      hasAccess = roles.some(r => hasRole.value(r))
    }
    
    if (!hasAccess) {
      el.style.display = 'none'
      el.setAttribute('data-rbac-hidden', 'true')
    }
  },
  updated(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const { hasRole } = useRBAC3()
    
    let hasAccess = false
    const roles = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (binding.modifiers.any) {
      hasAccess = roles.some(r => hasRole.value(r))
    } else if (binding.modifiers.all) {
      hasAccess = roles.every(r => hasRole.value(r))
    } else {
      hasAccess = roles.some(r => hasRole.value(r))
    }
    
    if (!hasAccess) {
      el.style.display = 'none'
      el.setAttribute('data-rbac-hidden', 'true')
    } else {
      el.style.display = ''
      el.removeAttribute('data-rbac-hidden')
    }
  }
}

/**
 * v-rbac-resource directive
 * 
 * Usage:
 *   v-rbac-resource="{ resource: 'vm', action: 'create' }"
 *   v-rbac-resource="{ resource: 'backup', action: 'restore' }"
 */
export const vRBACResource = {
  mounted(el: HTMLElement, binding: DirectiveBinding<{ resource: string; action: string }>) {
    const { checkResourceAccess } = useRBAC3()
    
    const { resource, action } = binding.value
    const hasAccess = checkResourceAccess(resource, action)
    
    if (!hasAccess) {
      el.style.display = 'none'
      el.setAttribute('data-rbac-hidden', 'true')
    }
  },
  updated(el: HTMLElement, binding: DirectiveBinding<{ resource: string; action: string }>) {
    const { checkResourceAccess } = useRBAC3()
    
    const { resource, action } = binding.value
    const hasAccess = checkResourceAccess(resource, action)
    
    if (!hasAccess) {
      el.style.display = 'none'
      el.setAttribute('data-rbac-hidden', 'true')
    } else {
      el.style.display = ''
      el.removeAttribute('data-rbac-hidden')
    }
  }
}

/**
 * v-rbac-disable directive
 * 
 * Disables element instead of hiding it
 * 
 * Usage:
 *   v-rbac-disable="'vm:create'"
 *   v-rbac-disable="['vm:create', 'vm:delete']"
 */
export const vRBACDisable = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const { hasPermission, hasAnyPermission, hasAllPermissions } = useRBAC3()
    
    let hasAccess = false
    const permissions = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (binding.modifiers.any) {
      hasAccess = hasAnyPermission.value(permissions)
    } else if (binding.modifiers.all) {
      hasAccess = hasAllPermissions.value(permissions)
    } else {
      hasAccess = hasAllPermissions.value(permissions)
    }
    
    if (!hasAccess) {
      el.setAttribute('disabled', 'true')
      el.classList.add('opacity-50', 'cursor-not-allowed')
    }
  },
  updated(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const { hasPermission, hasAnyPermission, hasAllPermissions } = useRBAC3()
    
    let hasAccess = false
    const permissions = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (binding.modifiers.any) {
      hasAccess = hasAnyPermission.value(permissions)
    } else if (binding.modifiers.all) {
      hasAccess = hasAllPermissions.value(permissions)
    } else {
      hasAccess = hasAllPermissions.value(permissions)
    }
    
    if (!hasAccess) {
      el.setAttribute('disabled', 'true')
      el.classList.add('opacity-50', 'cursor-not-allowed')
    } else {
      el.removeAttribute('disabled')
      el.classList.remove('opacity-50', 'cursor-not-allowed')
    }
  }
}
