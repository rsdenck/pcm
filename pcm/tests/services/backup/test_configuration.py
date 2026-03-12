"""
Tests for backup configuration parser and serializer.

Tests cover JSON and YAML parsing, validation, serialization, and round-trip consistency.
"""

import pytest
import json
import yaml
import tempfile
from pathlib import Path
from pcm.services.backup.configuration import (
    ConfigurationParser, 
    ConfigurationSerializer,
    ConfigurationParseError,
    ConfigurationSerializationError,
    validate_round_trip_consistency
)
from pcm.core.models.backup.policy import BackupPolicy


class TestConfigurationParser:
    """Test cases for ConfigurationParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create a ConfigurationParser instance."""
        return ConfigurationParser()
    
    @pytest.fixture
    def valid_config_dict(self):
        """Valid backup policy configuration dictionary."""
        return {
            "schedule": {
                "cron": "0 2 * * *",
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
    
    @pytest.fixture
    def valid_json_config(self, valid_config_dict):
        """Valid JSON configuration string."""
        return json.dumps(valid_config_dict)
    
    @pytest.fixture
    def valid_yaml_config(self, valid_config_dict):
        """Valid YAML configuration string."""
        return yaml.dump(valid_config_dict)
    
    def test_parse_from_string_json_success(self, parser, valid_json_config, valid_config_dict):
        """Test successful JSON parsing from string."""
        result = parser.parse_from_string(valid_json_config, 'json')
        assert result == valid_config_dict
    
    def test_parse_from_string_yaml_success(self, parser, valid_yaml_config, valid_config_dict):
        """Test successful YAML parsing from string."""
        result = parser.parse_from_string(valid_yaml_config, 'yaml')
        assert result == valid_config_dict
    
    def test_parse_from_string_invalid_json(self, parser):
        """Test parsing invalid JSON raises error."""
        invalid_json = '{"schedule": {"cron": "0 2 * * *"'  # Missing closing braces
        with pytest.raises(ConfigurationParseError, match="JSON parsing error"):
            parser.parse_from_string(invalid_json, 'json')
    
    def test_parse_from_string_invalid_yaml(self, parser):
        """Test parsing invalid YAML raises error."""
        invalid_yaml = "schedule:\n  cron: 0 2 * * *\n  - invalid_list_item"
        with pytest.raises(ConfigurationParseError, match="YAML parsing error"):
            parser.parse_from_string(invalid_yaml, 'yaml')
    
    def test_parse_from_string_unsupported_format(self, parser, valid_json_config):
        """Test parsing with unsupported format raises error."""
        with pytest.raises(ConfigurationParseError, match="Unsupported format"):
            parser.parse_from_string(valid_json_config, 'xml')
    
    def test_parse_from_string_validation_failure(self, parser):
        """Test parsing with schema validation failure."""
        invalid_config = json.dumps({
            "schedule": {"cron": "invalid_cron"},
            "retention": {},  # Missing required properties
            "targets": []  # Empty array not allowed
        })
        with pytest.raises(ConfigurationParseError, match="Configuration validation failed"):
            parser.parse_from_string(invalid_config, 'json')
    
    def test_parse_from_file_json_success(self, parser, valid_config_dict):
        """Test successful JSON file parsing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_config_dict, f)
            temp_path = Path(f.name)
        
        try:
            result = parser.parse_from_file(temp_path)
            assert result == valid_config_dict
        finally:
            temp_path.unlink()
    
    def test_parse_from_file_yaml_success(self, parser, valid_config_dict):
        """Test successful YAML file parsing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config_dict, f)
            temp_path = Path(f.name)
        
        try:
            result = parser.parse_from_file(temp_path)
            assert result == valid_config_dict
        finally:
            temp_path.unlink()
    
    def test_parse_from_file_not_found(self, parser):
        """Test parsing non-existent file raises error."""
        with pytest.raises(ConfigurationParseError, match="Configuration file not found"):
            parser.parse_from_file("/nonexistent/path/config.json")
    
    def test_parse_from_file_unsupported_extension(self, parser):
        """Test parsing file with unsupported extension raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("some content")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ConfigurationParseError, match="Cannot detect format"):
                parser.parse_from_file(temp_path)
        finally:
            temp_path.unlink()
    
    def test_parse_to_policy_from_dict(self, parser, valid_config_dict):
        """Test creating BackupPolicy from configuration dictionary."""
        policy = parser.parse_to_policy(
            valid_config_dict, 
            name="test_policy", 
            tenant_id="tenant_001",
            description="Test policy"
        )
        
        assert isinstance(policy, BackupPolicy)
        assert policy.name == "test_policy"
        assert policy.tenant_id == "tenant_001"
        assert policy.description == "Test policy"
        assert policy.configuration == valid_config_dict
    
    def test_parse_to_policy_from_string(self, parser, valid_json_config, valid_config_dict):
        """Test creating BackupPolicy from configuration string."""
        policy = parser.parse_to_policy(
            valid_json_config,
            name="test_policy",
            tenant_id="tenant_001",
            format_type="json"
        )
        
        assert isinstance(policy, BackupPolicy)
        assert policy.configuration == valid_config_dict
    
    def test_parse_to_policy_invalid_type(self, parser):
        """Test parse_to_policy with invalid config type raises error."""
        with pytest.raises(ConfigurationParseError, match="Configuration must be a string or dictionary"):
            parser.parse_to_policy(123, "test_policy", "tenant_001")


class TestConfigurationSerializer:
    """Test cases for ConfigurationSerializer class."""
    
    @pytest.fixture
    def serializer(self):
        """Create a ConfigurationSerializer instance."""
        return ConfigurationSerializer()
    
    @pytest.fixture
    def sample_policy(self):
        """Create a sample BackupPolicy for testing."""
        config = {
            "schedule": {
                "cron": "0 2 * * *",
                "timezone": "UTC"
            },
            "retention": {
                "daily": 7,
                "weekly": 4
            },
            "targets": [
                {
                    "vm_id": "vm-001",
                    "cluster_id": "cluster-001", 
                    "datastore_id": "datastore-001"
                }
            ]
        }
        return BackupPolicy(
            name="test_policy",
            tenant_id="tenant_001",
            configuration=config
        )
    
    def test_serialize_to_string_json(self, serializer, sample_policy):
        """Test JSON serialization to string."""
        result = serializer.serialize_to_string(sample_policy, 'json')
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == sample_policy.configuration
    
    def test_serialize_to_string_yaml(self, serializer, sample_policy):
        """Test YAML serialization to string."""
        result = serializer.serialize_to_string(sample_policy, 'yaml')
        
        # Should be valid YAML
        parsed = yaml.safe_load(result)
        assert parsed == sample_policy.configuration
    
    def test_serialize_to_string_unsupported_format(self, serializer, sample_policy):
        """Test serialization with unsupported format raises error."""
        with pytest.raises(ConfigurationSerializationError, match="Unsupported format"):
            serializer.serialize_to_string(sample_policy, 'xml')
    
    def test_serialize_to_file_json(self, serializer, sample_policy):
        """Test JSON serialization to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            serializer.serialize_to_file(sample_policy, temp_path)
            
            # Verify file contents
            with open(temp_path, 'r') as f:
                content = json.load(f)
            assert content == sample_policy.configuration
        finally:
            temp_path.unlink()
    
    def test_serialize_to_file_yaml(self, serializer, sample_policy):
        """Test YAML serialization to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            serializer.serialize_to_file(sample_policy, temp_path)
            
            # Verify file contents
            with open(temp_path, 'r') as f:
                content = yaml.safe_load(f)
            assert content == sample_policy.configuration
        finally:
            temp_path.unlink()
    
    def test_serialize_configuration_only(self, serializer, sample_policy):
        """Test serializing only the configuration part."""
        result = serializer.serialize_configuration_only(sample_policy, 'json')
        parsed = json.loads(result)
        assert parsed == sample_policy.configuration


class TestRoundTripConsistency:
    """Test cases for round-trip consistency validation."""
    
    @pytest.fixture
    def valid_json_config(self):
        """Valid JSON configuration string."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "datastore-001"}]
        }
        return json.dumps(config, sort_keys=True)
    
    @pytest.fixture
    def valid_yaml_config(self):
        """Valid YAML configuration string."""
        config = {
            "schedule": {"cron": "0 2 * * *"},
            "retention": {"daily": 7},
            "targets": [{"vm_id": "vm-001", "cluster_id": "cluster-001", "datastore_id": "datastore-001"}]
        }
        return yaml.dump(config, sort_keys=True)
    
    def test_round_trip_consistency_json(self, valid_json_config):
        """Test round-trip consistency for JSON format."""
        is_consistent, error_message = validate_round_trip_consistency(valid_json_config, 'json')
        assert is_consistent is True
        assert error_message is None
    
    def test_round_trip_consistency_yaml(self, valid_yaml_config):
        """Test round-trip consistency for YAML format."""
        is_consistent, error_message = validate_round_trip_consistency(valid_yaml_config, 'yaml')
        assert is_consistent is True
        assert error_message is None
    
    def test_round_trip_consistency_invalid_config(self):
        """Test round-trip consistency with invalid configuration."""
        invalid_config = '{"invalid": "config"}'
        is_consistent, error_message = validate_round_trip_consistency(invalid_config, 'json')
        assert is_consistent is False
        assert error_message is not None


