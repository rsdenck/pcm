# RBAC3 Quick Start Guide

## For Backend Developers

### Initialize RBAC3 Service

```python
from sqlalchemy.ext.asyncio import AsyncSession
from pcm.services.rbac3_service import RBAC3Service
from pcm.services.ldap_service import LDAPService

# Create RBAC3 service (without LDAP)
rbac3_service = RBAC3Service(db_session)

# Or with LDAP support
ldap_service = LDAPService(
    server_uri="ldap://ldap.example.com:389",
    bind_dn="cn=admin,dc=example,dc=com",
    bind_password="admin_password",
    base_dn="dc=example,dc=com"
)
rbac3_service = RBAC3Service(db_session, ldap_service)

# Initialize default roles
await rbac3_service.initialize_default_roles()
```

### Authenticate User

```python
# Local authentication
success, user, error = await rbac3_service.authenticate_user(
    username="user@example.com",
    password="password",
    use_ldap=False
)

# LDAP authentication
success, user, error = await rbac3_service.authenticate_user(
    username="ldapuser",
    password="password",
    use_ldap=True
)

if success:
    print(f"User authenticated: {user.email}")
else:
    print(f"Authentication failed: {error}")
```

### Check Authorization

```python
# Check single permission
authorized = await rbac3_service.authorize_user(
    user=user,
    required_permission="vm:create"
)

# Get all user permissions
permissions = await rbac3_service.get_user_permissions(user)
print(f"User permissions: {permissions}")

# Get all user roles
roles = await rbac3_service.get_user_roles(user)
print(f"User roles: {roles}")
```

### Assign Roles

```python
# Assign role to user
success = await rbac3_service.assign_role_to_user(user, "admin")

if success:
    print("Role assigned successfully")
else:
    print("Failed to assign role")
```

## For Frontend Developers

### Use RBAC3 Composable

```vue
<script setup lang="ts">
import { useRBAC3 } from '~/composables/useRBAC3'

const {
  rbacUser,
  userRoles,
  userPermissions,
  isAdmin,
  isTenantAdmin,
  hasPermission,
  hasRole,
  canCreate,
  canRead,
  canUpdate,
  canDelete,
  checkResourceAccess
} = useRBAC3()
</script>

<template>
  <!-- Check permission in template -->
  <div v-if="hasPermission('vm:create')">
    <button @click="createVM">Create VM</button>
  </div>

  <!-- Check role in template -->
  <div v-if="isAdmin">
    <button @click="openAdminPanel">Admin Panel</button>
  </div>

  <!-- Check resource access -->
  <div v-if="canCreate('backup')">
    <button @click="createBackup">Create Backup</button>
  </div>

  <!-- Display user info -->
  <div>
    <p>User: {{ rbacUser?.email }}</p>
    <p>Roles: {{ userRoles.map(r => r.name).join(', ') }}</p>
    <p>LDAP User: {{ rbacUser?.is_ldap_user ? 'Yes' : 'No' }}</p>
  </div>
</template>
```

### Use RBAC Directives

```vue
<template>
  <!-- Hide if no permission -->
  <button v-rbac-permission="'vm:create'">Create VM</button>

  <!-- Hide if no role -->
  <div v-rbac-role="'admin'">Admin Panel</div>

  <!-- Hide if no resource access -->
  <button v-rbac-resource="{ resource: 'backup', action: 'restore' }">
    Restore Backup
  </button>

  <!-- Disable instead of hide -->
  <button v-rbac-disable="'vm:delete'">Delete VM</button>

  <!-- Check any permission -->
  <button v-rbac-permission.any="['vm:create', 'vm:update']">
    Manage VMs
  </button>

  <!-- Check all permissions -->
  <button v-rbac-permission.all="['vm:create', 'vm:delete']">
    Full VM Control
  </button>
</template>
```

### Programmatic Permission Checks

```typescript
import { useRBAC3 } from '~/composables/useRBAC3'

const { 
  checkPermission, 
  checkRole, 
  checkResourceAccess,
  requirePermission,
  requireRole
} = useRBAC3()

// Check permission
if (checkPermission('vm:create')) {
  // User can create VMs
}

// Check role
if (checkRole('admin')) {
  // User is admin
}

// Check resource access
if (checkResourceAccess('backup', 'restore')) {
  // User can restore backups
}

// Require permission (throws if not authorized)
try {
  requirePermission('vm:delete')
  // User can delete VMs
} catch (error) {
  console.error('Permission denied:', error.message)
}

// Require role (throws if not authorized)
try {
  requireRole('admin')
  // User is admin
} catch (error) {
  console.error('Role required:', error.message)
}
```

## Common Patterns

### Conditional Rendering Based on Permissions

```vue
<script setup lang="ts">
import { useRBAC3 } from '~/composables/useRBAC3'

const { hasPermission } = useRBAC3()

const canManageVMs = computed(() => 
  hasPermission('vm:create') && hasPermission('vm:delete')
)
</script>

<template>
  <div v-if="canManageVMs">
    <!-- VM management UI -->
  </div>
</template>
```

### Role-Based Navigation

