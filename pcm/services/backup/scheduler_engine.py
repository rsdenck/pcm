"""
Backup Scheduler Engine for managing backup job scheduling.

This module provides cron-based scheduling, job queuing, resource management,
and overlap prevention for backup operations.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from croniter import croniter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func as sa_func
from sqlalchemy.orm import selectinload

from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.policy import BackupPolicy, PolicyStatus
from pcm.core.models.backup.schedule_event import ScheduleEvent, ScheduleEventType, ScheduleEventSeverity
from pcm.services.backup.job_runner import BackupJobRunner


logger = logging.getLogger(__name__)


class SchedulerEngineError(Exception):
    """Base exception for scheduler engine errors."""
    pass


class SchedulingConflictError(SchedulerEngineError):
    """Raised when scheduling conflicts occur."""
    pass


class SchedulerEngine:
    """
    Backup scheduler engine with cron-based scheduling.
    
    Provides job queuing, resource management, overlap prevention,
    and automated backup scheduling based on policy configurations.
    """
    
    def __init__(self, db_session: AsyncSession, max_concurrent_jobs: int = 5):
        """
        Initialize scheduler engine.
        
        Args:
            db_session: Database session for operations
            max_concurrent_jobs: Maximum concurrent backup jobs
        """
        self.db_session = db_session
        self.max_concurrent_jobs = max_concurrent_jobs
        self.job_runner = BackupJobRunner(db_session)
        
        # Internal state
        self._running_jobs: Dict[str, asyncio.Task] = {}
        self._job_queue: List[str] = []  # Queue of pending job IDs
        self._scheduler_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._instance_id = f"scheduler-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        # Resource management
        self._resource_locks: Set[str] = set()  # VM IDs currently being backed up
        
        # Scheduling statistics
        self._stats = {
            'jobs_scheduled': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'scheduling_conflicts': 0,
            'resource_conflicts': 0
        }
    
    async def start(self) -> None:
        """Start the scheduler engine."""
        if self._is_running:
            logger.warning("Scheduler engine is already running")
            return
        
        self._is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Log scheduler start event
        await self._log_event(
            ScheduleEvent.create_system_event(
                ScheduleEventType.SCHEDULER_STARTED,
                f"Backup scheduler engine started (instance: {self._instance_id})",
                ScheduleEventSeverity.INFO,
                {'max_concurrent_jobs': self.max_concurrent_jobs}
            )
        )
        
        logger.info("Backup scheduler engine started")
    
    async def stop(self) -> None:
        """Stop the scheduler engine."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running jobs
        await self.job_runner.cleanup()
        
        # Log scheduler stop event
        await self._log_event(
            ScheduleEvent.create_system_event(
                ScheduleEventType.SCHEDULER_STOPPED,
                f"Backup scheduler engine stopped (instance: {self._instance_id})",
                ScheduleEventSeverity.INFO,
                self.get_statistics()
            )
        )
        
        logger.info("Backup scheduler engine stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        logger.info("Scheduler loop started")
        
        while self._is_running:
            try:
                # Check for scheduled jobs
                await self._check_scheduled_jobs()
                
                # Process job queue
                await self._process_job_queue()
                
                # Cleanup completed jobs
                await self._cleanup_completed_jobs()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
        
        logger.info("Scheduler loop stopped")
    
    async def _check_scheduled_jobs(self) -> None:
        """Check for jobs that need to be scheduled."""
        now = datetime.utcnow()
        
        # Get active policies with next_run <= now
        result = await self.db_session.execute(
            select(BackupPolicy)
            .where(
                and_(
                    BackupPolicy.status == PolicyStatus.ACTIVE,
                    BackupPolicy.enabled == True,
                    or_(
                        BackupPolicy.next_run <= now,
                        BackupPolicy.next_run.is_(None)
                    )
                )
            )
        )
        
        policies = result.scalars().all()
        
        for policy in policies:
            try:
                await self._schedule_policy_job(policy)
            except Exception as e:
                logger.error(f"Failed to schedule job for policy {policy.id}: {e}")
                policy.mark_error(f"Scheduling failed: {str(e)}")
                await self.db_session.flush()
    
    async def _schedule_policy_job(self, policy: BackupPolicy) -> None:
        """Schedule a backup job for a policy."""
        # Check for overlap prevention
        if await self._has_running_job_for_policy(policy.id):
            logger.info(f"Skipping policy {policy.id} - job already running")
            self._stats['scheduling_conflicts'] += 1
            
            # Log scheduling conflict
            await self._log_event(
                ScheduleEvent.create_scheduling_conflict(
                    policy.id,
                    policy.tenant_id,
                    "Job already running for policy",
                    {'policy_name': policy.name}
                )
            )
            
            # Reschedule for next interval
            await self._calculate_next_run(policy)
            return
        
        # Check resource conflicts
        vm_ids = [target['vm_id'] for target in policy.targets]
        if any(vm_id in self._resource_locks for vm_id in vm_ids):
            logger.info(f"Skipping policy {policy.id} - resource conflict")
            self._stats['resource_conflicts'] += 1
            
            # Log resource conflict
            conflicting_vms = [vm_id for vm_id in vm_ids if vm_id in self._resource_locks]
            await self._log_event(
                ScheduleEvent.create_resource_conflict(
                    policy.id,
                    policy.tenant_id,
                    conflicting_vms,
                    {'policy_name': policy.name, 'all_targets': vm_ids}
                )
            )
            
            # Retry in 5 minutes
            policy.next_run = datetime.utcnow() + timedelta(minutes=5)
            await self.db_session.flush()
            return
        
        # Create backup job
        job = BackupJob(
            policy_id=policy.id,
            tenant_id=policy.tenant_id,
            scheduled_time=datetime.utcnow(),
            status=JobStatus.PENDING
        )
        
        self.db_session.add(job)
        await self.db_session.flush()
        await self.db_session.refresh(job)
        
        # Add to queue
        self._job_queue.append(job.id)
        self._stats['jobs_scheduled'] += 1
        
        # Log job scheduled event
        await self._log_event(
            ScheduleEvent.create_job_scheduled(
                job.id,
                policy.id,
                policy.tenant_id,
                job.scheduled_time,
                {
                    'policy_name': policy.name,
                    'target_count': len(policy.targets),
                    'queue_position': len(self._job_queue)
                }
            )
        )
        
        # Calculate next run time
        await self._calculate_next_run(policy)
        
        logger.info(f"Scheduled backup job {job.id} for policy {policy.name}")
    
    async def _calculate_next_run(self, policy: BackupPolicy) -> None:
        """Calculate next run time for a policy based on cron schedule."""
        schedule_config = policy.schedule
        cron_expression = schedule_config.get('cron')
        
        if not cron_expression:
            logger.error(f"Policy {policy.id} has no cron schedule")
            return
        
        try:
            # Parse cron expression and get next run time
            cron = croniter(cron_expression, datetime.utcnow())
            next_run = cron.get_next(datetime)
            
            policy.next_run = next_run
            policy.last_run = datetime.utcnow()
            await self.db_session.flush()
            
            logger.debug(f"Next run for policy {policy.id}: {next_run}")
            
        except Exception as e:
            logger.error(f"Failed to calculate next run for policy {policy.id}: {e}")
            policy.mark_error(f"Invalid cron expression: {cron_expression}")
            await self.db_session.flush()
    
    async def _process_job_queue(self) -> None:
        """Process queued backup jobs."""
        while (self._job_queue and 
               len(self._running_jobs) < self.max_concurrent_jobs):
            
            job_id = self._job_queue.pop(0)
            
            try:
                # Get job details
                job = await self._get_job_with_policy(job_id)
                if not job:
                    logger.warning(f"Job {job_id} not found in queue processing")
                    continue
                
                # Check resource availability
                vm_ids = [target['vm_id'] for target in job.policy.targets]
                if any(vm_id in self._resource_locks for vm_id in vm_ids):
                    # Put back in queue for later
                    self._job_queue.append(job_id)
                    break
                
                # Reserve resources
                for vm_id in vm_ids:
                    self._resource_locks.add(vm_id)
                
                # Start job execution
                task = asyncio.create_task(self._execute_job_with_cleanup(job_id, vm_ids))
                self._running_jobs[job_id] = task
                
                logger.info(f"Started execution of job {job_id}")
                
            except Exception as e:
                logger.error(f"Failed to start job {job_id}: {e}")
                # Remove from queue to prevent infinite retry
                continue
    
    async def _execute_job_with_cleanup(self, job_id: str, vm_ids: List[str]) -> None:
        """Execute job and cleanup resources."""
        try:
            result = await self.job_runner.execute_job(job_id)
            
            if result['success']:
                self._stats['jobs_completed'] += 1
                logger.info(f"Job {job_id} completed successfully")
            else:
                self._stats['jobs_failed'] += 1
                logger.warning(f"Job {job_id} failed")
                
        except Exception as e:
            self._stats['jobs_failed'] += 1
            logger.error(f"Job {job_id} execution failed: {e}")
            
        finally:
            # Release resources
            for vm_id in vm_ids:
                self._resource_locks.discard(vm_id)
            
            # Remove from running jobs
            if job_id in self._running_jobs:
                del self._running_jobs[job_id]
    
    async def _cleanup_completed_jobs(self) -> None:
        """Cleanup completed job tasks."""
        completed_jobs = []
        
        for job_id, task in self._running_jobs.items():
            if task.done():
                completed_jobs.append(job_id)
        
        for job_id in completed_jobs:
            task = self._running_jobs.pop(job_id)
            try:
                await task  # Ensure any exceptions are handled
            except Exception as e:
                logger.error(f"Error in completed job {job_id}: {e}")
    
    async def _has_running_job_for_policy(self, policy_id: str) -> bool:
        """Check if there's already a running job for a policy."""
        result = await self.db_session.execute(
            select(BackupJob)
            .where(
                and_(
                    BackupJob.policy_id == policy_id,
                    BackupJob.status.in_([JobStatus.PENDING, JobStatus.RUNNING])
                )
            )
        )
        
        return result.first() is not None
    
    async def _get_job_with_policy(self, job_id: str) -> Optional[BackupJob]:
        """Get job with policy relationship loaded."""
        result = await self.db_session.execute(
            select(BackupJob)
            .options(selectinload(BackupJob.policy))
            .where(BackupJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def schedule_immediate_job(self, policy_id: str) -> str:
        """
        Schedule an immediate backup job for a policy.
        
        Args:
            policy_id: Policy ID to schedule
            
        Returns:
            Job ID of the scheduled job
            
        Raises:
            SchedulerEngineError: If scheduling fails
        """
        # Get policy
        result = await self.db_session.execute(
            select(BackupPolicy).where(BackupPolicy.id == policy_id)
        )
        policy = result.scalar_one_or_none()
        
        if not policy:
            raise SchedulerEngineError(f"Policy {policy_id} not found")
        
        if not policy.is_active:
            raise SchedulerEngineError(f"Policy {policy_id} is not active")
        
        # Check for existing running job
        if await self._has_running_job_for_policy(policy_id):
            raise SchedulingConflictError(f"Policy {policy_id} already has a running job")
        
        # Create immediate job
        job = BackupJob(
            policy_id=policy_id,
            tenant_id=policy.tenant_id,
            scheduled_time=datetime.utcnow(),
            status=JobStatus.PENDING
        )
        
        self.db_session.add(job)
        await self.db_session.flush()
        await self.db_session.refresh(job)
        
        # Add to front of queue for immediate processing
        self._job_queue.insert(0, job.id)
        
        logger.info(f"Scheduled immediate job {job.id} for policy {policy.name}")
        return job.id
    
    async def cancel_scheduled_jobs(self, policy_id: str) -> int:
        """
        Cancel all scheduled jobs for a policy.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Number of jobs cancelled
        """
        # Cancel pending jobs in database
        result = await self.db_session.execute(
            update(BackupJob)
            .where(
                and_(
                    BackupJob.policy_id == policy_id,
                    BackupJob.status == JobStatus.PENDING
                )
            )
            .values(
                status=JobStatus.CANCELLED,
                error_message="Cancelled by scheduler",
                end_time=datetime.utcnow()
            )
        )
        
        cancelled_count = result.rowcount
        
        # Remove from queue
        self._job_queue = [job_id for job_id in self._job_queue 
                          if not await self._is_job_for_policy(job_id, policy_id)]
        
        # Cancel running jobs
        for job_id, task in list(self._running_jobs.items()):
            if await self._is_job_for_policy(job_id, policy_id):
                await self.job_runner.cancel_job(job_id)
                cancelled_count += 1
        
        await self.db_session.flush()
        
        logger.info(f"Cancelled {cancelled_count} jobs for policy {policy_id}")
        return cancelled_count
    
    async def _is_job_for_policy(self, job_id: str, policy_id: str) -> bool:
        """Check if a job belongs to a specific policy."""
        result = await self.db_session.execute(
            select(BackupJob.policy_id).where(BackupJob.id == job_id)
        )
        job_policy_id = result.scalar_one_or_none()
        return job_policy_id == policy_id
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            **self._stats,
            'running_jobs': len(self._running_jobs),
            'queued_jobs': len(self._job_queue),
            'resource_locks': len(self._resource_locks),
            'max_concurrent_jobs': self.max_concurrent_jobs,
            'is_running': self._is_running
        }
    
    async def get_job_queue_status(self) -> List[Dict[str, Any]]:
        """Get current job queue status."""
        queue_status = []
        
        for job_id in self._job_queue:
            job = await self._get_job_with_policy(job_id)
            if job:
                queue_status.append({
                    'job_id': job_id,
                    'policy_id': job.policy_id,
                    'policy_name': job.policy.name if job.policy else None,
                    'scheduled_time': job.scheduled_time.isoformat(),
                    'tenant_id': job.tenant_id
                })
        
        return queue_status
    
    async def get_running_jobs_status(self) -> List[Dict[str, Any]]:
        """Get status of currently running jobs."""
        running_status = []
        
        for job_id in self._running_jobs.keys():
            status = await self.job_runner.get_job_status(job_id)
            if status:
                running_status.append(status)
        
        return running_status
    
    async def _log_event(self, event: ScheduleEvent) -> None:
        """Log a schedule event to the database."""
        try:
            event.set_context(self._instance_id)
            self.db_session.add(event)
            await self.db_session.flush()
        except Exception as e:
            logger.error(f"Failed to log schedule event: {e}")
            # Don't raise - logging failures shouldn't break scheduling
    
    async def get_event_history(
        self, 
        tenant_id: Optional[str] = None,
        policy_id: Optional[str] = None,
        event_type: Optional[ScheduleEventType] = None,
        severity: Optional[ScheduleEventSeverity] = None,
        limit: int = 100
    ) -> List[ScheduleEvent]:
        """
        Get schedule event history with optional filtering.
        
        Args:
            tenant_id: Filter by tenant ID
            policy_id: Filter by policy ID
            event_type: Filter by event type
            severity: Filter by severity level
            limit: Maximum number of events to return
            
        Returns:
            List of schedule events
        """
        query = select(ScheduleEvent).order_by(ScheduleEvent.event_time.desc())
        
        if tenant_id:
            query = query.where(ScheduleEvent.tenant_id == tenant_id)
        if policy_id:
            query = query.where(ScheduleEvent.policy_id == policy_id)
        if event_type:
            query = query.where(ScheduleEvent.event_type == event_type)
        if severity:
            query = query.where(ScheduleEvent.severity == severity)
        
        query = query.limit(limit)
        
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
    
    async def get_scheduling_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get scheduling metrics for the specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Scheduling metrics dictionary
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get event counts by type
        result = await self.db_session.execute(
            select(ScheduleEvent.event_type, sa_func.count(ScheduleEvent.id))
            .where(ScheduleEvent.event_time >= since)
            .group_by(ScheduleEvent.event_type)
        )
        
        event_counts = dict(result.fetchall())
        
        # Get error counts by severity
        result = await self.db_session.execute(
            select(ScheduleEvent.severity, sa_func.count(ScheduleEvent.id))
            .where(
                and_(
                    ScheduleEvent.event_time >= since,
                    ScheduleEvent.severity.in_([ScheduleEventSeverity.ERROR, ScheduleEventSeverity.CRITICAL])
                )
            )
            .group_by(ScheduleEvent.severity)
        )
        
        error_counts = dict(result.fetchall())
        
        # Calculate success rate
        jobs_completed = event_counts.get(ScheduleEventType.JOB_COMPLETED, 0)
        jobs_failed = event_counts.get(ScheduleEventType.JOB_FAILED, 0)
        total_jobs = jobs_completed + jobs_failed
        success_rate = (jobs_completed / total_jobs * 100) if total_jobs > 0 else 0
        
        return {
            'period_hours': hours,
            'event_counts': event_counts,
            'error_counts': error_counts,
            'success_rate': success_rate,
            'total_jobs': total_jobs,
            'conflicts': {
                'scheduling': event_counts.get(ScheduleEventType.SCHEDULING_CONFLICT, 0),
                'resource': event_counts.get(ScheduleEventType.RESOURCE_CONFLICT, 0)
            },
            'current_stats': self.get_statistics()
        }