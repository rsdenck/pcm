# Backup module models
"""
Backup module models for PCM Backup-as-a-Service.

This package contains all data models related to backup operations,
including PBS servers, datastores, policies, jobs, and snapshots.
"""

from .pbs_server import PBSServer, ServerStatus
from .datastore import Datastore, DatastoreStatus
from .policy import BackupPolicy, PolicyStatus, validate_policy_configuration, BACKUP_POLICY_SCHEMA
from .job import BackupJob, JobStatus
from .snapshot import BackupSnapshot, VerificationStatus
from .schedule_event import ScheduleEvent, ScheduleEventType, ScheduleEventSeverity

__all__ = [
    "PBSServer",
    "ServerStatus", 
    "Datastore",
    "DatastoreStatus",
    "BackupPolicy",
    "PolicyStatus",
    "validate_policy_configuration",
    "BACKUP_POLICY_SCHEMA",
    "BackupJob",
    "JobStatus",
    "BackupSnapshot",
    "VerificationStatus",
    "ScheduleEvent",
    "ScheduleEventType",
    "ScheduleEventSeverity",
]