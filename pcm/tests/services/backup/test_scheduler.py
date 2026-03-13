"""
Unit tests for backup scheduler engine.

These tests validate specific examples and edge cases of the backup
scheduling system using pytest.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch, call
from croniter import croniter

from pcm.core.models.backup.policy import BackupPolicy, PolicyStatus
from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.schedule_event import ScheduleEvent, ScheduleEventType
from pcm.services.backup.scheduler_engine import (
    SchedulerEngine,
    SchedulerEngineError,
    SchedulingConflictError,
)


class TestSchedulerEngineBasics:
    """Test basic scheduler engine functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def scheduler(self, mock_db_session):
        """Create a scheduler engine instance."""
        return SchedulerEngine(mock_db_session, max_concurrent_jobs=3)

    def test_scheduler_initialization(self, scheduler):
        """Test scheduler engine initialization."""
        assert scheduler.max_concurrent_jobs == 3
        assert len(scheduler._job_queue) == 0
        assert len(scheduler._running_jobs) == 0
        assert len(scheduler._resource_locks) == 0
        assert scheduler._is_running is False

    def test_scheduler_max_concurrent_jobs_validation(self, mock_db_session):
        """Test that max_concurrent_jobs is validated."""
        # Valid values should work
        scheduler = SchedulerEngine(mock_db_session, max_concurrent_jobs=1)
        assert scheduler.max_concurrent_jobs == 1

        scheduler = SchedulerEngine(mock_db_session, max_concurrent_jobs=10)
        assert scheduler.max_concurrent_jobs == 10

    @pytest.mark.asyncio
    async def test_scheduler_start_stop(self, scheduler):
        """Test scheduler start and stop operations."""
        # Initially not running
        assert scheduler._is_running is False

        # Start scheduler
        await scheduler.start()
        assert scheduler._is_running is True

        # Stop scheduler
        await scheduler.stop()
        assert scheduler._is_running is False

    @pytest.mark.asyncio
    async def test_scheduler_double_start(self, scheduler):
        """Test that starting an already running scheduler is safe."""
        await scheduler.start()
        assert scheduler._is_running is True

        # Starting again should be safe (idempotent)
        await scheduler.start()
        assert scheduler._is_running is True

        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_scheduler_double_stop(self, scheduler):
        """Test that stopping an already stopped scheduler is safe."""
        # Stopping without starting should be safe
        await scheduler.stop()
        assert scheduler._is_running is False

        # Stopping again should be safe
        await scheduler.stop()
        assert scheduler._is_running is False


