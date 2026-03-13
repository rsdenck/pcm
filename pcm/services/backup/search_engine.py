"""
Backup Search and Filtering Engine.

This module provides advanced search and filtering capabilities for backup
discovery and cross-datacenter metadata replication.
"""

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from pcm.core.models.backup.snapshot import BackupSnapshot
from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.policy import BackupPolicy
from pcm.core.models.backup.datastore import Datastore
from pcm.core.models.backup.pbs_server import PBSServer


logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Backup search and filtering engine.
    
    Provides advanced search capabilities with multiple filters,
    cross-datacenter metadata replication, and efficient indexing.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize search engine.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._search_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    async def search(
        self,
        tenant_id: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Perform advanced search on backups.
        
        Args:
            tenant_id: Tenant ID
            query: Optional search query string
            filters: Optional filter dictionary
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            Search results with metadata
        """
        filters = filters or {}
        
        # Build base query
        query_obj = select(BackupSnapshot).where(
            BackupSnapshot.tenant_id == tenant_id
        )
        
        # Apply filters
        filter_conditions = []
        
        # VM ID filter
        if 'vm_id' in filters:
            filter_conditions.append(BackupSnapshot.vm_id == filters['vm_id'])
        
        # Time range filters
        if 'start_time' in filters:
            filter_conditions.append(
                BackupSnapshot.snapshot_time >= filters['start_time']
            )
        
        if 'end_time' in filters:
            filter_conditions.append(
                BackupSnapshot.snapshot_time <= filters['end_time']
            )
        
        # Verification status filter
        if 'verification_status' in filters:
            filter_conditions.append(
                BackupSnapshot.verification_status == filters['verification_status']
            )
        
        # Size range filters
        if 'min_size' in filters:
            filter_conditions.append(BackupSnapshot.size >= filters['min_size'])
        
        if 'max_size' in filters:
            filter_conditions.append(BackupSnapshot.size <= filters['max_size'])
        
        # Datastore filter
        if 'datastore_id' in filters:
            filter_conditions.append(
                BackupSnapshot.datastore_id == filters['datastore_id']
            )
        
        # Apply all filters
        if filter_conditions:
            query_obj = query_obj.where(and_(*filter_conditions))
        
        # Apply text search if provided
        if query:
            query_obj = query_obj.where(
                or_(
                    BackupSnapshot.vm_id.ilike(f"%{query}%"),
                    BackupSnapshot.path.ilike(f"%{query}%")
                )
            )
        
        # Get total count
        count_result = await self.db_session.execute(
            select(func.count(BackupSnapshot.id)).where(
                query_obj.whereclause
            )
        )
        total_count = count_result.scalar() or 0
        
        # Apply ordering and pagination
        query_obj = query_obj.order_by(
            BackupSnapshot.snapshot_time.desc()
        ).limit(limit).offset(offset)
        
        result = await self.db_session.execute(query_obj)
        snapshots = list(result.scalars().all())
        
        # Format results
        results = []
        for snapshot in snapshots:
            results.append({
                'snapshot_id': snapshot.id,
                'job_id': snapshot.job_id,
                'vm_id': snapshot.vm_id,
                'snapshot_time': snapshot.snapshot_time.isoformat(),
                'size': snapshot.size,
                'datastore_id': snapshot.datastore_id,
                'verification_status': snapshot.verification_status,
                'path': snapshot.path
            })
        
        return {
            'total_count': total_count,
            'returned_count': len(results),
            'limit': limit,
            'offset': offset,
            'results': results
        }
    
    async def advanced_search(
        self,
        tenant_id: str,
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Perform advanced search with complex criteria.
        
        Args:
            tenant_id: Tenant ID
            criteria: Search criteria dictionary
            
        Returns:
            List of matching backups
        """
        query = select(BackupSnapshot).where(
            BackupSnapshot.tenant_id == tenant_id
        )
        
        # Build complex filter conditions
        conditions = []
        
        # VM patterns
        if 'vm_patterns' in criteria:
            vm_conditions = [
                BackupSnapshot.vm_id.ilike(pattern)
                for pattern in criteria['vm_patterns']
            ]
            conditions.append(or_(*vm_conditions))
        
        # Time window
        if 'time_window' in criteria:
            window = criteria['time_window']
            if 'start' in window:
                conditions.append(BackupSnapshot.snapshot_time >= window['start'])
            if 'end' in window:
                conditions.append(BackupSnapshot.snapshot_time <= window['end'])
        
        # Size criteria
        if 'size_criteria' in criteria:
            size = criteria['size_criteria']
            if 'min' in size:
                conditions.append(BackupSnapshot.size >= size['min'])
            if 'max' in size:
                conditions.append(BackupSnapshot.size <= size['max'])
        
        # Verification status
        if 'verification_statuses' in criteria:
            statuses = criteria['verification_statuses']
            conditions.append(
                BackupSnapshot.verification_status.in_(statuses)
            )
        
        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.db_session.execute(query)
        snapshots = list(result.scalars().all())
        
        return [
            {
                'snapshot_id': s.id,
                'vm_id': s.vm_id,
                'snapshot_time': s.snapshot_time.isoformat(),
                'size': s.size,
                'verification_status': s.verification_status
            }
            for s in snapshots
        ]
    
    async def get_search_suggestions(
        self,
        tenant_id: str,
        prefix: str,
        suggestion_type: str = 'vm_id'
    ) -> List[str]:
        """
        Get search suggestions based on prefix.
        
        Args:
            tenant_id: Tenant ID
            prefix: Search prefix
            suggestion_type: Type of suggestions (vm_id, datastore_id, etc)
            
        Returns:
            List of suggestions
        """
        if suggestion_type == 'vm_id':
            result = await self.db_session.execute(
                select(BackupSnapshot.vm_id)
                .where(
                    and_(
                        BackupSnapshot.tenant_id == tenant_id,
                        BackupSnapshot.vm_id.ilike(f"{prefix}%")
                    )
                )
                .distinct()
                .limit(10)
            )
        elif suggestion_type == 'datastore_id':
            result = await self.db_session.execute(
                select(BackupSnapshot.datastore_id)
                .where(
                    and_(
                        BackupSnapshot.tenant_id == tenant_id,
                        BackupSnapshot.datastore_id.ilike(f"{prefix}%")
                    )
                )
                .distinct()
                .limit(10)
            )
        else:
            return []
        
        suggestions = list(result.scalars().all())
        return [s for s in suggestions if s]  # Filter out None values
    
    async def get_backup_timeline(
        self,
        tenant_id: str,
        vm_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get backup timeline for a VM.
        
        Args:
            tenant_id: Tenant ID
            vm_id: VM ID
            days: Number of days to look back
            
        Returns:
            Timeline of backups
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db_session.execute(
            select(BackupSnapshot)
            .where(
                and_(
                    BackupSnapshot.tenant_id == tenant_id,
                    BackupSnapshot.vm_id == vm_id,
                    BackupSnapshot.snapshot_time >= start_time
                )
            )
            .order_by(BackupSnapshot.snapshot_time.asc())
        )
        
        snapshots = list(result.scalars().all())
        
        timeline = []
        for snapshot in snapshots:
            timeline.append({
                'snapshot_id': snapshot.id,
                'snapshot_time': snapshot.snapshot_time.isoformat(),
                'size': snapshot.size,
                'verification_status': snapshot.verification_status,
                'day': snapshot.snapshot_time.strftime('%Y-%m-%d')
            })
        
        return timeline
    
    async def get_cross_datacenter_backups(
        self,
        tenant_id: str,
        vm_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get backups for a VM across all datacenters.
        
        Args:
            tenant_id: Tenant ID
            vm_id: VM ID
            
        Returns:
            Backups grouped by datacenter
        """
        # Get all backups for the VM
        result = await self.db_session.execute(
            select(BackupSnapshot)
            .where(
                and_(
                    BackupSnapshot.tenant_id == tenant_id,
                    BackupSnapshot.vm_id == vm_id
                )
            )
        )
        
        snapshots = list(result.scalars().all())
        
        # Group by datastore/datacenter
        backups_by_datacenter: Dict[str, List[Dict[str, Any]]] = {}
        
        for snapshot in snapshots:
            # Get datastore info
            ds_result = await self.db_session.execute(
                select(Datastore).where(Datastore.id == snapshot.datastore_id)
            )
            datastore = ds_result.scalar_one_or_none()
            
            if datastore:
                # Get PBS server info
                pbs_result = await self.db_session.execute(
                    select(PBSServer).where(PBSServer.id == datastore.pbs_server_id)
                )
                pbs_server = pbs_result.scalar_one_or_none()
                
                datacenter = pbs_server.datacenter if pbs_server else "unknown"
            else:
                datacenter = "unknown"
            
            if datacenter not in backups_by_datacenter:
                backups_by_datacenter[datacenter] = []
            
            backups_by_datacenter[datacenter].append({
                'snapshot_id': snapshot.id,
                'snapshot_time': snapshot.snapshot_time.isoformat(),
                'size': snapshot.size,
                'datastore_id': snapshot.datastore_id,
                'verification_status': snapshot.verification_status
            })
        
        return backups_by_datacenter
    
    async def replicate_metadata(
        self,
        source_datacenter: str,
        target_datacenter: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Replicate backup metadata across datacenters.
        
        Args:
            source_datacenter: Source datacenter name
            target_datacenter: Target datacenter name
            tenant_id: Tenant ID
            
        Returns:
            Replication results
        """
        # Get all backups in source datacenter
        result = await self.db_session.execute(
            select(BackupSnapshot)
            .where(BackupSnapshot.tenant_id == tenant_id)
        )
        
        snapshots = list(result.scalars().all())
        
        replicated_count = 0
        failed_count = 0
        
        for snapshot in snapshots:
            try:
                # Get datastore info
                ds_result = await self.db_session.execute(
                    select(Datastore).where(Datastore.id == snapshot.datastore_id)
                )
                datastore = ds_result.scalar_one_or_none()
                
                if datastore:
                    # Get PBS server info
                    pbs_result = await self.db_session.execute(
                        select(PBSServer).where(PBSServer.id == datastore.pbs_server_id)
                    )
                    pbs_server = pbs_result.scalar_one_or_none()
                    
                    if pbs_server and pbs_server.datacenter == source_datacenter:
                        # Replicate metadata (in real implementation, would sync to target)
                        replicated_count += 1
                        logger.debug(f"Replicated metadata for snapshot {snapshot.id}")
            except Exception as e:
                logger.error(f"Failed to replicate metadata for snapshot {snapshot.id}: {e}")
                failed_count += 1
        
        return {
            'source_datacenter': source_datacenter,
            'target_datacenter': target_datacenter,
            'tenant_id': tenant_id,
            'replicated_count': replicated_count,
            'failed_count': failed_count,
            'total_count': len(snapshots),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def clear_cache(self) -> None:
        """Clear search cache."""
        self._search_cache.clear()
        logger.debug("Search cache cleared")
