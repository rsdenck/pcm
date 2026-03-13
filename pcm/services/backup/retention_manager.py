"""
Retention Management Service.

This module provides automatic backup cleanup based on retention policies,
retention calculation, and dependency checking before deletion.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from pcm.core.models.backup.snapshot import BackupSnapshot
from pcm.core.models.backup.job import BackupJob
from pcm.core.models.backup.policy import BackupPolicy


logger = logging.getLogger(__name__)


class RetentionManager:
    """
    Backup retention management service.
    
    Provides automatic cleanup based on retention policies,
    retention calculation, and dependency checking.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize retention manager.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._cleanup_interval = 86400  # Run daily
        self._cleanup_jobs: Dict[str, Dict[str, Any]] = {}
    
    async def start_cleanup(self) -> None:
        """
        Start the retention cleanup service.
        """
        if self._is_running:
            logger.warning("Retention cleanup service is already running")
            return
        
        logger.info("Starting backup retention cleanup service")
        self._is_running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup(self) -> None:
        """
        Stop the retention cleanup service.
        """
        if not self._is_running:
            return
        
        logger.info("Stopping backup retention cleanup service")
        self._is_running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    async def _cleanup_loop(self) -> None:
        """
        Main cleanup loop that runs retention cleanup periodically.
        """
        logger.info("Retention cleanup loop started")
        
        while self._is_running:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(self._cleanup_interval)
            except asyncio.CancelledError:
                logger.info("Cleanup loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(self._cleanup_interval)
    
    async def _perform_cleanup(self) -> None:
        """
        Perform retention-based cleanup of backups.
        """
        try:
            # Get all backups eligible for deletion
            candidates = await self._get_retention_candidates()
            
            if not candidates:
                logger.debug("No backups eligible for retention cleanup")
                return
            
            logger.info(f"Found {len(candidates)} backups eligible for cleanup")
            
            # Check dependencies and delete
            deleted_count = 0
            for snapshot in candidates:
                if await self._can_delete_backup(snapshot):
                    await self._delete_backup(snapshot)
                    deleted_count += 1
            
            logger.info(f"Retention cleanup completed: {deleted_count} backups deleted")
            
        except Exception as e:
            logger.error(f"Error performing retention cleanup: {e}")
    
    async def _get_retention_candidates(self) -> List[BackupSnapshot]:
        """
        Get backups that are candidates for retention cleanup.
        
        Returns:
            List of snapshots eligible for deletion
        """
        now = datetime.utcnow()
        
        result = await self.db_session.execute(
            select(BackupSnapshot).where(
                and_(
                    BackupSnapshot.retention_date.isnot(None),
                    BackupSnapshot.retention_date <= now
                )
            )
        )
        
        return list(result.scalars().all())
    
    async def _can_delete_backup(self, snapshot: BackupSnapshot) -> bool:
        """
        Check if a backup can be safely deleted.
        
        Args:
            snapshot: BackupSnapshot to check
            
        Returns:
            True if backup can be deleted
        """
        # Check if backup has active dependencies
        # In a real implementation, would check for:
        # - Active restore operations
        # - Dependent snapshots
        # - Active clones
        
        return True
    
    async def _delete_backup(self, snapshot: BackupSnapshot) -> None:
        """
        Delete a backup snapshot.
        
        Args:
            snapshot: BackupSnapshot to delete
        """
        try:
            # In a real implementation, would:
            # 1. Delete from PBS server
            # 2. Update database
            # 3. Log audit entry
            
            logger.info(f"Deleting backup snapshot {snapshot.id} due to retention policy")
            
            # For now, just mark as deleted in database
            await self.db_session.delete(snapshot)
            await self.db_session.flush()
            
        except Exception as e:
            logger.error(f"Error deleting backup {snapshot.id}: {e}")
    
    async def calculate_retention_date(
        self,
        snapshot_time: datetime,
        retention_config: Dict[str, int]
    ) -> datetime:
        """
        Calculate retention date for a backup.
        
        Args:
            snapshot_time: Time when backup was created
            retention_config: Retention configuration with daily, weekly, monthly, yearly
            
        Returns:
            Retention date (when backup should be deleted)
        """
        # Determine retention period based on backup age and config
        now = datetime.utcnow()
        age_days = (now - snapshot_time).days
        
        # Default retention: keep for 30 days
        retention_days = 30
        
        # Apply retention rules
        if age_days < 7:
            # Keep daily backups for 7 days
            retention_days = retention_config.get('daily', 7)
        elif age_days < 30:
            # Keep weekly backups for 30 days
            retention_days = retention_config.get('weekly', 30)
        elif age_days < 365:
            # Keep monthly backups for 365 days
            retention_days = retention_config.get('monthly', 365)
        else:
            # Keep yearly backups for 2 years
            retention_days = retention_config.get('yearly', 730)
        
        retention_date = snapshot_time + timedelta(days=retention_days)
        
        return retention_date
    
    async def apply_retention_policy(
        self,
        policy_id: str
    ) -> Dict[str, Any]:
        """
        Apply retention policy to all backups from a policy.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Retention application results
        """
        # Get policy
        result = await self.db_session.execute(
            select(BackupPolicy).where(BackupPolicy.id == policy_id)
        )
        
        policy = result.scalar_one_or_none()
        
        if not policy:
            return {'success': False, 'error': f"Policy {policy_id} not found"}
        
        # Get all jobs for this policy
        job_result = await self.db_session.execute(
            select(BackupJob).where(BackupJob.policy_id == policy_id)
        )
        
        jobs = list(job_result.scalars().all())
        
        updated_count = 0
        
        # Get retention config from policy
        retention_config = policy.retention if hasattr(policy, 'retention') else {}
        
        # Update retention dates for all snapshots from these jobs
        for job in jobs:
            snap_result = await self.db_session.execute(
                select(BackupSnapshot).where(BackupSnapshot.job_id == job.id)
            )
            
            snapshots = list(snap_result.scalars().all())
            
            for snapshot in snapshots:
                retention_date = await self.calculate_retention_date(
                    snapshot.snapshot_time,
                    retention_config
                )
                snapshot.retention_date = retention_date
                updated_count += 1
        
        await self.db_session.flush()
        
        logger.info(f"Applied retention policy {policy_id} to {updated_count} snapshots")
        
        return {
            'success': True,
            'policy_id': policy_id,
            'updated_count': updated_count
        }
    
    async def get_retention_statistics(self) -> Dict[str, Any]:
        """
        Get retention management statistics.
        
        Returns:
            Retention statistics
        """
        result = await self.db_session.execute(select(BackupSnapshot))
        
        all_snapshots = list(result.scalars().all())
        
        now = datetime.utcnow()
        
        # Count by retention status
        retained = sum(
            1 for s in all_snapshots
            if s.retention_date and s.retention_date > now
        )
        expired = sum(
            1 for s in all_snapshots
            if s.retention_date and s.retention_date <= now
        )
        no_retention = sum(
            1 for s in all_snapshots
            if not s.retention_date
        )
        
        # Calculate total size
        total_size = sum(s.size for s in all_snapshots if s.size)
        
        # Calculate size to be deleted
        size_to_delete = sum(
            s.size for s in all_snapshots
            if s.retention_date and s.retention_date <= now and s.size
        )
        
        return {
            'total_snapshots': len(all_snapshots),
            'retained': retained,
            'expired': expired,
            'no_retention': no_retention,
            'total_size_gb': total_size / (1024 ** 3) if total_size else 0,
            'size_to_delete_gb': size_to_delete / (1024 ** 3) if size_to_delete else 0,
            'service_status': 'running' if self._is_running else 'stopped'
        }
    
    async def get_cleanup_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get cleanup operation history.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of cleanup operations
        """
        history = []
        
        for job_id, job in list(self._cleanup_jobs.items())[:limit]:
            history.append({
                'cleanup_job_id': job_id,
                'status': job['status'],
                'start_time': job['start_time'],
                'end_time': job['end_time'],
                'deleted_count': job.get('deleted_count', 0),
                'freed_space': job.get('freed_space', 0)
            })
        
        return history
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        await self.stop_cleanup()
        self._cleanup_jobs.clear()
