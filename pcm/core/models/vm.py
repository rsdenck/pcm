from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from pcm.core.database.base import Base


class VMType(str, Enum):
    QEMU = "qemu"
    LXC = "lxc"


class VMStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


class VirtualMachine(Base):
    __tablename__ = "virtual_machines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    vmid: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    vm_type: Mapped[VMType] = mapped_column(
        SQLEnum(VMType, native_enum=False), 
        default=VMType.QEMU, 
        nullable=False
    )
    status: Mapped[VMStatus] = mapped_column(
        SQLEnum(VMStatus, native_enum=False), 
        default=VMStatus.UNKNOWN, 
        nullable=False
    )
    
    cpu_cores: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cpu_usage: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    memory_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    disk_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    uptime: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("proxmox_nodes.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    node: Mapped["ProxmoxNode"] = relationship(back_populates="vms")
    tenant: Mapped["Tenant"] = relationship(back_populates="vms")

    def __repr__(self) -> str:
        return f"<VirtualMachine(id={self.id}, vmid={self.vmid}, name={self.name}, status={self.status})>"
