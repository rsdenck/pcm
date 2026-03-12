"""
Property-based tests for backup policy validation.

**Property 2: Policy configuration round-trip consistency**
**Validates: Requirements 19.4**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime
import json
import copy
from pcm.core.models.backup.policy import BackupPolicy, PolicyStatus
from pcm.services.backup.configuration import ConfigurationParser, ConfigurationSerializer


# Strategy for generating valid cron expressions
@st.composite
def cron_expression(draw):
    """Generate valid cron expressions."""
    minute = draw(st.sampled_from(["0", "15", "30", "45", "*", "*/15"]))
    hour = draw(st.sampled_from(["0", "1", "2", "6", "12", "18", "*", "*/6"]))
    day = draw(st.sampled_from(["*", "1", "15", "*/7"]))
    month = draw(st.sampled_from(["*", "1", "6", "12"]))
    weekday = draw(st.sampled_from(["*", "0", "1", "6", "7"]))
    return f"{minute} {hour} {day} {month} {weekday}"


# Strategy for generating valid backup policy configurations
@st.composite
def backup_policy_config(draw):
    """Generate valid backup policy configurations."""
    # Schedule configuration
    schedule = {
        "cron": draw(cron_expression()),
    }
    if draw(st.booleans()):
        schedule["timezone"] = draw(st.sampled_from(["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]))
    
    # Retention configuration
    retention = {}
    if draw(st.booleans()):
        retention["daily"] = draw(st.integers(min_value=1, max_value=30))
    if draw(st.booleans()):
        retention["weekly"] = draw(st.integers(min_value=1, max_value=52))
    if draw(st.booleans()):
        retention["monthly"] = draw(st.integers(min_value=1, max_value=24))
    if draw(st.booleans()):
        retention["yearly"] = draw(st.integers(min_value=1, max_value=10))
    
    # Ensure at least one retention period is set
    if not retention:
        retention["daily"] = draw(st.integers(min_value=1, max_value=30))
    
    # Targets configuration
    targets = []
    num_targets = draw(st.integers(min_value=1, max_value=5))
    for i in range(num_targets):
        target = {
            "vm_id": f"vm-{draw(st.integers(min_value=100, max_value=999))}",
            "cluster_id": f"cluster-{draw(st.integers(min_value=1, max_value=10))}",
            "datastore_id": f"datastore-{draw(st.integers(min_value=1, max_value=20))}"
        }
        targets.append(target)
    
    config = {
        "schedule": schedule,
        "retention": retention,
        "targets": targets
    }
    
    # Optional options configuration
    if draw(st.booleans()):
        options = {}
        if draw(st.booleans()):
            options["compression"] = draw(st.sampled_from(["none", "lz4", "zstd"]))
        if draw(st.booleans()):
            options["encryption"] = draw(st.booleans())
        if draw(st.booleans()):
            options["verification"] = draw(st.booleans())
        if draw(st.booleans()):
            options["bandwidth_limit"] = draw(st.integers(min_value=100, max_value=10000))
        if draw(st.booleans()):
            options["max_concurrent_jobs"] = draw(st.integers(min_value=1, max_value=10))
        
        if options:
            config["options"] = options
    
    return config


class TestBackupPolicyProperties:
    """Property-based tests for backup policy validation."""

    @given(
        config=backup_policy_config(),
        name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd')), min_size=1, max_size=100),
        tenant_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd')), min_size=1, max_size=50),
        description=st.text(max_size=500)
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=50)
    def test_policy_configuration_round_trip_consistency_property(
        self, config, name, tenant_id, description
    ):
        """
        **Property 2: Policy configuration round-trip consistency**
        **Validates: Requirements 19.4**
        
        Property: For all valid Policy objects, parsing then serializing then parsing 
        shall produce an equivalent object (round-trip property).
        """
        # Create parser and serializer instances
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Step 1: Create a BackupPolicy from the generated configuration
        original_policy = BackupPolicy(
            name=name,
            tenant_id=tenant_id,
            description=description,
            configuration=config
        )
        
        # Verify the original policy is valid
        is_valid, error = original_policy.validate_configuration()
        assert is_valid, f"Generated configuration should be valid: {error}"
        
        # Step 2: Serialize the policy to JSON string
        json_string = serializer.serialize_to_string(original_policy, 'json')
        
        # Step 3: Parse the JSON string back to configuration dict
        reparsed_config = parser.parse_from_string(json_string, 'json')
        
        # Step 4: Create a new policy from the reparsed configuration
        reparsed_policy = BackupPolicy(
            name=name,
            tenant_id=tenant_id,
            description=description,
            configuration=reparsed_config
        )
        
        # Property assertions: Round-trip consistency
        
        # 4a: Configuration content should be equivalent
        assert original_policy.configuration == reparsed_policy.configuration, \
            "Configuration should be identical after round-trip"
        
        # 4b: Policy properties should be equivalent
        assert original_policy.schedule == reparsed_policy.schedule, \
            "Schedule should be identical after round-trip"
        assert original_policy.retention == reparsed_policy.retention, \
            "Retention should be identical after round-trip"
        assert original_policy.targets == reparsed_policy.targets, \
            "Targets should be identical after round-trip"
        assert original_policy.options == reparsed_policy.options, \
            "Options should be identical after round-trip"
        
        # 4c: Both policies should be valid
        original_valid, original_error = original_policy.validate_configuration()
        reparsed_valid, reparsed_error = reparsed_policy.validate_configuration()
        assert original_valid and reparsed_valid, \
            f"Both policies should be valid: original={original_error}, reparsed={reparsed_error}"
        
        # 4d: Metadata should be preserved
        assert original_policy.name == reparsed_policy.name, \
            "Policy name should be preserved"
        assert original_policy.tenant_id == reparsed_policy.tenant_id, \
            "Tenant ID should be preserved"
        assert original_policy.description == reparsed_policy.description, \
            "Description should be preserved"

    @given(
        config=backup_policy_config(),
        name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd')), min_size=1, max_size=100),
        tenant_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd')), min_size=1, max_size=50),
        format_type=st.sampled_from(['json', 'yaml'])
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=30)
    def test_policy_multi_format_round_trip_consistency_property(
        self, config, name, tenant_id, format_type
    ):
        """
        **Property 2: Policy configuration round-trip consistency - Multi-format**
        **Validates: Requirements 19.4**
        
        Property: Round-trip consistency should hold for both JSON and YAML formats.
        """
        # Create parser and serializer instances
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Create original policy
        original_policy = BackupPolicy(
            name=name,
            tenant_id=tenant_id,
            configuration=config
        )
        
        # Verify the original policy is valid
        is_valid, error = original_policy.validate_configuration()
        assert is_valid, f"Generated configuration should be valid: {error}"
        
        # Serialize to specified format
        serialized_string = serializer.serialize_to_string(original_policy, format_type)
        
        # Parse back from the format
        reparsed_config = parser.parse_from_string(serialized_string, format_type)
        
        # Create new policy from reparsed config
        reparsed_policy = BackupPolicy(
            name=name,
            tenant_id=tenant_id,
            configuration=reparsed_config
        )
        
        # Property: Configuration equivalence regardless of format
        assert original_policy.configuration == reparsed_policy.configuration, \
            f"Configuration should be identical after {format_type} round-trip"

    @given(
        config=backup_policy_config()
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=20)
    def test_policy_configuration_idempotency_property(
        self, config
    ):
        """
        **Property 2: Policy configuration round-trip consistency - Idempotency**
        **Validates: Requirements 19.4**
        
        Property: Multiple round-trips should produce identical results (idempotency).
        """
        # Create parser and serializer instances
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Create original policy
        policy = BackupPolicy(
            name="test-policy",
            tenant_id="test-tenant",
            configuration=config
        )
        
        current_config = config
        
        # Perform multiple round-trips
        for i in range(3):
            # Serialize current configuration
            json_string = serializer.serialize_to_string(
                BackupPolicy(name="test", tenant_id="test", configuration=current_config), 
                'json'
            )
            
            # Parse back
            current_config = parser.parse_from_string(json_string, 'json')
        
        # Property: Final configuration should equal original
        assert current_config == config, \
            "Multiple round-trips should be idempotent"