```vue
<script setup lang="ts">
import { useRBAC3 } from '~/composables/useRBAC3'

const { isAdmin, isTenantAdmin, isTenantUser } = useRBAC3()

const navigationItems = computed(() => {
  const items = [
    { label: 'Dashboard', to: '/dashboard' }
  ]

  if (isAdmin.value) {
    items.push({ label: 'System Settings', to: '/admin/settings' })
    items.push({ label: 'Users', to: '/admin/users' })
  }

  if (isTenantAdmin.value) {
    items.push({ label: 'Tenant Settings', to: '/tenant/settings' })
  }

  return items
})
</script>

<template>
  <nav>
    <router-link 
      v-for="item in navigationItems" 
      :key="item.to"
      :to="item.to"
    >
      {{ item.label }}
    </router-link>
  </nav>
</template>
```

### Permission-Based Button States

```vue
<script setup lang="ts">
import { useRBAC3 } from '~/composables/useRBAC3'

const { canDelete, canUpdate } = useRBAC3()

const deleteButtonDisabled = computed(() => !canDelete('vm'))
const updateButtonDisabled = computed(() => !canUpdate('vm'))
</script>

<template>
  <div>
    <button 
      @click="deleteVM"
      :disabled="deleteButtonDisabled"
      :class="{ 'opacity-50 cursor-not-allowed': deleteButtonDisabled }"
    >
      Delete VM
    </button>

    <button 
      @click="updateVM"
      :disabled="updateButtonDisabled"
      :class="{ 'opacity-50 cursor-not-allowed': updateButtonDisabled }"
    >
      Update VM
    </button>
  </div>
</template>
```

### LDAP User Detection

```vue
<script setup lang="ts">
import { useRBAC3 } from '~/composables/useRBAC3'

const { isLDAPUser, ldapGroups, rbacUser } = useRBAC3()
</script>

<template>
  <div v-if="isLDAPUser">
    <p>LDAP User: {{ rbacUser?.username }}</p>
    <p>LDAP Groups: {{ ldapGroups.join(', ') }}</p>
  </div>
</template>
```

## Default Roles & Permissions

### Admin Role
- Full system access
- All permissions granted
- Can manage users, roles, and permissions

### Tenant Admin Role
- Tenant-level administrative access
- Can manage tenant resources
- Can manage tenant users
- Cannot access other tenants

### Tenant Manager Role
- Tenant resource management
- Can create and manage VMs, backups, etc.
- Cannot manage users
- Cannot access other tenants

### Tenant User Role
- Read-only access to tenant resources
- Can view VMs, backups, etc.
- Cannot create or modify resources
- Cannot access other tenants

## Permission Naming Convention

Permissions follow the pattern: `resource:action`

**Common Resources:**
- `vm` - Virtual machines
- `backup` - Backups
- `tenant` - Tenants
- `user` - Users
- `role` - Roles
- `permission` - Permissions
- `cluster` - Clusters
- `storage` - Storage

**Common Actions:**
- `create` - Create resource
- `read` - View resource
- `update` - Modify resource
- `delete` - Delete resource
- `manage` - Full management

**Examples:**
- `vm:create` - Create virtual machines
- `backup:restore` - Restore from backups
- `tenant:manage` - Full tenant management
- `user:delete` - Delete users

## Testing

### Backend Tests

```bash
# Run RBAC3 tests
pytest pcm/tests/services/test_rbac3_service.py -v

# Run specific test
pytest pcm/tests/services/test_rbac3_service.py::test_authenticate_user_local_success -v
```

### Frontend Tests

```bash
# Run useRBAC3 tests
npm run test -- composables/__tests__/useRBAC3.test.ts

# Run with coverage
npm run test -- composables/__tests__/useRBAC3.test.ts --coverage
```

## Troubleshooting

### LDAP Connection Issues

```python
# Check LDAP connection
try:
    ldap_service.connect()
    print("LDAP connection successful")
except LDAPConnectionError as e:
    print(f"LDAP connection failed: {e}")
```

### Permission Not Found

```python
# Check if permission exists
permission = await PermissionService.get_permission_by_name(
    db_session, 
    "vm:create"
)
if not permission:
    print("Permission not found, creating...")
    # Create permission
```

### User Not Authorized

```python
# Debug authorization
permissions = await rbac3_service.get_user_permissions(user)
print(f"User permissions: {permissions}")

# Check specific permission
has_perm = await rbac3_service.authorize_user(user, "vm:create")
print(f"Has vm:create: {has_perm}")
```

## Resources

- [RBAC3 Implementation Guide](./TASK_4_RBAC3_IMPLEMENTATION.md)
- [Task 4 Progress Report](./TASK_4_PROGRESS.md)
- [Frontend Security & Authentication Spec](./kiro/specs/frontend-security-authentication/requirements.md)
- [ROADMAP](./ROADMAP.md)

## Support

For issues or questions:
1. Check the documentation files
2. Review test cases for examples
3. Check git commit history for implementation details
4. Open an issue on GitHub

---

**Last Updated**: March 13, 2026
**Version**: 1.0.0
**Status**: ✅ Complete
