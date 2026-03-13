"""Permission and RBAC service for access control."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pcm.core.models.permission import Permission, Role, AuditLog, user_roles
from pcm.core.models.user import User
from pcm.core.models.tenant import Tenant
from uuid import uuid4
from datetime import datetime


class PermissionService:
    """Service for managing permissions and roles."""

    @staticmethod
    async def create_permission(
        session: AsyncSession,
        name: str,
        resource: str,
        action: str,
        description: Optional[str] = None
    ) -> Permission:
        """Create a new permission."""
        permission = Permission(
            id=str(uuid4()),
            name=name,
            resource=resource,
            action=action,
            description=description
        )
        session.add(permission)
        await session.flush()
        return permission

    @staticmethod
    async def get_permission(session: AsyncSession, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        result = await session.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_permission_by_name(session: AsyncSession, name: str) -> Optional[Permission]:
        """Get permission by name."""
        result = await session.execute(
            select(Permission).where(Permission.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_permissions(session: AsyncSession) -> List[Permission]:
        """List all permissions."""
        result = await session.execute(select(Permission))
        return result.scalars().all()

    @staticmethod
    async def list_permissions_by_resource(
        session: AsyncSession,
        resource: str
    ) -> List[Permission]:
        """List permissions for a specific resource."""
        result = await session.execute(
            select(Permission).where(Permission.resource == resource)
        )
        return result.scalars().all()


class RoleService:
    """Service for managing roles."""

    @staticmethod
    async def create_role(
        session: AsyncSession,
        name: str,
        description: Optional[str] = None,
        is_system_role: bool = False,
        tenant_id: Optional[str] = None
    ) -> Role:
        """Create a new role."""
        role = Role(
            id=str(uuid4()),
            name=name,
            description=description,
            is_system_role=is_system_role,
            tenant_id=tenant_id
        )
        session.add(role)
        await session.flush()
        return role

    @staticmethod
    async def get_role(session: AsyncSession, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        result = await session.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_role_by_name(
        session: AsyncSession,
        name: str,
        tenant_id: Optional[str] = None
    ) -> Optional[Role]:
        """Get role by name."""
        query = select(Role).where(Role.name == name)
        if tenant_id:
            query = query.where(Role.tenant_id == tenant_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_roles(session: AsyncSession, tenant_id: Optional[str] = None) -> List[Role]:
        """List roles, optionally filtered by tenant."""
        query = select(Role)
        if tenant_id:
            query = query.where(
                (Role.tenant_id == tenant_id) | (Role.is_system_role == True)
            )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def add_permission_to_role(
        session: AsyncSession,
        role: Role,
        permission: Permission
    ) -> None:
        """Add a permission to a role."""
        if permission not in role.permissions:
            role.permissions.append(permission)
            await session.flush()

    @staticmethod
    async def remove_permission_from_role(
        session: AsyncSession,
        role: Role,
        permission: Permission
    ) -> None:
        """Remove a permission from a role."""
        if permission in role.permissions:
            role.permissions.remove(permission)
            await session.flush()

    @staticmethod
    async def delete_role(session: AsyncSession, role: Role) -> None:
        """Delete a role (only if not system role)."""
        if role.is_system_role:
            raise ValueError("Cannot delete system roles")
        await session.delete(role)
        await session.flush()


class UserRoleService:
    """Service for managing user roles."""

    @staticmethod
    async def assign_role_to_user(
        session: AsyncSession,
        user: User,
        role: Role
    ) -> None:
        """Assign a role to a user."""
        if role not in user.roles:
            user.roles.append(role)
            await session.flush()

    @staticmethod
    async def remove_role_from_user(
        session: AsyncSession,
        user: User,
        role: Role
    ) -> None:
        """Remove a role from a user."""
        if role in user.roles:
            user.roles.remove(role)
            await session.flush()

    @staticmethod
    async def get_user_roles(session: AsyncSession, user_id: str) -> List[Role]:
        """Get all roles for a user."""
        result = await session.execute(
            select(Role).join(user_roles).where(user_roles.c.user_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_user_permissions(session: AsyncSession, user_id: str) -> List[Permission]:
        """Get all permissions for a user through their roles."""
        result = await session.execute(
            select(Permission)
            .join(user_roles, user_roles.c.role_id == Role.id)
            .join(Role.permissions)
            .where(user_roles.c.user_id == user_id)
            .distinct()
        )
        return result.scalars().all()

    @staticmethod
    async def user_has_permission(
        session: AsyncSession,
        user_id: str,
        permission_name: str
    ) -> bool:
        """Check if user has a specific permission."""
        result = await session.execute(
            select(Permission)
            .join(user_roles, user_roles.c.role_id == Role.id)
            .join(Role.permissions)
            .where(
                and_(
                    user_roles.c.user_id == user_id,
                    Permission.name == permission_name
                )
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def user_has_any_permission(
        session: AsyncSession,
        user_id: str,
        permission_names: List[str]
    ) -> bool:
        """Check if user has any of the given permissions."""
        result = await session.execute(
            select(Permission)
            .join(user_roles, user_roles.c.role_id == Role.id)
            .join(Role.permissions)
            .where(
                and_(
                    user_roles.c.user_id == user_id,
                    Permission.name.in_(permission_names)
                )
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def user_has_all_permissions(
        session: AsyncSession,
        user_id: str,
        permission_names: List[str]
    ) -> bool:
        """Check if user has all of the given permissions."""
        for permission_name in permission_names:
            has_perm = await UserRoleService.user_has_permission(
                session, user_id, permission_name
            )
            if not has_perm:
                return False
        return True


class AuditLogService:
    """Service for managing audit logs."""

    @staticmethod
    async def log_action(
        session: AsyncSession,
        user_id: Optional[str],
        tenant_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry."""
        audit_log = AuditLog(
            id=str(uuid4()),
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        session.add(audit_log)
        await session.flush()
        return audit_log

    @staticmethod
    async def get_audit_logs(
        session: AsyncSession,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with optional filtering."""
        query = select(AuditLog)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if tenant_id:
            query = query.where(AuditLog.tenant_id == tenant_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)

        query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_user_audit_logs(
        session: AsyncSession,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        return await AuditLogService.get_audit_logs(
            session, user_id=user_id, limit=limit, offset=offset
        )

    @staticmethod
    async def get_tenant_audit_logs(
        session: AsyncSession,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs for a specific tenant."""
        return await AuditLogService.get_audit_logs(
            session, tenant_id=tenant_id, limit=limit, offset=offset
        )

