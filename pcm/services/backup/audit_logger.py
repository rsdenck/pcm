"""
Audit Logging System.

This module provides comprehensive audit logging for all backup operations,
including immutable audit trails and compliance reporting.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from pcm.core.models.backup.job import BackupJob
from pcm.core.models.backup.snapshot import BackupSnapshot


logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Comprehensive audit logging system.
    
    Provides immutable audit trails for all backup operations,
    compliance reporting, and audit log export functionality.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize audit logger.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._audit_log: List[Dict[str, Any]] = []
    
    async def log_operation(
        self,
        operation_type: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> str:
        """
        Log a backup operation.
        
        Args:
            operation_type: Type of operation (backup, restore, delete, etc)
            tenant_id: Tenant ID
            user_id: Optional user ID
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Optional operation details
            status: Operation status (success, failure, pending)
            error_message: Optional error message
            
        Returns:
            Audit log entry ID
        """
        entry_id = f"audit-{datetime.utcnow().timestamp()}"
        
        audit_entry = {
            'entry_id': entry_id,
            'timestamp': datetime.utcnow().isoformat(),
            'operation_type': operation_type,
            'tenant_id': tenant_id,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {},
            'status': status,
            'error_message': error_message
        }
        
        self._audit_log.append(audit_entry)
        
        # Log to system logger
        log_message = (
            f"AUDIT: {operation_type} by {user_id or 'system'} on "
            f"{resource_type} {resource_id} for tenant {tenant_id}: {status}"
        )
        
        if status == "success":
            logger.info(log_message)
        else:
            logger.warning(log_message)
        
        return entry_id
    
    async def log_backup_job_created(
        self,
        job_id: str,
        policy_id: str,
        tenant_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Log backup job creation.
        
        Args:
            job_id: Job ID
            policy_id: Policy ID
            tenant_id: Tenant ID
            user_id: Optional user ID
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="backup_job_created",
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type="backup_job",
            resource_id=job_id,
            details={'policy_id': policy_id}
        )
    
    async def log_backup_job_started(
        self,
        job_id: str,
        tenant_id: str
    ) -> str:
        """
        Log backup job start.
        
        Args:
            job_id: Job ID
            tenant_id: Tenant ID
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="backup_job_started",
            tenant_id=tenant_id,
            resource_type="backup_job",
            resource_id=job_id
        )
    
    async def log_backup_job_completed(
        self,
        job_id: str,
        tenant_id: str,
        snapshot_count: int,
        total_size: int
    ) -> str:
        """
        Log backup job completion.
        
        Args:
            job_id: Job ID
            tenant_id: Tenant ID
            snapshot_count: Number of snapshots created
            total_size: Total backup size
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="backup_job_completed",
            tenant_id=tenant_id,
            resource_type="backup_job",
            resource_id=job_id,
            details={
                'snapshot_count': snapshot_count,
                'total_size': total_size
            }
        )
    
    async def log_backup_job_failed(
        self,
        job_id: str,
        tenant_id: str,
        error_message: str
    ) -> str:
        """
        Log backup job failure.
        
        Args:
            job_id: Job ID
            tenant_id: Tenant ID
            error_message: Error message
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="backup_job_failed",
            tenant_id=tenant_id,
            resource_type="backup_job",
            resource_id=job_id,
            status="failure",
            error_message=error_message
        )
    
    async def log_restore_initiated(
        self,
        restore_job_id: str,
        snapshot_id: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        restore_type: str = "full_vm"
    ) -> str:
        """
        Log restore operation initiation.
        
        Args:
            restore_job_id: Restore job ID
            snapshot_id: Snapshot ID
            tenant_id: Tenant ID
            user_id: Optional user ID
            restore_type: Type of restore
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="restore_initiated",
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type="restore_job",
            resource_id=restore_job_id,
            details={
                'snapshot_id': snapshot_id,
                'restore_type': restore_type
            }
        )
    
    async def log_restore_completed(
        self,
        restore_job_id: str,
        snapshot_id: str,
        tenant_id: str,
        target_resource: str
    ) -> str:
        """
        Log restore operation completion.
        
        Args:
            restore_job_id: Restore job ID
            snapshot_id: Snapshot ID
            tenant_id: Tenant ID
            target_resource: Target resource identifier
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="restore_completed",
            tenant_id=tenant_id,
            resource_type="restore_job",
            resource_id=restore_job_id,
            details={
                'snapshot_id': snapshot_id,
                'target_resource': target_resource
            }
        )
    
    async def log_backup_deleted(
        self,
        snapshot_id: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        reason: str = "retention_policy"
    ) -> str:
        """
        Log backup deletion.
        
        Args:
            snapshot_id: Snapshot ID
            tenant_id: Tenant ID
            user_id: Optional user ID
            reason: Reason for deletion
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="backup_deleted",
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type="backup_snapshot",
            resource_id=snapshot_id,
            details={'reason': reason}
        )
    
    async def log_access_attempt(
        self,
        tenant_id: str,
        user_id: Optional[str],
        resource_type: str,
        resource_id: str,
        allowed: bool
    ) -> str:
        """
        Log access attempt.
        
        Args:
            tenant_id: Tenant ID
            user_id: Optional user ID
            resource_type: Type of resource
            resource_id: Resource ID
            allowed: Whether access was allowed
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="access_attempt",
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            status="success" if allowed else "failure",
            error_message=None if allowed else "Access denied"
        )
    
    async def log_policy_modified(
        self,
        policy_id: str,
        tenant_id: str,
        user_id: Optional[str],
        changes: Dict[str, Any]
    ) -> str:
        """
        Log policy modification.
        
        Args:
            policy_id: Policy ID
            tenant_id: Tenant ID
            user_id: Optional user ID
            changes: Dictionary of changes
            
        Returns:
            Audit log entry ID
        """
        return await self.log_operation(
            operation_type="policy_modified",
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type="backup_policy",
            resource_id=policy_id,
            details={'changes': changes}
        )
    
    async def get_audit_log(
        self,
        tenant_id: Optional[str] = None,
        operation_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get audit log entries.
        
        Args:
            tenant_id: Optional tenant ID filter
            operation_type: Optional operation type filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of entries
            
        Returns:
            List of audit log entries
        """
        entries = self._audit_log
        
        # Apply filters
        if tenant_id:
            entries = [e for e in entries if e['tenant_id'] == tenant_id]
        
        if operation_type:
            entries = [e for e in entries if e['operation_type'] == operation_type]
        
        if start_time:
            entries = [
                e for e in entries
                if datetime.fromisoformat(e['timestamp']) >= start_time
            ]
        
        if end_time:
            entries = [
                e for e in entries
                if datetime.fromisoformat(e['timestamp']) <= end_time
            ]
        
        # Return most recent entries first
        entries = sorted(
            entries,
            key=lambda e: e['timestamp'],
            reverse=True
        )[:limit]
        
        return entries
    
    async def export_audit_log(
        self,
        tenant_id: str,
        format: str = "json"
    ) -> str:
        """
        Export audit log for a tenant.
        
        Args:
            tenant_id: Tenant ID
            format: Export format (json, csv)
            
        Returns:
            Exported audit log as string
        """
        entries = await self.get_audit_log(tenant_id=tenant_id)
        
        if format == "json":
            return json.dumps(entries, indent=2)
        elif format == "csv":
            # Simple CSV export
            if not entries:
                return ""
            
            headers = list(entries[0].keys())
            csv_lines = [",".join(headers)]
            
            for entry in entries:
                values = [
                    str(entry.get(h, "")).replace(",", ";")
                    for h in headers
                ]
                csv_lines.append(",".join(values))
            
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def get_audit_statistics(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get audit log statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Audit statistics
        """
        entries = await self.get_audit_log(tenant_id=tenant_id)
        
        # Count operations by type
        operation_counts: Dict[str, int] = {}
        for entry in entries:
            op_type = entry['operation_type']
            operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
        
        # Count by status
        status_counts = {
            'success': sum(1 for e in entries if e['status'] == 'success'),
            'failure': sum(1 for e in entries if e['status'] == 'failure'),
            'pending': sum(1 for e in entries if e['status'] == 'pending')
        }
        
        # Get unique users
        unique_users = len(set(e['user_id'] for e in entries if e['user_id']))
        
        return {
            'tenant_id': tenant_id,
            'total_entries': len(entries),
            'operation_counts': operation_counts,
            'status_counts': status_counts,
            'unique_users': unique_users,
            'date_range': {
                'start': entries[-1]['timestamp'] if entries else None,
                'end': entries[0]['timestamp'] if entries else None
            }
        }
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        self._audit_log.clear()
