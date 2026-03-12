from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict, Any, List, Optional
import json
import jsonschema
from pcm.core.database.base import Base


class PolicyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ERROR = "error"


class BackupPolicy(Base):
    """
    Backup Policy model for managing backup schedules and retention settings.
    
    Provides tenant-based policy isolation, JSON schema validation for policy
    configuration, and automated backup scheduling. Each policy defines backup
    targets, schedules, retention rules, and execution options.
    """
    __tablename__ = "backup_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Tenant isolation
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    
    # Policy configuration as JSON
    configuration: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Policy status and control
    status: Mapped[PolicyStatus] = mapped_column(
        SQLEnum(PolicyStatus, native_enum=False), 
        default=PolicyStatus.ACTIVE, 
        nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Scheduling information
    next_run: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_run: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Statistics and monitoring
    job_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Error tracking
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship()
    backup_jobs: Mapped[list["BackupJob"]] = relationship(
        back_populates="policy", 
        cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        """Initialize BackupPolicy with proper defaults."""
        # Set defaults for fields that might not be set by SQLAlchemy in tests
        if 'status' not in kwargs:
            kwargs['status'] = PolicyStatus.ACTIVE
        if 'enabled' not in kwargs:
            kwargs['enabled'] = True
        if 'job_count' not in kwargs:
            kwargs['job_count'] = 0
        if 'success_count' not in kwargs:
            kwargs['success_count'] = 0
        if 'failure_count' not in kwargs:
            kwargs['failure_count'] = 0
        if 'error_count' not in kwargs:
            kwargs['error_count'] = 0
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
        
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<BackupPolicy(id={self.id}, name={self.name}, tenant_id={self.tenant_id}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Check if the policy is active and enabled."""
        return self.status == PolicyStatus.ACTIVE and self.enabled

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of backup jobs for this policy."""
        if self.job_count is None or self.job_count == 0:
            return 0.0
        if self.success_count is None:
            return 0.0
        return (self.success_count / self.job_count) * 100

    @property
    def schedule(self) -> Dict[str, Any]:
        """Get the schedule configuration from the policy."""
        return self.configuration.get("schedule", {})

    @property
    def retention(self) -> Dict[str, Any]:
        """Get the retention configuration from the policy."""
        return self.configuration.get("retention", {})

    @property
    def targets(self) -> List[Dict[str, Any]]:
        """Get the backup targets from the policy."""
        return self.configuration.get("targets", [])

    @property
    def options(self) -> Dict[str, Any]:
        """Get the backup options from the policy."""
        return self.configuration.get("options", {})

    def validate_configuration(self) -> tuple[bool, Optional[str]]:
        """
        Validate the policy configuration against the JSON schema.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            jsonschema.validate(self.configuration, BACKUP_POLICY_SCHEMA)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    def update_statistics(self, success: bool) -> None:
        """Update policy statistics after a backup job completion."""
        if self.job_count is None:
            self.job_count = 0
        if self.success_count is None:
            self.success_count = 0
        if self.failure_count is None:
            self.failure_count = 0
        if self.error_count is None:
            self.error_count = 0
            
        self.job_count += 1
        if success:
            self.success_count += 1
            self.last_error = None
            self.error_count = 0
        else:
            self.failure_count += 1
            self.error_count += 1

    def mark_error(self, error_message: str) -> None:
        """Mark the policy as having an error."""
        self.status = PolicyStatus.ERROR
        self.last_error = error_message
        if self.error_count is None:
            self.error_count = 0
        self.error_count += 1

    def clear_error(self) -> None:
        """Clear the error state and mark as active."""
        if self.enabled:
            self.status = PolicyStatus.ACTIVE
        else:
            self.status = PolicyStatus.INACTIVE
        self.last_error = None
        if self.error_count is None:
            self.error_count = 0
        else:
            self.error_count = 0

    def suspend(self, reason: str) -> None:
        """Suspend the policy with a reason."""
        self.status = PolicyStatus.SUSPENDED
        self.enabled = False
        self.last_error = f"Suspended: {reason}"

    def activate(self) -> None:
        """Activate the policy."""
        self.status = PolicyStatus.ACTIVE
        self.enabled = True
        self.last_error = None
        if self.error_count is None:
            self.error_count = 0
        else:
            self.error_count = 0


# JSON Schema for backup policy configuration validation
BACKUP_POLICY_SCHEMA = {
    "type": "object",
    "properties": {
        "schedule": {
            "type": "object",
            "properties": {
                "cron": {
                    "type": "string",
                    "pattern": r"^[0-9\*\-\,\/\s]+$",
                    "description": "Cron expression for backup scheduling"
                },
                "timezone": {
                    "type": "string",
                    "description": "Timezone for schedule execution"
                }
            },
            "required": ["cron"],
            "additionalProperties": False
        },
        "retention": {
            "type": "object",
            "properties": {
                "daily": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Number of daily backups to retain"
                },
                "weekly": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Number of weekly backups to retain"
                },
                "monthly": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Number of monthly backups to retain"
                },
                "yearly": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Number of yearly backups to retain"
                }
            },
            "additionalProperties": False,
            "minProperties": 1
        },
        "targets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "vm_id": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Virtual machine identifier"
                    },
                    "cluster_id": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Proxmox cluster identifier"
                    },
                    "datastore_id": {
                        "type": "string",
                        "minLength": 1,
                        "description": "PBS datastore identifier"
                    }
                },
                "required": ["vm_id", "cluster_id", "datastore_id"],
                "additionalProperties": False
            },
            "minItems": 1,
            "description": "List of backup targets"
        },
        "options": {
            "type": "object",
            "properties": {
                "compression": {
                    "type": "string",
                    "enum": ["none", "lz4", "zstd"],
                    "default": "lz4",
                    "description": "Compression algorithm for backups"
                },
                "encryption": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable backup encryption"
                },
                "verification": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable backup verification"
                },
                "bandwidth_limit": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Bandwidth limit in KB/s (0 = unlimited)"
                },
                "max_concurrent_jobs": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 1,
                    "description": "Maximum concurrent backup jobs"
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["schedule", "retention", "targets"],
    "additionalProperties": False
}


def validate_policy_configuration(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Standalone function to validate backup policy configuration.
    
    Args:
        config: Policy configuration dictionary
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        jsonschema.validate(config, BACKUP_POLICY_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"Configuration validation failed: {e.message}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"