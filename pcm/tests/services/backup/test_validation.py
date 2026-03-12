"""
Tests for the PolicyValidationService.

Tests comprehensive policy validation including schema validation,
business logic validation, tenant quota enforcement, and policy versioning.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from pcm.services.backup.validation import (
    PolicyValidationService,
    ValidationSeverity,
    ValidationError,
    ValidationResult,
    TenantQuota,
    PolicyVersion,
    create_validation_service
)
from pcm.core.models.backup.policy import BackupPolicy
from pcm.core.models.tenant import Tenant
from pcm.core.models.backup.datastore import Datastore, DatastoreStatus
from pcm.core.models.cluster import ProxmoxCluster


class TestPolicyValidationService:
    """Test cases for PolicyValidationService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def validation_service(self, mock_db_session):
        """Create a PolicyValidationService instance."""
        return PolicyValidationService(mock_db_session)
    
    @pytest.fixture
    def valid_policy_config(self):
        """Create a valid policy configuration."""
        return {
            "schedule": {
                "cron": "0 2 * * *",  # Daily at 2 AM
                "timezone": "UTC"
            },
            "retention": {
                "daily": 7,
                "weekly": 4,
                "monthly": 12
            },
            "targets": [
                {
                    "vm_id": "vm-001",
                    "cluster_id": "cluster-001",
                    "datastore_id": "datastore-001"
                }
            ],
            "options": {
                "compression": "lz4",
                "encryption": True,
                "verification": True
            }
        }
    
    def _setup_successful_mocks(self, mock_db_session):
        """Setup mocks for successful validation."""
        # Mock policy count query
        mock_count_query = Mock()
        mock_count_query.filter.return_value.scalar.return_value = 0
        
        # Mock resource queries
        mock_cluster = Mock()
        mock_datastore = Mock()
        mock_datastore.usage_percentage.return_value = 50.0
        
        mock_resource_query = Mock()
        mock_resource_query.filter.return_value.first.return_value = mock_cluster
        
        def query_side_effect(model_or_func):
            # Handle func.count() queries
            if hasattr(model_or_func, 'element') or 'count' in str(model_or_func):
                return mock_count_query
            # Handle model queries
            elif model_or_func == ProxmoxCluster:
                mock_resource_query.filter.return_value.first.return_value = mock_cluster
                return mock_resource_query
            elif model_or_func == Datastore:
                mock_resource_query.filter.return_value.first.return_value = mock_datastore
                return mock_resource_query
            else:
                return mock_count_query
        
        mock_db_session.query.side_effect = query_side_effect
    
    
    def test_validate_policy_success(self, validation_service, valid_policy_config, mock_db_session):
        """Test successful policy validation."""
        self._setup_successful_mocks(mock_db_session)
        
        result = validation_service.validate_policy(
            valid_policy_config, 
            "tenant-001"
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_policy_schema_error(self, validation_service, mock_db_session):
        """Test policy validation with schema errors."""
        invalid_config = {
            "schedule": {
                "cron": "invalid-cron"
            },
            "retention": {},  # Missing required retention
            "targets": []  # Empty targets
        }
        
        # Mock database queries to avoid comparison errors
        mock_count_query = Mock()
        mock_count_query.filter.return_value.scalar.return_value = 0
        mock_db_session.query.return_value = mock_count_query
        
        result = validation_service.validate_policy(invalid_config, "tenant-001")
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("Schema validation failed" in error.message for error in result.errors)
    
    def test_validate_cron_expression(self, validation_service, mock_db_session):
        """Test cron expression validation."""
        config = {
            "schedule": {"cron": "invalid cron"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}]
        }
        
        # Mock database queries to return proper values
        mock_db_session.query.return_value.filter.return_value.scalar.return_value = 0
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert not result.is_valid
        cron_errors = [e for e in result.errors if "cron" in e.field.lower()]
        assert len(cron_errors) > 0
        assert "Invalid cron expression" in cron_errors[0].message
    
    def test_validate_frequent_schedule_warning(self, validation_service, mock_db_session):
        """Test warning for very frequent backup schedules."""
        config = {
            "schedule": {"cron": "*/15 * * * *"},  # Every 15 minutes
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}]
        }
        
        # Mock cluster and datastore to exist
        mock_cluster = Mock()
        mock_datastore = Mock()
        mock_datastore.usage_percentage.return_value = 50.0  # 50% full
        
        # Create separate mock query objects for different queries
        mock_count_query = Mock()
        mock_count_query.filter.return_value.scalar.return_value = 0
        
        mock_cluster_query = Mock()
        mock_cluster_query.filter.return_value.first.return_value = mock_cluster
        
        mock_datastore_query = Mock()
        mock_datastore_query.filter.return_value.first.return_value = mock_datastore
        
        # Set up the query mock to return different objects based on call order
        mock_db_session.query.side_effect = [
            mock_count_query,  # First call for policy count
            mock_cluster_query,  # Second call for cluster lookup
            mock_datastore_query  # Third call for datastore lookup
        ]
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert result.is_valid  # Should be valid but with warnings
        assert len(result.warnings) > 0
        assert any("very frequent" in warning.message for warning in result.warnings)
    
    def test_validate_retention_logic(self, validation_service, mock_db_session):
        """Test retention validation logic."""
        # Test no retention specified
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 0, "weekly": 0, "monthly": 0},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}]
        }
        
        # Mock database queries
        mock_db_session.query.return_value.filter.return_value.scalar.return_value = 0
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert not result.is_valid
        retention_errors = [e for e in result.errors if "retention" in e.field]
        assert len(retention_errors) > 0
        assert "at least one retention period" in retention_errors[0].message.lower()
    
    def test_validate_excessive_retention_warning(self, validation_service, mock_db_session):
        """Test warning for excessive retention periods."""
        # Set a higher retention quota to allow the test
        from pcm.services.backup.validation import TenantQuota
        quota = TenantQuota(max_retention_days=5000)  # Allow up to 5000 days
        validation_service.set_tenant_quota("tenant-001", quota)
        
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"yearly": 11},  # 11 years to trigger the warning
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}]
        }
        
        # Mock cluster and datastore to exist
        mock_cluster = Mock()
        mock_datastore = Mock()
        mock_datastore.usage_percentage.return_value = 50.0  # 50% full
        
        # Create separate mock query objects for different queries
        mock_count_query = Mock()
        mock_count_query.filter.return_value.scalar.return_value = 0
        
        mock_cluster_query = Mock()
        mock_cluster_query.filter.return_value.first.return_value = mock_cluster
        
        mock_datastore_query = Mock()
        mock_datastore_query.filter.return_value.first.return_value = mock_datastore
        
        # Set up the query mock to return different objects based on call order
        mock_db_session.query.side_effect = [
            mock_count_query,  # First call for policy count
            mock_cluster_query,  # Second call for cluster lookup
            mock_datastore_query  # Third call for datastore lookup
        ]
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert result.is_valid
        assert len(result.warnings) > 0
        assert any("exceeds 10 years" in warning.message for warning in result.warnings)
    
    def test_validate_duplicate_targets(self, validation_service, mock_db_session):
        """Test validation of duplicate backup targets."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [
                {"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"},
                {"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-002"}  # Duplicate VM
            ]
        }
        
        # Mock database queries
        mock_db_session.query.return_value.filter.return_value.scalar.return_value = 0
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert not result.is_valid
        duplicate_errors = [e for e in result.errors if "duplicate" in e.message.lower()]
        assert len(duplicate_errors) > 0
    
    def test_validate_tenant_quota_enforcement(self, validation_service, mock_db_session):
        """Test tenant quota enforcement."""
        # Set a restrictive quota
        quota = TenantQuota(max_policies=1, max_targets_per_policy=1)
        validation_service.set_tenant_quota("tenant-001", quota)
        
        # Mock that tenant already has 1 policy
        mock_db_session.query.return_value.filter.return_value.scalar.return_value = 1
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}]
        }
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert not result.is_valid
        quota_errors = [e for e in result.errors if "quota" in e.code.lower()]
        assert len(quota_errors) > 0
        assert "maximum policy limit" in quota_errors[0].message
    
    def test_validate_targets_quota_exceeded(self, validation_service, mock_db_session):
        """Test targets per policy quota enforcement."""
        quota = TenantQuota(max_targets_per_policy=1)
        validation_service.set_tenant_quota("tenant-001", quota)
        
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [
                {"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"},
                {"vm_id": "vm-002", "cluster_id": "cluster-001", "datastore_id": "ds-001"}
            ]
        }
        
        # Mock database queries
        mock_db_session.query.return_value.filter.return_value.scalar.return_value = 0
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert not result.is_valid
        quota_errors = [e for e in result.errors if "targets" in e.field and "quota" in e.code.lower()]
        assert len(quota_errors) > 0
    
    def test_validate_resource_availability(self, validation_service, mock_db_session):
        """Test resource availability validation."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}]
        }
        
        # Mock cluster not found
        mock_db_session.query.return_value.filter.return_value.scalar.return_value = 0
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert not result.is_valid
        resource_errors = [e for e in result.errors if "not accessible" in e.message]
        assert len(resource_errors) > 0
    
    def test_validate_datastore_capacity_warning(self, validation_service, mock_db_session):
        """Test datastore capacity warning."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}]
        }
        
        # Mock cluster and datastore
        mock_cluster = Mock()
        mock_datastore = Mock()
        mock_datastore.usage_percentage.return_value = 95.0  # 95% full
        mock_datastore.name = "test-datastore"
        
        # Create separate mock query objects for different queries
        mock_count_query = Mock()
        mock_count_query.filter.return_value.scalar.return_value = 0
        
        mock_cluster_query = Mock()
        mock_cluster_query.filter.return_value.first.return_value = mock_cluster
        
        mock_datastore_query = Mock()
        mock_datastore_query.filter.return_value.first.return_value = mock_datastore
        
        # Set up the query mock to return different objects based on call order
        mock_db_session.query.side_effect = [
            mock_count_query,  # First call for policy count
            mock_cluster_query,  # Second call for cluster lookup
            mock_datastore_query  # Third call for datastore lookup
        ]
        
        result = validation_service.validate_policy(config, "tenant-001")
        
        assert result.is_valid
        assert len(result.warnings) > 0
        capacity_warnings = [w for w in result.warnings if "90% full" in w.message]
        assert len(capacity_warnings) > 0
    
    def test_validate_policy_update(self, validation_service, mock_db_session):
        """Test policy update validation with change impact analysis."""
        # Create existing policy
        existing_policy = BackupPolicy(
            id="policy-001",
            name="Test Policy",
            tenant_id="tenant-001",
            configuration={
                "schedule": {"cron": "0 2 * * *"},
                "retention": {"daily": 14, "weekly": 4},
                "targets": [
                    {"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"},
                    {"vm_id": "vm-002", "cluster_id": "cluster-001", "datastore_id": "ds-001"}
                ]
            }
        )
        
        # New configuration removes a target and reduces retention
        new_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7, "weekly": 4},  # Reduced daily retention
            "targets": [
                {"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}
                # vm-002 removed
            ]
        }
        
        # Mock cluster and datastore to exist
        mock_cluster = Mock()
        mock_datastore = Mock()
        mock_datastore.usage_percentage.return_value = 50.0  # 50% full
        
        # Create separate mock query objects for different queries
        mock_count_query = Mock()
        mock_count_query.filter.return_value.scalar.return_value = 1
        
        mock_cluster_query = Mock()
        mock_cluster_query.filter.return_value.first.return_value = mock_cluster
        
        mock_datastore_query = Mock()
        mock_datastore_query.filter.return_value.first.return_value = mock_datastore
        
        # Set up the query mock to return different objects based on call order
        mock_db_session.query.side_effect = [
            mock_count_query,  # First call for policy count
            mock_cluster_query,  # Second call for cluster lookup
            mock_datastore_query  # Third call for datastore lookup
        ]
        
        result = validation_service.validate_policy_update(new_config, existing_policy)
        
        assert result.is_valid  # Should be valid but with warnings
        assert len(result.warnings) > 0
        
        # Check for target removal warning
        target_warnings = [w for w in result.warnings if "removing targets" in w.message.lower()]
        assert len(target_warnings) > 0
        
        # Check for retention reduction warning
        retention_warnings = [w for w in result.warnings if "reducing" in w.message.lower()]
        assert len(retention_warnings) > 0
    
    def test_tenant_quota_management(self, validation_service):
        """Test tenant quota management."""
        tenant_id = "tenant-001"
        custom_quota = TenantQuota(max_policies=100, max_targets_per_policy=50)
        
        # Set custom quota
        validation_service.set_tenant_quota(tenant_id, custom_quota)
        
        # Retrieve quota
        retrieved_quota = validation_service.get_tenant_quota(tenant_id)
        
        assert retrieved_quota.max_policies == 100
        assert retrieved_quota.max_targets_per_policy == 50
        
        # Test default quota for unknown tenant
        default_quota = validation_service.get_tenant_quota("unknown-tenant")
        assert default_quota.max_policies == 50  # Default value
    
    def test_policy_versioning(self, validation_service):
        """Test policy version creation and tracking."""
        policy = BackupPolicy(
            id="policy-001",
            name="Test Policy",
            tenant_id="tenant-001",
            configuration={}
        )
        
        changes = {
            "retention": {"old": {"daily": 7}, "new": {"daily": 14}},
            "targets": {"added": ["vm-003"], "removed": []}
        }
        
        version = validation_service.create_policy_version(
            policy, 
            changes, 
            created_by="user-001",
            reason="Increased retention for compliance"
        )
        
        assert version.version == 1  # First version
        assert version.changes == changes
        assert version.created_by == "user-001"
        assert version.reason == "Increased retention for compliance"
        assert isinstance(version.timestamp, datetime)
    
    def test_format_validation_errors(self, validation_service):
        """Test validation error formatting."""
        errors = [
            ValidationError(
                field="schedule.cron",
                message="Invalid cron expression",
                severity=ValidationSeverity.ERROR,
                code="INVALID_CRON"
            )
        ]
        warnings = [
            ValidationError(
                field="retention",
                message="Excessive retention period",
                severity=ValidationSeverity.WARNING,
                code="EXCESSIVE_RETENTION"
            )
        ]
        
        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        formatted = validation_service.format_validation_errors(result)
        
        assert "Policy validation failed" in formatted
        assert "schedule.cron: Invalid cron expression" in formatted
        assert "retention: Excessive retention period" in formatted
    
    def test_validation_summary(self, validation_service):
        """Test validation result summary generation."""
        errors = [
            ValidationError(
                field="targets",
                message="No targets specified",
                severity=ValidationSeverity.ERROR,
                code="NO_TARGETS",
                details={"target_count": 0}
            )
        ]
        
        result = ValidationResult(is_valid=False, errors=errors, warnings=[])
        summary = validation_service.get_validation_summary(result)
        
        assert summary["is_valid"] is False
        assert summary["error_count"] == 1
        assert summary["warning_count"] == 0
        assert len(summary["errors"]) == 1
        assert summary["errors"][0]["field"] == "targets"
        assert summary["errors"][0]["code"] == "NO_TARGETS"
        assert summary["errors"][0]["details"]["target_count"] == 0


class TestValidationComponents:
    """Test individual validation components."""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation."""
        error = ValidationError(
            field="test.field",
            message="Test error message",
            severity=ValidationSeverity.ERROR,
            code="TEST_ERROR",
            details={"key": "value"}
        )
        
        assert error.field == "test.field"
        assert error.message == "Test error message"
        assert error.severity == ValidationSeverity.ERROR
        assert error.code == "TEST_ERROR"
        assert error.details == {"key": "value"}
    
    def test_validation_result_properties(self):
        """Test ValidationResult properties."""
        errors = [ValidationError("field1", "error", ValidationSeverity.ERROR, "CODE1")]
        warnings = [ValidationError("field2", "warning", ValidationSeverity.WARNING, "CODE2")]
        
        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        assert result.has_errors is True
        assert result.has_warnings is True
        assert not result.is_valid
    
    def test_tenant_quota_defaults(self):
        """Test TenantQuota default values."""
        quota = TenantQuota()
        
        assert quota.max_policies == 50
        assert quota.max_targets_per_policy == 100
        assert quota.max_retention_days == 365
        assert quota.max_concurrent_jobs == 10
        assert quota.max_policy_size_mb == 10
    
    def test_create_validation_service_factory(self):
        """Test validation service factory function."""
        mock_session = Mock(spec=Session)
        service = create_validation_service(mock_session)
        
        assert isinstance(service, PolicyValidationService)
        assert service.db == mock_session