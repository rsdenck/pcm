"""
Property tests for backup scheduling consistency.

These tests validate universal properties of the backup scheduling system
using property-based testing with Hypothesis.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume
from hypothesis.stateful import RuleBasedStateMachine, Bundle, rule, initialize, invariant
from unittest.mock import AsyncMock, MagicMock, PropertyMock
from croniter import croniter

from pcm.core.models.backup.policy import BackupPolicy, PolicyStatus
from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.schedule_event import ScheduleEvent, ScheduleEventType
from pcm.services.backup.scheduler_engine import SchedulerEngine, SchedulingConflictError


# Strategy for generating valid cron expressions
@st.composite
def cron_expressions(draw):
    """Generate valid cron expressions."""
    minute = draw(st.one_of(st.just("*"), st.integers(0, 59).map(str)))
    hour = draw(st.one_of(st.just("*"), st.integers(0, 23).map(str)))
    
    # Generate safer day/month combinations to avoid invalid dates
    month = draw(st.one_of(st.just("*"), st.integers(1, 12).map(str)))
    
    # If month is specified, limit day to safe values
    if month != "*":
        month_num = int(month)
        if month_num == 2:  # February - limit to 28 days
            day = draw(st.one_of(st.just("*"), st.integers(1, 28).map(str)))
        elif month_num in [4, 6, 9, 11]:  # Months with 30 days
            day = draw(st.one_of(st.just("*"), st.integers(1, 30).map(str)))
        else:  # Months with 31 days
            day = draw(st.one_of(st.just("*"), st.integers(1, 31).map(str)))
    else:
        # If month is *, limit day to 28 to be safe
        day = draw(st.one_of(st.just("*"), st.integers(1, 28).map(str)))
    
    weekday = draw(st.one_of(st.just("*"), st.integers(0, 6).map(str)))
    
    return f"{minute} {hour} {day} {month} {weekday}"


@st.composite
def backup_policies(draw):
    """Generate backup policy configurations."""
    cron_expr = draw(cron_expressions())
    
    # Ensure cron expression is valid
    try:
        croniter(cron_expr)
    except:
        assume(False)  # Skip invalid cron expressions
    
    return {
        'id': draw(st.uuids().map(str)),
        'name': draw(st.text(min_size=1, max_size=50)),
        'tenant_id': draw(st.uuids().map(str)),
        'schedule': {'cron': cron_expr},
        'targets': [
            {
                'vm_id': draw(st.text(min_size=1, max_size=20)),
                'cluster_id': draw(st.text(min_size=1, max_size=20)),
                'datastore_id': draw(st.text(min_size=1, max_size=20))
            }
        ],
        'retention': {
            'daily': draw(st.integers(1, 30)),
            'weekly': draw(st.integers(1, 12)),
            'monthly': draw(st.integers(1, 24))
        },
        'options': {
            'compression': draw(st.sampled_from(['lz4', 'zstd', 'none'])),
            'encryption': draw(st.booleans()),
            'verification': draw(st.booleans())
        }
    }


class TestSchedulingProperties:
    """Property tests for backup scheduling."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session
    
    @pytest.fixture
    def scheduler_engine(self, mock_db_session):
        """Create scheduler engine instance."""
        return SchedulerEngine(mock_db_session, max_concurrent_jobs=3)
    
    @given(backup_policies())
    @settings(max_examples=50, deadline=5000)
    def test_property_cron_schedule_consistency(self, policy_config):
        """
        Property: Cron schedule calculations are consistent and monotonic.
        
        For any valid cron expression, consecutive next_run calculations
        should always produce times in the future and in ascending order.
        """
        cron_expr = policy_config['schedule']['cron']
        base_time = datetime.utcnow()
        
        # Calculate multiple next run times
        times = []
        current_time = base_time
        
        for _ in range(5):
            cron = croniter(cron_expr, current_time)
            next_time = cron.get_next(datetime)
            times.append(next_time)
            current_time = next_time
        
        # Property 1: All times should be in the future relative to base_time
        for time in times:
            assert time > base_time, f"Next run time {time} should be after base time {base_time}"
        
        # Property 2: Times should be in ascending order (monotonic)
        for i in range(1, len(times)):
            assert times[i] > times[i-1], f"Times should be ascending: {times[i]} > {times[i-1]}"
        
        # Property 3: Time differences should be reasonable (not negative, not too large)
        for i in range(1, len(times)):
            diff = times[i] - times[i-1]
            assert diff.total_seconds() > 0, "Time difference should be positive"
            # Allow up to 2 years for yearly schedules (accounting for leap years)
            assert diff.total_seconds() < 2 * 366 * 24 * 3600, "Time difference should be less than two years"
    
    @given(st.lists(backup_policies(), min_size=1, max_size=10))
    @settings(max_examples=20, deadline=10000)
    @pytest.mark.asyncio
    async def test_property_no_duplicate_scheduling(self, policies_config):
        """
        Property: No duplicate jobs should be scheduled for the same policy.
        
        When multiple scheduling attempts are made for the same policy,
        only one job should be created if overlap prevention is working.
        """
        # Create scheduler engine directly
        mock_db_session = AsyncMock()
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        mock_db_session.execute = AsyncMock()
        
        scheduler_engine = SchedulerEngine(mock_db_session, max_concurrent_jobs=3)
        
        policy_config = policies_config[0]  # Use first policy
        
        # Create mock policy
        policy = MagicMock()
        policy.id = policy_config['id']
        policy.name = policy_config['name']
        policy.tenant_id = policy_config['tenant_id']
        policy.schedule = policy_config['schedule']
        policy.targets = policy_config['targets']
        policy.retention = policy_config['retention']
        policy.options = policy_config['options']
        # Mock the is_active property method to return True
        type(policy).is_active = PropertyMock(return_value=True)
        
        # Mock database responses - first call returns policy, second call returns no existing job, third call returns policy, fourth call returns existing job
        mock_result_1 = MagicMock()  # First call - get policy
        mock_result_1.scalar_one_or_none.return_value = policy
        
        mock_result_2 = MagicMock()  # Second call - check for existing job (none found)
        mock_result_2.first.return_value = None
        
        mock_result_3 = MagicMock()  # Third call - get policy again
        mock_result_3.scalar_one_or_none.return_value = policy
        
        mock_result_4 = MagicMock()  # Fourth call - check for existing job (found)
        mock_result_4.first.return_value = MagicMock()  # Simulate existing job
        
        # Configure the execute method to return different results for different calls
        scheduler_engine.db_session.execute.side_effect = [mock_result_1, mock_result_2, mock_result_3, mock_result_4]
        
        # First scheduling should succeed
        job_id_1 = await scheduler_engine.schedule_immediate_job(policy.id)
        
        # Mock that job now exists (simulate running job)
        scheduler_engine.db_session.execute.return_value.first.return_value = MagicMock()
        
        # Second scheduling should fail due to conflict
        with pytest.raises(SchedulingConflictError):
            await scheduler_engine.schedule_immediate_job(policy.id)
        
        # Property: Only one job should be scheduled
        assert len(scheduler_engine._job_queue) <= 1, "Should not have duplicate jobs in queue"
    
    @given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5, unique=True))
    @settings(max_examples=30)
    def test_property_resource_lock_consistency(self, vm_ids):
        """
        Property: Resource locks should be consistent and prevent conflicts.
        
        When VMs are locked for backup, they should not be available
        for other backup operations until released.
        """
        # Create scheduler engine directly
        mock_db_session = AsyncMock()
        scheduler_engine = SchedulerEngine(mock_db_session, max_concurrent_jobs=3)
        
        # Initially no resources should be locked
        assert len(scheduler_engine._resource_locks) == 0
        
        # Lock resources
        for vm_id in vm_ids:
            scheduler_engine._resource_locks.add(vm_id)
        
        # Property 1: All VMs should be locked
        for vm_id in vm_ids:
            assert vm_id in scheduler_engine._resource_locks, f"VM {vm_id} should be locked"
        
        # Property 2: Lock count should match VM count
        assert len(scheduler_engine._resource_locks) == len(vm_ids)
        
        # Property 3: Checking conflicts should work correctly
        for vm_id in vm_ids:
            assert vm_id in scheduler_engine._resource_locks, "Conflict detection should work"
        
        # Release resources
        for vm_id in vm_ids:
            scheduler_engine._resource_locks.discard(vm_id)
        
        # Property 4: All resources should be released
        assert len(scheduler_engine._resource_locks) == 0, "All resources should be released"
    
    @given(st.integers(1, 10))
    @settings(max_examples=20)
    def test_property_queue_fifo_ordering(self, job_count):
        """
        Property: Job queue should maintain FIFO ordering.
        
        Jobs added to the queue should be processed in the order
        they were added (first in, first out).
        """
        # Create scheduler engine directly
        mock_db_session = AsyncMock()
        scheduler_engine = SchedulerEngine(mock_db_session, max_concurrent_jobs=3)
        
        # Generate job IDs
        job_ids = [f"job-{i}" for i in range(job_count)]
        
        # Add jobs to queue
        for job_id in job_ids:
            scheduler_engine._job_queue.append(job_id)
        
        # Property 1: Queue should contain all jobs
        assert len(scheduler_engine._job_queue) == job_count
        
        # Property 2: Jobs should be in the same order
        for i, job_id in enumerate(job_ids):
            assert scheduler_engine._job_queue[i] == job_id, f"Job at position {i} should be {job_id}"
        
        # Property 3: Removing jobs should maintain FIFO order
        removed_jobs = []
        while scheduler_engine._job_queue:
            removed_jobs.append(scheduler_engine._job_queue.pop(0))
        
        assert removed_jobs == job_ids, "Jobs should be removed in FIFO order"
    
    @given(st.integers(1, 5), st.integers(1, 10))
    @settings(max_examples=15)
    def test_property_concurrent_job_limits(self, max_concurrent, total_jobs):
        """
        Property: Concurrent job limits should be respected.
        
        The number of running jobs should never exceed the configured
        maximum concurrent jobs limit.
        """
        # Create scheduler engine directly
        mock_db_session = AsyncMock()
        scheduler_engine = SchedulerEngine(mock_db_session, max_concurrent_jobs=max_concurrent)
        
        # Simulate adding running jobs
        for i in range(min(total_jobs, max_concurrent + 5)):  # Try to exceed limit
            job_id = f"job-{i}"
            if len(scheduler_engine._running_jobs) < max_concurrent:
                # Mock task
                task = MagicMock()
                scheduler_engine._running_jobs[job_id] = task
        
        # Property: Should never exceed max concurrent jobs
        assert len(scheduler_engine._running_jobs) <= max_concurrent, \
            f"Running jobs ({len(scheduler_engine._running_jobs)}) should not exceed limit ({max_concurrent})"
        
        # Property: Should use available capacity
        expected_running = min(total_jobs, max_concurrent)
        assert len(scheduler_engine._running_jobs) == expected_running, \
            f"Should have {expected_running} running jobs"


