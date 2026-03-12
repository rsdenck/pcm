#!/usr/bin/env python3
"""
Example demonstrating the PolicyValidationService usage.

This example shows how to use the PolicyValidationService to validate
backup policy configurations with comprehensive error reporting and
tenant quota enforcement.
"""

import sys
import os
from unittest.mock import Mock

# Add the parent directory to the path so we can import pcm modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pcm.services.backup.validation import (
    PolicyValidationService,
    TenantQuota,
    ValidationSeverity
)


def main():
    """Demonstrate PolicyValidationService usage."""
    print("=== PCM Policy Validation Service Example ===\n")
    
    # Create a mock database session (in real usage, this would be a real session)
    mock_db = Mock()
    
    # Setup proper mocks for database queries
    mock_count_query = Mock()
    mock_count_query.filter.return_value.scalar.return_value = 0
    
    mock_cluster = Mock()
    mock_datastore = Mock()
    mock_datastore.usage_percentage.return_value = 50.0  # 50% usage
    
    mock_resource_query = Mock()
    mock_resource_query.filter.return_value.first.return_value = mock_cluster
    
    def query_side_effect(model_or_func):
        if hasattr(model_or_func, 'element') or 'count' in str(model_or_func):
            return mock_count_query
        else:
            # For resource queries, alternate between cluster and datastore
            if hasattr(query_side_effect, 'call_count'):
                query_side_effect.call_count += 1
            else:
                query_side_effect.call_count = 1
            
            if query_side_effect.call_count % 2 == 1:
                mock_resource_query.filter.return_value.first.return_value = mock_cluster
            else:
                mock_resource_query.filter.return_value.first.return_value = mock_datastore
            return mock_resource_query
    
    mock_db.query.side_effect = query_side_effect
    
    # Create validation service
    validator = PolicyValidationService(mock_db)
    
    # Example 1: Valid policy configuration
    print("1. Testing valid policy configuration:")
    valid_config = {
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
    
    # Note: This will fail resource validation due to mocking, but shows schema validation
    result = validator.validate_policy(valid_config, "tenant-001")
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    if result.errors:
        print("   Error details:")
        for error in result.errors[:2]:  # Show first 2 errors
            print(f"     - {error.field}: {error.message}")
    print()
    
    # Example 2: Invalid policy configuration
    print("2. Testing invalid policy configuration:")
    invalid_config = {
        "schedule": {
            "cron": "invalid-cron-expression"
        },
        "retention": {},  # Missing required retention
        "targets": []  # Empty targets not allowed
    }
    
    result = validator.validate_policy(invalid_config, "tenant-001")
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    if result.errors:
        print("   Error details:")
        for error in result.errors[:3]:  # Show first 3 errors
            print(f"     - {error.field}: {error.message}")
    print()
    
    # Example 3: Policy with warnings
    print("3. Testing policy with warnings:")
    warning_config = {
        "schedule": {
            "cron": "*/15 * * * *"  # Very frequent - every 15 minutes
        },
        "retention": {
            "yearly": 20  # Excessive - 20 years
        },
        "targets": [
            {
                "vm_id": "vm-001",
                "cluster_id": "cluster-001", 
                "datastore_id": "datastore-001"
            }
        ],
        "options": {
            "verification": False,  # Disabled verification
            "bandwidth_limit": 500  # Low bandwidth
        }
    }
    
    result = validator.validate_policy(warning_config, "tenant-001")
    print(f"   Valid: {result.is_valid}")
    print(f"   Warnings: {len(result.warnings)}")
    if result.warnings:
        print("   Warning details:")
        for warning in result.warnings[:3]:  # Show first 3 warnings
            print(f"     - {warning.field}: {warning.message}")
    print()
    
    # Example 4: Tenant quota enforcement
    print("4. Testing tenant quota enforcement:")
    restrictive_quota = TenantQuota(
        max_policies=1,
        max_targets_per_policy=1,
        max_retention_days=30
    )
    validator.set_tenant_quota("restricted-tenant", restrictive_quota)
    
    # Mock that tenant already has 1 policy
    mock_db.query.return_value.filter.return_value.scalar.return_value = 1
    
    quota_test_config = {
        "schedule": {"cron": "0 2 * * *"},
        "retention": {"daily": 60},  # Exceeds 30-day limit
        "targets": [
            {"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "ds-001"},
            {"vm_id": "vm-002", "cluster_id": "cluster-001", "datastore_id": "ds-001"}  # Exceeds 1 target limit
        ]
    }
    
    result = validator.validate_policy(quota_test_config, "restricted-tenant")
    print(f"   Valid: {result.is_valid}")
    print(f"   Quota errors: {len([e for e in result.errors if 'quota' in e.code.lower()])}")
    if result.errors:
        print("   Quota error details:")
        for error in [e for e in result.errors if 'quota' in e.code.lower()][:2]:
            print(f"     - {error.message}")
    print()
    
    # Example 5: Formatted error output
    print("5. Formatted validation output:")
    formatted_output = validator.format_validation_errors(result)
    print(formatted_output)
    print()
    
    # Example 6: Validation summary
    print("6. Validation summary:")
    summary = validator.get_validation_summary(result)
    print(f"   Summary: {summary['error_count']} errors, {summary['warning_count']} warnings")
    print(f"   Error codes: {[e['code'] for e in summary['errors']]}")
    
    print("\n=== Example completed ===")


if __name__ == "__main__":
    main()