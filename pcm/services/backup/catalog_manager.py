"""
Backup Catalog Management Service.

This module provides comprehensive backup metadata management, including
history tracking, relationships, and verification status tracking.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from pcm.core.models.backup.snapshot import BackupSnapshot
from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.policy import BackupPolicy


logger = logging.getLogger(__name__)


class CatalogManager:
    """
    Backup catalog management service.
    
    Manages backup metadata, history tracking, relationships,
    and verification status.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize catalog manager.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
    
    async def get_backup_history(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get backup history for a tenant.
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum number of backups to return
            offset: Offset for pagination
            
        Returns:
            List of backup history entries
        """
        result = await self.db_session.execute(
            select(BackupSnapshot)
            .where(BackupSnapshot.tenant_id == tenant_id)
            .order_by(BackupSnapshot.snapshot_time.desc())
            .limit(limit)
            .offset(offset)
        )
        
        snapshots = list(result.scalars().all())
        
        history = []
        for snapshot in snapshots:
            history.append({
                'snapshot_id': snapshot.id,
                'job_id': snapshot.job_id,
                'vm_id': snapshot.vm_id,
                'snapshot_time': snapshot.snapshot_time.isoformat(),
                'size': snapshot.size,
                'datastore_id': snapshot.datastore_id,
                'verification_status': snapshot.verification_status,
                'retention_date': snapshot.retention_date.isoformat() if snapshot.retention_date else None
            })
        
        return history
    
    async def get_vm_backups(
        self,
        tenant_id: str,
        vm_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all backups for a specific VM.
        
        Args:
            tenant_id: Tenant ID
            vm_id: VM ID
            limit: Maximum number of backups to return
            
        Returns:
            List of backups for the VM
        """
        result = await self.db_session.execute(
            select(BackupSnapshot)
            .where(
                and_(
                    BackupSnapshot.tenant_id == tenant_id,
                    BackupSnapshot.vm_id == vm_id
                )
            )
            .order_by(BackupSnapshot.snapshot_time.desc())
            .limit(limit)
        )
        
        snapshots = list(result.scalars().all())
        
        backups = []
        for snapshot in snapshots:
            backups.append({
                'snapshot_id': snapshot.id,
                'job_id': snapshot.job_id,
                'snapshot_time': snapshot.snapshot_time.isoformat(),
                'size': snapshot.size,
                'datastore_id': snapshot.datastore_id,
                'verification_status': snapshot.verification_status,
                'path': snapshot.path
            })
        
        return backups
    
    async def get_backup_details(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a backup.
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            Backup details or None if not found
        """
        result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.id == snapshot_id)
        )
        
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            return None
        
        # Get associated job
        job_result = await self.db_session.execute(
            select(BackupJob).where(BackupJob.id == snapshot.job_id)
        )
        
        job = job_result.scalar_one_or_none()
        
        # Get associated policy
        policy_result = await self.db_session.execute(
            select(BackupPolicy).where(BackupPolicy.id == job.policy_id if job else None)
        )
        
        policy = policy_result.scalar_one_or_none()
        
        return {
            'snapshot_id': snapshot.id,
            'job_id': snapshot.job_id,
            'tenant_id': snapshot.tenant_id,
            'vm_id': snapshot.vm_id,
            'snapshot_time': snapshot.snapshot_time.isoformat(),
            'size': snapshot.size,
            'datastore_id': snapshot.datastore_id,
            'path': snapshot.path,
            'verification_status': snapshot.verification_status,
            'retention_date': snapshot.retention_date.isoformat() if snapshot.retention_date else None,
            'job_status': job.status.value if job else None,
            'policy_name': policy.name if policy else None
        }
    
    async def get_verification_status(self, snapshot_id: str) -> Optional[str]:
        """
        Get verification status of a backup.
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            Verification status or None if not found
        """
        result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.id == snapshot_id)
        )
        
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            return None
        
        return snapshot.verification_status
    
    async def update_verification_status(
        self,
        snapshot_id: str,
        status: str
    ) -> bool:
        """
        Update verification status of a backup.
        
        Args:
            snapshot_id: Snapshot ID
            status: New verification status
            
        Returns:
            True if updated, False if not found
        """
        result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.id == snapshot_id)
        )
        
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            return False
        
        snapshot.verification_status = status
        await self.db_session.flush()
        
        logger.info(f"Updated verification status for snapshot {snapshot_id} to {status}")
        
        return True
    
    async def get_retention_candidates(
        self,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get backups that are candidates for retention cleanup.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of backups eligible for deletion
        """
        now = datetime.utcnow()
        
        result = await self.db_session.execute(
            select(BackupSnapshot).where(
                and_(
                    BackupSnapshot.tenant_id == tenant_id,
                    BackupSnapshot.retention_date <= now
                )
            )
        )
        
        snapshots = list(result.scalars().all())
        
        candidates = []
        for snapshot in snapshots:
            candidates.append({
                'snapshot_id': snapshot.id,
                'job_id': snapshot.job_id,
                'vm_id': snapshot.vm_id,
                'snapshot_time': snapshot.snapshot_time.isoformat(),
                'size': snapshot.size,
                'retention_date': snapshot.retention_date.isoformat(),
                'days_overdue': (now - snapshot.retention_date).days
            })
        
        return candidates
    
    async def get_catalog_statistics(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get catalog statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Catalog statistics
        """
        # Get total snapshots
        result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.tenant_id == tenant_id)
        )
        
        all_snapshots = list(result.scalars().all())
        total_snapshots = len(all_snapshots)
        
        # Calculate total size
        total_size = sum(s.size for s in all_snapshots if s.size)
        
        # Get verification status breakdown
        verified = sum(1 for s in all_snapshots if s.verification_status == "verified")
        failed = sum(1 for s in all_snapshots if s.verification_status == "failed")
        pending = sum(1 for s in all_snapshots if s.verification_status is None)
        
        # Get retention candidates
        now = datetime.utcnow()
        retention_candidates = sum(
            1 for s in all_snapshots
            if s.retention_date and s.retention_date <= now
        )
        
        # Get unique VMs
        unique_vms = len(set(s.vm_id for s in all_snapshots))
        
        # Get oldest and newest backups
        oldest_backup = min(
            (s.snapshot_time for s in all_snapshots),
            default=None
        )
        newest_backup = max(
            (s.snapshot_time for s in all_snapshots),
            default=None
        )
        
        return {
            'total_snapshots': total_snapshots,
            'total_size_bytes': total_size,
            'total_size_gb': total_size / (1024 ** 3) if total_size else 0,
            'verification_status': {
                'verified': verified,
                'failed': failed,
                'pending': pending
            },
            'retention_candidates': retention_candidates,
            'unique_vms': unique_vms,
            'oldest_backup': oldest_backup.isoformat() if oldest_backup else None,
            'newest_backup': newest_backup.isoformat() if newest_backup else None
        }
    
    async def search_backups(
        self,
        tenant_id: str,
        vm_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        verification_status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for backups with multiple filters.
        
        Args:
            tenant_id: Tenant ID
            vm_id: Optional VM ID filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            verification_status: Optional verification status filter
            limit: Maximum number of results
            
        Returns:
            List of matching backups
        """
        query = select(BackupSnapshot).where(
            BackupSnapshot.tenant_id == tenant_id
        )
        
        # Apply filters
        filters = []
        
        if vm_id:
            filters.append(BackupSnapshot.vm_id == vm_id)
        
        if start_time:
            filters.append(BackupSnapshot.snapshot_time >= start_time)
        
        if end_time:
            filters.append(BackupSnapshot.snapshot_time <= end_time)
        
        if verification_status:
            filters.append(BackupSnapshot.verification_status == verification_status)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(BackupSnapshot.snapshot_time.desc()).limit(limit)
        
        result = await self.db_session.execute(query)
        snapshots = list(result.scalars().all())
        
        results = []
        for snapshot in snapshots:
            results.append({
                'snapshot_id': snapshot.id,
                'job_id': snapshot.job_id,
                'vm_id': snapshot.vm_id,
                'snapshot_time': snapshot.snapshot_time.isoformat(),
                'size': snapshot.size,
                'datastore_id': snapshot.datastore_id,
                'verification_status': snapshot.verification_status
            })
        
        return results
    
    async def get_backup_relationships(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Get relationships for a backup (job, policy, VM, etc).
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            Backup relationships
        """
        result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.id == snapshot_id)
        )
        
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            return {}
        
        # Get job
        job_result = await self.db_session.execute(
            select(BackupJob).where(BackupJob.id == snapshot.job_id)
        )
        job = job_result.scalar_one_or_none()
        
        # Get policy
        policy_result = await self.db_session.execute(
            select(BackupPolicy).where(BackupPolicy.id == job.policy_id if job else None)
        )
        policy = policy_result.scalar_one_or_none()
        
        # Get other snapshots from same job
        other_snapshots_result = await self.db_session.execute(
            select(BackupSnapshot).where(
                and_(
                    BackupSnapshot.job_id == snapshot.job_id,
                    BackupSnapshot.id != snapshot_id
                )
            )
        )
        other_snapshots = list(other_snapshots_result.scalars().all())
        
        return {
            'snapshot_id': snapshot.id,
            'job': {
                'job_id': job.id if job else None,
                'status': job.status.value if job else None,
                'start_time': job.start_time.isoformat() if job and job.start_time else None,
                'end_time': job.end_time.isoformat() if job and job.end_time else None
            },
            'policy': {
                'policy_id': policy.id if policy else None,
                'name': policy.name if policy else None
            },
            'other_snapshots_in_job': len(other_snapshots),
            'tenant_id': snapshot.tenant_id,
            'vm_id': snapshot.vm_id
        }