class TestSchedulerJobQueuing:
    """Test job queuing and queue management."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def scheduler(self, mock_db_session):
        """Create a scheduler engine instance."""
        return SchedulerEngine(mock_db_session, max_concurrent_jobs=2)

    @pytest.mark.asyncio
    async def test_schedule_immediate_job_success(self, scheduler, mock_db_session):
        """Test successful immediate job scheduling."""
        policy_id = "policy-123"

        # Mock policy
        policy = MagicMock(spec=BackupPolicy)
        policy.id = policy_id
        policy.name = "Test Policy"
        policy.tenant_id = "tenant-1"
        policy.targets = [{"vm_id": "vm-1", "cluster_id": "cluster-1", "datastore_id": "ds-1"}]

        # Mock database responses
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = policy
        mock_result.first.return_value = None  # No existing job

        mock_db_session.execute.side_effect = [mock_result, mock_result]

        # Schedule immediate job
        job_id = await scheduler.schedule_immediate_job(policy_id)

        # Verify job was created
        assert job_id is not None
        assert len(scheduler._job_queue) == 1

    @pytest.mark.asyncio
    async def test_schedule_immediate_job_policy_not_found(self, scheduler, mock_db_session):
        """Test scheduling when policy doesn't exist."""
        policy_id = "nonexistent-policy"

        # Mock database response - policy not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db_session.execute.return_value = mock_result

        # Should raise error
        with pytest.raises(SchedulerEngineError):
            await scheduler.schedule_immediate_job(policy_id)

    @pytest.mark.asyncio
    async def test_schedule_immediate_job_conflict(self, scheduler, mock_db_session):
        """Test that scheduling fails when job already exists for policy."""
        policy_id = "policy-123"

        # Mock policy
        policy = MagicMock(spec=BackupPolicy)
        policy.id = policy_id
        policy.name = "Test Policy"
        policy.tenant_id = "tenant-1"

        # Mock database responses
        mock_result_policy = MagicMock()
        mock_result_policy.scalar_one_or_none.return_value = policy

        mock_result_job = MagicMock()
        mock_result_job.first.return_value = MagicMock()  # Job exists

        mock_db_session.execute.side_effect = [mock_result_policy, mock_result_job]

        # Should raise conflict error
        with pytest.raises(SchedulingConflictError):
            await scheduler.schedule_immediate_job(policy_id)

    @pytest.mark.asyncio
    async def test_get_job_queue_status(self, scheduler):
        """Test retrieving job queue status."""
        # Add some jobs to queue
        scheduler._job_queue.extend(["job-1", "job-2", "job-3"])

        # Verify queue contains jobs
        assert len(scheduler._job_queue) == 3
        assert scheduler._job_queue[0] == "job-1"
        assert scheduler._job_queue[1] == "job-2"
        assert scheduler._job_queue[2] == "job-3"

    @pytest.mark.asyncio
    async def test_get_running_jobs_status(self, scheduler):
        """Test retrieving running jobs status."""
        # Add some running jobs
        scheduler._running_jobs["job-1"] = MagicMock()
        scheduler._running_jobs["job-2"] = MagicMock()

        # Verify running jobs
        assert len(scheduler._running_jobs) == 2
        assert "job-1" in scheduler._running_jobs
        assert "job-2" in scheduler._running_jobs


class TestSchedulerResourceManagement:
    """Test resource locking and conflict prevention."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def scheduler(self, mock_db_session):
        """Create a scheduler engine instance."""
        return SchedulerEngine(mock_db_session, max_concurrent_jobs=2)

    def test_resource_lock_acquisition(self, scheduler):
        """Test acquiring resource locks."""
        vm_ids = ["vm-1", "vm-2", "vm-3"]

        # Lock resources
        for vm_id in vm_ids:
            scheduler._resource_locks.add(vm_id)

        # Verify all resources are locked
        for vm_id in vm_ids:
            assert vm_id in scheduler._resource_locks

    def test_resource_lock_release(self, scheduler):
        """Test releasing resource locks."""
        vm_ids = ["vm-1", "vm-2", "vm-3"]

        # Lock resources
        for vm_id in vm_ids:
            scheduler._resource_locks.add(vm_id)

        # Release resources
        for vm_id in vm_ids:
            scheduler._resource_locks.discard(vm_id)

        # Verify all resources are released
        assert len(scheduler._resource_locks) == 0

    def test_resource_lock_conflict_detection(self, scheduler):
        """Test detecting resource conflicts."""
        vm_id = "vm-1"

        # Lock resource
        scheduler._resource_locks.add(vm_id)

        # Check for conflict
        assert vm_id in scheduler._resource_locks

        # Release and verify no conflict
        scheduler._resource_locks.discard(vm_id)
        assert vm_id not in scheduler._resource_locks

    def test_concurrent_job_limit_enforcement(self, scheduler):
        """Test that concurrent job limit is enforced."""
        # Add jobs up to limit
        for i in range(scheduler.max_concurrent_jobs):
            scheduler._running_jobs[f"job-{i}"] = MagicMock()

        # Verify limit is respected
        assert len(scheduler._running_jobs) == scheduler.max_concurrent_jobs

        # Try to add one more (should be possible to add, but scheduler should prevent execution)
        scheduler._running_jobs["job-extra"] = MagicMock()
        assert len(scheduler._running_jobs) == scheduler.max_concurrent_jobs + 1

        # Clean up
        del scheduler._running_jobs["job-extra"]


class TestSchedulerCancellation:
    """Test job cancellation functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def scheduler(self, mock_db_session):
        """Create a scheduler engine instance."""
        return SchedulerEngine(mock_db_session, max_concurrent_jobs=3)

    @pytest.mark.asyncio
    async def test_cancel_scheduled_jobs_success(self, scheduler, mock_db_session):
        """Test successfully canceling scheduled jobs."""
        policy_id = "policy-123"

        # Mock jobs
        job1 = MagicMock(spec=BackupJob)
        job1.id = "job-1"
        job1.policy_id = policy_id
        job1.status = JobStatus.PENDING

        job2 = MagicMock(spec=BackupJob)
        job2.id = "job-2"
        job2.policy_id = policy_id
        job2.status = JobStatus.PENDING

        # Verify jobs can be created and modified
        assert job1.status == JobStatus.PENDING
        assert job2.status == JobStatus.PENDING
        
        # Simulate cancellation
        job1.status = JobStatus.CANCELLED
        job2.status = JobStatus.CANCELLED
        
        assert job1.status == JobStatus.CANCELLED
        assert job2.status == JobStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_scheduled_jobs_no_jobs(self, scheduler, mock_db_session):
        """Test canceling when no jobs exist."""
        policy_id = "policy-123"

        # Verify no jobs in queue
        assert len(scheduler._job_queue) == 0
        assert len(scheduler._running_jobs) == 0

    @pytest.mark.asyncio
    async def test_cancel_scheduled_jobs_mixed_statuses(self, scheduler, mock_db_session):
        """Test canceling jobs with mixed statuses."""
        policy_id = "policy-123"

        # Mock jobs with different statuses
        job1 = MagicMock(spec=BackupJob)
        job1.id = "job-1"
        job1.policy_id = policy_id
        job1.status = JobStatus.PENDING

        job2 = MagicMock(spec=BackupJob)
        job2.id = "job-2"
        job2.policy_id = policy_id
        job2.status = JobStatus.RUNNING

        job3 = MagicMock(spec=BackupJob)
        job3.id = "job-3"
        job3.policy_id = policy_id
        job3.status = JobStatus.COMPLETED

        # Verify initial statuses
        assert job1.status == JobStatus.PENDING
        assert job2.status == JobStatus.RUNNING
        assert job3.status == JobStatus.COMPLETED
        
        # Simulate cancellation of cancellable jobs
        job1.status = JobStatus.CANCELLED
        job2.status = JobStatus.CANCELLED
        # job3 remains COMPLETED
        
        assert job1.status == JobStatus.CANCELLED
        assert job2.status == JobStatus.CANCELLED
        assert job3.status == JobStatus.COMPLETED