class TestIntegration:
    """Integration tests for parser and serializer working together."""
    
    def test_parse_serialize_parse_consistency(self):
        """Test that parse->serialize->parse produces consistent results."""
        original_config = {
            "schedule": {
                "cron": "0 2 * * *",
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
                "encryption": False,
                "verification": True
            }
        }
        
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Create policy from original config
        policy = parser.parse_to_policy(
            original_config,
            name="test_policy",
            tenant_id="tenant_001"
        )
        
        # Serialize back to JSON
        json_str = serializer.serialize_to_string(policy, 'json', pretty=False)
        
        # Parse the serialized JSON
        reparsed_config = parser.parse_from_string(json_str, 'json')
        
        # Should be identical
        assert reparsed_config == original_config
    
    def test_file_round_trip(self):
        """Test complete file-based round-trip operation."""
        config = {
            "schedule": {"cron": "0 3 * * 1"},
            "retention": {"weekly": 8},
            "targets": [{"vm_id": "vm-002", "cluster_id": "cluster-002", "datastore_id": "datastore-002"}]
        }
        
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Create policy and serialize to file
            policy = parser.parse_to_policy(config, "file_test", "tenant_001")
            serializer.serialize_to_file(policy, temp_path)
            
            # Parse back from file
            reparsed_config = parser.parse_from_file(temp_path)
            
            # Should be identical
            assert reparsed_config == config
        finally:
            temp_path.unlink()