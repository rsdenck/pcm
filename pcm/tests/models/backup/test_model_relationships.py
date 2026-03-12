"""
Unit tests for backup model relationships and cross-model validation.

Tests relationship integrity, tenant isolation across models, and
complex validation scenarios involving multiple models.
"""

import pytest
from datetime import datetime, timedelta
from pcm.core.models.backup import (
    PBSServer, ServerStatus,
    Datastore, DatastoreStatus,
    BackupPolicy, PolicyStatus,
    BackupJob, JobStatus,
    BackupSnapshot, VerificationStatus
)


class TestModelRelationships:
    """Test cases for relationships between backup models."""

    def test_pbs_server_datastore_relationship(self):
        """Test relationship between PBS server and datastores."""
        # Create PBS server
        server = PBSServer(
            name="Test Server",
            hostname="pbs.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Create datastores for the server
        datastore1 = Datastore(
            name="datastore1",
            pbs_server_id=server.id,
            tenant_id="tenant-1",
            path="/backup/ds1"
        )
        
        datastore2 = Datastore(
            name="datastore2",
            pbs_server_id=server.id,
            tenant_id="tenant-2",
            path="/backup/ds2"
        )
        
        # Verify foreign key relationships
        assert datastore1.pbs_server_id == server.id
        assert datastore2.pbs_server_id == server.id
        
        # Verify different tenants can use same server
        assert datastore1.tenant_id != datastore2.tenant_id

    def test_policy_job_relationship(self):
        """Test relationship between backup policy and jobs."""
        # Create policy
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            }
        )
        
        # Create jobs for the policy
        job1 = BackupJob(
            policy_id=policy.id,
            tenant_id=policy.tenant_id,
            scheduled_time=datetime.utcnow()
        )
        
        job2 = BackupJob(
            policy_id=policy.id,
            tenant_id=policy.tenant_id,
            scheduled_time=datetime.utcnow() + timedelta(days=1)
        )
        
        # Verify foreign key relationships
        assert job1.policy_id == policy.id
        assert job2.policy_id == policy.id
        
        # Verify tenant consistency
        assert job1.tenant_id == policy.tenant_id
        assert job2.tenant_id == policy.tenant_id

    def test_job_snapshot_relationship(self):
        """Test relationship between backup job and snapshots."""
        # Create job
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-456",
            scheduled_time=datetime.utcnow()
        )
        
        # Create snapshots for the job
        snapshot1 = BackupSnapshot(
            job_id=job.id,
            tenant_id=job.tenant_id,
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="vm-100-snapshot-1",
            datastore_id="ds-1",
            path="/backup/vm-100/snapshot-1"
        )
        
        snapshot2 = BackupSnapshot(
            job_id=job.id,
            tenant_id=job.tenant_id,
            vm_id="vm-101",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="vm-101-snapshot-1",
            datastore_id="ds-1",
            path="/backup/vm-101/snapshot-1"
        )
        
        # Verify foreign key relationships
        assert snapshot1.job_id == job.id
        assert snapshot2.job_id == job.id
        
        # Verify tenant consistency
        assert snapshot1.tenant_id == job.tenant_id
        assert snapshot2.tenant_id == job.tenant_id
    def test_datastore_snapshot_relationship(self):
        """Test relationship between datastore and snapshots."""
        # Create datastore
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Create snapshots in the datastore
        snapshot1 = BackupSnapshot(
            job_id="job-1",
            tenant_id=datastore.tenant_id,
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="snapshot-1",
            datastore_id=datastore.id,
            path="/backup/test/vm-100/snapshot-1"
        )
        
        snapshot2 = BackupSnapshot(
            job_id="job-2",
            tenant_id=datastore.tenant_id,
            vm_id="vm-101",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="snapshot-2",
            datastore_id=datastore.id,
            path="/backup/test/vm-101/snapshot-2"
        )
        
        # Verify foreign key relationships
        assert snapshot1.datastore_id == datastore.id
        assert snapshot2.datastore_id == datastore.id
        
        # Verify tenant consistency
        assert snapshot1.tenant_id == datastore.tenant_id
        assert snapshot2.tenant_id == datastore.tenant_id

    def test_tenant_isolation_across_models(self):
        """Test that tenant isolation is enforced across all models."""
        tenant1_id = "tenant-1"
        tenant2_id = "tenant-2"
        
        # Create resources for tenant 1
        policy1 = BackupPolicy(
            name="Tenant 1 Policy",
            tenant_id=tenant1_id,
            configuration={
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            }
        )
        
        datastore1 = Datastore(
            name="tenant1-datastore",
            pbs_server_id="server-123",
            tenant_id=tenant1_id,
            path="/backup/tenant1"
        )
        
        job1 = BackupJob(
            policy_id=policy1.id,
            tenant_id=tenant1_id,
            scheduled_time=datetime.utcnow()
        )
        
        snapshot1 = BackupSnapshot(
            job_id=job1.id,
            tenant_id=tenant1_id,
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="tenant1-snapshot",
            datastore_id=datastore1.id,
            path="/backup/tenant1/vm-100/snapshot"
        )
        
        # Create resources for tenant 2
        policy2 = BackupPolicy(
            name="Tenant 2 Policy",
            tenant_id=tenant2_id,
            configuration={
                "schedule": {"cron": "0 3 * * *"},
                "retention": {"daily": 14},
                "targets": [{"vm_id": "200", "cluster_id": "cluster2", "datastore_id": "ds2"}]
            }
        )
        
        datastore2 = Datastore(
            name="tenant2-datastore",
            pbs_server_id="server-456",
            tenant_id=tenant2_id,
            path="/backup/tenant2"
        )
        
        job2 = BackupJob(
            policy_id=policy2.id,
            tenant_id=tenant2_id,
            scheduled_time=datetime.utcnow()
        )
        
        snapshot2 = BackupSnapshot(
            job_id=job2.id,
            tenant_id=tenant2_id,
            vm_id="vm-200",
            cluster_id="cluster-2",
            snapshot_time=datetime.utcnow(),
            snapshot_name="tenant2-snapshot",
            datastore_id=datastore2.id,
            path="/backup/tenant2/vm-200/snapshot"
        )
        
        # Verify tenant isolation
        assert policy1.tenant_id != policy2.tenant_id
        assert datastore1.tenant_id != datastore2.tenant_id
        assert job1.tenant_id != job2.tenant_id
        assert snapshot1.tenant_id != snapshot2.tenant_id
        
        # Verify all resources for tenant 1 have correct tenant ID
        assert policy1.tenant_id == tenant1_id
        assert datastore1.tenant_id == tenant1_id
        assert job1.tenant_id == tenant1_id
        assert snapshot1.tenant_id == tenant1_id
        
        # Verify all resources for tenant 2 have correct tenant ID
        assert policy2.tenant_id == tenant2_id
        assert datastore2.tenant_id == tenant2_id
        assert job2.tenant_id == tenant2_id
        assert snapshot2.tenant_id == tenant2_id

    def test_cascade_delete_implications(self):
        """Test implications of cascade delete relationships."""
        # Create a complete backup hierarchy
        server = PBSServer(
            name="Test Server",
            hostname="pbs.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id=server.id,
            tenant_id="tenant-123",
            path="/backup/test"
        )
        
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": datastore.id}]
            }
        )
        
        job = BackupJob(
            policy_id=policy.id,
            tenant_id="tenant-123",
            scheduled_time=datetime.utcnow()
        )
        
        snapshot = BackupSnapshot(
            job_id=job.id,
            tenant_id="tenant-123",
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id=datastore.id,
            path="/backup/test/vm-100/snapshot"
        )
        
        # Verify all relationships are properly set
        assert datastore.pbs_server_id == server.id
        assert job.policy_id == policy.id
        assert snapshot.job_id == job.id
        assert snapshot.datastore_id == datastore.id
        
        # In a real database, deleting the server would cascade to datastores
        # and deleting datastores would cascade to snapshots
        # Here we just verify the foreign key relationships are correct
        assert snapshot.datastore_id == datastore.id
        assert datastore.pbs_server_id == server.id