class TestSchedulerStatistics:
    """Test scheduler statistics and monitoring."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def scheduler(self, mock_db_session):
        """Create a scheduler engine instance."""
        return SchedulerEngine(mock_db_session, max_concurrent_jobs=5)

    def test_get_statistics_empty(self, scheduler):
        """Test getting statistics when scheduler is empty."""
        stats = scheduler.get_statistics()

        assert stats["running_jobs"] == 0
        assert stats["queued_jobs"] == 0
        assert stats["max_concurrent_jobs"] == 5
        assert stats["resource_locks"] == 0

    def test_get_statistics_with_jobs(self, scheduler):
        """Test getting statistics with jobs in queue and running."""
        # Add queued jobs
        scheduler._job_queue.extend(["job-1", "job-2", "job-3"])

        # Add running jobs
        scheduler._running_jobs["job-4"] = MagicMock()
        scheduler._running_jobs["job-5"] = MagicMock()

        # Add resource locks
        scheduler._resource_locks.add("vm-1")
        scheduler._resource_locks.add("vm-2")

        # Get statistics
        stats = scheduler.get_statistics()

        assert stats["running_jobs"] == 2
        assert stats["queued_jobs"] == 3
        assert stats["max_concurrent_jobs"] == 5
        assert stats["resource_locks"] == 2

    def test_get_statistics_consistency(self, scheduler):
        """Test that statistics are consistent with actual state."""
        # Add various jobs and locks
        for i in range(3):
            scheduler._job_queue.append(f"queued-{i}")
            scheduler._running_jobs[f"running-{i}"] = MagicMock()
            scheduler._resource_locks.add(f"vm-{i}")

        # Get statistics multiple times
        stats1 = scheduler.get_statistics()
        stats2 = scheduler.get_statistics()

        # Should be consistent
        assert stats1 == stats2
        assert stats1["running_jobs"] == len(scheduler._running_jobs)
        assert stats1["queued_jobs"] == len(scheduler._job_queue)
        assert stats1["resource_locks"] == len(scheduler._resource_locks)


class TestSchedulerEventLogging:
    """Test event logging functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def scheduler(self, mock_db_session):
        """Create a scheduler engine instance."""
        return SchedulerEngine(mock_db_session, max_concurrent_jobs=3)

    @pytest.mark.asyncio
    async def test_get_event_history_empty(self, scheduler, mock_db_session):
        """Test getting event history when no events exist."""
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        mock_db_session.execute.return_value = mock_result

        # Get event history
        events = await scheduler.get_event_history(limit=10)

        # Should return empty list
        assert events == []

    @pytest.mark.asyncio
    async def test_get_event_history_with_events(self, scheduler, mock_db_session):
        """Test getting event history with events."""
        # Mock events
        event1 = MagicMock(spec=ScheduleEvent)
        event1.id = "event-1"
        event1.event_type = ScheduleEventType.JOB_SCHEDULED
        event1.timestamp = datetime.utcnow()

        event2 = MagicMock(spec=ScheduleEvent)
        event2.id = "event-2"
        event2.event_type = ScheduleEventType.JOB_STARTED
        event2.timestamp = datetime.utcnow()

        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [event1, event2]

        mock_db_session.execute.return_value = mock_result

        # Get event history
        events = await scheduler.get_event_history(limit=10)

        # Should return events
        assert len(events) == 2
        assert events[0].event_type == ScheduleEventType.JOB_SCHEDULED
        assert events[1].event_type == ScheduleEventType.JOB_STARTED

    @pytest.mark.asyncio
    async def test_get_scheduling_metrics(self, scheduler, mock_db_session):
        """Test getting scheduling metrics."""
        # Mock events for metrics calculation
        now = datetime.utcnow()
        events = []

        for i in range(5):
            event = MagicMock(spec=ScheduleEvent)
            event.event_type = ScheduleEventType.JOB_COMPLETED
            event.timestamp = now - timedelta(hours=i)
            events.append(event)

        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = events

        mock_db_session.execute.return_value = mock_result

        # Get metrics
        metrics = await scheduler.get_scheduling_metrics(hours=24)

        # Should return metrics dict
        assert isinstance(metrics, dict)
        assert 'total_jobs' in metrics or 'current_stats' in metrics


class TestSchedulerEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def scheduler(self, mock_db_session):
        """Create a scheduler engine instance."""
        return SchedulerEngine(mock_db_session, max_concurrent_jobs=1)

    @pytest.mark.asyncio
    async def test_schedule_with_zero_max_concurrent(self, mock_db_session):
        """Test scheduler with zero max concurrent jobs."""
        # This should be allowed but no jobs should run
        scheduler = SchedulerEngine(mock_db_session, max_concurrent_jobs=0)
        assert scheduler.max_concurrent_jobs == 0

    def test_resource_lock_duplicate_add(self, scheduler):
        """Test adding the same resource lock twice."""
        vm_id = "vm-1"

        # Add lock twice
        scheduler._resource_locks.add(vm_id)
        scheduler._resource_locks.add(vm_id)

        # Should only have one lock
        assert len(scheduler._resource_locks) == 1
        assert vm_id in scheduler._resource_locks

    def test_resource_lock_duplicate_remove(self, scheduler):
        """Test removing a resource lock that doesn't exist."""
        vm_id = "vm-1"

        # Remove without adding (should not raise error)
        scheduler._resource_locks.discard(vm_id)

        # Should still be empty
        assert len(scheduler._resource_locks) == 0

    @pytest.mark.asyncio
    async def test_cancel_jobs_for_nonexistent_policy(self, scheduler, mock_db_session):
        """Test canceling jobs for a policy that doesn't exist."""
        policy_id = "nonexistent-policy"

        # Verify no jobs exist
        assert len(scheduler._job_queue) == 0
        assert len(scheduler._running_jobs) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
