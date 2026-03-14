# RBAC Multi-Tenant System - Tasks

## Task Status Legend
- ⏳ pending - Not started
- 🔄 in_progress - Currently being worked on
- ✅ completed - Finished and tested
- ❌ blocked - Blocked by dependencies
- 🔍 review - Ready for review

---

## PHASE 1: Database Models & Migrations

### Task 1.1: Create Organization Model
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 30 minutes
**Dependencies**: None

**Description**:
Create SQLAlchemy model for organizations table.

**Acceptance Criteria**:
- Model created in `pcm/core/models/organization.py`
- Fields: id, name, slug, description, created_at, updated_at
- Relationship with tenants (1:N)
- __repr__ method implemented

**Files to Create/Modify**:
- `pcm/core/models/organization.py` (create)

---

### Task 1.2: Create Project Model
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 30 minutes
**Dependencies**: None

**Description**:
Create SQLAlchemy model for projects table.

**Acceptance Criteria**:
- Model created in `pcm/core/models/project.py`
- Fields: id, tenant_id, name, description, created_at, updated_at
- Relationship with tenant (N:1)
- __repr__ method implemented

**Files to Create/Modify**:
- `pcm/core/models/project.py` (create)

---

### Task 1.3: Create Group Model
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 30 minutes
**Dependencies**: None

**Description**:
Create SQLAlchemy model for groups table.

**Acceptance Criteria**:
- Model created in `pcm/core/models/group.py`
- Fields: id, tenant_id, name, description, created_at, updated_at
- Relationship with tenant (N:1)
- Relationship with users (N:M)
- __repr__ method implemented

**Files to Create/Modify**:
- `pcm/core/models/group.py` (create)

---

### Task 1.4: Create Role Model
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 45 minutes
**Dependencies**: None

**Description**:
Create SQLAlchemy model for roles table.

**Acceptance Criteria**:
- Model created in `pcm/core/models/role.py`
- Fields: id, tenant_id, name, description, is_system_role, created_at, updated_at
- Relationship with tenant (N:1)
- Relationship with permissions (N:M)
- Relationship with users (N:M)
- __repr__ method implemented

**Files to Create/Modify**:
- `pcm/core/models/role.py` (create)

---

### Task 1.5: Update Permission Model
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 30 minutes
**Dependencies**: None

**Description**:
Update existing Permission model or create new one.

**Acceptance Criteria**:
- Model in `pcm/core/models/permission.py`
- Fields: id, name, resource, action, description, created_at
- Relationship with roles (N:M)
- Unique constraint on name
- __repr__ method implemented

**Files to Create/Modify**:
- `pcm/core/models/permission.py` (modify or create)

---

### Task 1.6: Create ACL Entry Model
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 45 minutes
**Dependencies**: None

**Description**:
Create SQLAlchemy model for ACL entries table.

**Acceptance Criteria**:
- Model created in `pcm/core/models/acl.py`
- Fields: id, resource_type, resource_id, principal_type, principal_id, permission, allow, created_at
- Indexes on resource_type, resource_id, principal_type, principal_id
- __repr__ method implemented

**Files to Create/Modify**:
- `pcm/core/models/acl.py` (create)

---

### Task 1.7: Update Tenant Model
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 30 minutes
**Dependencies**: Task 1.1

**Description**:
Update Tenant model to add organization relationship.

**Acceptance Criteria**:
- Add organization_id foreign key
- Add relationship with organization (N:1)
- Add relationship with projects (1:N)
- Update __repr__ method

**Files to Create/Modify**:
- `pcm/core/models/tenant.py` (modify)

---

### Task 1.8: Update User Model
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 45 minutes
**Dependencies**: Task 1.3, Task 1.4

**Description**:
Update User model to add relationships with roles and groups.

**Acceptance Criteria**:
- Add relationship with roles (N:M via user_roles)
- Add relationship with groups (N:M via user_groups)
- Update permissions field to be JSON
- Add helper methods: has_role(), has_permission()
- Update __repr__ method

