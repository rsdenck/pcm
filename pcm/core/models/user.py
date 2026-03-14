from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from typing import List
from pcm.core.database.base import Base


class UserRole(str, Enum):
    PROVIDER_ADMIN = "provider_admin"
    TENANT_ADMIN = "tenant_admin"
    TENANT_USER = "tenant_user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False), 
        default=UserRole.TENANT_USER, 
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Account security
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Permissions cache (JSON for quick access)
    permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # LDAP integration
    ldap_dn: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    ldap_groups: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    is_ldap_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_ldap_sync: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    tenant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    roles: Mapped[List["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users"
    )
    groups: Mapped[List["Group"]] = relationship(
        secondary="user_groups",
        back_populates="users"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(r.name == role_name for r in self.roles)
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission through their roles."""
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        return False
    
    def get_all_permissions(self) -> List[str]:
        """Get all permission names from all roles."""
        permissions = set()
        for role in self.roles:
            permissions.update(role.get_permission_names())
        return list(permissions)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hashed password."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(password, self.hashed_password)
