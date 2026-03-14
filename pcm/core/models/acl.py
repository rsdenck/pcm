"""
ACL (Access Control List) Model
Provides fine-grained access control for specific resources
"""
from sqlalchemy import String, DateTime, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from uuid import uuid4
from pcm.core.database.base import Base


class ACLEntry(Base):
    """
    ACL Entry model for fine-grained resource access control.
    
    Allows or denies specific principals (users, groups, roles) access to specific resources.
    """
    __tablename__ = "acl_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Resource information
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    # Principal (who gets access)
    principal_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'user', 'group', 'role'
    principal_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    # Permission
    permission: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., 'read', 'write', 'delete'
    
    # Allow or deny
    allow: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_acl_resource', 'resource_type', 'resource_id'),
        Index('idx_acl_principal', 'principal_type', 'principal_id'),
        Index('idx_acl_lookup', 'resource_type', 'resource_id', 'principal_type', 'principal_id'),
    )

    def __repr__(self) -> str:
        action = "ALLOW" if self.allow else "DENY"
        return f"<ACLEntry({action} {self.principal_type}:{self.principal_id} {self.permission} on {self.resource_type}:{self.resource_id})>"
