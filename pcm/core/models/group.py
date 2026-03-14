"""
Group Model
Represents a group of users within a tenant
"""
from sqlalchemy import String, DateTime, Text, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from typing import List
from pcm.core.database.base import Base


# Association table for user-group many-to-many relationship
user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', String(36), ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
)


class Group(Base):
    """
    Group model - collection of users within a tenant.
    Used for bulk permission assignment and organization.
    """
    __tablename__ = "groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="groups")
    users: Mapped[List["User"]] = relationship(
        secondary=user_groups,
        back_populates="groups"
    )

    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"
