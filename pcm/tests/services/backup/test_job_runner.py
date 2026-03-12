"""
Unit tests for Backup Job Runner.

Tests job execution, progress tracking, error handling, and retry mechanisms.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.snapshot import BackupSnapshot, VerificationStatus
from pcm.core.models.backup.policy import BackupPolicy, PolicyStatus
from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
from pcm.core.models.backup.datastore import Datastore, DatastoreStatus
from pcm.services.backup.job_runner import (
    BackupJobRunner,
    BackupJobRunnerError,
    BackupExecutionError
)


class TestBackupJobRunner:
    """Test cases for BackupJobRunner."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session
    
    @pytest.fixture
    def job_runner(self, mock_db_session):
        """Create BackupJobRunner instance."""
        return BackupJobRunner(mock_db_session)
    
    @pytest.fixture
    def sample_policy(self):
        """Sample backup policy."""
        policy = MagicMock(spec=BackupPolicy)
        policy.id = "policy-123"
        policy.name = "Test Policy"
        policy.targets = [
            {
                'vm_id': 'vm-100',
                'cluster_id': 'cluster-1',
                'datastore_id': 'datastore-1'
            }
        ]
        policy.options = {
            'compression': 'lz4',
            'encryption': False,
            'verification': True,
            'bandwidth_limit': 0
        }
        policy.retention = {
            'daily': 7,
            'weekly': 4,
            'monthly': 12
        }
        policy.update_statistics = MagicMock()
        return policy
    
    @pytest.fixture
    def sample_job(self, sample_policy):
        """Sample backup job."""
        job = MagicMock(spec=BackupJob)
        job.id = "job-456"
        job.tenant_id = "tenant-789"
        job.status = JobStatus.PENDING
        job.progress = 0
        job.retry_count = 0
        job.policy = sample_policy
        job.snapshots = []
        job.start_time = None
        job.end_time = None
        job.error_message = None
        return job
    
    @pytest.fixture
    def sample_datastore(self):
        """Sample datastore with PBS server."""
        pbs_server = MagicMock(spec=PBSServer)
        pbs_server.id = "pbs-1"
        pbs_server.name = "test-pbs"
        
        datastore = MagicMock(spec=Datastore)
        datastore.id = "datastore-1"
        datastore.name = "backup-store"
        datastore.pbs_server = pbs_server
        return datastore
    
    @pytest.mark.asyncio
    async def test_execute_job_success(self, job_runner, sample_job, sample_datastore):
        """Test successful job execution."""
        # Mock database queries
        mock_job_result = MagicMock()
        mock_job_result.scalar_one_or_none.return_value = sample_job
        
        mock_datastore_result = MagicMock()
        mock_datastore_result.scalar_one_or_none.return_value = sample_datastore
        
        job_runner.db_session.execute.side_effect = [
            mock_job_result,  # Get job
            mock_datastore_result  # Get datastore
        ]
        
        # Mock PBS client
        mock_backup_result = {
            'success': True,
            'size': 1024 * 1024 * 1024,
            'compressed_size': 512 * 1024 * 1024,
            'duration': 300,
            'transfer_rate': 100 * 1024 * 1024
        }
        
        with patch('pcm.services.backup.job_runner.PBSAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.create_backup.return_value = mock_backup_result
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await job_runner.execute_job(sample_job.id)
        
        # Verify results
        assert result['success'] is True
        assert result['job_id'] == sample_job.id
        assert result['targets_processed'] == 1
        assert result['targets_successful'] == 1
        
        # Verify job status updates
        assert sample_job.status == JobStatus.COMPLETED
        assert sample_job.start_time is not None
        assert sample_job.end_time is not None
        
        # Verify policy statistics update
        sample_job.policy.update_statistics.assert_called_once_with(True)
    
    @pytest.mark.asyncio
    async def test_execute_job_not_found(self, job_runner):
        """Test job execution with non-existent job."""
        # Mock job not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        job_runner.db_session.execute.return_value = mock_result
        
        with pytest.raises(BackupJobRunnerError, match="not found"):
            await job_runner.execute_job("non-existent-job")
    
    @pytest.mark.asyncio
    async def test_execute_job_wrong_status(self, job_runner, sample_job):
        """Test job execution with wrong status."""
        sample_job.status = JobStatus.RUNNING
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        job_runner.db_session.execute.return_value = mock_result
        
        with pytest.raises(BackupJobRunnerError, match="not in pending status"):
            await job_runner.execute_job(sample_job.id)
    
    @pytest.mark.asyncio
    async def test_execute_job_already_running(self, job_runner, sample_job):
        """Test job execution when job is already running."""
        # Add job to running jobs
        job_runner._running_jobs[sample_job.id] = AsyncMock()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        job_runner.db_session.execute.return_value = mock_result
        
        with pytest.raises(BackupJobRunnerError, match="already running"):
            await job_runner.execute_job(sample_job.id)
    
    @pytest.mark.asyncio
    async def test_execute_job_backup_failure(self, job_runner, sample_job, sample_datastore):
        """Test job execution with backup failure."""
        # Mock database queries
        mock_job_result = MagicMock()
        mock_job_result.scalar_one_or_none.return_value = sample_job
        
        mock_datastore_result = MagicMock()
        mock_datastore_result.scalar_one_or_none.return_value = sample_datastore
        
        job_runner.db_session.execute.side_effect = [
            mock_job_result,  # Get job
            mock_datastore_result  # Get datastore
        ]
        
        # Mock PBS client failure
        mock_backup_result = {
            'success': False,
            'error': 'Backup operation failed'
        }
        
        with patch('pcm.services.backup.job_runner.PBSAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.create_backup.return_value = mock_backup_result
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await job_runner.execute_job(sample_job.id)
        
        # Verify results
        assert result['success'] is False
        assert result['targets_successful'] == 0
        
        # Verify job status
        assert sample_job.status == JobStatus.FAILED
        assert sample_job.error_message == "All backup targets failed"
        
        # Verify policy statistics update
        sample_job.policy.update_statistics.assert_called_once_with(False)
    
    @pytest.mark.asyncio
    async def test_execute_job_datastore_not_found(self, job_runner, sample_job):
        """Test job execution with missing datastore."""
        # Mock job found but datastore not found
        mock_job_result = MagicMock()
        mock_job_result.scalar_one_or_none.return_value = sample_job
        
        mock_datastore_result = MagicMock()
        mock_datastore_result.scalar_one_or_none.return_value = None
        
        job_runner.db_session.execute.side_effect = [
            mock_job_result,  # Get job
            mock_datastore_result  # Get datastore (not found)
        ]
        
        # Should complete but with failed targets
        result = await job_runner.execute_job(sample_job.id)
        
        # Verify job marked as failed due to all targets failing
        assert result['success'] is False
        assert result['targets_successful'] == 0
        assert sample_job.status == JobStatus.FAILED
        assert sample_job.error_message == "All backup targets failed"
    
    @pytest.mark.asyncio
    async def test_retry_failed_job_success(self, job_runner, sample_job, sample_datastore):
        """Test successful retry of failed job."""
        sample_job.status = JobStatus.FAILED
        sample_job.retry_count = 1
        sample_job.error_message = "Previous failure"
        
        # Mock database queries for retry
        mock_job_result = MagicMock()
        mock_job_result.scalar_one_or_none.return_value = sample_job
        
        mock_datastore_result = MagicMock()
        mock_datastore_result.scalar_one_or_none.return_value = sample_datastore
        
        job_runner.db_session.execute.side_effect = [
            mock_job_result,  # Get job for retry
            mock_job_result,  # Get job for execution
            mock_datastore_result  # Get datastore
        ]
        
        # Mock successful backup
        mock_backup_result = {
            'success': True,
            'size': 1024 * 1024 * 1024,
            'compressed_size': 512 * 1024 * 1024,
            'duration': 300,
            'transfer_rate': 100 * 1024 * 1024
        }
        
        with patch('pcm.services.backup.job_runner.PBSAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.create_backup.return_value = mock_backup_result
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await job_runner.retry_failed_job(sample_job.id)
        
        # Verify retry incremented
        assert sample_job.retry_count == 2
        
        # Verify successful execution
        assert result['success'] is True
        assert sample_job.status == JobStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_retry_failed_job_max_retries(self, job_runner, sample_job):
        """Test retry with maximum retries exceeded."""
        sample_job.status = JobStatus.FAILED
        sample_job.retry_count = 3
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        job_runner.db_session.execute.return_value = mock_result
        
        with pytest.raises(BackupJobRunnerError, match="exceeded maximum retries"):
            await job_runner.retry_failed_job(sample_job.id, max_retries=3)
    
    @pytest.mark.asyncio
    async def test_retry_failed_job_wrong_status(self, job_runner, sample_job):
        """Test retry with job not in failed status."""
        sample_job.status = JobStatus.COMPLETED
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        job_runner.db_session.execute.return_value = mock_result
        
        with pytest.raises(BackupJobRunnerError, match="not in failed status"):
            await job_runner.retry_failed_job(sample_job.id)
    
    @pytest.mark.asyncio
    async def test_cancel_job_success(self, job_runner, sample_job):
        """Test successful job cancellation."""
        sample_job.status = JobStatus.RUNNING
        
        # Add running task
        mock_task = AsyncMock()
        job_runner._running_jobs[sample_job.id] = mock_task
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        job_runner.db_session.execute.return_value = mock_result
        
        result = await job_runner.cancel_job(sample_job.id)
        
        assert result is True
        assert sample_job.status == JobStatus.CANCELLED
        assert sample_job.error_message == "Job cancelled by user"
        assert sample_job.end_time is not None
        
        # Verify task was cancelled
        mock_task.cancel.assert_called_once()
        assert sample_job.id not in job_runner._running_jobs
    
    @pytest.mark.asyncio
    async def test_cancel_job_not_found(self, job_runner):
        """Test cancelling non-existent job."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        job_runner.db_session.execute.return_value = mock_result
        
        result = await job_runner.cancel_job("non-existent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cancel_job_wrong_status(self, job_runner, sample_job):
        """Test cancelling job with wrong status."""
        sample_job.status = JobStatus.COMPLETED
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        job_runner.db_session.execute.return_value = mock_result
        
        result = await job_runner.cancel_job(sample_job.id)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_job_status(self, job_runner, sample_job):
        """Test getting job status."""
        sample_job.status = JobStatus.RUNNING
        sample_job.progress = 50
        sample_job.start_time = datetime.utcnow()
        sample_job.snapshots = [MagicMock(), MagicMock()]
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_job
        job_runner.db_session.execute.return_value = mock_result
        
        status = await job_runner.get_job_status(sample_job.id)
        
        assert status['job_id'] == sample_job.id
        assert status['status'] == JobStatus.RUNNING.value
        assert status['progress'] == 50
        assert status['snapshots_created'] == 2
        assert status['policy_name'] == sample_job.policy.name
    
    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self, job_runner):
        """Test getting status for non-existent job."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        job_runner.db_session.execute.return_value = mock_result
        
        status = await job_runner.get_job_status("non-existent")
        assert status is None
    
    @pytest.mark.asyncio
    async def test_cleanup(self, job_runner):
        """Test cleanup of running jobs."""
        # Add some running tasks (use real asyncio tasks)
        async def dummy_task():
            await asyncio.sleep(10)
        
        task1 = asyncio.create_task(dummy_task())
        task2 = asyncio.create_task(dummy_task())
        
        job_runner._running_jobs = {
            'job1': task1,
            'job2': task2
        }
        
        await job_runner.cleanup()
        
        # Verify all tasks were cancelled
        assert task1.cancelled()
        assert task2.cancelled()
        
        # Verify running jobs cleared
        assert len(job_runner._running_jobs) == 0
    
    def test_generate_snapshot_name(self, job_runner):
        """Test snapshot name generation."""
        vm_id = "vm-100"
        job_id = "job-456789"
        
        name = job_runner._generate_snapshot_name(vm_id, job_id)
        
        assert name.startswith("vm-vm-100-")
        assert name.endswith("-job-4567")
        # Format: vm-{vm_id}-{timestamp}-{job_id_prefix}
        parts = name.split('-')
        assert len(parts) == 6  # vm, vm, 100, timestamp, job, 4567
    
    def test_calculate_retention_days(self, job_runner):
        """Test retention days calculation."""
        # Test with daily retention
        retention_config = {'daily': 30}
        days = job_runner._calculate_retention_days(retention_config)
        assert days == 30
        
        # Test with weekly retention (longer)
        retention_config = {'daily': 7, 'weekly': 8}
        days = job_runner._calculate_retention_days(retention_config)
        assert days == 56  # 8 weeks * 7 days
        
        # Test with yearly retention (longest)
        retention_config = {'daily': 7, 'weekly': 4, 'monthly': 12, 'yearly': 2}
        days = job_runner._calculate_retention_days(retention_config)
        assert days == 730  # 2 years * 365 days
        
        # Test with empty config (minimum 7 days)
        retention_config = {}
        days = job_runner._calculate_retention_days(retention_config)
        assert days == 7


class TestBackupJobRunnerIntegration:
    """Integration tests for backup job runner."""
    
    @pytest.mark.asyncio
    async def test_multiple_targets_execution(self):
        """Test execution with multiple backup targets."""
        mock_db_session = AsyncMock(spec=AsyncSession)
        job_runner = BackupJobRunner(mock_db_session)
        
        # Create job with multiple targets
        policy = MagicMock(spec=BackupPolicy)
        policy.targets = [
            {'vm_id': 'vm-100', 'cluster_id': 'cluster-1', 'datastore_id': 'ds-1'},
            {'vm_id': 'vm-200', 'cluster_id': 'cluster-1', 'datastore_id': 'ds-1'},
            {'vm_id': 'vm-300', 'cluster_id': 'cluster-2', 'datastore_id': 'ds-2'}
        ]
        policy.options = {'compression': 'lz4', 'encryption': False, 'verification': True}
        policy.retention = {'daily': 7}
        policy.update_statistics = MagicMock()
        
        job = MagicMock(spec=BackupJob)
        job.id = "multi-target-job"
        job.tenant_id = "tenant-1"
        job.status = JobStatus.PENDING
        job.policy = policy
        job.snapshots = []
        
        # Mock database and PBS operations
        mock_job_result = MagicMock()
        mock_job_result.scalar_one_or_none.return_value = job
        
        mock_datastore = MagicMock(spec=Datastore)
        mock_datastore.name = "backup-store"
        mock_datastore.pbs_server = MagicMock(spec=PBSServer)
        
        mock_datastore_result = MagicMock()
        mock_datastore_result.scalar_one_or_none.return_value = mock_datastore
        
        mock_db_session.execute.side_effect = [
            mock_job_result,  # Get job
            mock_datastore_result,  # Get datastore for target 1
            mock_datastore_result,  # Get datastore for target 2
            mock_datastore_result   # Get datastore for target 3
        ]
        
        # Mock successful backups
        mock_backup_result = {
            'success': True,
            'size': 1024 * 1024 * 1024,
            'compressed_size': 512 * 1024 * 1024,
            'duration': 300
        }
        
        with patch('pcm.services.backup.job_runner.PBSAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.create_backup.return_value = mock_backup_result
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await job_runner.execute_job(job.id)
        
        # Verify all targets processed
        assert result['targets_processed'] == 3
        assert result['targets_successful'] == 3
        assert result['success'] is True
        
        # Verify progress updates (should reach 100%)
        assert job.progress == 100