**Files to Create/Modify**:
- `pcm/core/models/user.py` (modify)

---

### Task 1.9: Create Database Migration - Organizations
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 30 minutes
**Dependencies**: Task 1.1

**Description**:
Create Alembic migration for organizations table.

**Acceptance Criteria**:
- Migration file created
- Creates organizations table
- Adds indexes
- Can upgrade and downgrade

**Files to Create/Modify**:
- `pcm/alembic/versions/008_add_organizations.py` (create)

---

### Task 1.10: Create Database Migration - RBAC Tables
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1 hour
**Dependencies**: Task 1.2, Task 1.3, Task 1.4, Task 1.5, Task 1.6

**Description**:
Create Alembic migration for all RBAC tables.

**Acceptance Criteria**:
- Migration file created
- Creates: projects, groups, roles, permissions, role_permissions, user_roles, user_groups, acl_entries
- Adds all foreign keys
- Adds all indexes
- Can upgrade and downgrade

**Files to Create/Modify**:
- `pcm/alembic/versions/009_add_rbac_tables.py` (create)

---

### Task 1.11: Create Permission Seeds
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1 hour
**Dependencies**: Task 1.10

**Description**:
Create script to seed default permissions and system roles.

**Acceptance Criteria**:
- Script created
- Seeds all default permissions (tenant:*, user:*, vm:*, etc.)
- Seeds system roles (PROVIDER_ADMIN, TENANT_ADMIN, TENANT_MANAGER, TENANT_USER)
- Associates permissions with roles
- Idempotent (can run multiple times)

**Files to Create/Modify**:
- `pcm/seed_rbac_permissions.py` (create)

---

## PHASE 2: Backend Services

### Task 2.1: Create Organization Service
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1 hour
**Dependencies**: Task 1.9

**Description**:
Create service for organization management.

**Acceptance Criteria**:
- Service created in `pcm/services/organization_service.py`
- Methods: create, get, list, update, delete
- Proper error handling
- Async/await pattern
- Type hints

**Files to Create/Modify**:
- `pcm/services/organization_service.py` (create)

---

### Task 2.2: Create Project Service
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1 hour
**Dependencies**: Task 1.10

**Description**:
Create service for project management.

**Acceptance Criteria**:
- Service created in `pcm/services/project_service.py`
- Methods: create, get, list, update, delete
- Tenant isolation enforced
- Proper error handling
- Async/await pattern

**Files to Create/Modify**:
- `pcm/services/project_service.py` (create)

---

### Task 2.3: Create Group Service
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1.5 hours
**Dependencies**: Task 1.10

**Description**:
Create service for group management.

**Acceptance Criteria**:
- Service created in `pcm/services/group_service.py`
- Methods: create, get, list, update, delete, add_user, remove_user, list_users
- Tenant isolation enforced
- Proper error handling
- Async/await pattern

**Files to Create/Modify**:
- `pcm/services/group_service.py` (create)

---

### Task 2.4: Create Role Service
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 1.10

**Description**:
Create service for role management.

**Acceptance Criteria**:
- Service created in `pcm/services/role_service.py`
- Methods: create, get, list, update, delete, add_permission, remove_permission, list_permissions
- Tenant isolation enforced
- System roles cannot be deleted
- Proper error handling
- Async/await pattern

**Files to Create/Modify**:
- `pcm/services/role_service.py` (create)

---

### Task 2.5: Update Permission Service
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1.5 hours
**Dependencies**: Task 1.10

**Description**:
Update or create permission service.

**Acceptance Criteria**:
- Service in `pcm/services/permission_service.py`
- Methods: create, get, list, update, delete
- Permission validation
- Proper error handling
- Async/await pattern

**Files to Create/Modify**:
- `pcm/services/permission_service.py` (modify or create)

---

### Task 2.6: Create ACL Service
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 2 hours
**Dependencies**: Task 1.10

**Description**:
Create service for ACL management.

