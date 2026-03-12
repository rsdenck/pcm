from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from pcm.core.database.base import Base


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackupJob(Base):
    """
    Backup Job model for tracking individual backup executions.
    
    Represents a single execution instance of a backup policy, tracking
    progress, status, and results of backup operations.
    """
    __tablename__ = "backup_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Policy relationship
    policy_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("backup_policies.id", ondelete="CASCADE"), nullable=False
    )
    
    # Tenant isolation
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    
    # Job execution details
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, native_enum=False), 
        default=JobStatus.PENDING, 
        nullable=False
    )
    
    # Timing information
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Progress tracking
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    
    # Results and statistics
    backup_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # bytes
    transferred_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # bytes
    
    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    policy: Mapped["BackupPolicy"] = relationship(back_populates="backup_jobs")
    tenant: Mapped["Tenant"] = relationship()
    snapshots: Mapped[list["BackupSnapshot"]] = relationship(
        back_populates="job", 
        cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        """Initialize BackupJob with proper defaults."""
        # Set defaults for fields that might not be set by SQLAlchemy in tests
        if 'status' not in kwargs:
            kwargs['status'] = JobStatus.PENDING
        if 'progress' not in kwargs:
            kwargs['progress'] = 0
        if 'retry_count' not in kwargs:
            kwargs['retry_count'] = 0
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
        
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<BackupJob(id={self.id}, policy_id={self.policy_id}, status={self.status})>"