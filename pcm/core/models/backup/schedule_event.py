"""
Schedule Event model for tracking critical scheduling events.

This model stores historical data about backup scheduling operations,
conflicts, and system events for audit and monitoring purposes.
"""

from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict, Any, Optional, List
from pcm.core.database.base import Base


class ScheduleEventType(str, Enum):
    """Types of schedule events."""
    JOB_SCHEDULED = "job_scheduled"
    JOB_QUEUED = "job_queued"
    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    JOB_CANCELLED = "job_cancelled"
    SCHEDULING_CONFLICT = "scheduling_conflict"
    RESOURCE_CONFLICT = "resource_conflict"
    POLICY_ERROR = "policy_error"
    SCHEDULER_STARTED = "scheduler_started"
    SCHEDULER_STOPPED = "scheduler_stopped"
    QUEUE_OVERFLOW = "queue_overflow"
    SYSTEM_ERROR = "system_error"


class ScheduleEventSeverity(str, Enum):
    """Severity levels for schedule events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ScheduleEvent(Base):
    """
    Schedule Event model for tracking backup scheduling operations.
    
    Stores critical events, conflicts, and system operations for
    audit trails, monitoring, and troubleshooting purposes.
    """
    __tablename__ = "schedule_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Event classification
    event_type: Mapped[ScheduleEventType] = mapped_column(
        SQLEnum(ScheduleEventType, native_enum=False), 
        nullable=False
    )
    severity: Mapped[ScheduleEventSeverity] = mapped_column(
        SQLEnum(ScheduleEventSeverity, native_enum=False), 
        default=ScheduleEventSeverity.INFO,
        nullable=False
    )
    
    # Event details
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Related entities
    tenant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True
    )
    policy_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("backup_policies.id", ondelete="SET NULL"), nullable=True
    )
    job_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("backup_jobs.id", ondelete="SET NULL"), nullable=True
    )
    
    # System context
    scheduler_instance: Mapped[str | None] = mapped_column(String(255), nullable=True)
    node_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Performance metrics
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resource_usage: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Error information
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamps
    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tenant: Mapped["Tenant"] = relationship()
    policy: Mapped["BackupPolicy"] = relationship()
    job: Mapped["BackupJob"] = relationship()

    def __init__(self, **kwargs):
        """Initialize ScheduleEvent with proper defaults."""
        if 'severity' not in kwargs:
            kwargs['severity'] = ScheduleEventSeverity.INFO
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
        if 'event_time' not in kwargs:
            kwargs['event_time'] = datetime.utcnow()
        
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<ScheduleEvent(id={self.id}, type={self.event_type}, severity={self.severity})>"

    @classmethod
    def create_job_scheduled(
        cls,
        job_id: str,
        policy_id: str,
        tenant_id: str,
        scheduled_time: datetime,
        details: Optional[Dict[str, Any]] = None
    ) -> "ScheduleEvent":
        """Create a job scheduled event."""
        return cls(
            event_type=ScheduleEventType.JOB_SCHEDULED,
            severity=ScheduleEventSeverity.INFO,
            message=f"Backup job scheduled for policy {policy_id}",
            job_id=job_id,
            policy_id=policy_id,
            tenant_id=tenant_id,
            details={
                'scheduled_time': scheduled_time.isoformat(),
                **(details or {})
            }
        )
    
    @classmethod
    def create_scheduling_conflict(
        cls,
        policy_id: str,
        tenant_id: str,
        conflict_reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> "ScheduleEvent":
        """Create a scheduling conflict event."""
        return cls(
            event_type=ScheduleEventType.SCHEDULING_CONFLICT,
            severity=ScheduleEventSeverity.WARNING,
            message=f"Scheduling conflict for policy {policy_id}: {conflict_reason}",
            policy_id=policy_id,
            tenant_id=tenant_id,
            error_code="SCHEDULING_CONFLICT",
            details=details
        )
    
    @classmethod
    def create_resource_conflict(
        cls,
        policy_id: str,
        tenant_id: str,
        resource_ids: List[str],
        details: Optional[Dict[str, Any]] = None
    ) -> "ScheduleEvent":
        """Create a resource conflict event."""
        return cls(
            event_type=ScheduleEventType.RESOURCE_CONFLICT,
            severity=ScheduleEventSeverity.WARNING,
            message=f"Resource conflict for policy {policy_id}: resources {resource_ids} in use",
            policy_id=policy_id,
            tenant_id=tenant_id,
            error_code="RESOURCE_CONFLICT",
            details={
                'conflicting_resources': resource_ids,
                **(details or {})
            }
        )
    
    @classmethod
    def create_job_completed(
        cls,
        job_id: str,
        policy_id: str,
        tenant_id: str,
        success: bool,
        duration_ms: int,
        details: Optional[Dict[str, Any]] = None
    ) -> "ScheduleEvent":
        """Create a job completion event."""
        return cls(
            event_type=ScheduleEventType.JOB_COMPLETED if success else ScheduleEventType.JOB_FAILED,
            severity=ScheduleEventSeverity.INFO if success else ScheduleEventSeverity.ERROR,
            message=f"Backup job {'completed successfully' if success else 'failed'} for policy {policy_id}",
            job_id=job_id,
            policy_id=policy_id,
            tenant_id=tenant_id,
            duration_ms=duration_ms,
            details=details
        )
    
    @classmethod
    def create_policy_error(
        cls,
        policy_id: str,
        tenant_id: str,
        error_message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "ScheduleEvent":
        """Create a policy error event."""
        return cls(
            event_type=ScheduleEventType.POLICY_ERROR,
            severity=ScheduleEventSeverity.ERROR,
            message=f"Policy error for {policy_id}: {error_message}",
            policy_id=policy_id,
            tenant_id=tenant_id,
            error_code=error_code or "POLICY_ERROR",
            error_details=error_message,
            details=details
        )
    
    @classmethod
    def create_system_event(
        cls,
        event_type: ScheduleEventType,
        message: str,
        severity: ScheduleEventSeverity = ScheduleEventSeverity.INFO,
        details: Optional[Dict[str, Any]] = None
    ) -> "ScheduleEvent":
        """Create a system-level event."""
        return cls(
            event_type=event_type,
            severity=severity,
            message=message,
            details=details
        )

    def add_performance_metrics(self, duration_ms: int, resource_usage: Dict[str, Any]) -> None:
        """Add performance metrics to the event."""
        self.duration_ms = duration_ms
        self.resource_usage = resource_usage

    def add_error_details(self, error_code: str, error_message: str, stack_trace: Optional[str] = None) -> None:
        """Add error details to the event."""
        self.error_code = error_code
        self.error_details = error_message
        if stack_trace:
            self.stack_trace = stack_trace

    def set_context(self, scheduler_instance: str, node_id: Optional[str] = None) -> None:
        """Set system context for the event."""
        self.scheduler_instance = scheduler_instance
        if node_id:
            self.node_id = node_id