**Acceptance Criteria**:
- Service created in `pcm/services/acl_service.py`
- Methods: create_entry, delete_entry, check_access, list_entries
- Efficient permission checking
- Cache support
- Proper error handling

**Files to Create/Modify**:
- `pcm/services/acl_service.py` (create)

---

### Task 2.7: Update User Service
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 1.10, Task 2.4

**Description**:
Update user service with role management.

**Acceptance Criteria**:
- Add methods: assign_role, remove_role, list_roles, get_permissions
- Add method: reset_password (for admins)
- Tenant isolation enforced
- PROVIDER_ADMIN can manage all users
- TENANT_ADMIN can manage tenant users only
- Proper error handling

**Files to Create/Modify**:
- `pcm/services/user_service.py` (modify or create)

---

### Task 2.8: Create Authorization Service
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 3 hours
**Dependencies**: Task 2.5, Task 2.6

**Description**:
Create centralized authorization service.

**Acceptance Criteria**:
- Service created in `pcm/services/authorization_service.py`
- Methods: check_permission, check_tenant_access, get_user_permissions
- Handles PROVIDER_ADMIN bypass
- Handles tenant isolation
- Evaluates ACL entries
- Permission caching
- Proper error handling

**Files to Create/Modify**:
- `pcm/services/authorization_service.py` (create)

---

## PHASE 3: Backend API Routes

### Task 3.1: Create Organization Routes
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1.5 hours
**Dependencies**: Task 2.1

**Description**:
Create REST API routes for organizations.

**Acceptance Criteria**:
- Routes created in `pcm/services/api/routes/organizations.py`
- Endpoints: GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id}
- Requires PROVIDER_ADMIN role
- Proper validation
- Error handling
- OpenAPI documentation

**Files to Create/Modify**:
- `pcm/services/api/routes/organizations.py` (create)
- `pcm/services/api/main.py` (modify - add router)

---

### Task 3.2: Create Project Routes
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1.5 hours
**Dependencies**: Task 2.2

**Description**:
Create REST API routes for projects.

**Acceptance Criteria**:
- Routes created in `pcm/services/api/routes/projects.py`
- Endpoints: GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id}
- Tenant isolation enforced
- Proper validation
- Error handling
- OpenAPI documentation

**Files to Create/Modify**:
- `pcm/services/api/routes/projects.py` (create)
- `pcm/services/api/main.py` (modify - add router)

---

### Task 3.3: Create Group Routes
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 2.3

**Description**:
Create REST API routes for groups.

**Acceptance Criteria**:
- Routes created in `pcm/services/api/routes/groups.py`
- Endpoints: GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id}
- Endpoints: GET /{id}/users, PUT /{id}/users
- Tenant isolation enforced
- Proper validation
- Error handling
- OpenAPI documentation

**Files to Create/Modify**:
- `pcm/services/api/routes/groups.py` (create)
- `pcm/services/api/main.py` (modify - add router)

---

### Task 3.4: Create Role Routes
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 2.4

**Description**:
Create REST API routes for roles.

**Acceptance Criteria**:
- Routes created in `pcm/services/api/routes/roles.py`
- Endpoints: GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id}
- Endpoints: GET /{id}/permissions, PUT /{id}/permissions
- Tenant isolation enforced
- System roles cannot be deleted
- Proper validation
- Error handling
- OpenAPI documentation

**Files to Create/Modify**:
- `pcm/services/api/routes/roles.py` (create)
- `pcm/services/api/main.py` (modify - add router)

---

### Task 3.5: Update User Routes
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2.5 hours
**Dependencies**: Task 2.7

**Description**:
Update user routes with role management and password reset.

**Acceptance Criteria**:
- Update `pcm/services/api/routes/users.py`
- Add endpoints: GET /{id}/roles, PUT /{id}/roles
- Add endpoint: POST /{id}/password (reset password)
- Tenant isolation enforced
- PROVIDER_ADMIN can manage all users
- TENANT_ADMIN can manage tenant users
- Proper validation
- Error handling
- OpenAPI documentation

