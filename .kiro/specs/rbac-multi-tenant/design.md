# RBAC Multi-Tenant System - Design Document

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Nuxt 3)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Admin Portal │  │ Tenant Portal│  │ User Portal  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │  useRBAC3   │                          │
│                    │  Composable │                          │
│                    └──────┬──────┘                          │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼──────────────────────────────────┐
│                     Backend API (FastAPI)                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Auth Middleware                         │    │
│  │  - JWT Validation                                    │    │
│  │  - Role Extraction                                   │    │
│  │  - Tenant Context                                    │    │
│  └──────────────────────────────────────────────────────┘    │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐    │
│  │           Authorization Middleware                   │    │
│  │  - Permission Check                                  │    │
│  │  - Tenant Isolation                                  │    │
│  │  - ACL Evaluation                                    │    │
│  └──────────────────────────────────────────────────────┘    │ 
│                            │                                 │
│  ┌────────────┬────────────┬────────────┬────────────┐       │
│  │   User     │   Role     │Permission  │    ACL     │       │ 
│  │  Service   │  Service   │  Service   │  Service   │       │
│  └────────────┴────────────┴────────────┴────────────┘       │
└───────────────────────────┼──────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                    Database (PostgreSQL)                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  organizations │ tenants │ projects │ users          │     │
│  │  groups │ roles │ permissions │ role_permissions     │     │
│  │  user_roles │ user_groups │ acl_entries              │     │
│  └──────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────┘
```

## Database Schema Design

### Entity Relationship Diagram

```
┌─────────────────┐
│ organizations   │
│─────────────────│
│ id (PK)         │
│ name            │
│ slug (UNIQUE)   │
│ description     │
└────────┬────────┘
         │ 1:N
         │
┌────────▼────────┐
│ tenants         │
│─────────────────│
│ id (PK)         │
│ organization_id │◄────┐
│ name            │     │
│ slug (UNIQUE)   │     │
│ status          │     │
└────────┬────────┘     │
         │ 1:N          │
         │              │
┌────────▼────────┐     │
│ projects        │     │
│─────────────────│     │
│ id (PK)         │     │
│ tenant_id (FK)  │     │
│ name            │     │
└─────────────────┘     │
                        │
