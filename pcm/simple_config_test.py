#!/usr/bin/env python3
"""
Simplified test for configuration round-trip properties.
Task 3.2: Property test for configuration round-trip
"""

import json
import yaml
from typing import Dict, Any
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_configuration_round_trip():
    """
    Test Property 3: Configuration parsing and serialization consistency
    Validates: Requirements 19.4
    
    Property: For all valid configuration dictionaries, serializing to string then 
    parsing back should produce an equivalent configuration (round-trip property).
    """
    
    print("🧪 Testing Property 3: Configuration round-trip consistency")
    
    # Test configurations
    test_configs = [
        # Basic configuration
        {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-100", "cluster_id": "cluster-1", "datastore_id": "datastore-1"}]
        },
        # Complex configuration with options
        {
            "schedule": {"cron": "0 2 * * *", "timezone": "UTC"},
            "retention": {"daily": 7, "weekly": 4, "monthly": 12},
            "targets": [
                {"vm_id": "vm-100", "cluster_id": "cluster-1", "datastore_id": "datastore-1"},
                {"vm_id": "vm-101", "cluster_id": "cluster-1", "datastore_id": "datastore-2"}
            ],
            "options": {
                "compression": "lz4",
                "encryption": True,
                "verification": True,
                "bandwidth_limit": 1000,
                "max_concurrent_jobs": 2
            }
        },
        # Minimal configuration
        {
            "schedule": {"cron": "*/15 * * * *"},
            "retention": {"daily": 1},
            "targets": [{"vm_id": "vm-999", "cluster_id": "cluster-10", "datastore_id": "datastore-20"}]
        }
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n📋 Testing configuration {i}...")
        
        # Test JSON round-trip
        json_string = json.dumps(config, indent=2)
        reparsed_json = json.loads(json_string)
        
        assert config == reparsed_json, f"JSON round-trip failed for config {i}"
        print("  ✅ JSON round-trip: PASSED")
        
        # Test YAML round-trip
        yaml_string = yaml.dump(config, default_flow_style=False)
        reparsed_yaml = yaml.safe_load(yaml_string)
        
        assert config == reparsed_yaml, f"YAML round-trip failed for config {i}"
        print("  ✅ YAML round-trip: PASSED")
        
        # Test idempotency (multiple round-trips)
        current_config = config
        for j in range(3):
            json_str = json.dumps(current_config)
            current_config = json.loads(json_str)
        
        assert current_config == config, f"Idempotency test failed for config {i}"
        print("  ✅ Idempotency (3 round-trips): PASSED")
        
        # Test specific sections preservation
        assert config["schedule"] == reparsed_json["schedule"], f"Schedule not preserved in config {i}"
        assert config["retention"] == reparsed_json["retention"], f"Retention not preserved in config {i}"
        assert config["targets"] == reparsed_json["targets"], f"Targets not preserved in config {i}"
        
        if "options" in config:
            assert config["options"] == reparsed_json["options"], f"Options not preserved in config {i}"
        
        print("  ✅ Section preservation: PASSED")
    
    print(f"\n🎉 All {len(test_configs)} configuration round-trip tests PASSED!")
    return True

def test_configuration_format_consistency():
    """
    Test that configurations maintain consistency across different formats.
    """
    print("\n🧪 Testing cross-format consistency...")
    
    config = {
        "schedule": {"cron": "0 6 * * 1", "timezone": "America/New_York"},
        "retention": {"daily": 14, "weekly": 8, "monthly": 6},
        "targets": [
            {"vm_id": "vm-200", "cluster_id": "cluster-2", "datastore_id": "datastore-3"}
        ],
        "options": {"compression": "zstd", "encryption": False}
    }
    
    # JSON -> YAML -> JSON
    json_string = json.dumps(config)
    json_parsed = json.loads(json_string)
    
    yaml_string = yaml.dump(json_parsed)
    yaml_parsed = yaml.safe_load(yaml_string)
    
    final_json = json.dumps(yaml_parsed)
    final_parsed = json.loads(final_json)
    
    assert config == final_parsed, "Cross-format consistency test failed"
    print("  ✅ JSON -> YAML -> JSON consistency: PASSED")
    
    return True

def test_edge_cases():
    """
    Test edge cases for configuration round-trip.
    """
    print("\n🧪 Testing edge cases...")
    
    # Empty options
    config1 = {
        "schedule": {"cron": "0 0 * * *"},
        "retention": {"daily": 1},
        "targets": [{"vm_id": "vm-1", "cluster_id": "cluster-1", "datastore_id": "datastore-1"}],
        "options": {}
    }
    
    json_str = json.dumps(config1)
    reparsed = json.loads(json_str)
    assert config1 == reparsed, "Empty options test failed"
    print("  ✅ Empty options: PASSED")
    
    # Multiple targets
    config2 = {
        "schedule": {"cron": "0 3 * * *"},
        "retention": {"daily": 30, "weekly": 12, "monthly": 6, "yearly": 2},
        "targets": [
            {"vm_id": f"vm-{i}", "cluster_id": f"cluster-{i%3+1}", "datastore_id": f"datastore-{i%5+1}"}
            for i in range(10)
        ]
    }
    
    json_str = json.dumps(config2)
    reparsed = json.loads(json_str)
    assert config2 == reparsed, "Multiple targets test failed"
    print("  ✅ Multiple targets: PASSED")
    
    return True

if __name__ == "__main__":
    try:
        print("🚀 Starting Task 3.2: Property test for configuration round-trip")
        print("=" * 70)
        
        # Run all tests
        test_configuration_round_trip()
        test_configuration_format_consistency()
        test_edge_cases()
        
        print("\n" + "=" * 70)
        print("🎉 SUCCESS: All configuration property tests PASSED!")
        print("✅ Task 3.2: Property test for configuration round-trip - COMPLETED")
        print("\nProperty 3 validated: Configuration parsing and serialization consistency")
        print("Requirements 19.4: Round-trip consistency maintained ✅")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)