class TestModelValidationConstraints:
    """Test validation constraints across models."""

    def test_policy_target_datastore_validation(self):
        """Test that policy targets reference valid datastores."""
        # Create datastore
        datastore = Datastore(
            name="valid-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/valid"
        )
        
        # Create policy with valid datastore reference
        valid_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": datastore.id}]
        }
        
        policy = BackupPolicy(
            name="Valid Policy",
            tenant_id="tenant-456",
            configuration=valid_config
        )
        
        # Verify configuration is valid
        is_valid, error = policy.validate_configuration()
        assert is_valid is True
        assert error is None
        
        # Verify target references correct datastore
        targets = policy.targets
        assert len(targets) == 1
        assert targets[0]["datastore_id"] == datastore.id

    def test_job_policy_tenant_consistency(self):
        """Test that jobs maintain tenant consistency with their policies."""
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            }
        )
        
        # Create job with matching tenant
        job = BackupJob(
            policy_id=policy.id,
            tenant_id=policy.tenant_id,
            scheduled_time=datetime.utcnow()
        )
        
        assert job.tenant_id == policy.tenant_id
        
        # In a real application, creating a job with mismatched tenant
        # would be prevented by business logic or database constraints
        # Here we just verify the fields can be set independently
        job_wrong_tenant = BackupJob(
            policy_id=policy.id,
            tenant_id="different-tenant",
            scheduled_time=datetime.utcnow()
        )
        
        assert job_wrong_tenant.tenant_id != policy.tenant_id

    def test_snapshot_datastore_tenant_consistency(self):
        """Test that snapshots maintain tenant consistency with datastores."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Create snapshot with matching tenant
        snapshot = BackupSnapshot(
            job_id="job-123",
            tenant_id=datastore.tenant_id,
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id=datastore.id,
            path="/backup/test/vm-100/snapshot"
        )
        
        assert snapshot.tenant_id == datastore.tenant_id
        assert snapshot.datastore_id == datastore.id

    def test_model_id_uniqueness(self):
        """Test that model IDs are unique across instances."""
        # Create multiple instances of each model
        servers = [
            PBSServer(
                name=f"Server {i}",
                hostname=f"pbs{i}.example.com",
                api_token_id=f"test{i}@pbs!token",
                api_token_secret=f"secret{i}",
                datacenter=f"dc{i}"
            ) for i in range(3)
        ]
        
        datastores = [
            Datastore(
                name=f"datastore{i}",
                pbs_server_id=f"server-{i}",
                tenant_id=f"tenant-{i}",
                path=f"/backup/ds{i}"
            ) for i in range(3)
        ]
        
        policies = [
            BackupPolicy(
                name=f"Policy {i}",
                tenant_id=f"tenant-{i}",
                configuration={
                    "schedule": {"cron": "0 2 * * *"},
                    "retention": {"daily": 7},
                    "targets": [{"vm_id": f"{100+i}", "cluster_id": "cluster1", "datastore_id": f"ds{i}"}]
                }
            ) for i in range(3)
        ]
        
        jobs = [
            BackupJob(
                policy_id=f"policy-{i}",
                tenant_id=f"tenant-{i}",
                scheduled_time=datetime.utcnow()
            ) for i in range(3)
        ]
        
        snapshots = [
            BackupSnapshot(
                job_id=f"job-{i}",
                tenant_id=f"tenant-{i}",
                vm_id=f"vm-{100+i}",
                cluster_id="cluster-1",
                snapshot_time=datetime.utcnow(),
                snapshot_name=f"snapshot-{i}",
                datastore_id=f"ds-{i}",
                path=f"/backup/ds{i}/vm-{100+i}/snapshot"
            ) for i in range(3)
        ]
        
        # Verify all IDs are unique within each model type
        server_ids = [s.id for s in servers]
        datastore_ids = [d.id for d in datastores]
        policy_ids = [p.id for p in policies]
        job_ids = [j.id for j in jobs]
        snapshot_ids = [s.id for s in snapshots]
        
        assert len(set(server_ids)) == len(server_ids)
        assert len(set(datastore_ids)) == len(datastore_ids)
        assert len(set(policy_ids)) == len(policy_ids)
        assert len(set(job_ids)) == len(job_ids)
        assert len(set(snapshot_ids)) == len(snapshot_ids)
        
        # Verify IDs are unique across all models
        all_ids = server_ids + datastore_ids + policy_ids + job_ids + snapshot_ids
        assert len(set(all_ids)) == len(all_ids)


class TestModelStatusConsistency:
    """Test status consistency and transitions across models."""

    def test_server_datastore_status_consistency(self):
        """Test status consistency between servers and their datastores."""
        server = PBSServer(
            name="Test Server",
            hostname="pbs.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id=server.id,
            tenant_id="tenant-123",
            path="/backup/test"
        )
        
        # Initially both should be in default states
        assert server.status == ServerStatus.OFFLINE
        assert datastore.status == DatastoreStatus.ACTIVE
        
        # When server goes online, datastore can remain active
        server.mark_online()
        assert server.status == ServerStatus.ONLINE
        assert datastore.status == DatastoreStatus.ACTIVE
        
        # When server goes offline, datastore might need to be marked inactive
        # (This would be handled by business logic, not the model itself)
        server.mark_offline("Connection lost")
        assert server.status == ServerStatus.OFFLINE
        # Datastore status would be updated by service layer

    def test_policy_job_status_consistency(self):
        """Test status consistency between policies and their jobs."""
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            }
        )
        
        job = BackupJob(
            policy_id=policy.id,
            tenant_id=policy.tenant_id,
            scheduled_time=datetime.utcnow()
        )
        
        # Initially policy is active, job is pending
        assert policy.status == PolicyStatus.ACTIVE
        assert job.status == JobStatus.PENDING
        
        # When policy is suspended, existing jobs might continue
        policy.suspend("Manual suspension")
        assert policy.status == PolicyStatus.SUSPENDED
        # Job status is independent of policy status
        assert job.status == JobStatus.PENDING
        
        # Job can complete even if policy is suspended
        job.status = JobStatus.COMPLETED
        assert job.status == JobStatus.COMPLETED
        assert policy.status == PolicyStatus.SUSPENDED

    def test_job_snapshot_status_consistency(self):
        """Test status consistency between jobs and their snapshots."""
        job = BackupJob(
            policy_id="policy-123",
            tenant_id="tenant-456",
            scheduled_time=datetime.utcnow()
        )
        
        snapshot = BackupSnapshot(
            job_id=job.id,
            tenant_id=job.tenant_id,
            vm_id="vm-100",
            cluster_id="cluster-1",
            snapshot_time=datetime.utcnow(),
            snapshot_name="test-snapshot",
            datastore_id="ds-123",
            path="/backup/test/vm-100/snapshot"
        )
        
        # Initially job is pending, snapshot verification is pending
        assert job.status == JobStatus.PENDING
        assert snapshot.verification_status == VerificationStatus.PENDING
        
        # When job completes, snapshot should be verified
        job.status = JobStatus.COMPLETED
        snapshot.mark_verified("sha256:abcd1234")
        
        assert job.status == JobStatus.COMPLETED
        assert snapshot.verification_status == VerificationStatus.VERIFIED
        
        # If job fails, snapshot might have errors
        job.status = JobStatus.FAILED
        job.error_message = "Backup failed"
        snapshot.mark_error("Incomplete backup")
        
        assert job.status == JobStatus.FAILED
        assert snapshot.has_errors is True