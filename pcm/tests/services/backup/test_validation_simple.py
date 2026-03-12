"""
Simplified tests for the PolicyValidationService focusing on core validation logic.
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


class TestPolicyValidationServiceCore:
    """Test core validation logic without complex database mocking."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def validation_service(self, mock_db_session):
        """Create a PolicyValidationService instance."""
        return PolicyValidationService(mock_db_session)
    
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
    
    def test_create_validation_service_factory(self):
        """Test validation service factory function."""
        mock_session = Mock(spec=Session)
        service = create_validation_service(mock_session)
        
        assert isinstance(service, PolicyValidationService)
        assert service.db == mock_session
    
    def test_schema_validation_with_invalid_config(self, validation_service):
        """Test schema validation with invalid configuration."""
        invalid_config = {
            "schedule": {"cron": "invalid"},
            "retention": {},  # Missing required fields
            "targets": []  # Empty targets not allowed
        }
        
        # Test the schema validation method directly
        errors = validation_service._validate_schema(invalid_config)
        
        assert len(errors) > 0
        assert any("Schema validation failed" in error.message for error in errors)
    
    def test_business_logic_validation_no_retention(self, validation_service):
        """Test business logic validation for missing retention."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 0, "weekly": 0, "monthly": 0},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"}]
        }
        
        errors, warnings = validation_service._validate_business_logic(config)
        
        retention_errors = [e for e in errors if "retention" in e.field]
        assert len(retention_errors) > 0
        assert "at least one retention period" in retention_errors[0].message.lower()
    
    def test_business_logic_validation_duplicate_targets(self, validation_service):
        """Test business logic validation for duplicate targets."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [
                {"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"},
                {"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-002"}  # Duplicate
            ]
        }
        
        errors, warnings = validation_service._validate_business_logic(config)
        
        duplicate_errors = [e for e in errors if "duplicate" in e.message.lower()]
        assert len(duplicate_errors) > 0
    
    def test_cron_validation_invalid_expression(self, validation_service):
        """Test cron expression validation."""
        schedule = {"cron": "invalid cron expression"}
        
        errors, warnings = validation_service._validate_schedule(schedule)
        
        assert len(errors) > 0
        cron_errors = [e for e in errors if "cron" in e.field.lower()]
        assert len(cron_errors) > 0
        assert "Invalid cron expression" in cron_errors[0].message
    
    def test_cron_validation_frequent_schedule_warning(self, validation_service):
        """Test warning for frequent backup schedules."""
        schedule = {"cron": "*/15 * * * *"}  # Every 15 minutes
        
        errors, warnings = validation_service._validate_schedule(schedule)
        
        assert len(errors) == 0  # Should be valid
        assert len(warnings) > 0
        frequent_warnings = [w for w in warnings if "frequent" in w.message.lower()]
        assert len(frequent_warnings) > 0
    
    def test_retention_validation_excessive_period(self, validation_service):
        """Test warning for excessive retention periods."""
        retention = {"yearly": 20}  # 20 years
        
        errors, warnings = validation_service._validate_retention(retention)
        
        assert len(errors) == 0  # Should be valid
        assert len(warnings) > 0
        excessive_warnings = [w for w in warnings if "exceeds 10 years" in w.message]
        assert len(excessive_warnings) > 0
    
    def test_options_validation_low_bandwidth(self, validation_service):
        """Test validation of backup options."""
        options = {"bandwidth_limit": 500}  # 500 KB/s, less than 1 MB/s
        
        errors, warnings = validation_service._validate_options(options)
        
        assert len(errors) == 0
        assert len(warnings) > 0
        bandwidth_warnings = [w for w in warnings if "bandwidth limit" in w.message.lower()]
        assert len(bandwidth_warnings) > 0
    
    def test_options_validation_disabled_verification(self, validation_service):
        """Test warning for disabled verification."""
        options = {"verification": False}
        
        errors, warnings = validation_service._validate_options(options)
        
        assert len(errors) == 0
        assert len(warnings) > 0
        verification_warnings = [w for w in warnings if "verification is disabled" in w.message.lower()]
        assert len(verification_warnings) > 0