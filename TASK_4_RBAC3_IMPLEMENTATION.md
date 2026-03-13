# Task 4: RBAC3 Hybrid System Implementation

## Overview

Task 4 implements a comprehensive Role-Based Access Control (RBAC3) hybrid system that supports both local authentication and LDAP integration for admin users. This document outlines the implementation details, architecture, and usage patterns.

## Architecture

### RBAC3 Hybrid Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Authentication Request                   │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
        ┌─────────────────────────────────┐
        │   RBAC3Service.authenticate()   │
        └─────────────────────────────────┘
                      ▼
        ┌─────────────────────────────────┐
        │   Local or LDAP?                │
        └──────┬──────────────────┬───────┘
               ▼                  ▼
        ┌──────────────┐  ┌──────────────┐
        │ Local Auth   │  │ LDAP Auth    │
        │ (Database)   │  │ (Directory)  │
        └──────┬───────┘  └──────┬───────┘
               │                 │
               └────────┬────────┘
                        ▼
        ┌─────────────────────────────────┐
        │   User Roles & Permissions      │
        │   (Database)                    │
        └─────────────────────────────────┘
                        ▼
        ┌─────────────────────────────────┐
        │   Authorization Check           │
        │   (Permission Validation)       │
        └─────────────────────────────────┘
```

### Components

#### Backend Components

1. **LDAPService** (`pcm/services/ldap_service.py`)
   - LDAP server connection management
   - User authentication against LDAP
   - User and group search
   - LDAP attribute extraction

2. **RBAC3Service** (`pcm/services/rbac3_service.py`)
   - Hybrid authentication (local + LDAP)
   - User authorization
   - Role and permission management
   - Default role initialization

3. **Database Models**
   - User model extended with LDAP fields
   - Permission model (resource:action pairs)
   - Role model (system and tenant-specific)
   - AuditLog model (for compliance)

4. **Database Migration** (`pcm/alembic/versions/007_add_ldap_support.py`)
   - LDAP fields in users table
   - LDAP configuration table
   - LDAP sync logs table

#### Frontend Components

1. **useRBAC3 Composable** (`pcmfe/composables/useRBAC3.ts`)
   - Reactive user roles and permissions
   - Permission checking methods
   - Role checking methods
   - Resource access validation

2. **RBAC Directives** (`pcmfe/directives/vRBAC.ts`)
   - `v-rbac-permission`: Hide/show based on permissions
   - `v-rbac-role`: Hide/show based on roles
   - `v-rbac-resource`: Hide/show based on resource access
   - `v-rbac-disable`: Disable elements based on permissions

3. **Plugin** (`pcmfe/plugins/rbac-directives.ts`)
   - Global directive registration

## Implementation Details

### Backend Implementation

#### 1. LDAP Service

```python
from pcm.services.ldap_service import LDAPService

# Initialize LDAP service
ldap_service = LDAPService(
    server_uri="ldap://ldap.example.com:389",
    bind_dn="cn=admin,dc=example,dc=com",
    bind_password="admin_password",
    base_dn="dc=example,dc=com"
)

# Authenticate user
success, ldap_user = ldap_service.authenticate_user("username", "password")

# Get user groups
groups = ldap_service.get_user_groups("username")
```

#### 2. RBAC3 Service

```python
from pcm.services.rbac3_service import RBAC3Service

# Initialize RBAC3 service
rbac3_service = RBAC3Service(db_session, ldap_service)

# Authenticate user (local or LDAP)
success, user, error = await rbac3_service.authenticate_user(
    username="user@example.com",
    password="password",
    use_ldap=False  # or True for LDAP
)

# Check authorization
authorized = await rbac3_service.authorize_user(
    user=user,
    required_permission="vm:create"
)

# Get user permissions
permissions = await rbac3_service.get_user_permissions(user)

# Assign role to user
success = await rbac3_service.assign_role_to_user(user, "admin")

