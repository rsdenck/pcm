"""Authentication and authorization middleware for FastAPI."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from typing import Optional, Callable, Any
from functools import wraps
import jwt
from pcm.core.config import settings
from pcm.services.permission_service import UserRoleService, AuditLogService
from sqlalchemy.ext.asyncio import AsyncSession


security = HTTPBearer()


class AuthMiddleware:
    """Middleware for handling JWT authentication."""

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    @staticmethod
    async def get_current_user(request: Request) -> dict:
        """Extract and verify current user from request."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )

        return AuthMiddleware.verify_token(token)

    @staticmethod
    async def get_current_user_id(request: Request) -> str:
        """Get current user ID from request."""
        user_data = await AuthMiddleware.get_current_user(request)
        return user_data.get("sub")

    @staticmethod
    async def get_current_tenant_id(request: Request) -> str:
        """Get current tenant ID from request."""
        user_data = await AuthMiddleware.get_current_user(request)
        return user_data.get("tenant_id")


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Any:
        try:
            user_data = await AuthMiddleware.get_current_user(request)
            request.state.user = user_data
            return await func(request, *args, **kwargs)
        except HTTPException:
            raise
    return wrapper


def require_permission(permission: str) -> Callable:
    """Decorator to require specific permission."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            request: Request,
            session: AsyncSession,
            *args,
            **kwargs
        ) -> Any:
            try:
                user_data = await AuthMiddleware.get_current_user(request)
                user_id = user_data.get("sub")
                tenant_id = user_data.get("tenant_id")

                # Check if user has permission
                has_permission = await UserRoleService.user_has_permission(
                    session, user_id, permission
                )

                if not has_permission:
                    # Log denied access
                    await AuditLogService.log_action(
                        session,
                        user_id=user_id,
                        tenant_id=tenant_id,
                        action=f"access_denied_{permission}",
                        resource_type="permission",
                        status="denied",
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent")
                    )
                    await session.commit()

                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied: {permission}"
                    )

                request.state.user = user_data
                return await func(request, session, *args, **kwargs)
            except HTTPException:
                raise
        return wrapper
    return decorator


def require_role(role: str) -> Callable:
    """Decorator to require specific role."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            request: Request,
            session: AsyncSession,
            *args,
            **kwargs
        ) -> Any:
            try:
                user_data = await AuthMiddleware.get_current_user(request)
                user_roles = user_data.get("roles", [])
                tenant_id = user_data.get("tenant_id")

                if role not in user_roles:
                    # Log denied access
                    await AuditLogService.log_action(
                        session,
                        user_id=user_data.get("sub"),
                        tenant_id=tenant_id,
                        action=f"access_denied_role_{role}",
                        resource_type="role",
                        status="denied",
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent")
                    )
                    await session.commit()

                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role required: {role}"
                    )

                request.state.user = user_data
                return await func(request, session, *args, **kwargs)
            except HTTPException:
                raise
        return wrapper
    return decorator


def require_tenant_access(func: Callable) -> Callable:
    """Decorator to require tenant access."""
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession,
        tenant_id: str,
        *args,
        **kwargs
    ) -> Any:
        try:
            user_data = await AuthMiddleware.get_current_user(request)
            user_tenant_id = user_data.get("tenant_id")
            user_id = user_data.get("sub")
            is_superuser = user_data.get("is_superuser", False)

            # Superusers can access any tenant
            if not is_superuser and user_tenant_id != tenant_id:
                # Log denied access
                await AuditLogService.log_action(
                    session,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    action="access_denied_tenant",
                    resource_type="tenant",
                    resource_id=tenant_id,
                    status="denied",
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent")
                )
                await session.commit()

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this tenant"
                )

            request.state.user = user_data
            return await func(request, session, tenant_id, *args, **kwargs)
        except HTTPException:
            raise
    return wrapper

