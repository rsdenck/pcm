import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePermission } from '../usePermission'

describe('usePermission Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('checks if user has permission', () => {
    const { hasPermission } = usePermission()
    
    // Mock auth composable
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:create', 'vm:read']
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(hasPermission('vm:create')).toBe(true)
    expect(hasPermission('vm:delete')).toBe(false)
  })

  it('checks if user has any permission', () => {
    const { hasAnyPermission } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:create', 'vm:read']
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(hasAnyPermission(['vm:create', 'vm:delete'])).toBe(true)
    expect(hasAnyPermission(['vm:delete', 'vm:restore'])).toBe(false)
  })

  it('checks if user has all permissions', () => {
    const { hasAllPermissions } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:create', 'vm:read', 'vm:update']
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(hasAllPermissions(['vm:create', 'vm:read'])).toBe(true)
    expect(hasAllPermissions(['vm:create', 'vm:delete'])).toBe(false)
  })

  it('checks if user has role', () => {
    const { hasRole } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:create']
          }
        },
        hasRole: vi.fn((role) => role === 'tenant_user'),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(hasRole('tenant_user')).toBe(true)
    expect(hasRole('tenant_admin')).toBe(false)
  })

  it('checks if user can access resource', () => {
    const { canAccess } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:create', 'vm:read']
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(canAccess('vm', 'create')).toBe(true)
    expect(canAccess('vm', 'delete')).toBe(false)
  })

  it('checks if user can create resource', () => {
    const { canCreate } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:create']
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(canCreate('vm')).toBe(true)
    expect(canCreate('backup')).toBe(false)
  })

  it('checks if user can read resource', () => {
    const { canRead } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:read']
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(canRead('vm')).toBe(true)
    expect(canRead('backup')).toBe(false)
  })

  it('checks if user can update resource', () => {
    const { canUpdate } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:update']
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(canUpdate('vm')).toBe(true)
    expect(canUpdate('backup')).toBe(false)
  })

  it('checks if user can delete resource', () => {
    const { canDelete } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: ['vm:delete']
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: false },
        isTenantUser: { value: true }
      })
    }))

    expect(canDelete('vm')).toBe(true)
    expect(canDelete('backup')).toBe(false)
  })

  it('returns computed properties for roles', () => {
    const { isAdmin, isTenantManager, isTenantUser } = usePermission()
    
    vi.mock('~/composables/useAuth', () => ({
      useAuth: () => ({
        user: {
          value: {
            permissions: []
          }
        },
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
        hasAllRoles: vi.fn(),
        isAdmin: { value: false },
        isTenantManager: { value: true },
        isTenantUser: { value: false }
      })
    }))

    expect(isAdmin.value).toBe(false)
    expect(isTenantManager.value).toBe(true)
    expect(isTenantUser.value).toBe(false)
  })
})

