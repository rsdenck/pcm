from sqlalchemy import String, Boolean, DateTime, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from pcm.core.database.base import Base


class StorageType(str, Enum):
    DIR = "dir"
    LVM = "lvm"
    LVMTHIN = "lvmthin"
    ZFS = "zfs"
    CEPH = "ceph"
    NFS = "nfs"
    CIFS = "cifs"


class StorageStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class Storage(Base):
    __tablename__ = "storage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    storage_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    storage_type: Mapped[StorageType] = mapped_column(
        SQLEnum(StorageType, native_enum=False), 
        nullable=False
    )
    status: Mapped[StorageStatus] = mapped_column(
        SQLEnum(StorageStatus, native_enum=False), 
        default=StorageStatus.UNKNOWN, 
        nullable=False
    )
    
    total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    available: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    cluster_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("proxmox_clusters.id", ondelete="CASCADE"), nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    cluster: Mapped["ProxmoxCluster"] = relationship(back_populates="storage")

    def __repr__(self) -> str:
        return f"<Storage(id={self.id}, name={self.name}, type={self.storage_type})>"
