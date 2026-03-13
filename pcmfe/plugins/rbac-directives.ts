/**
 * RBAC Directives Plugin
 * 
 * Registers all RBAC directives globally in the Vue app
 */

import { defineNuxtPlugin } from '#app'
import { vRBACPermission, vRBACRole, vRBACResource, vRBACDisable } from '~/directives/vRBAC'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('rbac-permission', vRBACPermission)
  nuxtApp.vueApp.directive('rbac-role', vRBACRole)
  nuxtApp.vueApp.directive('rbac-resource', vRBACResource)
  nuxtApp.vueApp.directive('rbac-disable', vRBACDisable)
})
