"""
Backup Job Monitoring Service.

This module provides real-time monitoring of backup jobs, including
progress tracking, status updates, and completion detection.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.snapshot import BackupSnapshot
from pcm.core.models.backup.policy import BackupPolicy


logger = logging.getLogger(__name__)


class JobMonitoringError(Exception):
    """Base exception for job monitoring errors."""
    pass


class JobMonitor:
    """
    Real-time backup job monitoring service.
    
    Tracks job progress, status updates, and completion detection
    for all active backup jobs.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize job monitor.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._check_interval = 10  # Check every 10 seconds
        self._job_callbacks: Dict[str, List[callable]] = {}  # job_id -> callbacks
    
    async def start_monitoring(self) -> None:
        """
        Start the job monitoring service.
        """
        if self._is_running:
            logger.warning("Job monitoring service is already running")
            return
        
        logger.info("Starting backup job monitoring service")
        self._is_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self) -> None:
        """
        Stop the job monitoring service.
        """
        if not self._is_running:
            return
        
        logger.info("Stopping backup job monitoring service")
        self._is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
    
    async def _monitoring_loop(self) -> None:
        """
        Main monitoring loop that checks job status periodically.
        """
        logger.info("Job monitoring loop started")
        
        while self._is_running:
            try:
                await self._check_job_status()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                logger.info("Job monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in job monitoring loop: {e}")
                await asyncio.sleep(self._check_interval)
    
    async def _check_job_status(self) -> None:
        """
        Check status of all running jobs.
        """
        try:
            # Get all running jobs
            running_jobs = await self._get_running_jobs()
            
            if not running_jobs:
                return
            
            logger.debug(f"Monitoring {len(running_jobs)} running backup jobs")
            
            # Check status of each job
            for job in running_jobs:
                await self._update_job_status(job)
                
        except Exception as e:
            logger.error(f"Error checking job status: {e}")
    
    async def _get_running_jobs(self) -> List[BackupJob]:
        """
        Get list of currently running jobs.
        
        Returns:
            List of running backup jobs
        """
        result = await self.db_session.execute(
            select(BackupJob).where(
                BackupJob.status.in_([JobStatus.PENDING, JobStatus.RUNNING])
            )
        )
        
        return list(result.scalars().all())
    
    async def _update_job_status(self, job: BackupJob) -> None:
        """
        Update status of a single job.
        
        Args:
            job: BackupJob instance to update
        """
        try:
            # Check if job has timed out
            if job.status == JobStatus.RUNNING:
                if await self._has_job_timed_out(job):
                    logger.warning(f"Job {job.id} has timed out")
                    job.status = JobStatus.FAILED
                    job.error_message = "Job execution timeout"
                    await self.db_session.flush()
                    await self._trigger_callbacks(job.id, "timeout")
                    return
            
            # Check if job has completed
            if await self._has_job_completed(job):
                logger.info(f"Job {job.id} has completed")
                job.status = JobStatus.COMPLETED
                job.end_time = datetime.utcnow()
                await self.db_session.flush()
                await self._trigger_callbacks(job.id, "completed")
                return
            
            # Check if job has failed
            if await self._has_job_failed(job):
                logger.warning(f"Job {job.id} has failed")
                job.status = JobStatus.FAILED
                await self.db_session.flush()
                await self._trigger_callbacks(job.id, "failed")
                return
            
            # Update progress if available
            progress = await self._get_job_progress(job)
            if progress is not None and progress != job.progress:
                job.progress = progress
                await self.db_session.flush()
                await self._trigger_callbacks(job.id, "progress", {"progress": progress})
                
        except Exception as e:
            logger.error(f"Error updating job {job.id} status: {e}")
    
    async def _has_job_timed_out(self, job: BackupJob) -> bool:
        """
        Check if a job has timed out.
        
        Args:
            job: BackupJob instance to check
            
        Returns:
            True if job has timed out, False otherwise
        """
        if job.start_time is None:
            return False
        
        # Default timeout: 24 hours
        timeout_duration = timedelta(hours=24)
        elapsed = datetime.utcnow() - job.start_time
        
        return elapsed > timeout_duration
    
    async def _has_job_completed(self, job: BackupJob) -> bool:
        """
        Check if a job has completed.
        
        Args:
            job: BackupJob instance to check
            
        Returns:
            True if job has completed, False otherwise
        """
        # Check if all snapshots for this job are completed
        result = await self.db_session.execute(
            select(BackupSnapshot).where(
                BackupSnapshot.job_id == job.id
            )
        )
        
        snapshots = list(result.scalars().all())
        
        if not snapshots:
            return False
        
        # All snapshots should have completion status
        return all(s.verification_status is not None for s in snapshots)
    
    async def _has_job_failed(self, job: BackupJob) -> bool:
        """
        Check if a job has failed.
        
        Args:
            job: BackupJob instance to check
            
        Returns:
            True if job has failed, False otherwise
        """
        # Check if any snapshot has failed
        result = await self.db_session.execute(
            select(BackupSnapshot).where(
                BackupSnapshot.job_id == job.id
            )
        )
        
        snapshots = list(result.scalars().all())
        
        # If any snapshot has failed status, job has failed
        return any(s.verification_status == "failed" for s in snapshots)
    
    async def _get_job_progress(self, job: BackupJob) -> Optional[int]:
        """
        Get current progress of a job.
        
        Args:
            job: BackupJob instance
            
        Returns:
            Progress percentage (0-100) or None if not available
        """
        # Get all snapshots for this job
        result = await self.db_session.execute(
            select(BackupSnapshot).where(
                BackupSnapshot.job_id == job.id
            )
        )
        
        snapshots = list(result.scalars().all())
        
        if not snapshots:
            return None
        
        # Calculate progress based on completed snapshots
        completed = sum(1 for s in snapshots if s.verification_status is not None)
        progress = int((completed / len(snapshots)) * 100)
        
        return progress
    
    async def _trigger_callbacks(self, job_id: str, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Trigger registered callbacks for a job event.
        
        Args:
            job_id: Job ID
            event: Event type (completed, failed, progress, timeout)
            data: Optional event data
        """
        if job_id not in self._job_callbacks:
            return
        
        callbacks = self._job_callbacks[job_id]
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(job_id, event, data)
                else:
                    callback(job_id, event, data)
            except Exception as e:
                logger.error(f"Error triggering callback for job {job_id}: {e}")
    
    def register_callback(self, job_id: str, callback: callable) -> None:
        """
        Register a callback for job events.
        
        Args:
            job_id: Job ID to monitor
            callback: Callback function to call on events
        """
        if job_id not in self._job_callbacks:
            self._job_callbacks[job_id] = []
        
        self._job_callbacks[job_id].append(callback)
        logger.debug(f"Registered callback for job {job_id}")
    
    def unregister_callback(self, job_id: str, callback: callable) -> None:
        """
        Unregister a callback for job events.
        
        Args:
            job_id: Job ID
            callback: Callback function to remove
        """
        if job_id in self._job_callbacks:
            try:
                self._job_callbacks[job_id].remove(callback)
                if not self._job_callbacks[job_id]:
                    del self._job_callbacks[job_id]
                logger.debug(f"Unregistered callback for job {job_id}")
            except ValueError:
                pass
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status information or None if not found
        """
        result = await self.db_session.execute(
            select(BackupJob).where(BackupJob.id == job_id)
        )
        
        job = result.scalar_one_or_none()
        
        if not job:
            return None
        
        # Get snapshots for this job
        snapshots_result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.job_id == job_id)
        )
        
        snapshots = list(snapshots_result.scalars().all())
        
        return {
            'job_id': job.id,
            'policy_id': job.policy_id,
            'tenant_id': job.tenant_id,
            'status': job.status.value,
            'progress': job.progress,
            'start_time': job.start_time.isoformat() if job.start_time else None,
            'end_time': job.end_time.isoformat() if job.end_time else None,
            'error_message': job.error_message,
            'snapshot_count': len(snapshots),
            'completed_snapshots': sum(1 for s in snapshots if s.verification_status is not None),
            'failed_snapshots': sum(1 for s in snapshots if s.verification_status == "failed")
        }
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get current monitoring service status.
        
        Returns:
            Monitoring service status and statistics
        """
        # Get job statistics
        running_jobs = await self._get_running_jobs()
        
        # Get completed jobs from last 24 hours
        yesterday = datetime.utcnow() - timedelta(hours=24)
        result = await self.db_session.execute(
            select(BackupJob).where(
                and_(
                    BackupJob.status == JobStatus.COMPLETED,
                    BackupJob.end_time >= yesterday
                )
            )
        )
        
        completed_jobs = list(result.scalars().all())
        
        # Get failed jobs from last 24 hours
        result = await self.db_session.execute(
            select(BackupJob).where(
                and_(
                    BackupJob.status == JobStatus.FAILED,
                    BackupJob.end_time >= yesterday
                )
            )
        )
        
        failed_jobs = list(result.scalars().all())
        
        return {
            'service_status': 'running' if self._is_running else 'stopped',
            'check_interval': self._check_interval,
            'running_jobs': len(running_jobs),
            'completed_jobs_24h': len(completed_jobs),
            'failed_jobs_24h': len(failed_jobs),
            'registered_callbacks': sum(len(cbs) for cbs in self._job_callbacks.values()),
            'last_check_time': datetime.utcnow().isoformat()
        }
    
    async def get_job_history(self, tenant_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get job history for a tenant.
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum number of jobs to return
            
        Returns:
            List of job history entries
        """
        result = await self.db_session.execute(
            select(BackupJob)
            .where(BackupJob.tenant_id == tenant_id)
            .order_by(BackupJob.start_time.desc())
            .limit(limit)
        )
        
        jobs = list(result.scalars().all())
        
        history = []
        for job in jobs:
            history.append({
                'job_id': job.id,
                'policy_id': job.policy_id,
                'status': job.status.value,
                'progress': job.progress,
                'start_time': job.start_time.isoformat() if job.start_time else None,
                'end_time': job.end_time.isoformat() if job.end_time else None,
                'error_message': job.error_message
            })
        
        return history
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        await self.stop_monitoring()
        self._job_callbacks.clear()