# Initialize default roles
success = await rbac3_service.initialize_default_roles()
```

#### 3. Database Schema

**Users Table (Extended)**
```sql
ALTER TABLE users ADD COLUMN ldap_dn VARCHAR(500);
ALTER TABLE users ADD COLUMN ldap_groups JSON;
ALTER TABLE users ADD COLUMN is_ldap_user BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN last_ldap_sync DATETIME;
```

**LDAP Configuration Table**
```sql
CREATE TABLE ldap_config (
    id VARCHAR(36) PRIMARY KEY,
    server_uri VARCHAR(255) NOT NULL,
    bind_dn VARCHAR(255) NOT NULL,
    bind_password VARCHAR(255) NOT NULL,
    base_dn VARCHAR(255) NOT NULL,
    user_search_filter VARCHAR(255) DEFAULT '(uid={username})',
    group_search_filter VARCHAR(255) DEFAULT '(cn=*)',
    is_enabled BOOLEAN DEFAULT FALSE,
    timeout INTEGER DEFAULT 10,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

**LDAP Sync Logs Table**
```sql
CREATE TABLE ldap_sync_logs (
    id VARCHAR(36) PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    users_synced INTEGER DEFAULT 0,
    groups_synced INTEGER DEFAULT 0,
    errors JSON,
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    duration_seconds FLOAT
);
```

### Frontend Implementation

#### 1. useRBAC3 Composable

```typescript
import { useRBAC3 } from '~/composables/useRBAC3'

export default {
  setup() {
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

    return {
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
    }
  }
}
```

#### 2. RBAC Directives

```vue
<!-- Hide element if user doesn't have permission -->
<button v-rbac-permission="'vm:create'">Create VM</button>

<!-- Hide element if user doesn't have any of the permissions -->
<button v-rbac-permission.any="['vm:create', 'vm:delete']">Manage VMs</button>

<!-- Hide element if user doesn't have all permissions -->
<button v-rbac-permission.all="['vm:create', 'vm:delete']">Full VM Control</button>

<!-- Hide element if user doesn't have role -->
<div v-rbac-role="'admin'">Admin Panel</div>

<!-- Hide element if user doesn't have any of the roles -->
<div v-rbac-role.any="['admin', 'tenant_admin']">Management Panel</div>

<!-- Hide element if user doesn't have resource access -->
<button v-rbac-resource="{ resource: 'vm', action: 'create' }">Create VM</button>

<!-- Disable element instead of hiding -->
<button v-rbac-disable="'vm:create'">Create VM</button>
```

## Default Roles

The system initializes with four default system roles:

1. **admin**
   - Full system access
   - Can manage all resources
   - Can manage users and roles
   - Can configure system settings

2. **tenant_admin**
   - Tenant-level administrative access
   - Can manage tenant resources
   - Can manage tenant users
   - Cannot access other tenants

3. **tenant_manager**
   - Tenant resource management
   - Can create and manage VMs, backups, etc.
   - Cannot manage users
   - Cannot access other tenants

4. **tenant_user**
   - Read-only access to tenant resources
   - Can view VMs, backups, etc.
   - Cannot create or modify resources
   - Cannot access other tenants

## Permission Model

Permissions follow the resource:action pattern:

```
vm:create          - Create virtual machines
vm:read            - View virtual machines
vm:update          - Modify virtual machines
vm:delete          - Delete virtual machines
vm:manage          - Full VM management

backup:create      - Create backups
backup:read        - View backups
backup:restore     - Restore from backups
backup:delete      - Delete backups
backup:manage      - Full backup management

tenant:create      - Create tenants
tenant:read        - View tenants
tenant:update      - Modify tenants
tenant:delete      - Delete tenants
tenant:manage      - Full tenant management

user:create        - Create users
user:read          - View users
user:update        - Modify users
user:delete        - Delete users
user:manage        - Full user management
```

## LDAP Integration

### Configuration

LDAP configuration is stored in the database and can be managed via API:

```python
# Create LDAP configuration
ldap_config = LDAPConfig(
    server_uri="ldap://ldap.example.com:389",
    bind_dn="cn=admin,dc=example,dc=com",
    bind_password="admin_password",
    base_dn="dc=example,dc=com",
    user_search_filter="(uid={username})",
    group_search_filter="(cn=*)",
    is_enabled=True,
    timeout=10
)
```

### User Sync

LDAP users are automatically synced when they authenticate:

1. User authenticates with LDAP credentials
2. System verifies credentials against LDAP server
3. User information is extracted from LDAP
4. User is created or updated in database
5. User is assigned admin role (configurable)
6. LDAP groups are stored for future reference

### Group Mapping

LDAP groups can be mapped to system roles:

```python
# Map LDAP group to system role
ldap_group_mapping = {
    "cn=admins,dc=example,dc=com": "admin",
    "cn=managers,dc=example,dc=com": "tenant_admin",
    "cn=users,dc=example,dc=com": "tenant_user"
}
```

## Testing

### Backend Tests

```bash
# Run RBAC3 service tests
pytest pcm/tests/services/test_rbac3_service.py -v

# Run LDAP service tests
pytest pcm/tests/services/test_ldap_service.py -v
```

### Frontend Tests

```bash
# Run useRBAC3 composable tests
npm run test -- composables/__tests__/useRBAC3.test.ts

# Run RBAC directive tests
npm run test -- directives/__tests__/vRBAC.test.ts
```

## Security Considerations

1. **Password Security**
   - Passwords are hashed using bcrypt
   - LDAP passwords are never stored
   - Password reset tokens are time-limited

2. **Token Security**
   - JWT tokens are stored securely
   - Tokens include user roles and permissions
   - Token refresh is automatic before expiration

3. **LDAP Security**
   - LDAP connection uses TLS/SSL
   - Bind credentials are encrypted in database
   - LDAP sync logs are audited

4. **Audit Logging**
   - All authentication attempts are logged
   - All authorization checks are logged
   - All role/permission changes are logged

## Migration Guide

### From Local-Only to RBAC3

1. **Run database migration**
   ```bash
   alembic upgrade head
   ```

2. **Initialize default roles**
   ```python
   rbac3_service = RBAC3Service(db_session)
   await rbac3_service.initialize_default_roles()
   ```

3. **Assign roles to existing users**
   ```python
   # Assign admin role to existing admins
   await rbac3_service.assign_role_to_user(user, "admin")
   ```

4. **Configure LDAP (optional)**
   ```python
   ldap_config = LDAPConfig(...)
   db_session.add(ldap_config)
   await db_session.commit()
   ```

## API Endpoints

### Authentication

```
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
GET /api/v1/auth/validate
```

### Users

```
GET /api/v1/users/{user_id}/rbac
GET /api/v1/users/{user_id}/permissions
GET /api/v1/users/{user_id}/roles
POST /api/v1/users/{user_id}/roles
DELETE /api/v1/users/{user_id}/roles/{role_id}
```

### Roles

```
GET /api/v1/roles
POST /api/v1/roles
GET /api/v1/roles/{role_id}
PUT /api/v1/roles/{role_id}
DELETE /api/v1/roles/{role_id}
POST /api/v1/roles/{role_id}/permissions
DELETE /api/v1/roles/{role_id}/permissions/{permission_id}
```

### Permissions

```
GET /api/v1/permissions
POST /api/v1/permissions
GET /api/v1/permissions/{permission_id}
PUT /api/v1/permissions/{permission_id}
DELETE /api/v1/permissions/{permission_id}
```

### LDAP Configuration

```
GET /api/v1/ldap/config
POST /api/v1/ldap/config
PUT /api/v1/ldap/config
DELETE /api/v1/ldap/config
POST /api/v1/ldap/sync
GET /api/v1/ldap/sync-logs
```

## Next Steps

1. Create API endpoints for role and permission management
2. Create API endpoints for LDAP configuration
3. Create frontend pages for role and permission management
4. Create frontend pages for LDAP configuration
5. Implement tenant-specific roles and permissions
6. Implement audit logging UI
7. Create comprehensive documentation
8. Create user guides and tutorials

## Files Created/Modified

### Backend
- `pcm/services/ldap_service.py` - LDAP authentication service
- `pcm/services/rbac3_service.py` - RBAC3 hybrid service
- `pcm/alembic/versions/007_add_ldap_support.py` - Database migration
- `pcm/core/models/user.py` - Extended with LDAP fields
- `pcm/tests/services/test_rbac3_service.py` - RBAC3 tests

### Frontend
- `pcmfe/composables/useRBAC3.ts` - RBAC3 composable
- `pcmfe/directives/vRBAC.ts` - RBAC directives
- `pcmfe/plugins/rbac-directives.ts` - Directive plugin
- `pcmfe/composables/__tests__/useRBAC3.test.ts` - Composable tests
- `pcmfe/nuxt.config.ts` - Updated with plugin registration

## Status

- ✅ LDAP Service implementation
- ✅ RBAC3 Service implementation
- ✅ Database migration
- ✅ User model extension
- ✅ Frontend composable
- ✅ Frontend directives
- ✅ Backend tests
- ✅ Frontend tests
- ⏳ API endpoints (next)
- ⏳ Frontend pages (next)
- ⏳ LDAP configuration UI (next)
- ⏳ Audit logging UI (next)
