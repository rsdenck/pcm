from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from pcm.core.database.base import Base


class ClusterType(str, Enum):
    PVE = "pve"
    PBS = "pbs"
    PMG = "pmg"


class ClusterStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class ProxmoxCluster(Base):
    __tablename__ = "proxmox_clusters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=8006, nullable=False)
    
    cluster_type: Mapped[ClusterType] = mapped_column(
        SQLEnum(ClusterType, native_enum=False), 
        default=ClusterType.PVE, 
        nullable=False
    )
    status: Mapped[ClusterStatus] = mapped_column(
        SQLEnum(ClusterStatus, native_enum=False), 
        default=ClusterStatus.OFFLINE, 
        nullable=False
    )
    
    api_token_id: Mapped[str] = mapped_column(String(255), nullable=False)
    api_token_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    
    verify_ssl: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_sync: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="clusters")
    nodes: Mapped[list["ProxmoxNode"]] = relationship(back_populates="cluster", cascade="all, delete-orphan")
    storage: Mapped[list["Storage"]] = relationship(back_populates="cluster", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ProxmoxCluster(id={self.id}, name={self.name}, type={self.cluster_type})>"


class ProxmoxNode(Base):
    __tablename__ = "proxmox_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    node_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="unknown", nullable=False)
    uptime: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    cpu_cores: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cpu_usage: Mapped[float | None] = mapped_column(nullable=True)
    
    memory_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    storage_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    cluster_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("proxmox_clusters.id", ondelete="CASCADE"), nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    cluster: Mapped["ProxmoxCluster"] = relationship(back_populates="nodes")
    vms: Mapped[list["VirtualMachine"]] = relationship(back_populates="node", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ProxmoxNode(id={self.id}, name={self.name}, status={self.status})>"
