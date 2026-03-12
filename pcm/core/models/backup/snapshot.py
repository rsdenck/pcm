from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from pcm.core.database.base import Base


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    SKIPPED = "skipped"


class BackupSnapshot(Base):
    """
    Backup Snapshot model for storing metadata about individual backup snapshots.
    
    Represents a single backup snapshot created by a backup job, including
    verification status, size information, and retention tracking.
    """
    __tablename__ = "backup_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Job relationship
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("backup_jobs.id", ondelete="CASCADE"), nullable=False
    )
    
    # Tenant isolation
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    
    # VM and target information
    vm_id: Mapped[str] = mapped_column(String(36), nullable=False)
    vm_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cluster_id: Mapped[str] = mapped_column(String(36), nullable=False)
    
    # Snapshot metadata
    snapshot_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    snapshot_name: Mapped[str] = mapped_column(String(255), nullable=False)
    snapshot_type: Mapped[str] = mapped_column(String(50), default="full", nullable=False)  # full, incremental
    
    # Storage information
    datastore_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("datastores.id", ondelete="CASCADE"), nullable=False
    )
    path: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # Size information (in bytes)
    size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    compressed_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    deduplicated_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    
    # Verification and integrity
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus, native_enum=False), 
        default=VerificationStatus.PENDING, 
        nullable=False
    )
    verification_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verification_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    
    # Retention management
    retention_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_protected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    protection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Backup configuration used
    encryption_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    compression_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Performance metrics
    backup_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # seconds
    transfer_rate: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # bytes per second
    
    # Error tracking
    has_errors: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    job: Mapped["BackupJob"] = relationship(back_populates="snapshots")
    datastore: Mapped["Datastore"] = relationship(back_populates="snapshots")
    tenant: Mapped["Tenant"] = relationship()

    def __init__(self, **kwargs):
        """Initialize BackupSnapshot with proper defaults."""
        # Set defaults for fields that might not be set by SQLAlchemy in tests
        if 'verification_status' not in kwargs:
            kwargs['verification_status'] = VerificationStatus.PENDING
        if 'snapshot_type' not in kwargs:
            kwargs['snapshot_type'] = "full"
        if 'is_protected' not in kwargs:
            kwargs['is_protected'] = False
        if 'encryption_enabled' not in kwargs:
            kwargs['encryption_enabled'] = False
        if 'has_errors' not in kwargs:
            kwargs['has_errors'] = False
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
        
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<BackupSnapshot(id={self.id}, job_id={self.job_id}, vm_id={self.vm_id}, snapshot_time={self.snapshot_time})>"

    @property
    def is_verified(self) -> bool:
        """Check if the snapshot has been successfully verified."""
        return self.verification_status == VerificationStatus.VERIFIED

    @property
    def is_expired(self) -> bool:
        """Check if the snapshot has passed its retention date."""
        if self.retention_date is None:
            return False
        return datetime.utcnow() > self.retention_date

    @property
    def can_be_deleted(self) -> bool:
        """Check if the snapshot can be safely deleted."""
        return self.is_expired and not self.is_protected

    @property
    def compression_ratio(self) -> float | None:
        """Calculate the compression ratio if both sizes are available."""
        if self.size and self.compressed_size:
            return self.compressed_size / self.size
        return None

    @property
    def deduplication_ratio(self) -> float | None:
        """Calculate the deduplication ratio if both sizes are available."""
        if self.compressed_size and self.deduplicated_size:
            return self.deduplicated_size / self.compressed_size
        return None

    def mark_verified(self, checksum: str | None = None) -> None:
        """Mark the snapshot as successfully verified."""
        self.verification_status = VerificationStatus.VERIFIED
        self.verification_time = datetime.utcnow()
        self.verification_error = None
        if checksum:
            self.checksum = checksum

    def mark_verification_failed(self, error_message: str) -> None:
        """Mark the snapshot verification as failed."""
        self.verification_status = VerificationStatus.FAILED
        self.verification_time = datetime.utcnow()
        self.verification_error = error_message

    def protect(self, reason: str) -> None:
        """Protect the snapshot from automatic deletion."""
        self.is_protected = True
        self.protection_reason = reason

    def unprotect(self) -> None:
        """Remove protection from the snapshot."""
        self.is_protected = False
        self.protection_reason = None

    def update_size_info(self, size: int, compressed_size: int | None = None, deduplicated_size: int | None = None) -> None:
        """Update the size information for the snapshot."""
        self.size = size
        if compressed_size is not None:
            self.compressed_size = compressed_size
        if deduplicated_size is not None:
            self.deduplicated_size = deduplicated_size

    def mark_error(self, error_message: str) -> None:
        """Mark the snapshot as having an error."""
        self.has_errors = True
        self.error_message = error_message

    def clear_error(self) -> None:
        """Clear the error state."""
        self.has_errors = False
        self.error_message = None