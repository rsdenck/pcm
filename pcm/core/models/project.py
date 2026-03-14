"""
Project Model
Represents a project within a tenant for resource organization
"""
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from pcm.core.database.base import Base


class Project(Base):
    """
    Project model - organizational unit within a tenant.
    Used to group resources like VMs, networks, etc.
    """
    __tablename__ = "projects"

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
    tenant: Mapped["Tenant"] = relationship(back_populates="projects")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"