┌───────────────────────┘
│
│        ┌─────────────────┐
│        │ users           │
│        │─────────────────│
│        │ id (PK)         │
│        │ tenant_id (FK)  │
│        │ email (UNIQUE)  │
│        │ username        │
│        │ hashed_password │
│        │ role            │
│        │ is_superuser    │
│        └────────┬────────┘
│                 │ N:M
│                 │
│        ┌────────▼────────┐
│        │ user_roles      │
│        │─────────────────│
│        │ user_id (FK)    │
│        │ role_id (FK)    │
│        └────────┬────────┘
│                 │
│        ┌────────▼────────┐
│        │ roles           │
│        │─────────────────│
│        │ id (PK)         │
│        │ tenant_id (FK)  │
│        │ name            │
│        │ is_system_role  │
│        └────────┬────────┘
│                 │ N:M
│                 │
│        ┌────────▼────────────┐
│        │ role_permissions    │
│        │─────────────────────│
│        │ role_id (FK)        │
│        │ permission_id (FK)  │
│        └────────┬────────────┘
│                 │
│        ┌────────▼────────┐
│        │ permissions     │
│        │─────────────────│
│        │ id (PK)         │
│        │ name (UNIQUE)   │
│        │ resource        │
│        │ action          │
│        └─────────────────┘
│
│        ┌─────────────────┐
│        │ groups          │
│        │─────────────────│
│        │ id (PK)         │
│        │ tenant_id (FK)  │
│        │ name            │
│        └────────┬────────┘
│                 │ N:M
│                 │
│        ┌────────▼────────┐
│        │ user_groups     │
│        │─────────────────│
│        │ user_id (FK)    │
│        │ group_id (FK)   │
│        └─────────────────┘
│
│        ┌─────────────────┐
│        │ acl_entries     │
│        │─────────────────│
│        │ id (PK)         │
│        │ resource_type   │
│        │ resource_id     │
│        │ principal_type  │
│        │ principal_id    │
│        │ permission      │
│        │ allow           │
│        └─────────────────┘
```

## Permission System Design

### Permission Naming Convention
Format: `{resource}:{action}`

Examples:
- `tenant:create`
- `tenant:read`
- `tenant:update`
- `tenant:delete`
- `user:manage`
- `vm:start`
- `firewall:configure`

### System Roles

#### 1. PROVIDER_ADMIN
```json
{
  "name": "PROVIDER_ADMIN",
  "is_system_role": true,
  "permissions": ["*:*"]  // Wildcard - all permissions
}
```

#### 2. TENANT_ADMIN
```json
{
  "name": "TENANT_ADMIN",
  "is_system_role": true,
  "permissions": [
    "user:create", "user:read", "user:update", "user:delete",
    "vm:*", "network:*", "firewall:*", "storage:*",
    "project:*", "group:*"
  ]
}
```

#### 3. TENANT_MANAGER
```json
{
  "name": "TENANT_MANAGER",
  "is_system_role": true,
  "permissions": [
    "user:read",
    "vm:*", "network:*", "firewall:*", "storage:*"
  ]
}
```

#### 4. TENANT_USER
```json
{
  "name": "TENANT_USER",
  "is_system_role": true,
  "permissions": [
    "user:read",
    "vm:read", "network:read", "firewall:read", "storage:read"
  ]
}
```

## Authorization Flow

### 1. Request Flow
```
1. User makes request → Frontend
2. Frontend adds JWT token → HTTP Header
3. Backend receives request
4. Auth Middleware validates JWT
5. Auth Middleware extracts user info
6. Authorization Middleware checks permissions
7. Authorization Middleware checks tenant isolation
8. Service layer executes business logic
9. Response returned to frontend
```

### 2. Permission Check Algorithm
```python
def check_permission(user, resource, action, tenant_id=None):
    # 1. Check if user is PROVIDER_ADMIN
    if user.role == "PROVIDER_ADMIN":
        return True
    
    # 2. Check tenant isolation
    if tenant_id and user.tenant_id != tenant_id:
        return False
    
    # 3. Check direct permissions
    permission_name = f"{resource}:{action}"
    if permission_name in user.permissions:
        return True
    
    # 4. Check role permissions
    for role in user.roles:
        if permission_name in role.permissions:
            return True
        # Check wildcard
        if f"{resource}:*" in role.permissions:
            return True
    
    # 5. Check ACL entries
    acl_result = check_acl(user, resource, action)
    if acl_result is not None:
        return acl_result
    
    # 6. Default deny
    return False
```

### 3. Tenant Isolation
```python
def enforce_tenant_isolation(user, query):
    # PROVIDER_ADMIN can access all tenants
    if user.role == "PROVIDER_ADMIN":
        return query
    
    # Other users can only access their tenant
    return query.filter(tenant_id == user.tenant_id)
