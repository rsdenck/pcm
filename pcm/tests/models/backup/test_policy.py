import pytest
from datetime import datetime
from pcm.core.models.backup import BackupPolicy, PolicyStatus, validate_policy_configuration


class TestBackupPolicy:
    """Test cases for BackupPolicy model."""

    def test_policy_creation(self):
        """Test basic policy creation."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7, "weekly": 4},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration=config
        )
        
        assert policy.name == "Test Policy"
        assert policy.tenant_id == "tenant-123"
        assert policy.status == PolicyStatus.ACTIVE
        assert policy.enabled is True
        assert policy.job_count == 0
        assert policy.success_count == 0
        assert policy.failure_count == 0

    def test_policy_properties(self):
        """Test policy property methods."""
        config = {
            "schedule": {"cron": "0 2 * * *", "timezone": "UTC"},
            "retention": {"daily": 7, "weekly": 4, "monthly": 12},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}],
            "options": {"compression": "lz4", "encryption": True}
        }
        
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration=config
        )
        
        assert policy.schedule == {"cron": "0 2 * * *", "timezone": "UTC"}
        assert policy.retention == {"daily": 7, "weekly": 4, "monthly": 12}
        assert len(policy.targets) == 1
        assert policy.targets[0]["vm_id"] == "100"
        assert policy.options == {"compression": "lz4", "encryption": True}

    def test_policy_is_active(self):
        """Test is_active property."""
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={"schedule": {"cron": "0 2 * * *"}, "retention": {"daily": 7}, "targets": []}
        )
        
        # Active and enabled
        assert policy.is_active is True
        
        # Disabled
        policy.enabled = False
        assert policy.is_active is False
        
        # Inactive status
        policy.enabled = True
        policy.status = PolicyStatus.INACTIVE
        assert policy.is_active is False

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={"schedule": {"cron": "0 2 * * *"}, "retention": {"daily": 7}, "targets": []}
        )
        
        # No jobs
        assert policy.success_rate == 0.0
        
        # Some successful jobs
        policy.job_count = 10
        policy.success_count = 8
        assert policy.success_rate == 80.0
        
        # All successful
        policy.success_count = 10
        assert policy.success_rate == 100.0
    def test_update_statistics(self):
        """Test statistics update methods."""
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={"schedule": {"cron": "0 2 * * *"}, "retention": {"daily": 7}, "targets": []}
        )
        
        # Successful job
        policy.update_statistics(success=True)
        assert policy.job_count == 1
        assert policy.success_count == 1
        assert policy.failure_count == 0
        assert policy.last_error is None
        assert policy.error_count == 0
        
        # Failed job
        policy.update_statistics(success=False)
        assert policy.job_count == 2
        assert policy.success_count == 1
        assert policy.failure_count == 1
        assert policy.error_count == 1

    def test_error_handling(self):
        """Test error handling methods."""
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={"schedule": {"cron": "0 2 * * *"}, "retention": {"daily": 7}, "targets": []}
        )
        
        # Mark error
        policy.mark_error("Test error message")
        assert policy.status == PolicyStatus.ERROR
        assert policy.last_error == "Test error message"
        assert policy.error_count == 1
        
        # Clear error
        policy.clear_error()
        assert policy.status == PolicyStatus.ACTIVE
        assert policy.last_error is None
        assert policy.error_count == 0

    def test_suspend_and_activate(self):
        """Test suspend and activate methods."""
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration={"schedule": {"cron": "0 2 * * *"}, "retention": {"daily": 7}, "targets": []}
        )
        
        # Suspend
        policy.suspend("Manual suspension")
        assert policy.status == PolicyStatus.SUSPENDED
        assert policy.enabled is False
        assert "Suspended: Manual suspension" in policy.last_error
        
        # Activate
        policy.activate()
        assert policy.status == PolicyStatus.ACTIVE
        assert policy.enabled is True
        assert policy.last_error is None
        assert policy.error_count == 0

    def test_configuration_validation(self):
        """Test configuration validation."""
        # Valid configuration
        valid_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7, "weekly": 4},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        policy = BackupPolicy(
            name="Test Policy",
            tenant_id="tenant-123",
            configuration=valid_config
        )
        
        is_valid, error = policy.validate_configuration()
        assert is_valid is True
        assert error is None
        
        # Invalid configuration - missing required fields
        invalid_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7}
            # Missing targets
        }
        
        policy.configuration = invalid_config
        is_valid, error = policy.validate_configuration()
        assert is_valid is False
        assert error is not None
        assert "targets" in error.lower()


class TestPolicyConfigurationValidation:
    """Test cases for policy configuration validation."""

    def test_valid_configuration(self):
        """Test validation of valid configurations."""
        valid_config = {
            "schedule": {"cron": "0 2 * * *", "timezone": "UTC"},
            "retention": {"daily": 7, "weekly": 4, "monthly": 12},
            "targets": [
                {"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"},
                {"vm_id": "101", "cluster_id": "cluster1", "datastore_id": "ds2"}
            ],
            "options": {
                "compression": "lz4",
                "encryption": True,
                "verification": True,
                "bandwidth_limit": 1000,
                "max_concurrent_jobs": 2
            }
        }
        
        is_valid, error = validate_policy_configuration(valid_config)
        assert is_valid is True
        assert error is None

    def test_minimal_valid_configuration(self):
        """Test validation of minimal valid configuration."""
        minimal_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        is_valid, error = validate_policy_configuration(minimal_config)
        assert is_valid is True
        assert error is None
    def test_invalid_configurations(self):
        """Test validation of invalid configurations."""
        # Missing required fields
        invalid_configs = [
            # Missing schedule
            {
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            },
            # Missing retention
            {
                "schedule": {"cron": "0 2 * * *"},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            },
            # Missing targets
            {
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7}
            },
            # Empty targets
            {
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": []
            },
            # Invalid cron pattern
            {
                "schedule": {"cron": "invalid-cron"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            },
            # Invalid retention values
            {
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": -1},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            },
            # Invalid compression option
            {
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}],
                "options": {"compression": "invalid"}
            },
            # Invalid target structure
            {
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100"}]  # Missing cluster_id and datastore_id
            }
        ]
        
        for config in invalid_configs:
            is_valid, error = validate_policy_configuration(config)
            assert is_valid is False
            assert error is not None

    def test_additional_properties_rejected(self):
        """Test that additional properties are rejected."""
        config_with_extra = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}],
            "extra_field": "not allowed"
        }
        
        is_valid, error = validate_policy_configuration(config_with_extra)
        assert is_valid is False
        assert error is not None

    def test_tenant_isolation_validation(self):
        """Test that tenant isolation is enforced in model creation."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        # Create policies for different tenants
        policy1 = BackupPolicy(
            name="Tenant 1 Policy",
            tenant_id="tenant-1",
            configuration=config
        )
        
        policy2 = BackupPolicy(
            name="Tenant 2 Policy", 
            tenant_id="tenant-2",
            configuration=config
        )
        
        # Verify tenant isolation
        assert policy1.tenant_id != policy2.tenant_id
        assert policy1.tenant_id == "tenant-1"
        assert policy2.tenant_id == "tenant-2"