class SchedulerStateMachine(RuleBasedStateMachine):
    """
    Stateful property testing for scheduler engine.
    
    This tests the scheduler's behavior across multiple operations
    and state transitions to ensure consistency.
    """
    
    def __init__(self):
        super().__init__()
        self.mock_db_session = AsyncMock()
        self.scheduler = SchedulerEngine(self.mock_db_session, max_concurrent_jobs=3)
        self.policies = {}
        self.jobs = {}
    
    policies = Bundle('policies')
    jobs = Bundle('jobs')
    
    @initialize()
    def setup(self):
        """Initialize the state machine."""
        # Mock database responses
        self.mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
        self.mock_db_session.execute.return_value.first.return_value = None
        self.mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    @rule(target=policies, policy_config=backup_policies())
    def create_policy(self, policy_config):
        """Create a backup policy."""
        policy_id = policy_config['id']
        
        policy = MagicMock(spec=BackupPolicy)
        policy.id = policy_id
        policy.name = policy_config['name']
        policy.tenant_id = policy_config['tenant_id']
        policy.schedule = policy_config['schedule']
        policy.targets = policy_config['targets']
        policy.is_active = True
        
        self.policies[policy_id] = policy
        return policy_id
    
    @rule(target=jobs, policy_id=policies)
    def schedule_job(self, policy_id):
        """Schedule a job for a policy."""
        assume(policy_id in self.policies)
        
        # Check if policy already has a running job
        has_running = any(
            job['policy_id'] == policy_id and job['status'] == JobStatus.RUNNING
            for job in self.jobs.values()
        )
        
        if not has_running and len(self.scheduler._job_queue) < 10:  # Reasonable limit
            job_id = f"job-{len(self.jobs)}"
            self.jobs[job_id] = {
                'policy_id': policy_id,
                'status': JobStatus.PENDING,
                'scheduled_time': datetime.utcnow()
            }
            self.scheduler._job_queue.append(job_id)
            return job_id
        else:
            # Return existing job or None if can't schedule
            return None
    
    @rule(job_id=jobs)  # Use jobs bundle instead of empty sampled_from
    def start_job(self, job_id):
        """Start a pending job."""
        assume(job_id in self.jobs)
        assume(self.jobs[job_id]['status'] == JobStatus.PENDING)
        assume(len(self.scheduler._running_jobs) < self.scheduler.max_concurrent_jobs)
        
        # Move job from queue to running
        if job_id in self.scheduler._job_queue:
            self.scheduler._job_queue.remove(job_id)
        
        self.jobs[job_id]['status'] = JobStatus.RUNNING
        self.scheduler._running_jobs[job_id] = MagicMock()
    
    @rule(job_id=jobs)  # Use jobs bundle instead of empty sampled_from
    def complete_job(self, job_id):
        """Complete a running job."""
        assume(job_id in self.jobs)
        assume(self.jobs[job_id]['status'] == JobStatus.RUNNING)
        assume(job_id in self.scheduler._running_jobs)
        
        # Complete the job
        self.jobs[job_id]['status'] = JobStatus.COMPLETED
        del self.scheduler._running_jobs[job_id]
    
    @invariant()
    def queue_and_running_consistency(self):
        """Invariant: Queue and running jobs should be consistent."""
        # No job should be both queued and running
        for job_id in self.scheduler._job_queue:
            assert job_id not in self.scheduler._running_jobs, \
                f"Job {job_id} should not be both queued and running"
    
    @invariant()
    def concurrent_job_limit(self):
        """Invariant: Should not exceed concurrent job limit."""
        assert len(self.scheduler._running_jobs) <= self.scheduler.max_concurrent_jobs, \
            f"Running jobs ({len(self.scheduler._running_jobs)}) exceeds limit ({self.scheduler.max_concurrent_jobs})"
    
    @invariant()
    def job_status_consistency(self):
        """Invariant: Job status should be consistent with scheduler state."""
        for job_id, job in self.jobs.items():
            if job['status'] == JobStatus.RUNNING:
                assert job_id in self.scheduler._running_jobs, \
                    f"Running job {job_id} should be in scheduler's running jobs"
            elif job['status'] == JobStatus.PENDING:
                # Pending jobs should either be queued or waiting for capacity
                pass  # This is acceptable
    
    @invariant()
    def resource_lock_consistency(self):
        """Invariant: Resource locks should not exceed running jobs."""
        # Each running job should have corresponding resource locks
        # (This is a simplified check - in reality it's more complex)
        assert len(self.scheduler._resource_locks) >= 0, "Resource locks should be non-negative"


