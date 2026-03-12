from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from pcm.core.database.base import Base


class DatastoreStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    FULL = "full"
    ERROR = "error"


class Datastore(Base):
    """
    PBS Datastore model for managing backup storage locations.
    
    Provides tenant isolation, capacity tracking, and monitoring for
    backup datastores on PBS servers. Each datastore can be assigned
    to specific tenants for complete data isolation.
    """
    __tablename__ = "datastores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # PBS server relationship
    pbs_server_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("pbs_servers.id", ondelete="CASCADE"), nullable=False
    )
    
    # Tenant isolation
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    
    # Storage configuration
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Capacity management (in bytes)
    total_capacity: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    used_capacity: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    available_capacity: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    
    # Threshold settings (percentages)
    warning_threshold: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    critical_threshold: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    
    # Status and monitoring
    status: Mapped[DatastoreStatus] = mapped_column(
        SQLEnum(DatastoreStatus, native_enum=False), 
        default=DatastoreStatus.ACTIVE, 
        nullable=False
    )
    last_capacity_check: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    capacity_check_interval: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)  # seconds
    
    # Performance metrics
    backup_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_backup: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Configuration options
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    compression_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deduplication_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Error tracking
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    pbs_server: Mapped["PBSServer"] = relationship(back_populates="datastores")
    tenant: Mapped["Tenant"] = relationship()
    snapshots: Mapped[list["BackupSnapshot"]] = relationship(
        back_populates="datastore", 
        cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        """Initialize Datastore with proper defaults."""
        # Set defaults for fields that might not be set by SQLAlchemy in tests
        if 'status' not in kwargs:
            kwargs['status'] = DatastoreStatus.ACTIVE
        if 'warning_threshold' not in kwargs:
            kwargs['warning_threshold'] = 80
        if 'critical_threshold' not in kwargs:
            kwargs['critical_threshold'] = 90
        if 'capacity_check_interval' not in kwargs:
            kwargs['capacity_check_interval'] = 3600
        if 'backup_count' not in kwargs:
            kwargs['backup_count'] = 0
        if 'is_encrypted' not in kwargs:
            kwargs['is_encrypted'] = False
        if 'compression_enabled' not in kwargs:
            kwargs['compression_enabled'] = True
        if 'deduplication_enabled' not in kwargs:
            kwargs['deduplication_enabled'] = True
        if 'error_count' not in kwargs:
            kwargs['error_count'] = 0
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.utcnow()
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = datetime.utcnow()
        
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Datastore(id={self.id}, name={self.name}, tenant_id={self.tenant_id}, status={self.status})>"

    @property
    def usage_percentage(self) -> float | None:
        """Calculate the current usage percentage of the datastore."""
        if self.total_capacity and self.used_capacity is not None:
            return (self.used_capacity / self.total_capacity) * 100
        return None

    @property
    def is_over_warning_threshold(self) -> bool:
        """Check if the datastore usage exceeds the warning threshold."""
        usage = self.usage_percentage
        return (usage is not None and 
                self.warning_threshold is not None and 
                usage >= self.warning_threshold)

    @property
    def is_over_critical_threshold(self) -> bool:
        """Check if the datastore usage exceeds the critical threshold."""
        usage = self.usage_percentage
        return (usage is not None and 
                self.critical_threshold is not None and 
                usage >= self.critical_threshold)

    @property
    def is_healthy(self) -> bool:
        """Check if the datastore is in a healthy state."""
        return (
            self.status == DatastoreStatus.ACTIVE and
            not self.is_over_critical_threshold
        )

    def update_capacity(self, total: int, used: int, available: int) -> None:
        """Update the capacity information for the datastore."""
        self.total_capacity = total
        self.used_capacity = used
        self.available_capacity = available
        self.last_capacity_check = datetime.utcnow()
        
        # Update status based on capacity (only if thresholds are set)
        if self.critical_threshold is not None and self.is_over_critical_threshold:
            self.status = DatastoreStatus.FULL
        elif self.status == DatastoreStatus.FULL and self.warning_threshold is not None and not self.is_over_warning_threshold:
            self.status = DatastoreStatus.ACTIVE

    def mark_error(self, error_message: str) -> None:
        """Mark the datastore as having an error."""
        self.status = DatastoreStatus.ERROR
        self.last_error = error_message
        if self.error_count is None:
            self.error_count = 0
        self.error_count += 1

    def clear_error(self) -> None:
        """Clear the error state and mark as active."""
        self.status = DatastoreStatus.ACTIVE
        self.last_error = None
        self.error_count = 0