class TestBackupPolicyConstraints:
    """Test cases for BackupPolicy model constraints and validation."""

    def test_policy_tenant_isolation_constraints(self):
        """Test that policies properly enforce tenant isolation."""
        tenant1_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        tenant2_config = {
            "schedule": {"cron": "0 3 * * *"},
            "retention": {"daily": 14},
            "targets": [{"vm_id": "200", "cluster_id": "cluster2", "datastore_id": "ds2"}]
        }
        
        policy1 = BackupPolicy(
            name="Tenant 1 Policy",
            tenant_id="tenant-1",
            configuration=tenant1_config
        )
        
        policy2 = BackupPolicy(
            name="Tenant 2 Policy",
            tenant_id="tenant-2",
            configuration=tenant2_config
        )
        
        # Verify tenant isolation
        assert policy1.tenant_id != policy2.tenant_id
        assert policy1.configuration != policy2.configuration
        
        # Verify policies can have same name for different tenants
        policy3 = BackupPolicy(
            name="Tenant 1 Policy",  # Same name as policy1
            tenant_id="tenant-3",    # Different tenant
            configuration=tenant1_config
        )
        
        assert policy1.name == policy3.name
        assert policy1.tenant_id != policy3.tenant_id

    def test_policy_configuration_field_validation(self):
        """Test validation of individual configuration fields."""
        base_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        # Test invalid cron expressions
        invalid_cron_configs = [
            {**base_config, "schedule": {"cron": "invalid-cron-with-letters"}},
            {**base_config, "schedule": {"cron": "!@#$%^&*()"}},  # Special characters not allowed
            {**base_config, "schedule": {"cron": ""}},  # Empty cron
        ]
        
        for config in invalid_cron_configs:
            is_valid, error = validate_policy_configuration(config)
            assert is_valid is False
            assert error is not None

    def test_policy_retention_validation(self):
        """Test retention policy validation."""
        base_config = {
            "schedule": {"cron": "0 2 * * *"},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        # Test valid retention configurations
        valid_retentions = [
            {"daily": 7},
            {"weekly": 4},
            {"monthly": 12},
            {"yearly": 1},
            {"daily": 7, "weekly": 4},
            {"daily": 7, "weekly": 4, "monthly": 12},
            {"daily": 7, "weekly": 4, "monthly": 12, "yearly": 1},
        ]
        
        for retention in valid_retentions:
            config = {**base_config, "retention": retention}
            is_valid, error = validate_policy_configuration(config)
            assert is_valid is True, f"Failed for retention: {retention}, error: {error}"

    def test_policy_targets_validation(self):
        """Test backup targets validation."""
        base_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7}
        }
        
        # Test valid target configurations
        valid_targets = [
            [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}],
            [
                {"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"},
                {"vm_id": "101", "cluster_id": "cluster1", "datastore_id": "ds2"}
            ],
            [
                {"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"},
                {"vm_id": "200", "cluster_id": "cluster2", "datastore_id": "ds3"}
            ]
        ]
        
        for targets in valid_targets:
            config = {**base_config, "targets": targets}
            is_valid, error = validate_policy_configuration(config)
            assert is_valid is True, f"Failed for targets: {targets}, error: {error}"

    def test_policy_options_validation(self):
        """Test backup options validation."""
        base_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        # Test valid options
        valid_options = [
            {"compression": "none"},
            {"compression": "lz4"},
            {"compression": "zstd"},
            {"encryption": True},
            {"encryption": False},
            {"verification": True},
            {"verification": False},
            {"bandwidth_limit": 0},
            {"bandwidth_limit": 1000},
            {"max_concurrent_jobs": 1},
            {"max_concurrent_jobs": 5},
            {"max_concurrent_jobs": 10},
            {
                "compression": "lz4",
                "encryption": True,
                "verification": True,
                "bandwidth_limit": 1000,
                "max_concurrent_jobs": 2
            }
        ]
        
        for options in valid_options:
            config = {**base_config, "options": options}
            is_valid, error = validate_policy_configuration(config)
            assert is_valid is True, f"Failed for options: {options}, error: {error}"

    def test_policy_statistics_edge_cases(self):
        """Test policy statistics with edge cases."""
        policy = BackupPolicy(
            name="Stats Test Policy",
            tenant_id="tenant-123",
            configuration={
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            }
        )
        
        # Test with None values (edge case)
        policy.job_count = None
        policy.success_count = None
        policy.failure_count = None
        policy.error_count = None
        
        # Update statistics should handle None values
        policy.update_statistics(success=True)
        assert policy.job_count == 1
        assert policy.success_count == 1
        assert policy.failure_count == 0
        assert policy.error_count == 0
        
        # Test success rate with None values
        policy.job_count = None
        assert policy.success_rate == 0.0
        
        policy.job_count = 10
        policy.success_count = None
        assert policy.success_rate == 0.0

    def test_policy_error_state_transitions(self):
        """Test policy error state transitions."""
        policy = BackupPolicy(
            name="Error Test Policy",
            tenant_id="tenant-123",
            configuration={
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 7},
                "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
            }
        )
        
        # Test error handling with None error_count
        policy.error_count = None
        policy.mark_error("Test error")
        assert policy.error_count == 1
        
        # Test clear error with disabled policy
        policy.enabled = False
        policy.clear_error()
        assert policy.status == PolicyStatus.INACTIVE
        assert policy.error_count == 0
        
        # Test clear error with enabled policy
        policy.enabled = True
        policy.mark_error("Another error")
        policy.clear_error()
        assert policy.status == PolicyStatus.ACTIVE
        assert policy.error_count == 0

    def test_policy_configuration_round_trip(self):
        """Test that policy configuration survives round-trip serialization."""
        original_config = {
            "schedule": {
                "cron": "0 2 * * *",
                "timezone": "UTC"
            },
            "retention": {
                "daily": 7,
                "weekly": 4,
                "monthly": 12,
                "yearly": 1
            },
            "targets": [
                {"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"},
                {"vm_id": "101", "cluster_id": "cluster1", "datastore_id": "ds2"}
            ],
            "options": {
                "compression": "lz4",
                "encryption": True,
                "verification": True,
                "bandwidth_limit": 1000,
                "max_concurrent_jobs": 2
            }
        }
        
        policy = BackupPolicy(
            name="Round Trip Test",
            tenant_id="tenant-123",
            configuration=original_config
        )
        
        # Verify configuration is preserved exactly
        assert policy.configuration == original_config
        assert policy.schedule == original_config["schedule"]
        assert policy.retention == original_config["retention"]
        assert policy.targets == original_config["targets"]
        assert policy.options == original_config["options"]

    def test_policy_validation_error_messages(self):
        """Test that validation provides helpful error messages."""
        # Test missing required field
        incomplete_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7}
            # Missing targets
        }
        
        is_valid, error = validate_policy_configuration(incomplete_config)
        assert is_valid is False
        assert error is not None
        assert "required" in error.lower() or "targets" in error.lower()
        
        # Test invalid field value
        invalid_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": -1},  # Invalid negative value
            "targets": [{"vm_id": "100", "cluster_id": "cluster1", "datastore_id": "ds1"}]
        }
        
        is_valid, error = validate_policy_configuration(invalid_config)
        assert is_valid is False
        assert error is not None