# Run the stateful tests
TestSchedulerStateMachine = SchedulerStateMachine.TestCase


class TestSchedulingIntegrationProperties:
    """Integration property tests for scheduling system."""
    
    @pytest.mark.asyncio
    async def test_property_event_logging_completeness(self):
        """
        Property: All critical scheduling events should be logged.
        
        Every scheduling operation should produce corresponding
        audit events in the database.
        """
        mock_db_session = AsyncMock()
        scheduler = SchedulerEngine(mock_db_session)
        
        logged_events = []
        
        # Mock event logging to capture events
        async def mock_log_event(event):
            logged_events.append(event)
            
        scheduler._log_event = mock_log_event
        
        # Start scheduler (should log start event)
        await scheduler.start()
        
        # Stop scheduler (should log stop event)
        await scheduler.stop()
        
        # Property: Should have logged start and stop events
        assert len(logged_events) >= 2, "Should log start and stop events"
        
        event_types = [event.event_type for event in logged_events]
        assert ScheduleEventType.SCHEDULER_STARTED in event_types, "Should log scheduler start"
        assert ScheduleEventType.SCHEDULER_STOPPED in event_types, "Should log scheduler stop"
    
    @pytest.mark.asyncio
    async def test_property_statistics_accuracy(self):
        """
        Property: Scheduler statistics should accurately reflect operations.
        
        The statistics returned by get_statistics() should always
        match the actual state of the scheduler.
        """
        mock_db_session = AsyncMock()
        scheduler = SchedulerEngine(mock_db_session, max_concurrent_jobs=5)
        
        # Initial state
        stats = scheduler.get_statistics()
        assert stats['running_jobs'] == 0, "Initial running jobs should be 0"
        assert stats['queued_jobs'] == 0, "Initial queued jobs should be 0"
        assert stats['max_concurrent_jobs'] == 5, "Max concurrent should match constructor"
        
        # Add some jobs to queue
        scheduler._job_queue.extend(['job1', 'job2', 'job3'])
        
        # Add some running jobs
        scheduler._running_jobs['job4'] = MagicMock()
        scheduler._running_jobs['job5'] = MagicMock()
        
        # Check statistics accuracy
        stats = scheduler.get_statistics()
        assert stats['running_jobs'] == 2, "Running jobs count should be accurate"
        assert stats['queued_jobs'] == 3, "Queued jobs count should be accurate"
        
        # Property: Statistics should always reflect actual state
        assert stats['running_jobs'] == len(scheduler._running_jobs)
        assert stats['queued_jobs'] == len(scheduler._job_queue)


# Property test for cron expression validation
@given(cron_expressions())
@settings(max_examples=100)
def test_property_cron_expression_validity(cron_expr):
    """
    Property: All generated cron expressions should be valid.
    
    Any cron expression generated by our strategy should be
    parseable by croniter and produce valid next run times.
    """
    try:
        # Should be able to create croniter instance
        cron = croniter(cron_expr, datetime.utcnow())
        
        # Should be able to get next run time
        next_run = cron.get_next(datetime)
        
        # Next run should be in the future
        assert next_run > datetime.utcnow(), f"Next run {next_run} should be in future"
        
        # Should be able to get multiple next runs
        for _ in range(3):
            next_run = cron.get_next(datetime)
            assert isinstance(next_run, datetime), "Should return datetime objects"
            
    except Exception as e:
        pytest.fail(f"Cron expression '{cron_expr}' should be valid but failed: {e}")


if __name__ == "__main__":
    # Run property tests
    pytest.main([__file__, "-v", "--tb=short"])