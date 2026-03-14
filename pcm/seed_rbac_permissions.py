"""
Seed script for RBAC permissions and system roles.
Creates all default permissions and system roles with their associations.
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pcm.core.database import engine, get_db
from pcm.core.models.permission import Permission, Role, AuditLog
from pcm.core.models.organization import Organization
from pcm.core.models.project import Project
from pcm.core.models.group import Group
from uuid import uuid4


# Define all permissions
PERMISSIONS = [
    # Tenant permissions
    {"name": "tenant:create", "resource": "tenant", "action": "create", "description": "Create new tenants"},
    {"name": "tenant:read", "resource": "tenant", "action": "read", "description": "View tenant details"},
    {"name": "tenant:update", "resource": "tenant", "action": "update", "description": "Update tenant settings"},
    {"name": "tenant:delete", "resource": "tenant", "action": "delete", "description": "Delete tenants"},
    {"name": "tenant:manage", "resource": "tenant", "action": "manage", "description": "Full tenant management"},
    
    # User permissions
    {"name": "user:create", "resource": "user", "action": "create", "description": "Create new users"},
    {"name": "user:read", "resource": "user", "action": "read", "description": "View user details"},
    {"name": "user:update", "resource": "user", "action": "update", "description": "Update user information"},
    {"name": "user:delete", "resource": "user", "action": "delete", "description": "Delete users"},
    {"name": "user:manage", "resource": "user", "action": "manage", "description": "Full user management"},
    
    # Cluster permissions
    {"name": "cluster:create", "resource": "cluster", "action": "create", "description": "Create new clusters"},
    {"name": "cluster:read", "resource": "cluster", "action": "read", "description": "View cluster details"},
    {"name": "cluster:update", "resource": "cluster", "action": "update", "description": "Update cluster settings"},
    {"name": "cluster:delete", "resource": "cluster", "action": "delete", "description": "Delete clusters"},
    {"name": "cluster:manage", "resource": "cluster", "action": "manage", "description": "Full cluster management"},
    {"name": "cluster:test_connection", "resource": "cluster", "action": "test_connection", "description": "Test cluster connection"},
    
    # VM permissions
    {"name": "vm:create", "resource": "vm", "action": "create", "description": "Create virtual machines"},
    {"name": "vm:read", "resource": "vm", "action": "read", "description": "View VM details"},
    {"name": "vm:update", "resource": "vm", "action": "update", "description": "Update VM configuration"},
    {"name": "vm:delete", "resource": "vm", "action": "delete", "description": "Delete virtual machines"},
    {"name": "vm:manage", "resource": "vm", "action": "manage", "description": "Full VM management"},
    {"name": "vm:start", "resource": "vm", "action": "start", "description": "Start virtual machines"},
    {"name": "vm:stop", "resource": "vm", "action": "stop", "description": "Stop virtual machines"},
    {"name": "vm:restart", "resource": "vm", "action": "restart", "description": "Restart virtual machines"},
    
    # Container permissions
    {"name": "container:create", "resource": "container", "action": "create", "description": "Create containers"},
    {"name": "container:read", "resource": "container", "action": "read", "description": "View container details"},
    {"name": "container:update", "resource": "container", "action": "update", "description": "Update container configuration"},
    {"name": "container:delete", "resource": "container", "action": "delete", "description": "Delete containers"},
    {"name": "container:manage", "resource": "container", "action": "manage", "description": "Full container management"},
    {"name": "container:start", "resource": "container", "action": "start", "description": "Start containers"},
    {"name": "container:stop", "resource": "container", "action": "stop", "description": "Stop containers"},
    {"name": "container:restart", "resource": "container", "action": "restart", "description": "Restart containers"},
    
    # Storage permissions
    {"name": "storage:create", "resource": "storage", "action": "create", "description": "Create storage"},
    {"name": "storage:read", "resource": "storage", "action": "read", "description": "View storage details"},
    {"name": "storage:update", "resource": "storage", "action": "update", "description": "Update storage configuration"},
    {"name": "storage:delete", "resource": "storage", "action": "delete", "description": "Delete storage"},
    {"name": "storage:manage", "resource": "storage", "action": "manage", "description": "Full storage management"},
    
    # Network permissions
    {"name": "network:create", "resource": "network", "action": "create", "description": "Create networks"},
    {"name": "network:read", "resource": "network", "action": "read", "description": "View network details"},
    {"name": "network:update", "resource": "network", "action": "update", "description": "Update network configuration"},
    {"name": "network:delete", "resource": "network", "action": "delete", "description": "Delete networks"},
    {"name": "network:manage", "resource": "network", "action": "manage", "description": "Full network management"},
    
    # Firewall permissions
    {"name": "firewall:create", "resource": "firewall", "action": "create", "description": "Create firewall rules"},
    {"name": "firewall:read", "resource": "firewall", "action": "read", "description": "View firewall rules"},
    {"name": "firewall:update", "resource": "firewall", "action": "update", "description": "Update firewall rules"},
    {"name": "firewall:delete", "resource": "firewall", "action": "delete", "description": "Delete firewall rules"},
    {"name": "firewall:manage", "resource": "firewall", "action": "manage", "description": "Full firewall management"},
    
    # Backup permissions
    {"name": "backup:create", "resource": "backup", "action": "create", "description": "Create backups"},
    {"name": "backup:read", "resource": "backup", "action": "read", "description": "View backup details"},
    {"name": "backup:update", "resource": "backup", "action": "update", "description": "Update backup configuration"},
    {"name": "backup:delete", "resource": "backup", "action": "delete", "description": "Delete backups"},
    {"name": "backup:manage", "resource": "backup", "action": "manage", "description": "Full backup management"},
    {"name": "backup:restore", "resource": "backup", "action": "restore", "description": "Restore from backups"},
    
    # Project permissions
    {"name": "project:create", "resource": "project", "action": "create", "description": "Create projects"},
    {"name": "project:read", "resource": "project", "action": "read", "description": "View project details"},
    {"name": "project:update", "resource": "project", "action": "update", "description": "Update project settings"},
    {"name": "project:delete", "resource": "project", "action": "delete", "description": "Delete projects"},
    {"name": "project:manage", "resource": "project", "action": "manage", "description": "Full project management"},
    
    # Group permissions
    {"name": "group:create", "resource": "group", "action": "create", "description": "Create groups"},
    {"name": "group:read", "resource": "group", "action": "read", "description": "View group details"},
    {"name": "group:update", "resource": "group", "action": "update", "description": "Update group settings"},
    {"name": "group:delete", "resource": "group", "action": "delete", "description": "Delete groups"},
    {"name": "group:manage", "resource": "group", "action": "manage", "description": "Full group management"},
    
    # Role permissions
    {"name": "role:create", "resource": "role", "action": "create", "description": "Create roles"},
    {"name": "role:read", "resource": "role", "action": "read", "description": "View role details"},
    {"name": "role:update", "resource": "role", "action": "update", "description": "Update role settings"},
    {"name": "role:delete", "resource": "role", "action": "delete", "description": "Delete roles"},
    {"name": "role:manage", "resource": "role", "action": "manage", "description": "Full role management"},
    
    # Permission permissions
    {"name": "permission:create", "resource": "permission", "action": "create", "description": "Create permissions"},
    {"name": "permission:read", "resource": "permission", "action": "read", "description": "View permission details"},
    {"name": "permission:update", "resource": "permission", "action": "update", "description": "Update permissions"},
    {"name": "permission:delete", "resource": "permission", "action": "delete", "description": "Delete permissions"},
    {"name": "permission:manage", "resource": "permission", "action": "manage", "description": "Full permission management"},
    
    # Organization permissions
    {"name": "organization:create", "resource": "organization", "action": "create", "description": "Create organizations"},
    {"name": "organization:read", "resource": "organization", "action": "read", "description": "View organization details"},
    {"name": "organization:update", "resource": "organization", "action": "update", "description": "Update organization settings"},
    {"name": "organization:delete", "resource": "organization", "action": "delete", "description": "Delete organizations"},
    {"name": "organization:manage", "resource": "organization", "action": "manage", "description": "Full organization management"},
    
    # Settings permissions
    {"name": "settings:read", "resource": "settings", "action": "read", "description": "View system settings"},
    {"name": "settings:update", "resource": "settings", "action": "update", "description": "Update system settings"},
    {"name": "settings:manage", "resource": "settings", "action": "manage", "description": "Full settings management"},
    
    # Dashboard permissions
    {"name": "dashboard:read", "resource": "dashboard", "action": "read", "description": "View dashboard"},
    {"name": "dashboard:manage", "resource": "dashboard", "action": "manage", "description": "Manage dashboard"},
    
    # Statistics permissions
    {"name": "statistics:read", "resource": "statistics", "action": "read", "description": "View statistics"},
    {"name": "statistics:manage", "resource": "statistics", "action": "manage", "description": "Manage statistics"},
    
    # Observability permissions
    {"name": "observability:read", "resource": "observability", "action": "read", "description": "View observability data"},
    {"name": "observability:manage", "resource": "observability", "action": "manage", "description": "Manage observability"},
    
    # System permissions
    {"name": "system:read", "resource": "system", "action": "read", "description": "View system information"},
    {"name": "system:update", "resource": "system", "action": "update", "description": "Update system configuration"},
    {"name": "system:manage", "resource": "system", "action": "manage", "description": "Full system management"},
    {"name": "system:admin", "resource": "system", "action": "admin", "description": "System administration"},
    
    # Wildcard permissions
    {"name": "admin:*", "resource": "admin", "action": "*", "description": "Admin wildcard - all admin permissions"},
    {"name": "*:*", "resource": "*", "action": "*", "description": "Global wildcard - all permissions"},
]


# Define system roles with their permissions
SYSTEM_ROLES = {
    "PROVIDER_ADMIN": {
        "description": "Global system administrator with full access to all resources",
        "permissions": ["*:*"]  # All permissions
    },
    "TENANT_ADMIN": {
        "description": "Tenant administrator with full access to tenant resources",
        "permissions": [
            "user:*", "vm:*", "container:*", "storage:*", "network:*",
            "firewall:*", "backup:*", "project:*", "group:*",
            "dashboard:read", "statistics:read", "tenant:read", "tenant:update"
        ]
    },
    "TENANT_MANAGER": {
        "description": "Tenant manager with resource management permissions",
        "permissions": [
            "user:read",
            "vm:*", "container:*", "storage:*", "network:*", "firewall:*",
            "backup:create", "backup:read", "backup:restore",
            "project:read", "group:read",
            "dashboard:read", "statistics:read"
        ]
    },
    "TENANT_USER": {
        "description": "Tenant user with read-only access",
        "permissions": [
            "user:read",
            "vm:read", "container:read", "storage:read", "network:read",
            "firewall:read", "backup:read",
            "project:read", "group:read",
            "dashboard:read", "statistics:read"
        ]
    }
}


async def seed_permissions(db: AsyncSession):
    """Seed all permissions into the database."""
    print("Seeding permissions...")
    
    created_count = 0
    existing_count = 0
    
    for perm_data in PERMISSIONS:
        # Check if permission already exists
        result = await db.execute(
            select(Permission).where(Permission.name == perm_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            permission = Permission(
                id=str(uuid4()),
                **perm_data
            )
            db.add(permission)
            created_count += 1
        else:
            existing_count += 1
    
    await db.commit()
    print(f"✓ Permissions: {created_count} created, {existing_count} already existed")
    return created_count


async def seed_roles(db: AsyncSession):
    """Seed system roles and associate them with permissions."""
    print("\nSeeding system roles...")
    
    created_count = 0
    updated_count = 0
    
    for role_name, role_data in SYSTEM_ROLES.items():
        # Check if role already exists
        result = await db.execute(
            select(Role).where(Role.name == role_name, Role.is_system_role == True)
        )
        role = result.scalar_one_or_none()
        
        if not role:
            role = Role(
                id=str(uuid4()),
                name=role_name,
                description=role_data["description"],
                is_system_role=True,
                tenant_id=None  # System roles are not tenant-specific
            )
            db.add(role)
            created_count += 1
        else:
            role.description = role_data["description"]
            updated_count += 1
        
        # Clear existing permissions
        role.permissions.clear()
        
        # Add permissions to role
        for perm_pattern in role_data["permissions"]:
            if perm_pattern.endswith(":*"):
                # Wildcard permission - add all permissions for this resource
                resource = perm_pattern.split(":")[0]
                result = await db.execute(
                    select(Permission).where(Permission.resource == resource)
                )
                permissions = result.scalars().all()
                for perm in permissions:
                    role.permissions.append(perm)
            else:
                # Specific permission
                result = await db.execute(
                    select(Permission).where(Permission.name == perm_pattern)
                )
                perm = result.scalar_one_or_none()
                if perm:
                    role.permissions.append(perm)
        
        print(f"  ✓ {role_name}: {len(role.permissions)} permissions assigned")
    
    await db.commit()
    print(f"\n✓ Roles: {created_count} created, {updated_count} updated")
    return created_count


async def main():
    """Main seed function."""
    print("=" * 60)
    print("RBAC Permission and Role Seeding")
    print("=" * 60)
    
    async with engine.begin() as conn:
        # Create tables if they don't exist
        from pcm.core.database.base import Base
        await conn.run_sync(Base.metadata.create_all)
    
    # Get database session
    async for db in get_db():
        try:
            # Seed permissions
            perm_count = await seed_permissions(db)
            
            # Seed roles
            role_count = await seed_roles(db)
            
            print("\n" + "=" * 60)
            print("✓ Seeding completed successfully!")
            print(f"  Total permissions: {len(PERMISSIONS)}")
            print(f"  Total system roles: {len(SYSTEM_ROLES)}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
        break  # Only need one iteration


if __name__ == "__main__":
    asyncio.run(main())