**Files to Create/Modify**:
- `pcm/services/api/routes/users.py` (modify or create)
- `pcm/services/api/main.py` (modify - add router if needed)

---

### Task 3.6: Create Permission Routes
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 1.5 hours
**Dependencies**: Task 2.5

**Description**:
Create REST API routes for permissions.

**Acceptance Criteria**:
- Routes created in `pcm/services/api/routes/permissions.py`
- Endpoints: GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id}
- Requires PROVIDER_ADMIN role
- Proper validation
- Error handling
- OpenAPI documentation

**Files to Create/Modify**:
- `pcm/services/api/routes/permissions.py` (create)
- `pcm/services/api/main.py` (modify - add router)

---

### Task 3.7: Create Authorization Middleware
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 2.8

**Description**:
Create middleware for authorization checks.

**Acceptance Criteria**:
- Middleware created in `pcm/services/api/middleware/authorization_middleware.py`
- Checks permissions on every request
- Enforces tenant isolation
- Handles PROVIDER_ADMIN bypass
- Proper error responses (403 Forbidden)
- Performance optimized

**Files to Create/Modify**:
- `pcm/services/api/middleware/authorization_middleware.py` (create)
- `pcm/services/api/main.py` (modify - add middleware)

---

## PHASE 4: Frontend - Admin Global

### Task 4.1: Create User Management Page - List
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 3.5

**Description**:
Create user list page for PROVIDER_ADMIN.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/users/index.vue`
- Shows all users across all tenants
- Filterable by tenant, role, status
- Searchable by name, email
- Actions: Create, Edit, Delete, Reset Password
- Pagination
- Responsive design
- Proxmox colors

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/users/index.vue` (modify or create)

---

### Task 4.2: Create User Management Page - Create/Edit
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2.5 hours
**Dependencies**: Task 3.5, Task 4.1

**Description**:
Create user create/edit form.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/users/new.vue`
- Page created in `pcmfe/pages/dashboard/users/[id]/edit.vue`
- Form fields: email, username, full_name, tenant, role, password
- Tenant selector (for PROVIDER_ADMIN)
- Role selector
- Validation
- Error handling
- Success feedback

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/users/new.vue` (create)
- `pcmfe/pages/dashboard/users/[id]/edit.vue` (create)

---

### Task 4.3: Create User Role Management Page
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 3.5, Task 4.1

**Description**:
Create page to manage user roles.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/users/[id]/roles.vue`
- Shows current roles
- Can add/remove roles
- Shows permissions per role
- Real-time updates
- Error handling

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/users/[id]/roles.vue` (create)

---

### Task 4.4: Create Role Management Page - List
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 3.4

**Description**:
Create role list page.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/roles/index.vue`
- Shows all roles
- Filterable by tenant, system/custom
- Actions: Create, Edit, Delete (except system roles)
- Shows permission count
- Responsive design

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/roles/index.vue` (create)

---

### Task 4.5: Create Role Management Page - Create/Edit
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 3 hours
**Dependencies**: Task 3.4, Task 4.4

**Description**:
Create role create/edit form with permission matrix.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/roles/new.vue`
- Page created in `pcmfe/pages/dashboard/roles/[id].vue`
- Form fields: name, description, tenant
- Permission matrix (grouped by resource)
- Select all/none per resource
- Validation
- Error handling

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/roles/new.vue` (create)
- `pcmfe/pages/dashboard/roles/[id].vue` (create)

---

### Task 4.6: Create Permission Management Page
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 2 hours
**Dependencies**: Task 3.6

**Description**:
Create permission list and management page.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/permissions/index.vue`
- Shows all permissions
- Grouped by resource
- Filterable by resource, action
- Actions: Create, Edit, Delete
- Responsive design

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/permissions/index.vue` (create)

---

### Task 4.7: Create Organization Management Pages
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 2.5 hours
**Dependencies**: Task 3.1

