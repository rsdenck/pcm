"""
Property-based tests for configuration parsing and serialization.

**Property 3: Configuration parsing and serialization consistency**
**Validates: Requirements 19.4**
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import json
import yaml
from pcm.services.backup.configuration import (
    ConfigurationParser, 
    ConfigurationSerializer,
    ConfigurationParseError,
    ConfigurationSerializationError
)
from pcm.core.models.backup.policy import BackupPolicy


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


class TestConfigurationParsingProperties:
    """Property-based tests for configuration parsing and serialization."""

    @given(
        config=backup_policy_config(),
        name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd')), min_size=1, max_size=100),
        tenant_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd')), min_size=1, max_size=50),
        description=st.text(max_size=500)
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=50)
    def test_configuration_round_trip_consistency_property(
        self, config, name, tenant_id, description
    ):
        """
        **Property 3: Configuration parsing and serialization consistency**
        **Validates: Requirements 19.4**
        
        Property: For all valid configuration dictionaries, serializing to string then 
        parsing back should produce an equivalent configuration (round-trip property).
        
        This tests the ConfigurationParser and ConfigurationSerializer directly,
        without going through the BackupPolicy model.
        """
        # Create parser and serializer instances
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Step 1: Create a BackupPolicy to use for serialization
        # (The serializer needs a Policy object, but we're testing the config round-trip)
        policy = BackupPolicy(
            name=name,
            tenant_id=tenant_id,
            description=description,
            configuration=config
        )
        
        # Verify the configuration is valid before testing
        is_valid, error = policy.validate_configuration()
        assert is_valid, f"Generated configuration should be valid: {error}"
        
        # Step 2: Serialize the policy configuration to JSON string
        json_string = serializer.serialize_to_string(policy, 'json')
        
        # Step 3: Parse the JSON string back to configuration dict
        reparsed_config = parser.parse_from_string(json_string, 'json')
        
        # Property assertions: Configuration round-trip consistency
        
        # 3a: Configuration content should be equivalent
        assert config == reparsed_config, \
            "Configuration should be identical after round-trip"
        
        # 3b: Specific configuration sections should be preserved
        assert config["schedule"] == reparsed_config["schedule"], \
            "Schedule configuration should be preserved"
        assert config["retention"] == reparsed_config["retention"], \
            "Retention configuration should be preserved"
        assert config["targets"] == reparsed_config["targets"], \
            "Targets configuration should be preserved"
        
        if "options" in config:
            assert config["options"] == reparsed_config["options"], \
                "Options configuration should be preserved"
        
        # 3c: Reparsed configuration should be valid
        reparsed_policy = BackupPolicy(
            name=name,
            tenant_id=tenant_id,
            description=description,
            configuration=reparsed_config
        )
        reparsed_valid, reparsed_error = reparsed_policy.validate_configuration()
        assert reparsed_valid, f"Reparsed configuration should be valid: {reparsed_error}"

    @given(
        config=backup_policy_config(),
        format_type=st.sampled_from(['json', 'yaml'])
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=30)
    def test_configuration_multi_format_round_trip_property(
        self, config, format_type
    ):
        """
        **Property 3: Configuration parsing and serialization consistency - Multi-format**
        **Validates: Requirements 19.4**
        
        Property: Round-trip consistency should hold for both JSON and YAML formats.
        """
        # Create parser and serializer instances
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Create a policy for serialization
        policy = BackupPolicy(
            name="test-policy",
            tenant_id="test-tenant",
            configuration=config
        )
        
        # Verify the configuration is valid
        is_valid, error = policy.validate_configuration()
        assert is_valid, f"Generated configuration should be valid: {error}"
        
        # Serialize to specified format
        serialized_string = serializer.serialize_to_string(policy, format_type)
        
        # Parse back from the format
        reparsed_config = parser.parse_from_string(serialized_string, format_type)
        
        # Property: Configuration equivalence regardless of format
        assert config == reparsed_config, \
            f"Configuration should be identical after {format_type} round-trip"

    @given(
        config=backup_policy_config()
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=20)
    def test_configuration_idempotency_property(
        self, config
    ):
        """
        **Property 3: Configuration parsing and serialization consistency - Idempotency**
        **Validates: Requirements 19.4**
        
        Property: Multiple round-trips should produce identical results (idempotency).
        """
        # Create parser and serializer instances
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        current_config = config
        
        # Perform multiple round-trips
        for i in range(3):
            # Create policy with current configuration
            policy = BackupPolicy(
                name="test-policy",
                tenant_id="test-tenant",
                configuration=current_config
            )
            
            # Serialize current configuration
            json_string = serializer.serialize_to_string(policy, 'json')
            
            # Parse back
            current_config = parser.parse_from_string(json_string, 'json')
        
        # Property: Final configuration should equal original
        assert current_config == config, \
            "Multiple round-trips should be idempotent"

    @given(
        config=backup_policy_config()
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=20)
    def test_configuration_serialization_only_round_trip_property(
        self, config
    ):
        """
        **Property 3: Configuration parsing and serialization consistency - Configuration-only**
        **Validates: Requirements 19.4**
        
        Property: Using serialize_configuration_only should produce parseable output
        that maintains configuration consistency.
        """
        # Create parser and serializer instances
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Create a policy for serialization
        policy = BackupPolicy(
            name="test-policy",
            tenant_id="test-tenant",
            configuration=config
        )
        
        # Verify the configuration is valid
        is_valid, error = policy.validate_configuration()
        assert is_valid, f"Generated configuration should be valid: {error}"
        
        # Serialize configuration only (without metadata)
        config_only_string = serializer.serialize_configuration_only(policy, 'json')
        
        # Parse back the configuration-only string
        reparsed_config = parser.parse_from_string(config_only_string, 'json')
        
        # Property: Configuration should be preserved
        assert config == reparsed_config, \
            "Configuration should be identical after configuration-only round-trip"

    @given(
        config=backup_policy_config(),
        name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd')), min_size=1, max_size=100),
        tenant_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd')), min_size=1, max_size=50)
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much], max_examples=30)
    def test_parse_to_policy_round_trip_property(
        self, config, name, tenant_id
    ):
        """
        **Property 3: Configuration parsing and serialization consistency - Policy parsing**
        **Validates: Requirements 19.4**
        
        Property: Using parse_to_policy should create a policy that, when serialized,
        produces the same configuration.
        """
        # Create parser and serializer instances
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Step 1: Parse configuration to policy using parse_to_policy
        parsed_policy = parser.parse_to_policy(config, name=name, tenant_id=tenant_id)
        
        # Verify the parsed policy is valid
        is_valid, error = parsed_policy.validate_configuration()
        assert is_valid, f"Parsed policy should be valid: {error}"
        
        # Step 2: Serialize the parsed policy back to string
        serialized_string = serializer.serialize_configuration_only(parsed_policy, 'json')
        
        # Step 3: Parse the serialized string back to configuration
        final_config = parser.parse_from_string(serialized_string, 'json')
        
        # Property: Final configuration should match original
        assert config == final_config, \
            "Configuration should be preserved through parse_to_policy round-trip"
        
        # Property: Policy properties should match configuration
        assert parsed_policy.configuration == config, \
            "Parsed policy configuration should match input"
        assert parsed_policy.name == name, \
            "Parsed policy name should match input"
        assert parsed_policy.tenant_id == tenant_id, \
            "Parsed policy tenant_id should match input"