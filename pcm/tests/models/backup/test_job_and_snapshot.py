import pytest
from datetime import datetime, timedelta
from pcm.core.models.backup import BackupJob, JobStatus, BackupSnapshot, VerificationStatus


class TestBackupJob:
    """Test cases for BackupJob model."""

    def test_job_creation(self):
        """Test basic job creation."""
        scheduled_time = datetime.utcnow()
        
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-123",
            scheduled_time=scheduled_time
        )
        
        assert job.policy_id == "policy-123"
        assert job.tenant_id == "tenant-123"
        assert job.status == JobStatus.PENDING
        assert job.scheduled_time == scheduled_time
        assert job.progress == 0
        assert job.retry_count == 0
        assert job.start_time is None
        assert job.end_time is None

    def test_job_status_transitions(self):
        """Test job status transitions."""
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-123",
            scheduled_time=datetime.utcnow()
        )
        
        # Test status changes
        job.status = JobStatus.RUNNING
        assert job.status == JobStatus.RUNNING
        
        job.status = JobStatus.COMPLETED
        assert job.status == JobStatus.COMPLETED

    def test_job_progress_tracking(self):
        """Test job progress tracking."""
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-123",
            scheduled_time=datetime.utcnow()
        )
        
        # Test progress updates
        job.progress = 50
        assert job.progress == 50
        
        job.progress = 100
        assert job.progress == 100

    def test_job_error_handling(self):
        """Test job error handling."""
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-123",
            scheduled_time=datetime.utcnow()
        )
        
        # Test error tracking
        job.status = JobStatus.FAILED
        job.error_message = "Backup failed due to network error"
        job.retry_count = 1
        
        assert job.status == JobStatus.FAILED
        assert job.error_message == "Backup failed due to network error"
        assert job.retry_count == 1

    def test_job_size_tracking(self):
        """Test job size tracking."""
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-123",
            scheduled_time=datetime.utcnow()
        )
        
        # Test size information
        job.backup_size = 1024 * 1024 * 1024  # 1GB
        job.transferred_size = 512 * 1024 * 1024  # 512MB
        
        assert job.backup_size == 1024 * 1024 * 1024
        assert job.transferred_size == 512 * 1024 * 1024


