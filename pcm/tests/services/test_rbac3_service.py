"""
Tests for RBAC3 hybrid authentication and authorization service.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, AsyncMock, patch

from pcm.services.rbac3_service import RBAC3Service, RBAC3ServiceError
from pcm.services.ldap_service import LDAPService, LDAPAuthenticationError
from pcm.core.models.user import User
from pcm.core.models.permission import Role, Permission


@pytest.fixture
def mock_ldap_service():
    """Create a mock LDAP service."""
    service = Mock(spec=LDAPService)
    return service


@pytest.fixture
async def rbac3_service(db_session: AsyncSession, mock_ldap_service):
    """Create RBAC3 service instance."""
    return RBAC3Service(db_session, mock_ldap_service)


@pytest.mark.asyncio
async def test_authenticate_user_local_success(rbac3_service: RBAC3Service, db_session: AsyncSession):
    """Test successful local authentication."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$test_hash",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # Mock password verification
    with patch.object(user, 'verify_password', return_value=True):
        success, authenticated_user, error = await rbac3_service.authenticate_user(
            "test@example.com",
            "password123",
            use_ldap=False
        )
    
    assert success is True
    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"
    assert error is None


@pytest.mark.asyncio
async def test_authenticate_user_local_invalid_credentials(rbac3_service: RBAC3Service):
    """Test local authentication with invalid credentials."""
    success, user, error = await rbac3_service.authenticate_user(
        "nonexistent@example.com",
        "password123",
        use_ldap=False
    )
    
    assert success is False
    assert user is None
    assert error is not None


@pytest.mark.asyncio
async def test_authenticate_user_ldap_success(rbac3_service: RBAC3Service, db_session: AsyncSession, mock_ldap_service):
    """Test successful LDAP authentication."""
    from pcm.services.ldap_service import LDAPUser
    
    # Mock LDAP user
    ldap_user = LDAPUser(
        username="ldapuser",
        email="ldap@example.com",
        full_name="LDAP User",
        distinguished_name="cn=ldapuser,dc=example,dc=com",
        groups=["admin", "developers"],
        attributes={}
    )
    
    # Mock LDAP service
    rbac3_service.ldap_service.authenticate_user = AsyncMock(return_value=(True, ldap_user))
    
    success, user, error = await rbac3_service.authenticate_user(
        "ldapuser",
        "password123",
        use_ldap=True
    )
    
    assert success is True
    assert user is not None
    assert user.email == "ldap@example.com"
    assert error is None


@pytest.mark.asyncio
async def test_authenticate_user_ldap_failure(rbac3_service: RBAC3Service, mock_ldap_service):
    """Test failed LDAP authentication."""
    # Mock LDAP service to raise error
    rbac3_service.ldap_service.authenticate_user = AsyncMock(
        side_effect=LDAPAuthenticationError("Invalid credentials")
    )
    
    success, user, error = await rbac3_service.authenticate_user(
        "ldapuser",
        "wrongpassword",
        use_ldap=True
    )
    
    assert success is False
    assert user is None
    assert error is not None


@pytest.mark.asyncio
async def test_authorize_user_with_permission(rbac3_service: RBAC3Service, db_session: AsyncSession):
    """Test user authorization with required permission."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$test_hash",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # Create permission
    permission = Permission(
        name="vm:create",
        resource="vm",
        action="create",
        description="Create virtual machines"
    )
    db_session.add(permission)
    await db_session.flush()
    
    # Create role with permission
    role = Role(
        name="admin",
        description="Administrator",
        is_system_role=True
    )
    role.permissions.append(permission)
    db_session.add(role)
    await db_session.flush()
    
    # Assign role to user
    user.roles.append(role)
    await db_session.flush()
    
    # Mock get_user_permissions to return the permission
    with patch.object(rbac3_service.user_role_service, 'get_user_permissions', 
                     return_value=[permission]):
        authorized = await rbac3_service.authorize_user(user, "vm:create")
    
    assert authorized is True


@pytest.mark.asyncio
async def test_authorize_user_without_permission(rbac3_service: RBAC3Service, db_session: AsyncSession):
    """Test user authorization without required permission."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$test_hash",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # Mock get_user_permissions to return empty list
    with patch.object(rbac3_service.user_role_service, 'get_user_permissions', 
                     return_value=[]):
        authorized = await rbac3_service.authorize_user(user, "vm:create")
    
    assert authorized is False


@pytest.mark.asyncio
async def test_get_user_permissions(rbac3_service: RBAC3Service, db_session: AsyncSession):
    """Test getting user permissions."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$test_hash",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # Create permissions
    permissions = [
        Permission(name="vm:create", resource="vm", action="create"),
        Permission(name="vm:delete", resource="vm", action="delete"),
        Permission(name="backup:restore", resource="backup", action="restore")
    ]
    for perm in permissions:
        db_session.add(perm)
    await db_session.flush()
    
    # Mock get_user_permissions
    with patch.object(rbac3_service.user_role_service, 'get_user_permissions', 
                     return_value=permissions):
        user_permissions = await rbac3_service.get_user_permissions(user)
    
    assert len(user_permissions) == 3
    assert "vm:create" in user_permissions
    assert "vm:delete" in user_permissions
    assert "backup:restore" in user_permissions


@pytest.mark.asyncio
async def test_get_user_roles(rbac3_service: RBAC3Service, db_session: AsyncSession):
    """Test getting user roles."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$test_hash",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # Create roles
    roles = [
        Role(name="admin", description="Administrator", is_system_role=True),
        Role(name="tenant_admin", description="Tenant Admin", is_system_role=True)
    ]
    for role in roles:
        db_session.add(role)
    await db_session.flush()
    
    # Mock get_user_roles
    with patch.object(rbac3_service.user_role_service, 'get_user_roles', 
                     return_value=roles):
        user_roles = await rbac3_service.get_user_roles(user)
    
    assert len(user_roles) == 2
    assert "admin" in user_roles
    assert "tenant_admin" in user_roles


@pytest.mark.asyncio
async def test_assign_role_to_user(rbac3_service: RBAC3Service, db_session: AsyncSession):
    """Test assigning role to user."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$test_hash",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # Create role
    role = Role(
        name="admin",
        description="Administrator",
        is_system_role=True
    )
    db_session.add(role)
    await db_session.flush()
    
    # Mock assign_role_to_user
    with patch.object(rbac3_service.user_role_service, 'assign_role_to_user', 
                     return_value=None):
        success = await rbac3_service.assign_role_to_user(user, "admin")
    
    assert success is True


@pytest.mark.asyncio
async def test_assign_nonexistent_role_to_user(rbac3_service: RBAC3Service, db_session: AsyncSession):
    """Test assigning nonexistent role to user."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$test_hash",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # Try to assign nonexistent role
    success = await rbac3_service.assign_role_to_user(user, "nonexistent_role")
    
    assert success is False


@pytest.mark.asyncio
async def test_initialize_default_roles(rbac3_service: RBAC3Service, db_session: AsyncSession):
    """Test initializing default roles."""
    success = await rbac3_service.initialize_default_roles()
    
    assert success is True
    
    # Verify roles were created
    from sqlalchemy import select
    result = await db_session.execute(select(Role))
    roles = result.scalars().all()
    
    role_names = [r.name for r in roles]
    assert "admin" in role_names
    assert "tenant_admin" in role_names
    assert "tenant_manager" in role_names
    assert "tenant_user" in role_names
