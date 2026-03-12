"""
Policy management service that integrates validation with policy operations.

This service demonstrates how to use the PolicyValidationService in practice
for creating and updating backup policies with comprehensive validation.
"""

from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from pcm.core.models.backup.policy import BackupPolicy
from pcm.services.backup.validation import PolicyValidationService, ValidationResult
from pcm.services.backup.configuration import ConfigurationParser, ConfigurationParseError


class PolicyManagerError(Exception):
    """Base exception for policy management errors."""
    pass


class PolicyValidationError(PolicyManagerError):
    """Raised when policy validation fails."""
    
    def __init__(self, message: str, validation_result: ValidationResult):
        super().__init__(message)
        self.validation_result = validation_result


class PolicyManager:
    """
    High-level policy management service with integrated validation.
    
    Provides a complete workflow for creating and updating backup policies
    with comprehensive validation, error handling, and change tracking.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the policy manager.
        
        Args:
            db_session: Database session for policy operations
        """
        self.db = db_session
        self.validator = PolicyValidationService(db_session)
        self.parser = ConfigurationParser()
    
    def create_policy(self, 
                     name: str,
                     tenant_id: str,
                     config: Dict[str, Any],
                     description: Optional[str] = None,
                     created_by: Optional[str] = None) -> BackupPolicy:
        """
        Create a new backup policy with validation.
        
        Args:
            name: Policy name
            tenant_id: Tenant identifier
            config: Policy configuration dictionary
            description: Optional policy description
            created_by: User who created the policy
            
        Returns:
            Created BackupPolicy object
            
        Raises:
            PolicyValidationError: If validation fails
            PolicyManagerError: If creation fails
        """
        # Validate the policy configuration
        validation_result = self.validator.validate_policy(config, tenant_id)
        
        if not validation_result.is_valid:
            error_message = self.validator.format_validation_errors(validation_result)
            raise PolicyValidationError(
                f"Policy validation failed for '{name}': {error_message}",
                validation_result
            )
        
        try:
            # Create the policy
            policy = BackupPolicy(
                name=name,
                description=description,
                tenant_id=tenant_id,
                configuration=config
            )
            
            # Create initial version for change tracking
            if created_by:
                version = self.validator.create_policy_version(
                    policy,
                    changes={"action": "created", "config": config},
                    created_by=created_by,
                    reason="Initial policy creation"
                )
            
            # Save to database
            self.db.add(policy)
            self.db.commit()
            
            return policy
            
        except Exception as e:
            self.db.rollback()
            raise PolicyManagerError(f"Failed to create policy '{name}': {str(e)}")
    
    def update_policy(self,
                     policy_id: str,
                     new_config: Dict[str, Any],
                     updated_by: Optional[str] = None,
                     reason: Optional[str] = None) -> BackupPolicy:
        """
        Update an existing backup policy with validation.
        
        Args:
            policy_id: Policy identifier
            new_config: New policy configuration
            updated_by: User who updated the policy
            reason: Reason for the update
            
        Returns:
            Updated BackupPolicy object
            
        Raises:
            PolicyValidationError: If validation fails
            PolicyManagerError: If update fails
        """
        # Get existing policy
        policy = self.db.query(BackupPolicy).filter(BackupPolicy.id == policy_id).first()
        if not policy:
            raise PolicyManagerError(f"Policy {policy_id} not found")
        
        # Validate the update
        validation_result = self.validator.validate_policy_update(new_config, policy)
        
        if not validation_result.is_valid:
            error_message = self.validator.format_validation_errors(validation_result)
            raise PolicyValidationError(
                f"Policy update validation failed: {error_message}",
                validation_result
            )
        
        try:
            # Store old configuration for change tracking
            old_config = policy.configuration.copy()
            
            # Update the policy
            policy.configuration = new_config
            policy.updated_at = datetime.utcnow()
            
            # Create version for change tracking
            if updated_by:
                changes = self._calculate_changes(old_config, new_config)
                version = self.validator.create_policy_version(
                    policy,
                    changes=changes,
                    created_by=updated_by,
                    reason=reason or "Policy configuration updated"
                )
            
            # Save to database
            self.db.commit()
            
            return policy
            
        except Exception as e:
            self.db.rollback()
            raise PolicyManagerError(f"Failed to update policy {policy_id}: {str(e)}")
    
    def validate_policy_config(self, 
                              config: Dict[str, Any], 
                              tenant_id: str) -> ValidationResult:
        """
        Validate a policy configuration without creating/updating.
        
        Args:
            config: Policy configuration to validate
            tenant_id: Tenant identifier
            
        Returns:
            ValidationResult with validation details
        """
        return self.validator.validate_policy(config, tenant_id)
    
    def parse_policy_from_file(self, 
                              file_path: str,
                              name: str,
                              tenant_id: str,
                              description: Optional[str] = None) -> BackupPolicy:
        """
        Parse and create a policy from a configuration file.
        
        Args:
            file_path: Path to configuration file
            name: Policy name
            tenant_id: Tenant identifier
            description: Optional policy description
            
        Returns:
            Created BackupPolicy object
            
        Raises:
            ConfigurationParseError: If parsing fails
            PolicyValidationError: If validation fails
        """
        try:
            config = self.parser.parse_from_file(file_path)
            return self.create_policy(name, tenant_id, config, description)
        except ConfigurationParseError as e:
            raise PolicyManagerError(f"Failed to parse configuration file: {str(e)}")
    
    def get_validation_summary(self, policy_id: str) -> Dict[str, Any]:
        """
        Get validation summary for an existing policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Validation summary dictionary
        """
        policy = self.db.query(BackupPolicy).filter(BackupPolicy.id == policy_id).first()
        if not policy:
            raise PolicyManagerError(f"Policy {policy_id} not found")
        
        validation_result = self.validator.validate_policy(
            policy.configuration, 
            policy.tenant_id,
            policy.id,
            policy
        )
        
        return self.validator.get_validation_summary(validation_result)
    
    def _calculate_changes(self, old_config: Dict[str, Any], 
                          new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate changes between old and new configurations.
        
        Args:
            old_config: Original configuration
            new_config: New configuration
            
        Returns:
            Dictionary describing the changes
        """
        changes = {
            "timestamp": datetime.utcnow().isoformat(),
            "modified_fields": []
        }
        
        # Compare top-level fields
        for key in set(old_config.keys()) | set(new_config.keys()):
            old_value = old_config.get(key)
            new_value = new_config.get(key)
            
            if old_value != new_value:
                changes["modified_fields"].append({
                    "field": key,
                    "old_value": old_value,
                    "new_value": new_value
                })
        
        return changes


def create_policy_manager(db_session: Session) -> PolicyManager:
    """
    Factory function to create a PolicyManager instance.
    
    Args:
        db_session: Database session
        
    Returns:
        Configured PolicyManager instance
    """
    return PolicyManager(db_session)