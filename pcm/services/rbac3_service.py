"""
RBAC3 Hybrid authentication and authorization service.

This module implements a hybrid RBAC system that supports both:
- Local authentication (database-based users)
- LDAP authentication (for admin users)

The system provides role-based access control with granular permissions.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from pcm.core.models.user import User
from pcm.core.models.permission import Role, Permission
from pcm.services.permission_service import UserRoleService, PermissionService
from pcm.services.ldap_service import LDAPService, LDAPAuthenticationError

logger = logging.getLogger(__name__)


class RBAC3ServiceError(Exception):
    """Base exception for RBAC3 service errors."""
    pass


class RBAC3Service:
    """
    RBAC3 Hybrid authentication and authorization service.
    
    Provides:
    - Hybrid authentication (local + LDAP)
    - Role-based access control
    - Permission management
    - User role assignment
    - Audit logging
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        ldap_service: Optional[LDAPService] = None
    ):
        """
        Initialize RBAC3 service.
        
        Args:
            db_session: Database session
            ldap_service: Optional LDAP service for admin authentication
        """
        self.db_session = db_session
        self.ldap_service = ldap_service
        self.user_role_service = UserRoleService(db_session)
        self.permission_service = PermissionService(db_session)
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        use_ldap: bool = False
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate a user using local or LDAP authentication.
        
        Args:
            username: Username or email
            password: Password
            use_ldap: Whether to use LDAP authentication
            
        Returns:
            Tuple of (success, user, error_message)
        """
        try:
            if use_ldap and self.ldap_service:
                return await self._authenticate_ldap(username, password)
            else:
                return await self._authenticate_local(username, password)
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None, str(e)
    
    async def _authenticate_local(
        self,
        username: str,
        password: str
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate user against local database.
        
        Args:
            username: Username or email
            password: Password
            
        Returns:
            Tuple of (success, user, error_message)
        """
        try:
            # Search for user by email or username
            query = select(User).where(
                (User.email == username) | (User.username == username)
            )
            result = await self.db_session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"User not found: {username}")
                return False, None, "Invalid credentials"
            
            # Verify password
            if not user.verify_password(password):
                logger.warning(f"Invalid password for user: {username}")
                return False, None, "Invalid credentials"
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"User is inactive: {username}")
                return False, None, "User account is inactive"
            
            logger.info(f"Successfully authenticated user: {username}")
            return True, user, None
        
        except Exception as e:
            logger.error(f"Error authenticating user locally: {e}")
            return False, None, "Authentication error"
    
    async def _authenticate_ldap(
        self,
        username: str,
        password: str
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate user against LDAP server.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, user, error_message)
        """
        try:
            if not self.ldap_service:
                return False, None, "LDAP service not configured"
            
            # Authenticate against LDAP
            success, ldap_user = self.ldap_service.authenticate_user(username, password)
            
            if not success:
                logger.warning(f"LDAP authentication failed for user: {username}")
                return False, None, "Invalid LDAP credentials"
            
            # Find or create user in database
            query = select(User).where(User.email == ldap_user.email)
            result = await self.db_session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                # Create new user from LDAP
                user = User(
                    username=ldap_user.username,
                    email=ldap_user.email,
                    full_name=ldap_user.full_name,
                    is_active=True,
                    ldap_dn=ldap_user.distinguished_name,
                    ldap_groups=ldap_user.groups
                )
                self.db_session.add(user)
                await self.db_session.flush()
                
                # Assign admin role to LDAP users
                admin_role = await self._get_or_create_admin_role()
                if admin_role:
                    await self.user_role_service.assign_role_to_user(
                        self.db_session,
                        user.id,
                        admin_role.id
                    )
                
                logger.info(f"Created new LDAP user: {username}")
            else:
                # Update user info from LDAP
                user.full_name = ldap_user.full_name
                user.ldap_dn = ldap_user.distinguished_name
                user.ldap_groups = ldap_user.groups
                user.updated_at = datetime.utcnow()
            
            await self.db_session.flush()
            logger.info(f"Successfully authenticated LDAP user: {username}")
            return True, user, None
        
        except LDAPAuthenticationError as e:
            logger.warning(f"LDAP authentication error: {e}")
            return False, None, str(e)
        except Exception as e:
            logger.error(f"Error authenticating user via LDAP: {e}")
            return False, None, "LDAP authentication error"
    
    async def authorize_user(
        self,
        user: User,
        required_permission: str,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Check if user has required permission.
        
        Args:
            user: User to check
            required_permission: Permission name (e.g., 'vm:create')
            resource_id: Optional resource ID for tenant-specific checks
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            # Get user permissions
            permissions = await self.user_role_service.get_user_permissions(
                self.db_session,
                user.id
            )
            
            # Check if user has required permission
            has_permission = any(p.name == required_permission for p in permissions)
            
            if has_permission:
                logger.debug(f"User {user.id} authorized for {required_permission}")
                return True
            
            logger.warning(f"User {user.id} not authorized for {required_permission}")
            return False
        
        except Exception as e:
            logger.error(f"Error checking authorization: {e}")
            return False
    
    async def get_user_permissions(self, user: User) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            user: User to get permissions for
            
        Returns:
            List of permission names
        """
        try:
            permissions = await self.user_role_service.get_user_permissions(
                self.db_session,
                user.id
            )
            return [p.name for p in permissions]
        
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []
    
    async def get_user_roles(self, user: User) -> List[str]:
        """
        Get all roles for a user.
        
        Args:
            user: User to get roles for
            
        Returns:
            List of role names
        """
        try:
            roles = await self.user_role_service.get_user_roles(
                self.db_session,
                user.id
            )
            return [r.name for r in roles]
        
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return []
    
    async def assign_role_to_user(
        self,
        user: User,
        role_name: str
    ) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user: User to assign role to
            role_name: Role name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get role
            query = select(Role).where(Role.name == role_name)
            result = await self.db_session.execute(query)
            role = result.scalar_one_or_none()
            
            if not role:
                logger.error(f"Role not found: {role_name}")
                return False
            
            # Assign role
            await self.user_role_service.assign_role_to_user(
                self.db_session,
                user.id,
                role.id
            )
            
            logger.info(f"Assigned role {role_name} to user {user.id}")
            return True
        
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            return False
    
    async def _get_or_create_admin_role(self) -> Optional[Role]:
        """
        Get or create the admin role.
        
        Returns:
            Admin role or None
        """
        try:
            query = select(Role).where(Role.name == "admin")
            result = await self.db_session.execute(query)
            role = result.scalar_one_or_none()
            
            if not role:
                # Create admin role
                role = Role(
                    name="admin",
                    description="Administrator role with full permissions",
                    is_system_role=True
                )
                self.db_session.add(role)
                await self.db_session.flush()
                logger.info("Created admin role")
            
            return role
        
        except Exception as e:
            logger.error(f"Error getting/creating admin role: {e}")
            return None
    
    async def initialize_default_roles(self) -> bool:
        """
        Initialize default system roles.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            default_roles = [
                {
                    "name": "admin",
                    "description": "Administrator with full system access",
                    "is_system_role": True
                },
                {
                    "name": "tenant_admin",
                    "description": "Tenant administrator with tenant-level access",
                    "is_system_role": True
                },
                {
                    "name": "tenant_manager",
                    "description": "Tenant manager with resource management access",
                    "is_system_role": True
                },
                {
                    "name": "tenant_user",
                    "description": "Tenant user with read-only access",
                    "is_system_role": True
                }
            ]
            
            for role_data in default_roles:
                query = select(Role).where(Role.name == role_data["name"])
                result = await self.db_session.execute(query)
                existing_role = result.scalar_one_or_none()
                
                if not existing_role:
                    role = Role(**role_data)
                    self.db_session.add(role)
                    logger.info(f"Created default role: {role_data['name']}")
            
            await self.db_session.flush()
            return True
        
        except Exception as e:
            logger.error(f"Error initializing default roles: {e}")
            return False
