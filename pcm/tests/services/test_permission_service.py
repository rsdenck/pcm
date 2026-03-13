"""Tests for permission service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from pcm.services.permission_service import (
    PermissionService,
    RoleService,
    UserRoleService,
    AuditLogService
)
from pcm.core.models.permission import Permission, Role, AuditLog
from pcm.core.models.user import User
from pcm.core.models.tenant import Tenant
from uuid import uuid4


@pytest.fixture
async def permission(session: AsyncSession):
    """Create a test permission."""
    return await PermissionService.create_permission(
        session,
        name="vm:create",
        resource="vm",
        action="create",
        description="Create virtual machines"
    )


@pytest.fixture
async def role(session: AsyncSession):
    """Create a test role."""
    return await RoleService.create_role(
        session,
        name="tenant_user",
        description="Tenant user role",
        is_system_role=True
    )


@pytest.fixture
async def user(session: AsyncSession):
    """Create a test user."""
    user = User(
        id=str(uuid4()),
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    session.add(user)
    await session.flush()
    return user


class TestPermissionService:
    """Test PermissionService class."""

    @pytest.mark.asyncio
    async def test_create_permission(self, session: AsyncSession):
        """Test creating a permission."""
        permission = await PermissionService.create_permission(
            session,
            name="vm:delete",
            resource="vm",
            action="delete",
            description="Delete virtual machines"
        )
        assert permission.name == "vm:delete"
        assert permission.resource == "vm"
        assert permission.action == "delete"

    @pytest.mark.asyncio
    async def test_get_permission(self, session: AsyncSession, permission: Permission):
        """Test getting a permission by ID."""
        retrieved = await PermissionService.get_permission(session, permission.id)
        assert retrieved is not None
        assert retrieved.id == permission.id
        assert retrieved.name == "vm:create"

    @pytest.mark.asyncio
    async def test_get_permission_by_name(self, session: AsyncSession, permission: Permission):
        """Test getting a permission by name."""
        retrieved = await PermissionService.get_permission_by_name(session, "vm:create")
        assert retrieved is not None
        assert retrieved.name == "vm:create"

    @pytest.mark.asyncio
    async def test_list_permissions(self, session: AsyncSession, permission: Permission):
        """Test listing all permissions."""
        permissions = await PermissionService.list_permissions(session)
        assert len(permissions) > 0
        assert any(p.name == "vm:create" for p in permissions)

    @pytest.mark.asyncio
    async def test_list_permissions_by_resource(self, session: AsyncSession, permission: Permission):
        """Test listing permissions by resource."""
        permissions = await PermissionService.list_permissions_by_resource(session, "vm")
        assert len(permissions) > 0
        assert all(p.resource == "vm" for p in permissions)


class TestRoleService:
    """Test RoleService class."""

    @pytest.mark.asyncio
    async def test_create_role(self, session: AsyncSession):
        """Test creating a role."""
        role = await RoleService.create_role(
            session,
            name="admin",
            description="Administrator role",
            is_system_role=True
        )
        assert role.name == "admin"
        assert role.is_system_role is True

    @pytest.mark.asyncio
    async def test_get_role(self, session: AsyncSession, role: Role):
        """Test getting a role by ID."""
        retrieved = await RoleService.get_role(session, role.id)
        assert retrieved is not None
        assert retrieved.id == role.id

    @pytest.mark.asyncio
    async def test_get_role_by_name(self, session: AsyncSession, role: Role):
        """Test getting a role by name."""
        retrieved = await RoleService.get_role_by_name(session, "tenant_user")
        assert retrieved is not None
        assert retrieved.name == "tenant_user"

    @pytest.mark.asyncio
    async def test_list_roles(self, session: AsyncSession, role: Role):
        """Test listing roles."""
        roles = await RoleService.list_roles(session)
        assert len(roles) > 0
        assert any(r.name == "tenant_user" for r in roles)

    @pytest.mark.asyncio
    async def test_add_permission_to_role(
        self,
        session: AsyncSession,
        role: Role,
        permission: Permission
    ):
        """Test adding permission to role."""
        await RoleService.add_permission_to_role(session, role, permission)
        assert permission in role.permissions

    @pytest.mark.asyncio
    async def test_remove_permission_from_role(
        self,
        session: AsyncSession,
        role: Role,
        permission: Permission
    ):
        """Test removing permission from role."""
        await RoleService.add_permission_to_role(session, role, permission)
        await RoleService.remove_permission_from_role(session, role, permission)
        assert permission not in role.permissions

    @pytest.mark.asyncio
    async def test_delete_role_system_role_fails(self, session: AsyncSession, role: Role):
        """Test deleting system role fails."""
        with pytest.raises(ValueError):
            await RoleService.delete_role(session, role)

    @pytest.mark.asyncio
    async def test_delete_role_custom_role(self, session: AsyncSession):
        """Test deleting custom role."""
        custom_role = await RoleService.create_role(
            session,
            name="custom_role",
            is_system_role=False
        )
        await RoleService.delete_role(session, custom_role)
        retrieved = await RoleService.get_role(session, custom_role.id)
        assert retrieved is None


class TestUserRoleService:
    """Test UserRoleService class."""

    @pytest.mark.asyncio
    async def test_assign_role_to_user(
        self,
        session: AsyncSession,
        user: User,
        role: Role
    ):
        """Test assigning role to user."""
        await UserRoleService.assign_role_to_user(session, user, role)
        assert role in user.roles

    @pytest.mark.asyncio
    async def test_remove_role_from_user(
        self,
        session: AsyncSession,
        user: User,
        role: Role
    ):
        """Test removing role from user."""
        await UserRoleService.assign_role_to_user(session, user, role)
        await UserRoleService.remove_role_from_user(session, user, role)
        assert role not in user.roles

    @pytest.mark.asyncio
    async def test_get_user_roles(
        self,
        session: AsyncSession,
        user: User,
        role: Role
    ):
        """Test getting user roles."""
        await UserRoleService.assign_role_to_user(session, user, role)
        roles = await UserRoleService.get_user_roles(session, user.id)
        assert len(roles) > 0
        assert any(r.id == role.id for r in roles)

    @pytest.mark.asyncio
    async def test_get_user_permissions(
        self,
        session: AsyncSession,
        user: User,
        role: Role,
        permission: Permission
    ):
        """Test getting user permissions."""
        await UserRoleService.assign_role_to_user(session, user, role)
        await RoleService.add_permission_to_role(session, role, permission)
        permissions = await UserRoleService.get_user_permissions(session, user.id)
        assert len(permissions) > 0
        assert any(p.id == permission.id for p in permissions)

    @pytest.mark.asyncio
    async def test_user_has_permission(
        self,
        session: AsyncSession,
        user: User,
        role: Role,
        permission: Permission
    ):
        """Test checking if user has permission."""
        await UserRoleService.assign_role_to_user(session, user, role)
        await RoleService.add_permission_to_role(session, role, permission)
        has_perm = await UserRoleService.user_has_permission(session, user.id, "vm:create")
        assert has_perm is True

    @pytest.mark.asyncio
    async def test_user_has_any_permission(
        self,
        session: AsyncSession,
        user: User,
        role: Role,
        permission: Permission
    ):
        """Test checking if user has any permission."""
        await UserRoleService.assign_role_to_user(session, user, role)
        await RoleService.add_permission_to_role(session, role, permission)
        has_perm = await UserRoleService.user_has_any_permission(
            session, user.id, ["vm:create", "vm:delete"]
        )
        assert has_perm is True

    @pytest.mark.asyncio
    async def test_user_has_all_permissions(
        self,
        session: AsyncSession,
        user: User,
        role: Role,
        permission: Permission
    ):
        """Test checking if user has all permissions."""
        await UserRoleService.assign_role_to_user(session, user, role)
        await RoleService.add_permission_to_role(session, role, permission)
        has_perm = await UserRoleService.user_has_all_permissions(
            session, user.id, ["vm:create"]
        )
        assert has_perm is True


class TestAuditLogService:
    """Test AuditLogService class."""

    @pytest.mark.asyncio
    async def test_log_action(self, session: AsyncSession):
        """Test logging an action."""
        audit_log = await AuditLogService.log_action(
            session,
            user_id="user-123",
            tenant_id="tenant-123",
            action="vm_created",
            resource_type="vm",
            resource_id="vm-123",
            status="success"
        )
        assert audit_log.action == "vm_created"
        assert audit_log.status == "success"

    @pytest.mark.asyncio
    async def test_get_audit_logs(self, session: AsyncSession):
        """Test getting audit logs."""
        await AuditLogService.log_action(
            session,
            user_id="user-123",
            tenant_id="tenant-123",
            action="vm_created",
            resource_type="vm",
            status="success"
        )
        logs = await AuditLogService.get_audit_logs(session)
        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_get_user_audit_logs(self, session: AsyncSession):
        """Test getting user audit logs."""
        await AuditLogService.log_action(
            session,
            user_id="user-123",
            tenant_id="tenant-123",
            action="vm_created",
            resource_type="vm",
            status="success"
        )
        logs = await AuditLogService.get_user_audit_logs(session, "user-123")
        assert len(logs) > 0
        assert all(log.user_id == "user-123" for log in logs)

    @pytest.mark.asyncio
    async def test_get_tenant_audit_logs(self, session: AsyncSession):
        """Test getting tenant audit logs."""
        await AuditLogService.log_action(
            session,
            user_id="user-123",
            tenant_id="tenant-123",
            action="vm_created",
            resource_type="vm",
            status="success"
        )
        logs = await AuditLogService.get_tenant_audit_logs(session, "tenant-123")
        assert len(logs) > 0
        assert all(log.tenant_id == "tenant-123" for log in logs)