**Description**:
Create organization list and form pages.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/organizations/index.vue`
- Page created in `pcmfe/pages/dashboard/organizations/new.vue`
- Page created in `pcmfe/pages/dashboard/organizations/[id].vue`
- CRUD operations
- Shows tenant count
- Responsive design

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/organizations/index.vue` (create)
- `pcmfe/pages/dashboard/organizations/new.vue` (create)
- `pcmfe/pages/dashboard/organizations/[id].vue` (create)

---

### Task 4.8: Create useUserManagement Composable
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 3.5

**Description**:
Create composable for user management operations.

**Acceptance Criteria**:
- Composable created in `pcmfe/composables/useUserManagement.ts`
- Methods: listUsers, createUser, updateUser, deleteUser, resetPassword
- Methods: assignRole, removeRole, listUserRoles
- Error handling
- Loading states
- Type safety

**Files to Create/Modify**:
- `pcmfe/composables/useUserManagement.ts` (create)

---

### Task 4.9: Create useRoleManagement Composable
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1.5 hours
**Dependencies**: Task 3.4

**Description**:
Create composable for role management operations.

**Acceptance Criteria**:
- Composable created in `pcmfe/composables/useRoleManagement.ts`
- Methods: listRoles, createRole, updateRole, deleteRole
- Methods: addPermission, removePermission, listRolePermissions
- Error handling
- Loading states
- Type safety

**Files to Create/Modify**:
- `pcmfe/composables/useRoleManagement.ts` (create)

---

### Task 4.10: Update Navigation Menu
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 1 hour
**Dependencies**: Task 4.1, Task 4.4, Task 4.6, Task 4.7

**Description**:
Update sidebar navigation to include new pages.

**Acceptance Criteria**:
- Update `pcmfe/layouts/default.vue`
- Add "User Management" menu item
- Add "Role Management" menu item
- Add "Permissions" menu item
- Add "Organizations" menu item
- Show/hide based on user role
- Proper icons

**Files to Create/Modify**:
- `pcmfe/layouts/default.vue` (modify)

---

## PHASE 5: Frontend - Tenant Admin

### Task 5.1: Create Tenant Dashboard
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 3 hours
**Dependencies**: Task 3.2

**Description**:
Create tenant-specific dashboard.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/tenant/index.vue`
- Shows tenant resources overview
- Shows user count
- Shows VM/network/firewall count
- Shows quota usage
- Tenant-scoped data only

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/tenant/index.vue` (create)

---

### Task 5.2: Create Tenant User Management
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 2 hours
**Dependencies**: Task 4.2, Task 4.3

**Description**:
Create tenant-scoped user management pages.

**Acceptance Criteria**:
- Reuse components from Task 4.2, 4.3
- Filter users by current tenant
- TENANT_ADMIN can create users in their tenant
- Cannot access other tenants
- Proper error handling

**Files to Create/Modify**:
- Update existing user pages to handle tenant context

---

### Task 5.3: Create Project Management Pages
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 2.5 hours
**Dependencies**: Task 3.2

**Description**:
Create project list and form pages.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/projects/index.vue`
- Page created in `pcmfe/pages/dashboard/projects/new.vue`
- Page created in `pcmfe/pages/dashboard/projects/[id].vue`
- Tenant-scoped
- CRUD operations
- Responsive design

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/projects/index.vue` (create)
- `pcmfe/pages/dashboard/projects/new.vue` (create)
- `pcmfe/pages/dashboard/projects/[id].vue` (create)

---

### Task 5.4: Create Group Management Pages
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 2.5 hours
**Dependencies**: Task 3.3

**Description**:
Create group list and form pages.

**Acceptance Criteria**:
- Page created in `pcmfe/pages/dashboard/groups/index.vue`
- Page created in `pcmfe/pages/dashboard/groups/new.vue`
- Page created in `pcmfe/pages/dashboard/groups/[id].vue`
- Tenant-scoped
- CRUD operations
- User assignment
- Responsive design

