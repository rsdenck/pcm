"""
Configuration management for backup policies.

This module provides parsing and serialization capabilities for backup policy
configurations, supporting JSON and YAML formats with comprehensive validation
against the backup policy schema.
"""

import json
import yaml
from typing import Dict, Any, Optional, Union, Tuple
from pathlib import Path
import jsonschema
from core.models.backup.policy import BackupPolicy, BACKUP_POLICY_SCHEMA, validate_policy_configuration


class ConfigurationParseError(Exception):
    """Raised when configuration parsing fails."""
    pass


class ConfigurationSerializationError(Exception):
    """Raised when configuration serialization fails."""
    pass


class ConfigurationParser:
    """
    Parses backup policy configurations from various formats into Policy objects.
    
    Supports JSON and YAML formats with comprehensive validation against the
    backup policy schema. Provides detailed error messages for invalid configurations.
    """
    
    SUPPORTED_FORMATS = {'json', 'yaml', 'yml'}
    
    def __init__(self):
        """Initialize the configuration parser."""
        self._schema = BACKUP_POLICY_SCHEMA
    
    def parse_from_string(self, config_str: str, format_type: str = 'json') -> Dict[str, Any]:
        """
        Parse configuration from a string.
        
        Args:
            config_str: Configuration string to parse
            format_type: Format type ('json' or 'yaml')
            
        Returns:
            Parsed configuration dictionary
            
        Raises:
            ConfigurationParseError: If parsing or validation fails
        """
        if format_type.lower() not in self.SUPPORTED_FORMATS:
            raise ConfigurationParseError(
                f"Unsupported format '{format_type}'. Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        try:
            # Parse the configuration string
            if format_type.lower() == 'json':
                config = json.loads(config_str)
            else:  # yaml or yml
                config = yaml.safe_load(config_str)
            
            # Validate against schema
            is_valid, error_message = self._validate_configuration(config)
            if not is_valid:
                raise ConfigurationParseError(f"Configuration validation failed: {error_message}")
            
            return config
            
        except json.JSONDecodeError as e:
            raise ConfigurationParseError(f"JSON parsing error: {str(e)}")
        except yaml.YAMLError as e:
            raise ConfigurationParseError(f"YAML parsing error: {str(e)}")
        except Exception as e:
            raise ConfigurationParseError(f"Unexpected parsing error: {str(e)}")
    
    def parse_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse configuration from a file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Parsed configuration dictionary
            
        Raises:
            ConfigurationParseError: If file reading, parsing, or validation fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigurationParseError(f"Configuration file not found: {file_path}")
        
        if not file_path.is_file():
            raise ConfigurationParseError(f"Path is not a file: {file_path}")
        
        # Determine format from file extension
        format_type = self._detect_format(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_str = f.read()
            
            return self.parse_from_string(config_str, format_type)
            
        except IOError as e:
            raise ConfigurationParseError(f"Error reading file {file_path}: {str(e)}")
    
    def parse_to_policy(self, config: Union[str, Dict[str, Any]], 
                       name: str, tenant_id: str, 
                       description: Optional[str] = None,
                       format_type: str = 'json') -> BackupPolicy:
        """
        Parse configuration and create a BackupPolicy object.
        
        Args:
            config: Configuration string or dictionary
            name: Policy name
            tenant_id: Tenant identifier
            description: Optional policy description
            format_type: Format type if config is a string
            
        Returns:
            BackupPolicy object
            
        Raises:
            ConfigurationParseError: If parsing or validation fails
        """
        if isinstance(config, str):
            config_dict = self.parse_from_string(config, format_type)
        elif isinstance(config, dict):
            # Validate the dictionary
            is_valid, error_message = self._validate_configuration(config)
            if not is_valid:
                raise ConfigurationParseError(f"Configuration validation failed: {error_message}")
            config_dict = config
        else:
            raise ConfigurationParseError("Configuration must be a string or dictionary")
        
        try:
            return BackupPolicy(
                name=name,
                description=description,
                tenant_id=tenant_id,
                configuration=config_dict
            )
        except Exception as e:
            raise ConfigurationParseError(f"Error creating BackupPolicy: {str(e)}")
    
    def _validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate configuration against the backup policy schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return validate_policy_configuration(config)
    
    def _detect_format(self, file_path: Path) -> str:
        """
        Detect configuration format from file extension.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Detected format type
            
        Raises:
            ConfigurationParseError: If format cannot be detected
        """
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            return 'json'
        elif suffix in ['.yaml', '.yml']:
            return 'yaml'
        else:
            raise ConfigurationParseError(
                f"Cannot detect format from file extension '{suffix}'. "
                f"Supported extensions: .json, .yaml, .yml"
            )


class ConfigurationSerializer:
    """
    Serializes Policy objects back to configuration files.
    
    Supports JSON and YAML formats with proper formatting and validation.
    Ensures round-trip consistency when used with ConfigurationParser.
    """
    
    SUPPORTED_FORMATS = {'json', 'yaml', 'yml'}
    
    def __init__(self):
        """Initialize the configuration serializer."""
        pass
    
    def serialize_to_string(self, policy: BackupPolicy, format_type: str = 'json', 
                          pretty: bool = True) -> str:
        """
        Serialize a BackupPolicy to a configuration string.
        
        Args:
            policy: BackupPolicy object to serialize
            format_type: Output format ('json' or 'yaml')
            pretty: Whether to format output for readability
            
        Returns:
            Serialized configuration string
            
        Raises:
            ConfigurationSerializationError: If serialization fails
        """
        if format_type.lower() not in self.SUPPORTED_FORMATS:
            raise ConfigurationSerializationError(
                f"Unsupported format '{format_type}'. Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        try:
            config = policy.configuration
            
            if format_type.lower() == 'json':
                if pretty:
                    return json.dumps(config, indent=2, sort_keys=True, ensure_ascii=False)
                else:
                    return json.dumps(config, separators=(',', ':'), ensure_ascii=False)
            else:  # yaml or yml
                return yaml.dump(
                    config, 
                    default_flow_style=False, 
                    sort_keys=True, 
                    allow_unicode=True,
                    indent=2
                )
                
        except Exception as e:
            raise ConfigurationSerializationError(f"Serialization error: {str(e)}")
    
    def serialize_to_file(self, policy: BackupPolicy, file_path: Union[str, Path], 
                         format_type: Optional[str] = None, pretty: bool = True) -> None:
        """
        Serialize a BackupPolicy to a configuration file.
        
        Args:
            policy: BackupPolicy object to serialize
            file_path: Output file path
            format_type: Output format (auto-detected from extension if None)
            pretty: Whether to format output for readability
            
        Raises:
            ConfigurationSerializationError: If serialization or file writing fails
        """
        file_path = Path(file_path)
        
        # Auto-detect format if not specified
        if format_type is None:
            format_type = self._detect_format(file_path)
        
        # Serialize to string
        config_str = self.serialize_to_string(policy, format_type, pretty)
        
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(config_str)
                
        except IOError as e:
            raise ConfigurationSerializationError(f"Error writing file {file_path}: {str(e)}")
    
    def serialize_configuration_only(self, policy: BackupPolicy, format_type: str = 'json',
                                   pretty: bool = True) -> str:
        """
        Serialize only the configuration part of a BackupPolicy.
        
        This method extracts just the configuration dictionary from the policy
        and serializes it, excluding metadata like name, description, etc.
        
        Args:
            policy: BackupPolicy object to serialize
            format_type: Output format ('json' or 'yaml')
            pretty: Whether to format output for readability
            
        Returns:
            Serialized configuration string
            
        Raises:
            ConfigurationSerializationError: If serialization fails
        """
        return self.serialize_to_string(policy, format_type, pretty)
    
    def _detect_format(self, file_path: Path) -> str:
        """
        Detect configuration format from file extension.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Detected format type
            
        Raises:
            ConfigurationSerializationError: If format cannot be detected
        """
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            return 'json'
        elif suffix in ['.yaml', '.yml']:
            return 'yaml'
        else:
            raise ConfigurationSerializationError(
                f"Cannot detect format from file extension '{suffix}'. "
                f"Supported extensions: .json, .yaml, .yml"
            )


def validate_round_trip_consistency(config_str: str, format_type: str = 'json') -> Tuple[bool, Optional[str]]:
    """
    Validate that a configuration string maintains consistency through parse->serialize->parse cycle.
    
    This function tests the round-trip property: parsing a configuration, serializing it back,
    and parsing it again should produce an equivalent configuration.
    
    Args:
        config_str: Configuration string to test
        format_type: Format type ('json' or 'yaml')
        
    Returns:
        Tuple of (is_consistent, error_message)
    """
    try:
        parser = ConfigurationParser()
        serializer = ConfigurationSerializer()
        
        # Parse original configuration
        original_config = parser.parse_from_string(config_str, format_type)
        
        # Create a temporary policy for serialization
        temp_policy = BackupPolicy(
            name="temp_policy",
            tenant_id="temp_tenant",
            configuration=original_config
        )
        
        # Serialize back to string
        serialized_str = serializer.serialize_to_string(temp_policy, format_type, pretty=False)
        
        # Parse the serialized string
        round_trip_config = parser.parse_from_string(serialized_str, format_type)
        
        # Compare configurations
        if original_config == round_trip_config:
            return True, None
        else:
            return False, "Configuration changed during round-trip serialization"
            
    except Exception as e:
        return False, f"Round-trip validation error: {str(e)}"