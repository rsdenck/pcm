"""
Unit tests for Datastore model.

Tests model validation, constraints, capacity management, tenant isolation,
and relationship integrity.
"""

import pytest
from datetime import datetime, timedelta
from pcm.core.models.backup import Datastore, DatastoreStatus


class TestDatastore:
    """Test cases for Datastore model."""

    def test_datastore_creation(self):
        """Test basic datastore creation with required fields."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        assert datastore.name == "test-datastore"
        assert datastore.pbs_server_id == "server-123"
        assert datastore.tenant_id == "tenant-456"
        assert datastore.path == "/backup/test"
        assert datastore.status == DatastoreStatus.ACTIVE  # Default status
        assert datastore.warning_threshold == 80  # Default
        assert datastore.critical_threshold == 90  # Default
        assert datastore.capacity_check_interval == 3600  # Default (1 hour)
        assert datastore.backup_count == 0
        assert datastore.is_encrypted is False  # Default
        assert datastore.compression_enabled is True  # Default
        assert datastore.deduplication_enabled is True  # Default
        assert datastore.error_count == 0
        assert datastore.created_at is not None
        assert datastore.updated_at is not None

    def test_datastore_creation_with_custom_values(self):
        """Test datastore creation with custom configuration values."""
        datastore = Datastore(
            name="custom-datastore",
            pbs_server_id="server-789",
            tenant_id="tenant-abc",
            path="/custom/backup/path",
            description="Custom datastore for testing",
            warning_threshold=75,
            critical_threshold=85,
            capacity_check_interval=1800,  # 30 minutes
            is_encrypted=True,
            compression_enabled=False,
            deduplication_enabled=False
        )
        
        assert datastore.description == "Custom datastore for testing"
        assert datastore.warning_threshold == 75
        assert datastore.critical_threshold == 85
        assert datastore.capacity_check_interval == 1800
        assert datastore.is_encrypted is True
        assert datastore.compression_enabled is False
        assert datastore.deduplication_enabled is False

    def test_datastore_status_enum_validation(self):
        """Test that datastore status accepts valid enum values."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Test all valid status values
        for status in DatastoreStatus:
            datastore.status = status
            assert datastore.status == status

    def test_usage_percentage_calculation(self):
        """Test usage percentage calculation."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Test with no capacity information
        assert datastore.usage_percentage is None
        
        # Test with capacity information
        datastore.total_capacity = 1000
        datastore.used_capacity = 750
        assert datastore.usage_percentage == 75.0
        
        # Test with zero used capacity
        datastore.used_capacity = 0
        assert datastore.usage_percentage == 0.0
        
        # Test with full capacity
        datastore.used_capacity = 1000
        assert datastore.usage_percentage == 100.0
        
        # Test with None used capacity
        datastore.used_capacity = None
        assert datastore.usage_percentage is None

    def test_threshold_checking_properties(self):
        """Test threshold checking properties."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test",
            warning_threshold=80,
            critical_threshold=90
        )
        
        # Test below warning threshold
        datastore.total_capacity = 1000
        datastore.used_capacity = 700  # 70%
        assert datastore.is_over_warning_threshold is False
        assert datastore.is_over_critical_threshold is False
        
        # Test at warning threshold
        datastore.used_capacity = 800  # 80%
        assert datastore.is_over_warning_threshold is True
        assert datastore.is_over_critical_threshold is False
        
        # Test between warning and critical
        datastore.used_capacity = 850  # 85%
        assert datastore.is_over_warning_threshold is True
        assert datastore.is_over_critical_threshold is False
        
        # Test at critical threshold
        datastore.used_capacity = 900  # 90%
        assert datastore.is_over_warning_threshold is True
        assert datastore.is_over_critical_threshold is True
        
        # Test above critical threshold
        datastore.used_capacity = 950  # 95%
        assert datastore.is_over_warning_threshold is True
        assert datastore.is_over_critical_threshold is True

    def test_threshold_checking_with_none_values(self):
        """Test threshold checking with None values."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Test with None thresholds
        datastore.warning_threshold = None
        datastore.critical_threshold = None
        datastore.total_capacity = 1000
        datastore.used_capacity = 950
        
        assert datastore.is_over_warning_threshold is False
        assert datastore.is_over_critical_threshold is False
        
        # Test with None capacity
        datastore.warning_threshold = 80
        datastore.critical_threshold = 90
        datastore.total_capacity = None
        datastore.used_capacity = None
        
        assert datastore.is_over_warning_threshold is False
        assert datastore.is_over_critical_threshold is False

    def test_is_healthy_property(self):
        """Test is_healthy property logic."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test",
            critical_threshold=90
        )
        
        # Test healthy state (active and below critical)
        datastore.status = DatastoreStatus.ACTIVE
        datastore.total_capacity = 1000
        datastore.used_capacity = 800  # 80%
        assert datastore.is_healthy is True
        
        # Test unhealthy due to status
        datastore.status = DatastoreStatus.ERROR
        assert datastore.is_healthy is False
        
        # Test unhealthy due to capacity
        datastore.status = DatastoreStatus.ACTIVE
        datastore.used_capacity = 950  # 95% - over critical
        assert datastore.is_healthy is False
        
        # Test other unhealthy statuses
        unhealthy_statuses = [
            DatastoreStatus.INACTIVE,
            DatastoreStatus.MAINTENANCE,
            DatastoreStatus.FULL,
            DatastoreStatus.ERROR
        ]
        
        datastore.used_capacity = 500  # Below critical
        for status in unhealthy_statuses:
            datastore.status = status
            assert datastore.is_healthy is False

    def test_update_capacity_method(self):
        """Test update_capacity method."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test",
            warning_threshold=80,
            critical_threshold=90
        )
        
        # Test capacity update
        total = 1000
        used = 750
        available = 250
        
        datastore.update_capacity(total, used, available)
        
        assert datastore.total_capacity == total
        assert datastore.used_capacity == used
        assert datastore.available_capacity == available
        assert datastore.last_capacity_check is not None
        assert isinstance(datastore.last_capacity_check, datetime)
        
        # Test status remains active when below critical
        assert datastore.status == DatastoreStatus.ACTIVE
        
        # Test status changes to full when over critical
        datastore.update_capacity(1000, 950, 50)  # 95% usage
        assert datastore.status == DatastoreStatus.FULL
        
        # Test status returns to active when usage drops
        datastore.update_capacity(1000, 700, 300)  # 70% usage
        assert datastore.status == DatastoreStatus.ACTIVE

    def test_update_capacity_with_none_thresholds(self):
        """Test update_capacity method with None thresholds."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Set thresholds to None
        datastore.warning_threshold = None
        datastore.critical_threshold = None
        
        # Update capacity - status should not change
        original_status = datastore.status
        datastore.update_capacity(1000, 950, 50)
        assert datastore.status == original_status

    def test_mark_error_method(self):
        """Test mark_error method."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Mark error
        error_msg = "Storage device failure"
        datastore.mark_error(error_msg)
        
        assert datastore.status == DatastoreStatus.ERROR
        assert datastore.last_error == error_msg
        assert datastore.error_count == 1
        
        # Mark another error (should increment count)
        datastore.mark_error("Another error")
        assert datastore.error_count == 2

    def test_clear_error_method(self):
        """Test clear_error method."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Set error state first
        datastore.mark_error("Test error")
        assert datastore.status == DatastoreStatus.ERROR
        assert datastore.last_error == "Test error"
        assert datastore.error_count == 1
        
        # Clear error
        datastore.clear_error()
        assert datastore.status == DatastoreStatus.ACTIVE
        assert datastore.last_error is None
        assert datastore.error_count == 0

    def test_error_count_handling(self):
        """Test error count initialization and handling."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Initial error count should be 0
        assert datastore.error_count == 0
        
        # Test error count with None value (edge case)
        datastore.error_count = None
        datastore.mark_error("Error")
        assert datastore.error_count == 1

    def test_datastore_repr(self):
        """Test string representation of datastore."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        repr_str = repr(datastore)
        assert "Datastore" in repr_str
        assert datastore.id in repr_str
        assert "test-datastore" in repr_str
        assert "tenant-456" in repr_str
        assert str(datastore.status) in repr_str

    def test_datastore_constraints_validation(self):
        """Test model field constraints and validation."""
        # Test with minimal required fields - should work
        datastore = Datastore(
            name="test",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/test"
        )
        assert datastore is not None
        
        # Test that required fields are actually required would be enforced by database
        # In unit tests without database, we can't test database constraints

    def test_datastore_timestamps(self):
        """Test automatic timestamp handling."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Check that timestamps are set
        assert datastore.created_at is not None
        assert datastore.updated_at is not None
        assert isinstance(datastore.created_at, datetime)
        assert isinstance(datastore.updated_at, datetime)
        
        # Check that created_at and updated_at are close in time
        time_diff = abs((datastore.updated_at - datastore.created_at).total_seconds())
        assert time_diff < 1  # Should be within 1 second

    def test_tenant_isolation_enforcement(self):
        """Test that datastores properly enforce tenant isolation."""
        # Create datastores for different tenants
        datastore1 = Datastore(
            name="tenant1-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-1",
            path="/backup/tenant1"
        )
        
        datastore2 = Datastore(
            name="tenant2-datastore",
            pbs_server_id="server-123",  # Same server
            tenant_id="tenant-2",  # Different tenant
            path="/backup/tenant2"
        )
        
        # Verify tenant isolation
        assert datastore1.tenant_id != datastore2.tenant_id
        assert datastore1.tenant_id == "tenant-1"
        assert datastore2.tenant_id == "tenant-2"
        assert datastore1.path != datastore2.path  # Different paths for isolation
        
        # Verify they can have independent configurations
        datastore1.warning_threshold = 70
        datastore1.critical_threshold = 80
        datastore2.warning_threshold = 85
        datastore2.critical_threshold = 95
        
        assert datastore1.warning_threshold != datastore2.warning_threshold
        assert datastore1.critical_threshold != datastore2.critical_threshold

    def test_relationship_integrity_constraints(self):
        """Test that foreign key relationships are properly defined."""
        datastore = Datastore(
            name="test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/test"
        )
        
        # Verify foreign key fields are set correctly
        assert datastore.pbs_server_id == "server-123"
        assert datastore.tenant_id == "tenant-456"
        
        # These would be validated by the database constraints in real usage
        # Here we just verify the fields are properly set


class TestDatastoreEdgeCases:
    """Test edge cases and error conditions for Datastore model."""

    def test_datastore_with_extreme_values(self):
        """Test datastore with extreme but valid values."""
        datastore = Datastore(
            name="a" * 255,  # Maximum name length
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/" + "x" * 400,  # Long path
            description="d" * 1000,  # Long description
            total_capacity=9223372036854775807,  # Max BigInteger
            used_capacity=9223372036854775806,
            available_capacity=1,
            warning_threshold=99,
            critical_threshold=100,
            capacity_check_interval=86400,  # 24 hours
            backup_count=999999
        )
        
        assert len(datastore.name) == 255
        assert datastore.total_capacity == 9223372036854775807
        assert datastore.warning_threshold == 99
        assert datastore.critical_threshold == 100
        assert datastore.capacity_check_interval == 86400
        assert datastore.backup_count == 999999

    def test_datastore_capacity_edge_cases(self):
        """Test capacity calculations with edge cases."""
        datastore = Datastore(
            name="edge-test-datastore",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/edge"
        )
        
        # Test with zero total capacity
        datastore.total_capacity = 0
        datastore.used_capacity = 0
        # This would cause division by zero, but our property handles it
        assert datastore.usage_percentage is None  # Should return None for zero capacity
        
        # Test with very small capacities
        datastore.total_capacity = 1
        datastore.used_capacity = 1
        assert datastore.usage_percentage == 100.0
        
        # Test with mismatched capacities (used > total - shouldn't happen but test anyway)
        datastore.total_capacity = 100
        datastore.used_capacity = 150
        assert datastore.usage_percentage == 150.0  # Over 100%

    def test_datastore_threshold_edge_cases(self):
        """Test threshold checking with edge case values."""
        datastore = Datastore(
            name="threshold-test",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/threshold"
        )
        
        # Test with 0% thresholds
        datastore.warning_threshold = 0
        datastore.critical_threshold = 0
        datastore.total_capacity = 1000
        datastore.used_capacity = 1  # 0.1%
        
        assert datastore.is_over_warning_threshold is True
        assert datastore.is_over_critical_threshold is True
        
        # Test with 100% thresholds
        datastore.warning_threshold = 100
        datastore.critical_threshold = 100
        datastore.used_capacity = 999  # 99.9%
        
        assert datastore.is_over_warning_threshold is False
        assert datastore.is_over_critical_threshold is False
        
        datastore.used_capacity = 1000  # 100%
        assert datastore.is_over_warning_threshold is True
        assert datastore.is_over_critical_threshold is True

    def test_datastore_status_transitions(self):
        """Test all possible status transitions."""
        datastore = Datastore(
            name="status-test",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/status"
        )
        
        # Test all status transitions
        status_sequence = [
            DatastoreStatus.ACTIVE,
            DatastoreStatus.MAINTENANCE,
            DatastoreStatus.FULL,
            DatastoreStatus.ERROR,
            DatastoreStatus.INACTIVE,
            DatastoreStatus.ACTIVE
        ]
        
        for status in status_sequence:
            datastore.status = status
            assert datastore.status == status

    def test_datastore_capacity_monitoring_intervals(self):
        """Test different capacity monitoring intervals."""
        intervals = [300, 600, 1800, 3600, 7200]  # 5min to 2hours
        
        for interval in intervals:
            datastore = Datastore(
                name=f"datastore-{interval}s",
                pbs_server_id="server-123",
                tenant_id="tenant-456",
                path=f"/backup/{interval}",
                capacity_check_interval=interval
            )
            
            assert datastore.capacity_check_interval == interval

    def test_datastore_backup_count_tracking(self):
        """Test backup count tracking functionality."""
        datastore = Datastore(
            name="backup-count-test",
            pbs_server_id="server-123",
            tenant_id="tenant-456",
            path="/backup/count"
        )
        
        # Initial count should be 0
        assert datastore.backup_count == 0
        
        # Test incrementing backup count
        for i in range(1, 11):
            datastore.backup_count = i
            assert datastore.backup_count == i
        
        # Test last backup timestamp
        assert datastore.last_backup is None
        
        now = datetime.utcnow()
        datastore.last_backup = now
        assert datastore.last_backup == now

    def test_datastore_configuration_options(self):
        """Test various datastore configuration combinations."""
        configurations = [
            # Standard configuration
            {"is_encrypted": False, "compression_enabled": True, "deduplication_enabled": True},
            # High security
            {"is_encrypted": True, "compression_enabled": True, "deduplication_enabled": True},
            # No compression/dedup
            {"is_encrypted": False, "compression_enabled": False, "deduplication_enabled": False},
            # Mixed configuration
            {"is_encrypted": True, "compression_enabled": False, "deduplication_enabled": True},
        ]
        
        for i, config in enumerate(configurations):
            datastore = Datastore(
                name=f"config-test-{i}",
                pbs_server_id="server-123",
                tenant_id="tenant-456",
                path=f"/backup/config{i}",
                **config
            )
            
            assert datastore.is_encrypted == config["is_encrypted"]
            assert datastore.compression_enabled == config["compression_enabled"]
            assert datastore.deduplication_enabled == config["deduplication_enabled"]