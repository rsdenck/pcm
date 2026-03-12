"""
Backup Job Runner for executing backup operations.

This module provides the core functionality for executing backup jobs,
including PBS API integration, progress tracking, and failure handling.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.snapshot import BackupSnapshot, VerificationStatus
from pcm.core.models.backup.policy import BackupPolicy
from pcm.core.models.backup.pbs_server import PBSServer
from pcm.core.models.backup.datastore import Datastore
from pcm.services.backup.pbs_client import PBSAPIClient, PBSClientError


logger = logging.getLogger(__name__)


class BackupJobRunnerError(Exception):
    """Base exception for backup job runner errors."""
    pass


class BackupExecutionError(BackupJobRunnerError):
    """Raised when backup execution fails."""
    pass


class BackupJobRunner:
    """
    Backup job execution engine.
    
    Handles the execution of individual backup jobs, including VM backup
    operations, progress tracking, snapshot creation, and error handling.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize backup job runner.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._running_jobs: Dict[str, asyncio.Task] = {}
    
    async def execute_job(self, job_id: str) -> Dict[str, Any]:
        """
        Execute a backup job.
        
        Args:
            job_id: ID of the backup job to execute
            
        Returns:
            Execution results dictionary
            
        Raises:
            BackupJobRunnerError: If job execution fails
        """
        logger.info(f"Starting execution of backup job: {job_id}")
        
        # Get job with all relationships
        job = await self._get_job_with_relationships(job_id)
        if not job:
            raise BackupJobRunnerError(f"Backup job {job_id} not found")
        
        # Check if job is already running
        if job_id in self._running_jobs:
            raise BackupJobRunnerError(f"Backup job {job_id} is already running")
        
        # Validate job can be executed
        if job.status != JobStatus.PENDING:
            raise BackupJobRunnerError(f"Job {job_id} is not in pending status: {job.status}")
        
        try:
            # Mark job as running
            await self._update_job_status(job, JobStatus.RUNNING)
            job.start_time = datetime.utcnow()
            await self.db_session.flush()
            
            # Execute backup for each target
            results = []
            total_targets = len(job.policy.targets)
            
            for i, target in enumerate(job.policy.targets):
                logger.info(f"Processing target {i+1}/{total_targets} for job {job_id}")
                
                try:
                    # Execute backup for this target
                    result = await self._execute_target_backup(job, target)
                    results.append(result)
                    
                    # Update progress
                    progress = int(((i + 1) / total_targets) * 100)
                    await self._update_job_progress(job, progress)
                    
                except Exception as e:
                    logger.error(f"Failed to backup target {target}: {e}")
                    result = {
                        'target': target,
                        'success': False,
                        'error': str(e)
                    }
                    results.append(result)
            
            # Determine overall job success
            successful_targets = sum(1 for r in results if r.get('success', False))
            job_success = successful_targets > 0  # At least one target succeeded
            
            # Update job completion
            job.end_time = datetime.utcnow()
            if job_success:
                await self._update_job_status(job, JobStatus.COMPLETED)
                job.policy.update_statistics(True)
            else:
                await self._update_job_status(job, JobStatus.FAILED)
                job.policy.update_statistics(False)
                job.error_message = "All backup targets failed"
            
            await self.db_session.flush()
            
            execution_result = {
                'job_id': job_id,
                'success': job_success,
                'targets_processed': total_targets,
                'targets_successful': successful_targets,
                'results': results,
                'duration': (job.end_time - job.start_time).total_seconds(),
                'start_time': job.start_time.isoformat(),
                'end_time': job.end_time.isoformat()
            }
            
            logger.info(f"Backup job {job_id} completed: {successful_targets}/{total_targets} targets successful")
            return execution_result
            
        except Exception as e:
            # Mark job as failed
            job.end_time = datetime.utcnow()
            job.error_message = str(e)
            await self._update_job_status(job, JobStatus.FAILED)
            job.policy.update_statistics(False)
            await self.db_session.flush()
            
            logger.error(f"Backup job {job_id} failed: {e}")
            raise BackupExecutionError(f"Job execution failed: {str(e)}") from e
        
        finally:
            # Remove from running jobs
            if job_id in self._running_jobs:
                del self._running_jobs[job_id]
    
    async def _execute_target_backup(self, job: BackupJob, target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute backup for a specific target.
        
        Args:
            job: BackupJob instance
            target: Target configuration dictionary
            
        Returns:
            Target execution result
        """
        vm_id = target['vm_id']
        cluster_id = target['cluster_id']
        datastore_id = target['datastore_id']
        
        logger.debug(f"Executing backup for VM {vm_id} on cluster {cluster_id}")
        
        # Get datastore and PBS server
        datastore = await self._get_datastore(datastore_id)
        if not datastore:
            raise BackupExecutionError(f"Datastore {datastore_id} not found")
        
        pbs_server = datastore.pbs_server
        if not pbs_server:
            raise BackupExecutionError(f"PBS server not found for datastore {datastore_id}")
        
        # Create snapshot record
        snapshot = BackupSnapshot(
            job_id=job.id,
            tenant_id=job.tenant_id,
            vm_id=vm_id,
            cluster_id=cluster_id,
            datastore_id=datastore_id,
            snapshot_time=datetime.utcnow(),
            snapshot_name=self._generate_snapshot_name(vm_id, job.id),
            path=f"vm/{vm_id}/{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}"
        )
        
        # Apply backup options from policy
        options = job.policy.options
        snapshot.encryption_enabled = options.get('encryption', False)
        snapshot.compression_type = options.get('compression', 'lz4')
        
        self.db_session.add(snapshot)
        await self.db_session.flush()
        
        try:
            # Execute backup via PBS API
            async with PBSAPIClient(pbs_server) as client:
                backup_result = await client.create_backup(
                    vm_id=vm_id,
                    datastore=datastore.name,
                    snapshot_name=snapshot.snapshot_name,
                    options={
                        'compression': snapshot.compression_type,
                        'encryption': snapshot.encryption_enabled,
                        'bandwidth_limit': options.get('bandwidth_limit', 0)
                    }
                )
            
            # Update snapshot with results
            if backup_result.get('success', False):
                snapshot.size = backup_result.get('size')
                snapshot.compressed_size = backup_result.get('compressed_size')
                snapshot.backup_duration = backup_result.get('duration')
                snapshot.transfer_rate = backup_result.get('transfer_rate')
                
                # Calculate retention date
                retention_config = job.policy.retention
                retention_days = self._calculate_retention_days(retention_config)
                snapshot.retention_date = datetime.utcnow() + timedelta(days=retention_days)
                
                # Schedule verification if enabled
                if options.get('verification', True):
                    await self._schedule_verification(snapshot)
                else:
                    snapshot.verification_status = VerificationStatus.SKIPPED
                
                await self.db_session.flush()
                
                return {
                    'target': target,
                    'success': True,
                    'snapshot_id': snapshot.id,
                    'size': snapshot.size,
                    'duration': snapshot.backup_duration
                }
            else:
                error_msg = backup_result.get('error', 'Unknown backup error')
                snapshot.mark_error(error_msg)
                await self.db_session.flush()
                
                return {
                    'target': target,
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            # Mark snapshot as failed
            snapshot.mark_error(str(e))
            await self.db_session.flush()
            raise BackupExecutionError(f"Backup failed for VM {vm_id}: {str(e)}") from e
    
    async def _get_job_with_relationships(self, job_id: str) -> Optional[BackupJob]:
        """Get backup job with all required relationships loaded."""
        result = await self.db_session.execute(
            select(BackupJob)
            .options(
                selectinload(BackupJob.policy),
                selectinload(BackupJob.snapshots)
            )
            .where(BackupJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_datastore(self, datastore_id: str) -> Optional[Datastore]:
        """Get datastore with PBS server relationship."""
        result = await self.db_session.execute(
            select(Datastore)
            .options(selectinload(Datastore.pbs_server))
            .where(Datastore.id == datastore_id)
        )
        return result.scalar_one_or_none()
    
    async def _update_job_status(self, job: BackupJob, status: JobStatus) -> None:
        """Update job status."""
        job.status = status
        job.updated_at = datetime.utcnow()
    
    async def _update_job_progress(self, job: BackupJob, progress: int) -> None:
        """Update job progress."""
        job.progress = min(100, max(0, progress))
        job.updated_at = datetime.utcnow()
        await self.db_session.flush()
    
    def _generate_snapshot_name(self, vm_id: str, job_id: str) -> str:
        """Generate a unique snapshot name."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"vm-{vm_id}-{timestamp}-{job_id[:8]}"
    
    def _calculate_retention_days(self, retention_config: Dict[str, Any]) -> int:
        """Calculate retention period in days based on policy configuration."""
        # Use the longest retention period specified
        daily = retention_config.get('daily', 0)
        weekly = retention_config.get('weekly', 0) * 7
        monthly = retention_config.get('monthly', 0) * 30
        yearly = retention_config.get('yearly', 0) * 365
        
        return max(daily, weekly, monthly, yearly, 7)  # Minimum 7 days
    
    async def _schedule_verification(self, snapshot: BackupSnapshot) -> None:
        """Schedule backup verification (placeholder for now)."""
        # For now, just mark as pending verification
        # In a full implementation, this would schedule a verification task
        snapshot.verification_status = VerificationStatus.PENDING
        logger.info(f"Verification scheduled for snapshot {snapshot.id}")
    
    async def retry_failed_job(self, job_id: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Retry a failed backup job.
        
        Args:
            job_id: ID of the failed job to retry
            max_retries: Maximum number of retry attempts
            
        Returns:
            Retry execution results
        """
        job = await self._get_job_with_relationships(job_id)
        if not job:
            raise BackupJobRunnerError(f"Backup job {job_id} not found")
        
        if job.status != JobStatus.FAILED:
            raise BackupJobRunnerError(f"Job {job_id} is not in failed status")
        
        if job.retry_count >= max_retries:
            raise BackupJobRunnerError(f"Job {job_id} has exceeded maximum retries ({max_retries})")
        
        # Increment retry count
        job.retry_count += 1
        job.status = JobStatus.PENDING
        job.error_message = None
        job.start_time = None
        job.end_time = None
        job.progress = 0
        await self.db_session.flush()
        
        logger.info(f"Retrying backup job {job_id} (attempt {job.retry_count}/{max_retries})")
        
        # Execute the job
        return await self.execute_job(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running backup job.
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            True if successfully cancelled
        """
        job = await self._get_job_with_relationships(job_id)
        if not job:
            return False
        
        if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
            return False
        
        # Cancel running task if exists
        if job_id in self._running_jobs:
            task = self._running_jobs[job_id]
            task.cancel()
            del self._running_jobs[job_id]
        
        # Update job status
        job.status = JobStatus.CANCELLED
        job.end_time = datetime.utcnow()
        job.error_message = "Job cancelled by user"
        await self.db_session.flush()
        
        logger.info(f"Backup job {job_id} cancelled")
        return True
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a backup job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Job status information
        """
        job = await self._get_job_with_relationships(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.id,
            'status': job.status.value,
            'progress': job.progress,
            'start_time': job.start_time.isoformat() if job.start_time else None,
            'end_time': job.end_time.isoformat() if job.end_time else None,
            'error_message': job.error_message,
            'retry_count': job.retry_count,
            'snapshots_created': len(job.snapshots),
            'policy_name': job.policy.name if job.policy else None
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and cancel running jobs."""
        logger.info("Cleaning up backup job runner")
        
        # Cancel all running jobs
        for job_id, task in list(self._running_jobs.items()):
            logger.info(f"Cancelling running job: {job_id}")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._running_jobs.clear()
        logger.info("Backup job runner cleanup completed")