class TestBackupSnapshot:
    """Test cases for BackupSnapshot model."""

    def test_snapshot_creation(self):
        """Test basic snapshot creation."""
        snapshot_time = datetime.utcnow()
        
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-123",
            vm_id="vm-456",
            cluster_id="cluster-789",
            snapshot_time=snapshot_time,
            snapshot_name="vm-456-20241219-120000",
            datastore_id="ds-123",
            path="/backups/vm-456/vm-456-20241219-120000.pxar"
        )
        
        assert snapshot.job_id == "job-123"
        assert snapshot.tenant_id == "tenant-123"
        assert snapshot.vm_id == "vm-456"
        assert snapshot.cluster_id == "cluster-789"
        assert snapshot.snapshot_time == snapshot_time
        assert snapshot.snapshot_name == "vm-456-20241219-120000"
        assert snapshot.datastore_id == "ds-123"
        assert snapshot.path == "/backups/vm-456/vm-456-20241219-120000.pxar"
        assert snapshot.verification_status == VerificationStatus.PENDING
        assert snapshot.is_protected is False
        assert snapshot.has_errors is False

    def test_snapshot_verification_methods(self):
        """Test snapshot verification methods."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-123",
            vm_id="vm-456",
            cluster_id="cluster-789",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id="ds-123",
            path="/test/path"
        )
        
        # Test mark_verified
        checksum = "sha256:abcd1234"
        snapshot.mark_verified(checksum)
        
        assert snapshot.verification_status == VerificationStatus.VERIFIED
        assert snapshot.checksum == checksum
        assert snapshot.verification_time is not None
        assert snapshot.verification_error is None
        assert snapshot.is_verified is True

    def test_snapshot_verification_failure(self):
        """Test snapshot verification failure."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-123",
            vm_id="vm-456",
            cluster_id="cluster-789",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id="ds-123",
            path="/test/path"
        )
        
        # Test mark_verification_failed
        error_msg = "Checksum mismatch"
        snapshot.mark_verification_failed(error_msg)
        
        assert snapshot.verification_status == VerificationStatus.FAILED
        assert snapshot.verification_error == error_msg
        assert snapshot.verification_time is not None
        assert snapshot.is_verified is False

    def test_snapshot_protection_methods(self):
        """Test snapshot protection methods."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-123",
            vm_id="vm-456",
            cluster_id="cluster-789",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id="ds-123",
            path="/test/path"
        )
        
        # Test protect
        reason = "Critical system backup"
        snapshot.protect(reason)
        
        assert snapshot.is_protected is True
        assert snapshot.protection_reason == reason
        
        # Test unprotect
        snapshot.unprotect()
        
        assert snapshot.is_protected is False
        assert snapshot.protection_reason is None

    def test_snapshot_retention_logic(self):
        """Test snapshot retention logic."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-123",
            vm_id="vm-456",
            cluster_id="cluster-789",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id="ds-123",
            path="/test/path"
        )
        
        # Test not expired (no retention date)
        assert snapshot.is_expired is False
        assert snapshot.can_be_deleted is False
        
        # Test expired but protected
        snapshot.retention_date = datetime.utcnow() - timedelta(days=1)
        snapshot.protect("Important backup")
        
        assert snapshot.is_expired is True
        assert snapshot.can_be_deleted is False
        
        # Test expired and not protected
        snapshot.unprotect()
        
        assert snapshot.is_expired is True
        assert snapshot.can_be_deleted is True

    def test_snapshot_size_methods(self):
        """Test snapshot size methods."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-123",
            vm_id="vm-456",
            cluster_id="cluster-789",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id="ds-123",
            path="/test/path"
        )
        
        # Test update_size_info
        size = 1024 * 1024 * 1024  # 1GB
        compressed_size = 512 * 1024 * 1024  # 512MB
        deduplicated_size = 256 * 1024 * 1024  # 256MB
        
        snapshot.update_size_info(size, compressed_size, deduplicated_size)
        
        assert snapshot.size == size
        assert snapshot.compressed_size == compressed_size
        assert snapshot.deduplicated_size == deduplicated_size

    def test_snapshot_compression_ratio(self):
        """Test snapshot compression ratio calculation."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-123",
            vm_id="vm-456",
            cluster_id="cluster-789",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id="ds-123",
            path="/test/path"
        )
        
        # Test with no sizes
        assert snapshot.compression_ratio is None
        assert snapshot.deduplication_ratio is None
        
        # Test with sizes
        snapshot.size = 1000
        snapshot.compressed_size = 500
        snapshot.deduplicated_size = 250
        
        assert snapshot.compression_ratio == 0.5
        assert snapshot.deduplication_ratio == 0.5

    def test_snapshot_error_handling(self):
        """Test snapshot error handling."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-123",
            vm_id="vm-456",
            cluster_id="cluster-789",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id="ds-123",
            path="/test/path"
        )
        
        # Test mark_error
        error_msg = "Storage error occurred"
        snapshot.mark_error(error_msg)
        
        assert snapshot.has_errors is True
        assert snapshot.error_message == error_msg
        
        # Test clear_error
        snapshot.clear_error()
        
        assert snapshot.has_errors is False
        assert snapshot.error_message is None
class TestBackupJobConstraints:
    """Test cases for BackupJob model constraints and validation."""

    def test_job_tenant_isolation_constraints(self):
        """Test that jobs properly enforce tenant isolation."""
        # Create jobs for different tenants
        job1 = BackupJob(
            policy_id="policy-1",
            tenant_id="tenant-1",
            scheduled_time=datetime.utcnow()
        )
        
        job2 = BackupJob(
            policy_id="policy-2",
            tenant_id="tenant-2",
            scheduled_time=datetime.utcnow()
        )
        
        # Verify tenant isolation
        assert job1.tenant_id != job2.tenant_id
        assert job1.policy_id != job2.policy_id
        
        # Jobs can have same policy for same tenant
        job3 = BackupJob(
            policy_id="policy-1",  # Same policy as job1
            tenant_id="tenant-1",  # Same tenant as job1
            scheduled_time=datetime.utcnow() + timedelta(hours=1)
        )
        
        assert job1.policy_id == job3.policy_id
        assert job1.tenant_id == job3.tenant_id
        assert job1.id != job3.id  # Different job instances

    def test_job_timing_constraints(self):
        """Test job timing field constraints."""
        scheduled_time = datetime.utcnow()
        
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-456",
            scheduled_time=scheduled_time
        )
        
        # Initially only scheduled_time is set
        assert job.scheduled_time == scheduled_time
        assert job.start_time is None
        assert job.end_time is None
        
        # Set start time (job begins)
        start_time = datetime.utcnow()
        job.start_time = start_time
        job.status = JobStatus.RUNNING
        
        assert job.start_time == start_time
        assert job.end_time is None
        
        # Set end time (job completes)
        end_time = datetime.utcnow()
        job.end_time = end_time
        job.status = JobStatus.COMPLETED
        
        assert job.end_time == end_time
        
        # Verify timing consistency
        assert job.scheduled_time <= job.start_time <= job.end_time

    def test_job_progress_constraints(self):
        """Test job progress field constraints."""
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-456",
            scheduled_time=datetime.utcnow()
        )
        
        # Test valid progress values
        valid_progress_values = [0, 25, 50, 75, 100]
        for progress in valid_progress_values:
            job.progress = progress
            assert job.progress == progress
        
        # Test edge cases
        job.progress = 0
        assert job.progress == 0
        
        job.progress = 100
        assert job.progress == 100

    def test_job_size_tracking_constraints(self):
        """Test job size tracking field constraints."""
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-456",
            scheduled_time=datetime.utcnow()
        )
        
        # Initially sizes should be None
        assert job.backup_size is None
        assert job.transferred_size is None
        
        # Test setting sizes
        backup_size = 1024 * 1024 * 1024  # 1GB
        transferred_size = 512 * 1024 * 1024  # 512MB
        
        job.backup_size = backup_size
        job.transferred_size = transferred_size
        
        assert job.backup_size == backup_size
        assert job.transferred_size == transferred_size
        
        # Test large sizes (BigInteger field)
        large_size = 9223372036854775807  # Max BigInteger
        job.backup_size = large_size
        assert job.backup_size == large_size

    def test_job_retry_logic_constraints(self):
        """Test job retry logic constraints."""
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-456",
            scheduled_time=datetime.utcnow()
        )
        
        # Initially no retries
        assert job.retry_count == 0
        assert job.error_message is None
        
        # Simulate retry scenarios
        for retry in range(1, 6):  # 5 retries
            job.retry_count = retry
            job.error_message = f"Attempt {retry} failed"
            job.status = JobStatus.FAILED
            
            assert job.retry_count == retry
            assert f"Attempt {retry}" in job.error_message
        
        # Final success
        job.status = JobStatus.COMPLETED
        job.error_message = None
        
        assert job.status == JobStatus.COMPLETED
        assert job.error_message is None
        assert job.retry_count == 5  # Retains retry count


class TestBackupSnapshotConstraints:
    """Test cases for BackupSnapshot model constraints and validation."""

    def test_snapshot_tenant_isolation_constraints(self):
        """Test that snapshots properly enforce tenant isolation."""
        # Create snapshots for different tenants
        snapshot1 = BackupSnapshot(
            job_id="job-1",
            tenant_id="tenant-1",
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="tenant1-snapshot",
            datastore_id="ds-1",
            path="/backup/tenant1/vm-100/snapshot"
        )
        
        snapshot2 = BackupSnapshot(
            job_id="job-2",
            tenant_id="tenant-2",
            vm_id="vm-200",
            cluster_id="cluster-2",
            snapshot_time=datetime.utcnow(),
            snapshot_name="tenant2-snapshot",
            datastore_id="ds-2",
            path="/backup/tenant2/vm-200/snapshot"
        )
        
        # Verify tenant isolation
        assert snapshot1.tenant_id != snapshot2.tenant_id
        assert snapshot1.vm_id != snapshot2.vm_id
        assert snapshot1.datastore_id != snapshot2.datastore_id
        assert snapshot1.path != snapshot2.path
        
        # Snapshots can be for same VM in same tenant
        snapshot3 = BackupSnapshot(
            job_id="job-3",
            tenant_id="tenant-1",  # Same tenant as snapshot1
            vm_id="vm-100",        # Same VM as snapshot1
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow() + timedelta(days=1),
            snapshot_name="tenant1-snapshot-2",
            datastore_id="ds-1",
            path="/backup/tenant1/vm-100/snapshot-2"
        )
        
        assert snapshot1.tenant_id == snapshot3.tenant_id
        assert snapshot1.vm_id == snapshot3.vm_id
        assert snapshot1.id != snapshot3.id  # Different snapshots

    def test_snapshot_size_constraints(self):
        """Test snapshot size field constraints."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-456",
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="size-test-snapshot",
            datastore_id="ds-123",
            path="/backup/test/size-snapshot"
        )
        
        # Initially sizes should be None
        assert snapshot.size is None
        assert snapshot.compressed_size is None
        assert snapshot.deduplicated_size is None
        
        # Test setting various sizes
        size = 10 * 1024 * 1024 * 1024  # 10GB
        compressed_size = 5 * 1024 * 1024 * 1024  # 5GB
        deduplicated_size = 2 * 1024 * 1024 * 1024  # 2GB
        
        snapshot.update_size_info(size, compressed_size, deduplicated_size)
        
        assert snapshot.size == size
        assert snapshot.compressed_size == compressed_size
        assert snapshot.deduplicated_size == deduplicated_size
        
        # Test compression and deduplication ratios
        assert snapshot.compression_ratio == 0.5  # 5GB / 10GB
        assert snapshot.deduplication_ratio == 0.4  # 2GB / 5GB

    def test_snapshot_verification_constraints(self):
        """Test snapshot verification field constraints."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-456",
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="verification-test",
            datastore_id="ds-123",
            path="/backup/test/verification"
        )
        
        # Initially verification is pending
        assert snapshot.verification_status == VerificationStatus.PENDING
        assert snapshot.verification_time is None
        assert snapshot.verification_error is None
        assert snapshot.checksum is None
        assert snapshot.is_verified is False
        
        # Test successful verification
        checksum = "sha256:abcdef1234567890"
        snapshot.mark_verified(checksum)
        
        assert snapshot.verification_status == VerificationStatus.VERIFIED
        assert snapshot.checksum == checksum
        assert snapshot.verification_time is not None
        assert snapshot.verification_error is None
        assert snapshot.is_verified is True
        
        # Test verification failure
        snapshot.mark_verification_failed("Checksum mismatch")
        
        assert snapshot.verification_status == VerificationStatus.FAILED
        assert snapshot.verification_error == "Checksum mismatch"
        assert snapshot.verification_time is not None
        assert snapshot.is_verified is False

    def test_snapshot_retention_constraints(self):
        """Test snapshot retention field constraints."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-456",
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="retention-test",
            datastore_id="ds-123",
            path="/backup/test/retention"
        )
        
        # Initially no retention date
        assert snapshot.retention_date is None
        assert snapshot.is_expired is False
        assert snapshot.can_be_deleted is False
        
        # Set future retention date
        future_date = datetime.utcnow() + timedelta(days=30)
        snapshot.retention_date = future_date
        
        assert snapshot.is_expired is False
        assert snapshot.can_be_deleted is False
        
        # Set past retention date
        past_date = datetime.utcnow() - timedelta(days=1)
        snapshot.retention_date = past_date
        
        assert snapshot.is_expired is True
        assert snapshot.can_be_deleted is True  # Not protected
        
        # Protect snapshot
        snapshot.protect("Critical backup")
        
        assert snapshot.is_expired is True
        assert snapshot.can_be_deleted is False  # Protected
        assert snapshot.is_protected is True
        assert snapshot.protection_reason == "Critical backup"

    def test_snapshot_performance_constraints(self):
        """Test snapshot performance field constraints."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-456",
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="performance-test",
            datastore_id="ds-123",
            path="/backup/test/performance"
        )
        
        # Initially performance metrics are None
        assert snapshot.backup_duration is None
        assert snapshot.transfer_rate is None
        
        # Set performance metrics
        duration = 3600  # 1 hour in seconds
        transfer_rate = 1024 * 1024  # 1MB/s
        
        snapshot.backup_duration = duration
        snapshot.transfer_rate = transfer_rate
        
        assert snapshot.backup_duration == duration
        assert snapshot.transfer_rate == transfer_rate

    def test_snapshot_configuration_constraints(self):
        """Test snapshot configuration field constraints."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-456",
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="config-test",
            datastore_id="ds-123",
            path="/backup/test/config",
            encryption_enabled=True,
            compression_type="lz4"
        )
        
        # Verify configuration fields
        assert snapshot.encryption_enabled is True
        assert snapshot.compression_type == "lz4"
        
        # Test different configurations
        configurations = [
            {"encryption_enabled": False, "compression_type": None},
            {"encryption_enabled": True, "compression_type": "zstd"},
            {"encryption_enabled": False, "compression_type": "lz4"},
        ]
        
        for config in configurations:
            test_snapshot = BackupSnapshot(
                job_id="job-456",
                tenant_id="tenant-789",
                vm_id="vm-200",
                cluster_id="cluster-2",
                snapshot_time=datetime.utcnow(),
                snapshot_name="config-test-2",
                datastore_id="ds-456",
                path="/backup/test/config2",
                **config
            )
            
            assert test_snapshot.encryption_enabled == config["encryption_enabled"]
            assert test_snapshot.compression_type == config["compression_type"]

    def test_snapshot_error_handling_constraints(self):
        """Test snapshot error handling field constraints."""
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id="tenant-456",
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="error-test",
            datastore_id="ds-123",
            path="/backup/test/error"
        )
        
        # Initially no errors
        assert snapshot.has_errors is False
        assert snapshot.error_message is None
        
        # Mark error
        error_msg = "Storage corruption detected"
        snapshot.mark_error(error_msg)
        
        assert snapshot.has_errors is True
        assert snapshot.error_message == error_msg
        
        # Clear error
        snapshot.clear_error()
        
        assert snapshot.has_errors is False
        assert snapshot.error_message is None