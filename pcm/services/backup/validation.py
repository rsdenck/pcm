"""
Policy validation service for backup policies.

This module provides comprehensive validation for backup policies including
business logic validation, tenant quota enforcement, and policy versioning
with detailed error messages and audit tracking.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import re
from croniter import croniter
from sqlalchemy.orm import Session
from sqlalchemy import func

from pcm.core.models.backup.policy import BackupPolicy, validate_policy_configuration
from pcm.core.models.tenant import Tenant
from pcm.core.models.backup.datastore import Datastore
from pcm.core.models.cluster import ProxmoxCluster


class ValidationSeverity(str, Enum):
    """Severity levels for validation errors."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Represents a validation error with detailed information."""
    field: str
    message: str
    severity: ValidationSeverity
    code: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of policy validation with errors and warnings."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any validation warnings."""
        return len(self.warnings) > 0


@dataclass
class TenantQuota:
    """Tenant quota configuration."""
    max_policies: int = 50
    max_targets_per_policy: int = 100
    max_retention_days: int = 365
    max_concurrent_jobs: int = 10
    max_policy_size_mb: int = 10

@dataclass
class PolicyVersion:
    """Represents a policy version for change tracking."""
    version: int
    timestamp: datetime
    changes: Dict[str, Any]
    created_by: Optional[str] = None
    reason: Optional[str] = None