```

## API Design

### Authentication Endpoints
```
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
```

### User Management Endpoints
```
GET    /api/v1/users                    # List users (filtered by tenant)
POST   /api/v1/users                    # Create user
GET    /api/v1/users/{id}               # Get user details
PUT    /api/v1/users/{id}               # Update user
DELETE /api/v1/users/{id}               # Delete user
POST   /api/v1/users/{id}/password      # Reset password
GET    /api/v1/users/{id}/roles         # Get user roles
PUT    /api/v1/users/{id}/roles         # Update user roles
GET    /api/v1/users/{id}/permissions   # Get user permissions
```

### Role Management Endpoints
```
GET    /api/v1/roles                    # List roles
POST   /api/v1/roles                    # Create role
GET    /api/v1/roles/{id}               # Get role details
PUT    /api/v1/roles/{id}               # Update role
DELETE /api/v1/roles/{id}               # Delete role
GET    /api/v1/roles/{id}/permissions   # Get role permissions
PUT    /api/v1/roles/{id}/permissions   # Update role permissions
```

### Permission Management Endpoints
```
GET    /api/v1/permissions              # List all permissions
POST   /api/v1/permissions              # Create permission
GET    /api/v1/permissions/{id}         # Get permission details
PUT    /api/v1/permissions/{id}         # Update permission
DELETE /api/v1/permissions/{id}         # Delete permission
```

### Organization Endpoints
```
GET    /api/v1/organizations            # List organizations
POST   /api/v1/organizations            # Create organization
GET    /api/v1/organizations/{id}       # Get organization
PUT    /api/v1/organizations/{id}       # Update organization
DELETE /api/v1/organizations/{id}       # Delete organization
```

### Project Endpoints
```
GET    /api/v1/projects                 # List projects (filtered by tenant)
POST   /api/v1/projects                 # Create project
GET    /api/v1/projects/{id}            # Get project
PUT    /api/v1/projects/{id}            # Update project
DELETE /api/v1/projects/{id}            # Delete project
```

### Group Endpoints
```
GET    /api/v1/groups                   # List groups (filtered by tenant)
POST   /api/v1/groups                   # Create group
GET    /api/v1/groups/{id}              # Get group
PUT    /api/v1/groups/{id}              # Update group
DELETE /api/v1/groups/{id}              # Delete group
GET    /api/v1/groups/{id}/users        # Get group users
PUT    /api/v1/groups/{id}/users        # Update group users
```

## Frontend Design

### Component Structure
```
pages/
├── dashboard/
│   ├── index.vue                    # Main dashboard
│   ├── users/
│   │   ├── index.vue                # User list
│   │   ├── new.vue                  # Create user
│   │   ├── [id].vue                 # User details
│   │   └── [id]/
│   │       ├── edit.vue             # Edit user
│   │       └── roles.vue            # Manage user roles
│   ├── roles/
│   │   ├── index.vue                # Role list
│   │   ├── new.vue                  # Create role
│   │   └── [id].vue                 # Role details
│   ├── permissions/
│   │   ├── index.vue                # Permission list
│   │   └── new.vue                  # Create permission
│   ├── organizations/
│   │   ├── index.vue                # Organization list
│   │   ├── new.vue                  # Create organization
│   │   └── [id].vue                 # Organization details
│   ├── projects/
│   │   ├── index.vue                # Project list
│   │   ├── new.vue                  # Create project
│   │   └── [id].vue                 # Project details
│   └── groups/
│       ├── index.vue                # Group list
│       ├── new.vue                  # Create group
│       └── [id].vue                 # Group details
```

### Composables
```typescript
// useRBAC3.ts - Already exists, needs enhancement
// useUserManagement.ts - New
// useRoleManagement.ts - New
// usePermissionManagement.ts - New
// useTenantContext.ts - New
```

### UI Components
```
components/
├── rbac/
│   ├── UserTable.vue
│   ├── UserForm.vue
│   ├── RoleSelector.vue
│   ├── PermissionMatrix.vue
│   ├── TenantSelector.vue
│   └── ACLEditor.vue
```

## Security Considerations

### 1. Authentication
- JWT tokens with 60-minute expiration
- Refresh tokens with 7-day expiration
- Secure password hashing with bcrypt (cost factor 12)
- Account lockout after 5 failed attempts

### 2. Authorization
- Permission checks on every API call
- Tenant isolation enforced at database level
- ACL evaluation for fine-grained control
- Audit logging for all sensitive operations

### 3. Data Protection
- Passwords never stored in plain text
- Sensitive data encrypted at rest
- HTTPS required for all communications
- CORS properly configured

### 4. Tenant Isolation
- Database-level row-level security
- Query filters automatically applied
- Cross-tenant access prevented
- PROVIDER_ADMIN bypass with audit trail

## Performance Considerations

### 1. Caching
- Permission cache per user session
- Role cache with 5-minute TTL
- ACL cache with 1-minute TTL

### 2. Database Optimization
- Indexes on foreign keys
- Indexes on frequently queried columns
- Composite indexes for common queries
- Query optimization for permission checks

### 3. API Optimization
- Pagination for all list endpoints
- Filtering and sorting support
- Selective field loading
- Batch operations where applicable

## Monitoring and Logging

### 1. Audit Logs
Log the following events:
- User login/logout
- User creation/deletion
- Role assignment/removal
- Permission changes
- Tenant access by PROVIDER_ADMIN
- Password resets
- Failed authorization attempts

### 2. Metrics
Track:
- API response times
- Permission check latency
- Failed authorization rate
- Active users per tenant
- Resource usage per tenant

## Migration Strategy

### Phase 1: Database
1. Create new tables
2. Migrate existing data
3. Add foreign keys
4. Create indexes

### Phase 2: Backend
1. Implement new models
2. Implement services
3. Implement API routes
4. Add middleware
5. Update existing routes

### Phase 3: Frontend
1. Update composables
2. Create new pages
3. Update existing pages
4. Add UI components
5. Testing

### Phase 4: Deployment
1. Database migration
2. Backend deployment
3. Frontend deployment
4. Smoke testing
5. Rollback plan ready
