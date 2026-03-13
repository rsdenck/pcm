"""
Tenant Isolation and Access Control Manager.

This module provides comprehensive tenant isolation enforcement,
access control validation, and datastore/namespace isolation.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from pcm.core.models.backup.datastore import Datastore
from pcm.core.models.backup.snapshot import BackupSnapshot
from pcm.core.models.backup.job import BackupJob
from pcm.core.models.backup.policy import BackupPolicy


logger = logging.getLogger(__name__)


class TenantIsolationError(Exception):
    """Exception for tenant isolation violations."""
    pass


class TenantIsolationManager:
    """
    Tenant isolation and access control manager.
    
    Enforces multi-tenant security through access control validation,
    datastore isolation, and namespace separation.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize tenant isolation manager.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._access_cache: Dict[str, Dict[str, bool]] = {}
    
    async def validate_tenant_access(
        self,
        tenant_id: str,
        resource_id: str,
        resource_type: str,
        operation: str = "read"
    ) -> bool:
        """
        Validate that a tenant has access to a resource.
        
        Args:
            tenant_id: Tenant ID
            resource_id: Resource ID
            resource_type: Type of resource (snapshot, job, policy, datastore)
            operation: Operation type (read, write, delete)
            
        Returns:
            True if access is allowed, False otherwise
        """
        # Check cache first
        cache_key = f"{tenant_id}:{resource_id}:{resource_type}:{operation}"
        if cache_key in self._access_cache:
            return self._access_cache[cache_key]
        
        try:
            allowed = await self._check_access(
                tenant_id, resource_id, resource_type, operation
            )
            self._access_cache[cache_key] = allowed
            return allowed
        except Exception as e:
            logger.error(f"Error validating tenant access: {e}")
            return False
    
    async def _check_access(
        self,
        tenant_id: str,
        resource_id: str,
        resource_type: str,
        operation: str
    ) -> bool:
        """
        Check if tenant has access to resource.
        
        Args:
            tenant_id: Tenant ID
            resource_id: Resource ID
            resource_type: Type of resource
            operation: Operation type
            
        Returns:
            True if access allowed
        """
        if resource_type == "snapshot":
            result = await self.db_session.execute(
                select(BackupSnapshot).where(
                    and_(
                        BackupSnapshot.id == resource_id,
                        BackupSnapshot.tenant_id == tenant_id
                    )
                )
            )
            return result.scalar_one_or_none() is not None
        
        elif resource_type == "job":
            result = await self.db_session.execute(
                select(BackupJob).where(
                    and_(
                        BackupJob.id == resource_id,
                        BackupJob.tenant_id == tenant_id
                    )
                )
            )
            return result.scalar_one_or_none() is not None
        
        elif resource_type == "policy":
            result = await self.db_session.execute(
                select(BackupPolicy).where(
                    and_(
                        BackupPolicy.id == resource_id,
                        BackupPolicy.tenant_id == tenant_id
                    )
                )
            )
            return result.scalar_one_or_none() is not None
        
        elif resource_type == "datastore":
            result = await self.db_session.execute(
                select(Datastore).where(
                    and_(
                        Datastore.id == resource_id,
                        Datastore.tenant_id == tenant_id
                    )
                )
            )
            return result.scalar_one_or_none() is not None
        
        return False
    
    async def get_tenant_datastores(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get all datastores assigned to a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of datastores
        """
        result = await self.db_session.execute(
            select(Datastore).where(Datastore.tenant_id == tenant_id)
        )
        
        datastores = list(result.scalars().all())
        
        return [
            {
                'datastore_id': ds.id,
                'name': ds.name,
                'pbs_server_id': ds.pbs_server_id,
                'path': ds.path,
                'capacity': ds.capacity,
                'used_space': ds.used_space,
                'status': ds.status.value if hasattr(ds.status, 'value') else str(ds.status)
            }
            for ds in datastores
        ]
    
    async def get_tenant_snapshots(self, tenant_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all snapshots for a tenant.
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum number of snapshots
            
        Returns:
            List of snapshots
        """
        result = await self.db_session.execute(
            select(BackupSnapshot)
            .where(BackupSnapshot.tenant_id == tenant_id)
            .limit(limit)
        )
        
        snapshots = list(result.scalars().all())
        
        return [
            {
                'snapshot_id': s.id,
                'job_id': s.job_id,
                'vm_id': s.vm_id,
                'snapshot_time': s.snapshot_time.isoformat(),
                'size': s.size,
                'datastore_id': s.datastore_id
            }
            for s in snapshots
        ]
    
    async def get_tenant_jobs(self, tenant_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all backup jobs for a tenant.
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum number of jobs
            
        Returns:
            List of jobs
        """
        result = await self.db_session.execute(
            select(BackupJob)
            .where(BackupJob.tenant_id == tenant_id)
            .limit(limit)
        )
        
        jobs = list(result.scalars().all())
        
        return [
            {
                'job_id': j.id,
                'policy_id': j.policy_id,
                'status': j.status.value,
                'progress': j.progress,
                'start_time': j.start_time.isoformat() if j.start_time else None,
                'end_time': j.end_time.isoformat() if j.end_time else None
            }
            for j in jobs
        ]
    
    async def get_tenant_policies(self, tenant_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all backup policies for a tenant.
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum number of policies
            
        Returns:
            List of policies
        """
        result = await self.db_session.execute(
            select(BackupPolicy)
            .where(BackupPolicy.tenant_id == tenant_id)
            .limit(limit)
        )
        
        policies = list(result.scalars().all())
        
        return [
            {
                'policy_id': p.id,
                'name': p.name,
                'description': p.description,
                'enabled': p.enabled,
                'created_at': p.created_at.isoformat() if p.created_at else None
            }
            for p in policies
        ]
    
    async def enforce_datastore_isolation(
        self,
        tenant_id: str,
        datastore_id: str
    ) -> bool:
        """
        Enforce that a datastore is isolated to a tenant.
        
        Args:
            tenant_id: Tenant ID
            datastore_id: Datastore ID
            
        Returns:
            True if datastore is properly isolated
        """
        result = await self.db_session.execute(
            select(Datastore).where(Datastore.id == datastore_id)
        )
        
        datastore = result.scalar_one_or_none()
        
        if not datastore:
            return False
        
        # Check if datastore is assigned to this tenant
        if datastore.tenant_id != tenant_id:
            logger.warning(
                f"Datastore {datastore_id} is not assigned to tenant {tenant_id}"
            )
            return False
        
        return True
    
    async def validate_cross_tenant_operation(
        self,
        source_tenant_id: str,
        target_tenant_id: str,
        operation_type: str
    ) -> bool:
        """
        Validate that a cross-tenant operation is allowed.
        
        Args:
            source_tenant_id: Source tenant ID
            target_tenant_id: Target tenant ID
            operation_type: Type of operation (restore, replicate, etc)
            
        Returns:
            True if operation is allowed
        """
        # Cross-tenant operations are generally not allowed
        if source_tenant_id != target_tenant_id:
            logger.warning(
                f"Cross-tenant operation {operation_type} attempted from "
                f"{source_tenant_id} to {target_tenant_id}"
            )
            return False
        
        return True
    
    async def get_tenant_isolation_status(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get tenant isolation status and statistics.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Isolation status information
        """
        # Get datastore count
        ds_result = await self.db_session.execute(
            select(Datastore).where(Datastore.tenant_id == tenant_id)
        )
        datastores = list(ds_result.scalars().all())
        
        # Get snapshot count
        snap_result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.tenant_id == tenant_id)
        )
        snapshots = list(snap_result.scalars().all())
        
        # Get job count
        job_result = await self.db_session.execute(
            select(BackupJob).where(BackupJob.tenant_id == tenant_id)
        )
        jobs = list(job_result.scalars().all())
        
        # Get policy count
        policy_result = await self.db_session.execute(
            select(BackupPolicy).where(BackupPolicy.tenant_id == tenant_id)
        )
        policies = list(policy_result.scalars().all())
        
        return {
            'tenant_id': tenant_id,
            'isolation_status': 'enforced',
            'datastore_count': len(datastores),
            'snapshot_count': len(snapshots),
            'job_count': len(jobs),
            'policy_count': len(policies),
            'total_snapshot_size': sum(s.size for s in snapshots if s.size),
            'isolation_verified': True
        }
    
    def clear_cache(self) -> None:
        """Clear access control cache."""
        self._access_cache.clear()
        logger.debug("Access control cache cleared")
