"""Tests for authentication middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from pcm.services.api.middleware.auth_middleware import (
    AuthMiddleware,
    require_auth,
    require_permission,
    require_role,
    require_tenant_access
)
import jwt
from datetime import datetime, timedelta


@pytest.fixture
def valid_token():
    """Create a valid JWT token."""
    payload = {
        "sub": "user-123",
        "email": "test@example.com",
        "tenant_id": "tenant-123",
        "roles": ["tenant_user"],
        "is_superuser": False,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    from pcm.core.config import settings
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token


@pytest.fixture
def expired_token():
    """Create an expired JWT token."""
    payload = {
        "sub": "user-123",
        "email": "test@example.com",
        "tenant_id": "tenant-123",
        "roles": ["tenant_user"],
        "is_superuser": False,
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    from pcm.core.config import settings
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token


@pytest.fixture
def mock_request(valid_token):
    """Create a mock request with valid token."""
    request = MagicMock()
    request.headers = {"Authorization": f"Bearer {valid_token}"}
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    return request


class TestAuthMiddleware:
    """Test AuthMiddleware class."""

    def test_verify_token_valid(self, valid_token):
        """Test verifying a valid token."""
        payload = AuthMiddleware.verify_token(valid_token)
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"
        assert payload["tenant_id"] == "tenant-123"

    def test_verify_token_expired(self, expired_token):
        """Test verifying an expired token."""
        with pytest.raises(HTTPException) as exc_info:
            AuthMiddleware.verify_token(expired_token)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in exc_info.value.detail.lower()

    def test_verify_token_invalid(self):
        """Test verifying an invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            AuthMiddleware.verify_token("invalid-token")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_valid(self, mock_request):
        """Test getting current user with valid token."""
        user_data = await AuthMiddleware.get_current_user(mock_request)
        assert user_data["sub"] == "user-123"
        assert user_data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_missing_header(self):
        """Test getting current user without authorization header."""
        request = MagicMock()
        request.headers = {}
        with pytest.raises(HTTPException) as exc_info:
            await AuthMiddleware.get_current_user(request)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_scheme(self):
        """Test getting current user with invalid scheme."""
        request = MagicMock()
        request.headers = {"Authorization": "Basic invalid"}
        with pytest.raises(HTTPException) as exc_info:
            await AuthMiddleware.get_current_user(request)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_id(self, mock_request):
        """Test getting current user ID."""
        user_id = await AuthMiddleware.get_current_user_id(mock_request)
        assert user_id == "user-123"

    @pytest.mark.asyncio
    async def test_get_current_tenant_id(self, mock_request):
        """Test getting current tenant ID."""
        tenant_id = await AuthMiddleware.get_current_tenant_id(mock_request)
        assert tenant_id == "tenant-123"


class TestRequireAuthDecorator:
    """Test require_auth decorator."""

    @pytest.mark.asyncio
    async def test_require_auth_with_valid_token(self, mock_request):
        """Test require_auth with valid token."""
        @require_auth
        async def test_func(request):
            return {"status": "ok"}

        result = await test_func(mock_request)
        assert result["status"] == "ok"
        assert hasattr(mock_request.state, "user")

    @pytest.mark.asyncio
    async def test_require_auth_without_token(self):
        """Test require_auth without token."""
        @require_auth
        async def test_func(request):
            return {"status": "ok"}

        request = MagicMock()
        request.headers = {}
        with pytest.raises(HTTPException):
            await test_func(request)


class TestRequirePermissionDecorator:
    """Test require_permission decorator."""

    @pytest.mark.asyncio
    async def test_require_permission_granted(self, mock_request):
        """Test require_permission when permission is granted."""
        @require_permission("vm:create")
        async def test_func(request, session):
            return {"status": "ok"}

        session = AsyncMock()
        with patch('pcm.services.permission_service.UserRoleService.user_has_permission', return_value=True):
            result = await test_func(mock_request, session)
            assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_require_permission_denied(self, mock_request):
        """Test require_permission when permission is denied."""
        @require_permission("vm:delete")
        async def test_func(request, session):
            return {"status": "ok"}

        session = AsyncMock()
        with patch('pcm.services.permission_service.UserRoleService.user_has_permission', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await test_func(mock_request, session)
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestRequireRoleDecorator:
    """Test require_role decorator."""

    @pytest.mark.asyncio
    async def test_require_role_granted(self, mock_request):
        """Test require_role when role is granted."""
        @require_role("tenant_admin")
        async def test_func(request, session):
            return {"status": "ok"}

        session = AsyncMock()
        mock_request.state = MagicMock()
        # Mock the user data to include the required role
        with patch('pcm.services.api.middleware.auth_middleware.AuthMiddleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "sub": "user-123",
                "roles": ["tenant_admin"],
                "tenant_id": "tenant-123"
            }
            result = await test_func(mock_request, session)
            assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_require_role_denied(self, mock_request):
        """Test require_role when role is denied."""
        @require_role("provider_admin")
        async def test_func(request, session):
            return {"status": "ok"}

        session = AsyncMock()
        with patch('pcm.services.api.middleware.auth_middleware.AuthMiddleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "sub": "user-123",
                "roles": ["tenant_user"],
                "tenant_id": "tenant-123"
            }
            with pytest.raises(HTTPException) as exc_info:
                await test_func(mock_request, session)
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestRequireTenantAccessDecorator:
    """Test require_tenant_access decorator."""

    @pytest.mark.asyncio
    async def test_require_tenant_access_granted(self, mock_request):
        """Test require_tenant_access when access is granted."""
        @require_tenant_access
        async def test_func(request, session, tenant_id):
            return {"status": "ok", "tenant_id": tenant_id}

        session = AsyncMock()
        with patch('pcm.services.api.middleware.auth_middleware.AuthMiddleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "sub": "user-123",
                "tenant_id": "tenant-123",
                "is_superuser": False
            }
            result = await test_func(mock_request, session, "tenant-123")
            assert result["status"] == "ok"
            assert result["tenant_id"] == "tenant-123"

    @pytest.mark.asyncio
    async def test_require_tenant_access_denied(self, mock_request):
        """Test require_tenant_access when access is denied."""
        @require_tenant_access
        async def test_func(request, session, tenant_id):
            return {"status": "ok"}

        session = AsyncMock()
        with patch('pcm.services.api.middleware.auth_middleware.AuthMiddleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "sub": "user-123",
                "tenant_id": "tenant-123",
                "is_superuser": False
            }
            with pytest.raises(HTTPException) as exc_info:
                await test_func(mock_request, session, "tenant-456")
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_require_tenant_access_superuser(self, mock_request):
        """Test require_tenant_access with superuser."""
        @require_tenant_access
        async def test_func(request, session, tenant_id):
            return {"status": "ok", "tenant_id": tenant_id}

        session = AsyncMock()
        with patch('pcm.services.api.middleware.auth_middleware.AuthMiddleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "sub": "user-123",
                "tenant_id": "tenant-123",
                "is_superuser": True
            }
            result = await test_func(mock_request, session, "tenant-456")
            assert result["status"] == "ok"
            assert result["tenant_id"] == "tenant-456"