**Files to Create/Modify**:
- `pcmfe/pages/dashboard/groups/index.vue` (create)
- `pcmfe/pages/dashboard/groups/new.vue` (create)
- `pcmfe/pages/dashboard/groups/[id].vue` (create)

---

## PHASE 6: Testing & Documentation

### Task 6.1: Write Backend Unit Tests
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 4 hours
**Dependencies**: Phase 2 complete

**Description**:
Write unit tests for all services.

**Acceptance Criteria**:
- Tests for all services
- Test coverage > 80%
- Test tenant isolation
- Test permission checks
- Test error cases

**Files to Create/Modify**:
- `pcm/tests/services/test_organization_service.py` (create)
- `pcm/tests/services/test_project_service.py` (create)
- `pcm/tests/services/test_group_service.py` (create)
- `pcm/tests/services/test_role_service.py` (create)
- `pcm/tests/services/test_acl_service.py` (create)
- `pcm/tests/services/test_authorization_service.py` (create)

---

### Task 6.2: Write API Integration Tests
**Status**: ⏳ pending
**Priority**: high
**Estimated Time**: 4 hours
**Dependencies**: Phase 3 complete

**Description**:
Write integration tests for all API routes.

**Acceptance Criteria**:
- Tests for all routes
- Test authentication
- Test authorization
- Test tenant isolation
- Test error responses

**Files to Create/Modify**:
- `pcm/tests/api/test_organizations.py` (create)
- `pcm/tests/api/test_projects.py` (create)
- `pcm/tests/api/test_groups.py` (create)
- `pcm/tests/api/test_roles.py` (create)
- `pcm/tests/api/test_users_rbac.py` (create)

---

### Task 6.3: Write Frontend Component Tests
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 3 hours
**Dependencies**: Phase 4 complete

**Description**:
Write tests for frontend components and composables.

**Acceptance Criteria**:
- Tests for composables
- Tests for key components
- Test user interactions
- Test error handling

**Files to Create/Modify**:
- `pcmfe/composables/__tests__/useUserManagement.test.ts` (create)
- `pcmfe/composables/__tests__/useRoleManagement.test.ts` (create)

---

### Task 6.4: Create API Documentation
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 2 hours
**Dependencies**: Phase 3 complete

**Description**:
Create comprehensive API documentation.

**Acceptance Criteria**:
- OpenAPI/Swagger documentation
- Examples for all endpoints
- Authentication guide
- Authorization guide
- Tenant isolation explained

**Files to Create/Modify**:
- `docs/API_DOCUMENTATION.md` (create)

---

### Task 6.5: Create User Guide
**Status**: ⏳ pending
**Priority**: medium
**Estimated Time**: 2 hours
**Dependencies**: Phase 4, 5 complete

**Description**:
Create user guide for RBAC system.

**Acceptance Criteria**:
- Guide for PROVIDER_ADMIN
- Guide for TENANT_ADMIN
- Guide for TENANT_MANAGER
- Guide for TENANT_USER
- Screenshots
- Common workflows

**Files to Create/Modify**:
- `docs/RBAC_USER_GUIDE.md` (create)

---

## Summary

**Total Tasks**: 60+
**Estimated Total Time**: 80-100 hours
**Priority Breakdown**:
- High Priority: 40 tasks
- Medium Priority: 15 tasks
- Low Priority: 5 tasks

**Phase Breakdown**:
- Phase 1 (Database): 11 tasks, ~8 hours
- Phase 2 (Services): 8 tasks, ~15 hours
- Phase 3 (API): 7 tasks, ~14 hours
- Phase 4 (Frontend Admin): 10 tasks, ~20 hours
- Phase 5 (Frontend Tenant): 4 tasks, ~10 hours
- Phase 6 (Testing): 5 tasks, ~15 hours

**Critical Path**:
1. Database models and migrations (Phase 1)
2. Core services (Phase 2)
3. API routes (Phase 3)
4. Frontend pages (Phase 4, 5)
5. Testing and documentation (Phase 6)