class PolicyValidationService:
    """
    Comprehensive policy validation service with business logic validation,
    tenant quota enforcement, and policy versioning capabilities.
    
    Provides detailed error messages and supports policy change tracking
    for audit purposes.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the policy validation service.
        
        Args:
            db_session: Database session for quota and resource validation
        """
        self.db = db_session
        self._default_quota = TenantQuota()
        self._tenant_quotas: Dict[str, TenantQuota] = {}
    
    def validate_policy(self, policy_config: Dict[str, Any], 
                       tenant_id: str,
                       policy_id: Optional[str] = None,
                       existing_policy: Optional[BackupPolicy] = None) -> ValidationResult:
        """
        Comprehensive policy validation including schema, business logic, and quotas.
        
        Args:
            policy_config: Policy configuration to validate
            tenant_id: Tenant ID for quota enforcement
            policy_id: Policy ID for updates (None for new policies)
            existing_policy: Existing policy for comparison (for updates)
            
        Returns:
            ValidationResult with detailed errors and warnings
        """
        errors = []
        warnings = []
        
        # 1. Schema validation
        schema_errors = self._validate_schema(policy_config)
        errors.extend(schema_errors)
        
        # 2. Business logic validation
        business_errors, business_warnings = self._validate_business_logic(policy_config)
        errors.extend(business_errors)
        warnings.extend(business_warnings)
        
        # 3. Tenant quota validation
        quota_errors, quota_warnings = self._validate_tenant_quotas(
            policy_config, tenant_id, policy_id
        )
        errors.extend(quota_errors)
        warnings.extend(quota_warnings)
        
        # 4. Resource availability validation
        resource_errors, resource_warnings = self._validate_resource_availability(
            policy_config, tenant_id
        )
        errors.extend(resource_errors)
        warnings.extend(resource_warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_policy_update(self, new_config: Dict[str, Any],
                             existing_policy: BackupPolicy) -> ValidationResult:
        """
        Validate policy updates with change impact analysis.
        
        Args:
            new_config: New policy configuration
            existing_policy: Current policy to update
            
        Returns:
            ValidationResult with update-specific validation
        """
        # First run standard validation
        result = self.validate_policy(
            new_config, 
            existing_policy.tenant_id,
            existing_policy.id,
            existing_policy
        )
        
        # Add update-specific validations
        update_errors, update_warnings = self._validate_policy_changes(
            new_config, existing_policy
        )
        result.errors.extend(update_errors)
        result.warnings.extend(update_warnings)
        
        return result
    
    def set_tenant_quota(self, tenant_id: str, quota: TenantQuota) -> None:
        """
        Set custom quota for a specific tenant.
        
        Args:
            tenant_id: Tenant identifier
            quota: Custom quota configuration
        """
        self._tenant_quotas[tenant_id] = quota
    
    def get_tenant_quota(self, tenant_id: str) -> TenantQuota:
        """
        Get quota configuration for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant quota configuration
        """
        return self._tenant_quotas.get(tenant_id, self._default_quota)
    
    def create_policy_version(self, policy: BackupPolicy, 
                            changes: Dict[str, Any],
                            created_by: Optional[str] = None,
                            reason: Optional[str] = None) -> PolicyVersion:
        """
        Create a new policy version for change tracking.
        
        Args:
            policy: Policy being versioned
            changes: Dictionary of changes made
            created_by: User who made the changes
            reason: Reason for the changes
            
        Returns:
            PolicyVersion object
        """
        # Get current version number
        current_version = self._get_current_version(policy.id) if policy.id else 0
        
        return PolicyVersion(
            version=current_version + 1,
            timestamp=datetime.now(timezone.utc),
            changes=changes,
            created_by=created_by,
            reason=reason
        )
    
    def _validate_schema(self, config: Dict[str, Any]) -> List[ValidationError]:
        """Validate configuration against JSON schema."""
        errors = []
        
        is_valid, error_message = validate_policy_configuration(config)
        if not is_valid:
            errors.append(ValidationError(
                field="configuration",
                message=f"Schema validation failed: {error_message}",
                severity=ValidationSeverity.ERROR,
                code="SCHEMA_VALIDATION_FAILED",
                details={"original_error": error_message}
            ))
        
        return errors
    
    def _validate_business_logic(self, config: Dict[str, Any]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate business logic rules."""
        errors = []
        warnings = []
        
        # Validate schedule
        schedule_errors, schedule_warnings = self._validate_schedule(config.get("schedule", {}))
        errors.extend(schedule_errors)
        warnings.extend(schedule_warnings)
        
        # Validate retention
        retention_errors, retention_warnings = self._validate_retention(config.get("retention", {}))
        errors.extend(retention_errors)
        warnings.extend(retention_warnings)
        
        # Validate targets
        targets_errors, targets_warnings = self._validate_targets(config.get("targets", []))
        errors.extend(targets_errors)
        warnings.extend(targets_warnings)
        
        # Validate options
        options_errors, options_warnings = self._validate_options(config.get("options", {}))
        errors.extend(options_errors)
        warnings.extend(options_warnings)
        
        return errors, warnings
    
    def _validate_schedule(self, schedule: Dict[str, Any]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate backup schedule configuration."""
        errors = []
        warnings = []
        
        cron_expr = schedule.get("cron")
        if cron_expr:
            try:
                # Validate cron expression
                cron = croniter(cron_expr)
                
                # Check if schedule is too frequent (less than 1 hour)
                next_run = cron.get_next(datetime)
                second_run = cron.get_next(datetime)
                interval_seconds = (second_run - next_run).total_seconds()
                
                if interval_seconds < 3600:  # Less than 1 hour
                    warnings.append(ValidationError(
                        field="schedule.cron",
                        message="Backup schedule is very frequent (less than 1 hour). This may impact system performance.",
                        severity=ValidationSeverity.WARNING,
                        code="SCHEDULE_TOO_FREQUENT",
                        details={"interval_seconds": interval_seconds}
                    ))
                
                # Check if schedule runs during business hours
                if self._runs_during_business_hours(cron_expr):
                    warnings.append(ValidationError(
                        field="schedule.cron",
                        message="Backup schedule runs during business hours (9 AM - 5 PM). Consider scheduling during off-hours for better performance.",
                        severity=ValidationSeverity.WARNING,
                        code="SCHEDULE_BUSINESS_HOURS"
                    ))
                    
            except (ValueError, TypeError) as e:
                errors.append(ValidationError(
                    field="schedule.cron",
                    message=f"Invalid cron expression: {str(e)}",
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_CRON_EXPRESSION",
                    details={"cron_expression": cron_expr, "error": str(e)}
                ))
        
        return errors, warnings
    
    def _validate_retention(self, retention: Dict[str, Any]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate backup retention configuration."""
        errors = []
        warnings = []
        
        # Check if at least one retention period is specified
        retention_periods = ["daily", "weekly", "monthly", "yearly"]
        has_retention = any(retention.get(period, 0) > 0 for period in retention_periods)
        
        if not has_retention:
            errors.append(ValidationError(
                field="retention",
                message="At least one retention period must be greater than 0",
                severity=ValidationSeverity.ERROR,
                code="NO_RETENTION_SPECIFIED"
            ))
        
        # Validate retention logic
        daily = retention.get("daily", 0)
        weekly = retention.get("weekly", 0)
        monthly = retention.get("monthly", 0)
        yearly = retention.get("yearly", 0)
        
        # Check for excessive retention
        total_retention_days = daily + (weekly * 7) + (monthly * 30) + (yearly * 365)
        if total_retention_days > 3650:  # More than 10 years
            warnings.append(ValidationError(
                field="retention",
                message="Total retention period exceeds 10 years. This may result in high storage costs.",
                severity=ValidationSeverity.WARNING,
                code="EXCESSIVE_RETENTION",
                details={"total_days": total_retention_days}
            ))
        
        # Check retention hierarchy logic
        if weekly > 0 and daily == 0:
            warnings.append(ValidationError(
                field="retention",
                message="Weekly retention is set but daily retention is 0. Consider setting daily retention for better recovery granularity.",
                severity=ValidationSeverity.WARNING,
                code="RETENTION_HIERARCHY_WARNING"
            ))
        
        return errors, warnings
    
    def _validate_targets(self, targets: List[Dict[str, Any]]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate backup targets."""
        errors = []
        warnings = []
        
        if not targets:
            errors.append(ValidationError(
                field="targets",
                message="At least one backup target must be specified",
                severity=ValidationSeverity.ERROR,
                code="NO_TARGETS_SPECIFIED"
            ))
            return errors, warnings
        
        # Check for duplicate targets
        target_keys = []
        for i, target in enumerate(targets):
            vm_id = target.get("vm_id")
            cluster_id = target.get("cluster_id")
            datastore_id = target.get("datastore_id")
            
            target_key = f"{cluster_id}:{vm_id}"
            if target_key in target_keys:
                errors.append(ValidationError(
                    field=f"targets[{i}]",
                    message=f"Duplicate target: VM {vm_id} in cluster {cluster_id} is specified multiple times",
                    severity=ValidationSeverity.ERROR,
                    code="DUPLICATE_TARGET",
                    details={"vm_id": vm_id, "cluster_id": cluster_id}
                ))
            else:
                target_keys.append(target_key)
        
        # Warn about too many targets
        if len(targets) > 50:
            warnings.append(ValidationError(
                field="targets",
                message=f"Policy has {len(targets)} targets. Large numbers of targets may impact backup performance.",
                severity=ValidationSeverity.WARNING,
                code="MANY_TARGETS",
                details={"target_count": len(targets)}
            ))
        
        return errors, warnings
    
    def _validate_options(self, options: Dict[str, Any]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate backup options."""
        errors = []
        warnings = []
        
        # Validate bandwidth limit
        bandwidth_limit = options.get("bandwidth_limit", 0)
        if bandwidth_limit is not None and bandwidth_limit < 0:
            errors.append(ValidationError(
                field="options.bandwidth_limit",
                message="Bandwidth limit cannot be negative",
                severity=ValidationSeverity.ERROR,
                code="INVALID_BANDWIDTH_LIMIT"
            ))
        elif bandwidth_limit is not None and 0 < bandwidth_limit < 1024:  # Less than 1 MB/s
            warnings.append(ValidationError(
                field="options.bandwidth_limit",
                message="Bandwidth limit is very low (< 1 MB/s). This may cause backup timeouts.",
                severity=ValidationSeverity.WARNING,
                code="LOW_BANDWIDTH_LIMIT",
                details={"bandwidth_limit_kbps": bandwidth_limit}
            ))
        
        # Validate concurrent jobs
        max_concurrent = options.get("max_concurrent_jobs", 1)
        if max_concurrent > 5:
            warnings.append(ValidationError(
                field="options.max_concurrent_jobs",
                message="High concurrent job count may impact system performance",
                severity=ValidationSeverity.WARNING,
                code="HIGH_CONCURRENT_JOBS",
                details={"max_concurrent_jobs": max_concurrent}
            ))
        
        # Warn about disabled verification
        if not options.get("verification", True):
            warnings.append(ValidationError(
                field="options.verification",
                message="Backup verification is disabled. This reduces data integrity assurance.",
                severity=ValidationSeverity.WARNING,
                code="VERIFICATION_DISABLED"
            ))
        
        return errors, warnings
    
    def _validate_tenant_quotas(self, config: Dict[str, Any], 
                               tenant_id: str,
                               policy_id: Optional[str] = None) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate tenant quota enforcement."""
        errors = []
        warnings = []
        
        quota = self.get_tenant_quota(tenant_id)
        
        # Check policy count quota
        current_policy_count = self.db.query(func.count(BackupPolicy.id)).filter(
            BackupPolicy.tenant_id == tenant_id,
            BackupPolicy.id != policy_id if policy_id else True
        ).scalar() or 0
        
        if current_policy_count >= quota.max_policies:
            errors.append(ValidationError(
                field="tenant_quota",
                message=f"Tenant has reached maximum policy limit ({quota.max_policies})",
                severity=ValidationSeverity.ERROR,
                code="POLICY_QUOTA_EXCEEDED",
                details={
                    "current_count": current_policy_count,
                    "max_allowed": quota.max_policies
                }
            ))
        elif current_policy_count >= quota.max_policies * 0.8:  # 80% warning
            warnings.append(ValidationError(
                field="tenant_quota",
                message=f"Tenant is approaching policy limit ({current_policy_count}/{quota.max_policies})",
                severity=ValidationSeverity.WARNING,
                code="POLICY_QUOTA_WARNING",
                details={
                    "current_count": current_policy_count,
                    "max_allowed": quota.max_policies
                }
            ))
        
        # Check targets per policy quota
        targets = config.get("targets", [])
        if len(targets) > quota.max_targets_per_policy:
            errors.append(ValidationError(
                field="targets",
                message=f"Policy exceeds maximum targets per policy ({quota.max_targets_per_policy})",
                severity=ValidationSeverity.ERROR,
                code="TARGETS_QUOTA_EXCEEDED",
                details={
                    "target_count": len(targets),
                    "max_allowed": quota.max_targets_per_policy
                }
            ))
        
        # Check retention quota
        retention = config.get("retention", {})
        max_retention_days = max([
            retention.get("daily", 0),
            retention.get("weekly", 0) * 7,
            retention.get("monthly", 0) * 30,
            retention.get("yearly", 0) * 365
        ])
        
        if max_retention_days > quota.max_retention_days:
            errors.append(ValidationError(
                field="retention",
                message=f"Retention period exceeds tenant limit ({quota.max_retention_days} days)",
                severity=ValidationSeverity.ERROR,
                code="RETENTION_QUOTA_EXCEEDED",
                details={
                    "requested_days": max_retention_days,
                    "max_allowed": quota.max_retention_days
                }
            ))
        
        # Check concurrent jobs quota
        options = config.get("options", {})
        max_concurrent = options.get("max_concurrent_jobs", 1)
        if max_concurrent > quota.max_concurrent_jobs:
            errors.append(ValidationError(
                field="options.max_concurrent_jobs",
                message=f"Concurrent jobs exceed tenant limit ({quota.max_concurrent_jobs})",
                severity=ValidationSeverity.ERROR,
                code="CONCURRENT_JOBS_QUOTA_EXCEEDED",
                details={
                    "requested_jobs": max_concurrent,
                    "max_allowed": quota.max_concurrent_jobs
                }
            ))
        
        return errors, warnings
    
    def _validate_resource_availability(self, config: Dict[str, Any], 
                                       tenant_id: str) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate that required resources are available and accessible."""
        errors = []
        warnings = []
        
        targets = config.get("targets", [])
        
        for i, target in enumerate(targets):
            vm_id = target.get("vm_id")
            cluster_id = target.get("cluster_id")
            datastore_id = target.get("datastore_id")
            
            # Validate cluster exists and is accessible to tenant
            cluster = self.db.query(ProxmoxCluster).filter(
                ProxmoxCluster.id == cluster_id,
                ProxmoxCluster.tenant_id == tenant_id
            ).first()
            
            if not cluster:
                errors.append(ValidationError(
                    field=f"targets[{i}].cluster_id",
                    message=f"Cluster {cluster_id} not found or not accessible to tenant",
                    severity=ValidationSeverity.ERROR,
                    code="CLUSTER_NOT_ACCESSIBLE",
                    details={"cluster_id": cluster_id, "tenant_id": tenant_id}
                ))
                continue
            
            # Validate datastore exists and is accessible to tenant
            datastore = self.db.query(Datastore).filter(
                Datastore.id == datastore_id,
                Datastore.tenant_id == tenant_id
            ).first()
            
            if not datastore:
                errors.append(ValidationError(
                    field=f"targets[{i}].datastore_id",
                    message=f"Datastore {datastore_id} not found or not accessible to tenant",
                    severity=ValidationSeverity.ERROR,
                    code="DATASTORE_NOT_ACCESSIBLE",
                    details={"datastore_id": datastore_id, "tenant_id": tenant_id}
                ))
                continue
            
            # Check datastore capacity
            if datastore.usage_percentage() and datastore.usage_percentage() > 90:
                warnings.append(ValidationError(
                    field=f"targets[{i}].datastore_id",
                    message=f"Datastore {datastore.name} is over 90% full",
                    severity=ValidationSeverity.WARNING,
                    code="DATASTORE_NEARLY_FULL",
                    details={
                        "datastore_id": datastore_id,
                        "usage_percentage": datastore.usage_percentage()
                    }
                ))
        
        return errors, warnings
    
    def _validate_policy_changes(self, new_config: Dict[str, Any], 
                               existing_policy: BackupPolicy) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate policy update changes and their impact."""
        errors = []
        warnings = []
        
        old_config = existing_policy.configuration
        
        # Check for breaking changes
        old_targets = {f"{t['cluster_id']}:{t['vm_id']}" for t in old_config.get("targets", [])}
        new_targets = {f"{t['cluster_id']}:{t['vm_id']}" for t in new_config.get("targets", [])}
        
        removed_targets = old_targets - new_targets
        if removed_targets:
            warnings.append(ValidationError(
                field="targets",
                message=f"Removing targets from active policy: {', '.join(removed_targets)}",
                severity=ValidationSeverity.WARNING,
                code="TARGETS_REMOVED",
                details={"removed_targets": list(removed_targets)}
            ))
        
        # Check retention changes
        old_retention = old_config.get("retention", {})
        new_retention = new_config.get("retention", {})
        
        for period in ["daily", "weekly", "monthly", "yearly"]:
            old_value = old_retention.get(period, 0)
            new_value = new_retention.get(period, 0)
            
            if new_value < old_value:
                warnings.append(ValidationError(
                    field=f"retention.{period}",
                    message=f"Reducing {period} retention from {old_value} to {new_value} may cause data loss",
                    severity=ValidationSeverity.WARNING,
                    code="RETENTION_REDUCED",
                    details={
                        "period": period,
                        "old_value": old_value,
                        "new_value": new_value
                    }
                ))
        
        return errors, warnings
    
    def _runs_during_business_hours(self, cron_expr: str) -> bool:
        """Check if cron expression runs during business hours (9 AM - 5 PM)."""
        try:
            cron = croniter(cron_expr)
            # Check next 7 runs to see if any fall during business hours
            for _ in range(7):
                next_run = cron.get_next(datetime)
                if 9 <= next_run.hour <= 17:  # 9 AM to 5 PM
                    return True
            return False
        except:
            return False
    
    def _get_current_version(self, policy_id: str) -> int:
        """Get current version number for a policy."""
        # This would typically query a policy_versions table
        # For now, return 0 as placeholder
        return 0
    
    def format_validation_errors(self, result: ValidationResult) -> str:
        """
        Format validation result into a human-readable error message.
        
        Args:
            result: ValidationResult to format
            
        Returns:
            Formatted error message string
        """
        if result.is_valid:
            return "Policy validation passed successfully"
        
        lines = ["Policy validation failed:"]
        
        if result.errors:
            lines.append("\nErrors:")
            for error in result.errors:
                lines.append(f"  • {error.field}: {error.message}")
        
        if result.warnings:
            lines.append("\nWarnings:")
            for warning in result.warnings:
                lines.append(f"  • {warning.field}: {warning.message}")
        
        return "\n".join(lines)
    
    def get_validation_summary(self, result: ValidationResult) -> Dict[str, Any]:
        """
        Get a structured summary of validation results.
        
        Args:
            result: ValidationResult to summarize
            
        Returns:
            Dictionary with validation summary
        """
        return {
            "is_valid": result.is_valid,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "errors": [
                {
                    "field": error.field,
                    "message": error.message,
                    "severity": error.severity.value,
                    "code": error.code,
                    "details": error.details
                }
                for error in result.errors
            ],
            "warnings": [
                {
                    "field": warning.field,
                    "message": warning.message,
                    "severity": warning.severity.value,
                    "code": warning.code,
                    "details": warning.details
                }
                for warning in result.warnings
            ]
        }


def create_validation_service(db_session: Session) -> PolicyValidationService:
    """
    Factory function to create a PolicyValidationService instance.
    
    Args:
        db_session: Database session
        
    Returns:
        Configured PolicyValidationService instance
    """
    return PolicyValidationService(db_session)