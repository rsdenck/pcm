#!/usr/bin/env python3
"""
Test runner for configuration properties tests.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Now run the tests
if __name__ == "__main__":
    try:
        # Import modules directly
        from services.backup.configuration import ConfigurationParser, ConfigurationSerializer
        from core.models.backup.policy import BackupPolicy
        
        print("Running configuration property tests...")
        
        # Test basic functionality
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Create a simple test configuration
        test_config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-100", "cluster_id": "cluster-1", "datastore_id": "datastore-1"}]
        }
        
        # Create policy
        policy = BackupPolicy(
            name="test-policy",
            tenant_id="test-tenant",
            configuration=test_config
        )
        
        # Validate configuration
        is_valid, error = policy.validate_configuration()
        if not is_valid:
            print(f"❌ Configuration validation failed: {error}")
            sys.exit(1)
        
        # Test round-trip
        json_string = serializer.serialize_to_string(policy, 'json')
        reparsed_config = parser.parse_from_string(json_string, 'json')
        
        assert test_config == reparsed_config, "Round-trip test failed"
        
        print("✅ Basic round-trip test passed!")
        
        # Test YAML round-trip
        yaml_string = serializer.serialize_to_string(policy, 'yaml')
        reparsed_yaml_config = parser.parse_from_string(yaml_string, 'yaml')
        
        assert test_config == reparsed_yaml_config, "YAML round-trip test failed"
        
        print("✅ YAML round-trip test passed!")
        
        # Test configuration-only serialization
        config_only_string = serializer.serialize_configuration_only(policy, 'json')
        reparsed_config_only = parser.parse_from_string(config_only_string, 'json')
        
        assert test_config == reparsed_config_only, "Configuration-only round-trip test failed"
        
        print("✅ Configuration-only round-trip test passed!")
        
        # Test parse_to_policy
        parsed_policy = parser.parse_to_policy(test_config, name="parsed-policy", tenant_id="parsed-tenant")
        assert parsed_policy.configuration == test_config, "parse_to_policy test failed"
        assert parsed_policy.name == "parsed-policy", "parse_to_policy name test failed"
        assert parsed_policy.tenant_id == "parsed-tenant", "parse_to_policy tenant_id test failed"
        
        print("✅ parse_to_policy test passed!")
        
        # Test idempotency (multiple round-trips)
        current_config = test_config
        for i in range(3):
            temp_policy = BackupPolicy(
                name="temp-policy",
                tenant_id="temp-tenant",
                configuration=current_config
            )
            json_str = serializer.serialize_to_string(temp_policy, 'json')
            current_config = parser.parse_from_string(json_str, 'json')
        
        assert current_config == test_config, "Idempotency test failed"
        
        print("✅ Idempotency test passed!")
        
        print("\n🎉 All configuration property tests passed successfully!")
        print("✅ Task 3.2: Property test for configuration round-trip - COMPLETED")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)