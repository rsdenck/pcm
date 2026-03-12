"""
Datastore Management Service for PBS Backup Module.

This module provides comprehensive datastore management including provisioning,
capacity monitoring, threshold alerting, and tenant-based assignment.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from pcm.core.models.backup.datastore import Datastore, DatastoreStatus
from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
from pcm.services.backup.pbs_client import PBSAPIClient, PBSClientError


logger = logging.getLogger(__name__)


class DatastoreManagerError(Exception):
    """Base exception for datastore manager errors."""
    pass


class DatastoreProvisioningError(DatastoreManagerError):
    """Raised when datastore provisioning fails."""
    pass


class DatastoreCapacityError(DatastoreManagerError):
    """Raised when datastore capacity issues occur."""
    pass


class DatastoreManager:
    """
    Comprehensive datastore management service.
    
    Provides datastore provisioning, capacity monitoring, threshold alerting,
    and tenant-based assignment for PBS servers.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize datastore manager.
        
        Args:
            db_session: Database session for datastore operations
        """
        self.db_session = db_session
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._alert_callbacks: List[callable] = []
    
    async def provision_datastore(
        self,
        pbs_server_id: str,
        tenant_id: str,
        name: str,
        path: str,
        description: Optional[str] = None,
        warning_threshold: int = 80,
        critical_threshold: int = 90,
        **options
    ) -> Datastore:
        """
        Provision a new datastore on a PBS server.
        
        Args:
            pbs_server_id: ID of the PBS server
            tenant_id: ID of the tenant to assign the datastore to
            name: Datastore name
            path: Storage path on the PBS server
            description: Optional description
            warning_threshold: Warning threshold percentage (default: 80)
            critical_threshold: Critical threshold percentage (default: 90)
            **options: Additional PBS datastore options
            
        Returns:
            Created Datastore instance
            
        Raises:
            DatastoreProvisioningError: If provisioning fails
        """
        try:
            # Get PBS server
            result = await self.db_session.execute(
                select(PBSServer).where(PBSServer.id == pbs_server_id)
            )
            pbs_server = result.scalar_one_or_none()
            
            if not pbs_server:
                raise DatastoreProvisioningError(f"PBS server {pbs_server_id} not found")
            
            if pbs_server.status != ServerStatus.ONLINE:
                raise DatastoreProvisioningError(
                    f"PBS server {pbs_server.name} is not online (status: {pbs_server.status})"
                )
            
            # Check if datastore name already exists on this server
            existing = await self.db_session.execute(
                select(Datastore).where(
                    and_(
                        Datastore.pbs_server_id == pbs_server_id,
                        Datastore.name == name
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise DatastoreProvisioningError(
                    f"Datastore '{name}' already exists on server {pbs_server.name}"
                )
            
            # Create datastore on PBS server
            async with PBSAPIClient(pbs_server) as client:
                await client.create_datastore(name, path, **options)
            
            # Create datastore record in database
            datastore = Datastore(
                name=name,
                pbs_server_id=pbs_server_id,
                tenant_id=tenant_id,
                path=path,
                description=description,
                warning_threshold=warning_threshold,
                critical_threshold=critical_threshold,
                status=DatastoreStatus.ACTIVE,
                is_encrypted=options.get('encrypt', False),
                compression_enabled=options.get('compress', True),
                deduplication_enabled=options.get('dedup', True)
            )
            
            self.db_session.add(datastore)
            await self.db_session.commit()
            await self.db_session.refresh(datastore)
            
            logger.info(f"Provisioned datastore '{name}' for tenant {tenant_id} on server {pbs_server.name}")
            
            # Start monitoring for the new datastore
            await self._start_datastore_monitoring(datastore.id)
            
            return datastore
            
        except PBSClientError as e:
            await self.db_session.rollback()
            raise DatastoreProvisioningError(f"Failed to create datastore on PBS server: {e}") from e
        except Exception as e:
            await self.db_session.rollback()
            raise DatastoreProvisioningError(f"Failed to provision datastore: {e}") from e
    
    async def assign_datastore_to_tenant(
        self,
        datastore_id: str,
        tenant_id: str
    ) -> Datastore:
        """
        Assign a datastore to a specific tenant.
        
        Args:
            datastore_id: ID of the datastore
            tenant_id: ID of the tenant
            
        Returns:
            Updated Datastore instance
            
        Raises:
            DatastoreManagerError: If assignment fails
        """
        try:
            result = await self.db_session.execute(
                select(Datastore).where(Datastore.id == datastore_id)
            )
            datastore = result.scalar_one_or_none()
            
            if not datastore:
                raise DatastoreManagerError(f"Datastore {datastore_id} not found")
            
            # Update tenant assignment
            datastore.tenant_id = tenant_id
            await self.db_session.commit()
            await self.db_session.refresh(datastore)
            
            logger.info(f"Assigned datastore '{datastore.name}' to tenant {tenant_id}")
            
            return datastore
            
        except Exception as e:
            await self.db_session.rollback()
            raise DatastoreManagerError(f"Failed to assign datastore to tenant: {e}") from e
    
    async def get_tenant_datastores(
        self,
        tenant_id: str,
        status_filter: Optional[DatastoreStatus] = None
    ) -> List[Datastore]:
        """
        Get all datastores assigned to a tenant.
        
        Args:
            tenant_id: ID of the tenant
            status_filter: Optional status filter
            
        Returns:
            List of Datastore instances
        """
        query = select(Datastore).options(
            selectinload(Datastore.pbs_server)
        ).where(Datastore.tenant_id == tenant_id)
        
        if status_filter:
            query = query.where(Datastore.status == status_filter)
        
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
    
    async def update_datastore_capacity(
        self,
        datastore_id: str,
        force_update: bool = False
    ) -> Datastore:
        """
        Update capacity information for a datastore.
        
        Args:
            datastore_id: ID of the datastore
            force_update: Force update even if recently checked
            
        Returns:
            Updated Datastore instance
            
        Raises:
            DatastoreManagerError: If update fails
        """
        try:
            result = await self.db_session.execute(
                select(Datastore).options(
                    selectinload(Datastore.pbs_server)
                ).where(Datastore.id == datastore_id)
            )
            datastore = result.scalar_one_or_none()
            
            if not datastore:
                raise DatastoreManagerError(f"Datastore {datastore_id} not found")
            
            # Check if update is needed
            if not force_update and datastore.last_capacity_check:
                time_since_check = datetime.utcnow() - datastore.last_capacity_check
                if time_since_check.total_seconds() < datastore.capacity_check_interval:
                    return datastore
            
            # Get capacity information from PBS server
            async with PBSAPIClient(datastore.pbs_server) as client:
                status_info = await client.get_datastore_status(datastore.name)
            
            # Update capacity information
            total = status_info.get('total', 0)
            used = status_info.get('used', 0)
            available = status_info.get('avail', total - used)
            
            old_status = datastore.status
            datastore.update_capacity(total, used, available)
            
            # Clear any previous errors if update successful
            if datastore.status == DatastoreStatus.ERROR:
                datastore.clear_error()
            
            await self.db_session.commit()
            await self.db_session.refresh(datastore)
            
            # Check for threshold alerts
            await self._check_capacity_thresholds(datastore, old_status)
            
            logger.debug(f"Updated capacity for datastore '{datastore.name}': {used}/{total} bytes")
            
            return datastore
            
        except PBSClientError as e:
            # Mark datastore as error state
            if 'datastore' in locals():
                datastore.mark_error(f"Failed to get capacity: {e}")
                await self.db_session.commit()
            raise DatastoreManagerError(f"Failed to update datastore capacity: {e}") from e
        except Exception as e:
            await self.db_session.rollback()
            raise DatastoreManagerError(f"Failed to update datastore capacity: {e}") from e
    
    async def monitor_all_datastores(self) -> Dict[str, Any]:
        """
        Monitor capacity for all active datastores.
        
        Returns:
            Monitoring results summary
        """
        try:
            # Get all active datastores
            result = await self.db_session.execute(
                select(Datastore).options(
                    selectinload(Datastore.pbs_server)
                ).where(Datastore.status.in_([
                    DatastoreStatus.ACTIVE,
                    DatastoreStatus.FULL
                ]))
            )
            datastores = list(result.scalars().all())
            
            monitoring_results = {
                'total_datastores': len(datastores),
                'updated': 0,
                'errors': 0,
                'warnings': 0,
                'critical': 0,
                'details': []
            }
            
            # Update capacity for each datastore
            for datastore in datastores:
                try:
                    updated_datastore = await self.update_datastore_capacity(datastore.id)
                    monitoring_results['updated'] += 1
                    
                    # Count threshold violations
                    if updated_datastore.is_over_critical_threshold:
                        monitoring_results['critical'] += 1
                    elif updated_datastore.is_over_warning_threshold:
                        monitoring_results['warnings'] += 1
                    
                    monitoring_results['details'].append({
                        'datastore_id': datastore.id,
                        'name': datastore.name,
                        'tenant_id': datastore.tenant_id,
                        'status': updated_datastore.status.value,
                        'usage_percentage': updated_datastore.usage_percentage,
                        'is_healthy': updated_datastore.is_healthy
                    })
                    
                except Exception as e:
                    monitoring_results['errors'] += 1
                    monitoring_results['details'].append({
                        'datastore_id': datastore.id,
                        'name': datastore.name,
                        'error': str(e)
                    })
                    logger.error(f"Failed to monitor datastore {datastore.name}: {e}")
            
            logger.info(f"Monitored {monitoring_results['updated']} datastores, "
                       f"{monitoring_results['warnings']} warnings, "
                       f"{monitoring_results['critical']} critical")
            
            return monitoring_results
            
        except Exception as e:
            logger.error(f"Failed to monitor datastores: {e}")
            raise DatastoreManagerError(f"Failed to monitor datastores: {e}") from e
    
    async def get_datastore_statistics(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive datastore statistics.
        
        Args:
            tenant_id: Optional tenant filter
            
        Returns:
            Datastore statistics
        """
        try:
            # Base query
            query = select(Datastore)
            if tenant_id:
                query = query.where(Datastore.tenant_id == tenant_id)
            
            result = await self.db_session.execute(query)
            datastores = list(result.scalars().all())
            
            # Calculate statistics
            total_datastores = len(datastores)
            active_datastores = sum(1 for ds in datastores if ds.status == DatastoreStatus.ACTIVE)
            total_capacity = sum(ds.total_capacity or 0 for ds in datastores)
            used_capacity = sum(ds.used_capacity or 0 for ds in datastores)
            
            # Status breakdown
            status_counts = {}
            for status in DatastoreStatus:
                status_counts[status.value] = sum(1 for ds in datastores if ds.status == status)
            
            # Threshold violations
            warning_count = sum(1 for ds in datastores if ds.is_over_warning_threshold)
            critical_count = sum(1 for ds in datastores if ds.is_over_critical_threshold)
            
            # Recent activity
            recent_backups = sum(1 for ds in datastores 
                               if ds.last_backup and 
                               ds.last_backup > datetime.utcnow() - timedelta(days=1))
            
            return {
                'total_datastores': total_datastores,
                'active_datastores': active_datastores,
                'total_capacity': total_capacity,
                'used_capacity': used_capacity,
                'available_capacity': total_capacity - used_capacity if total_capacity > 0 else 0,
                'usage_percentage': (used_capacity / total_capacity * 100) if total_capacity > 0 else 0,
                'status_breakdown': status_counts,
                'threshold_violations': {
                    'warning': warning_count,
                    'critical': critical_count
                },
                'recent_activity': {
                    'datastores_with_recent_backups': recent_backups
                },
                'tenant_id': tenant_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get datastore statistics: {e}")
            raise DatastoreManagerError(f"Failed to get datastore statistics: {e}") from e
    
    async def _check_capacity_thresholds(
        self,
        datastore: Datastore,
        old_status: DatastoreStatus
    ) -> None:
        """
        Check capacity thresholds and trigger alerts if needed.
        
        Args:
            datastore: Datastore to check
            old_status: Previous status for comparison
        """
        try:
            current_usage = datastore.usage_percentage
            if current_usage is None:
                return
            
            # Check for threshold violations
            alert_data = {
                'datastore_id': datastore.id,
                'datastore_name': datastore.name,
                'tenant_id': datastore.tenant_id,
                'pbs_server_id': datastore.pbs_server_id,
                'usage_percentage': current_usage,
                'total_capacity': datastore.total_capacity,
                'used_capacity': datastore.used_capacity,
                'available_capacity': datastore.available_capacity,
                'timestamp': datetime.utcnow()
            }
            
            # Critical threshold alert
            if datastore.is_over_critical_threshold and old_status != DatastoreStatus.FULL:
                alert_data.update({
                    'alert_type': 'critical',
                    'threshold': datastore.critical_threshold,
                    'message': f"Datastore '{datastore.name}' has exceeded critical threshold "
                              f"({current_usage:.1f}% > {datastore.critical_threshold}%)"
                })
                await self._trigger_alert(alert_data)
                
            # Warning threshold alert
            elif (datastore.is_over_warning_threshold and 
                  not datastore.is_over_critical_threshold and
                  not old_status in [DatastoreStatus.FULL]):
                alert_data.update({
                    'alert_type': 'warning',
                    'threshold': datastore.warning_threshold,
                    'message': f"Datastore '{datastore.name}' has exceeded warning threshold "
                              f"({current_usage:.1f}% > {datastore.warning_threshold}%)"
                })
                await self._trigger_alert(alert_data)
                
            # Recovery alert (if previously over threshold)
            elif (not datastore.is_over_warning_threshold and 
                  old_status == DatastoreStatus.FULL):
                alert_data.update({
                    'alert_type': 'recovery',
                    'message': f"Datastore '{datastore.name}' has recovered from capacity issues "
                              f"(usage now {current_usage:.1f}%)"
                })
                await self._trigger_alert(alert_data)
                
        except Exception as e:
            logger.error(f"Failed to check capacity thresholds for datastore {datastore.name}: {e}")
    
    async def _trigger_alert(self, alert_data: Dict[str, Any]) -> None:
        """
        Trigger capacity alert through registered callbacks.
        
        Args:
            alert_data: Alert information
        """
        try:
            logger.warning(f"Datastore capacity alert: {alert_data['message']}")
            
            # Call registered alert callbacks
            for callback in self._alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert_data)
                    else:
                        callback(alert_data)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    def register_alert_callback(self, callback: callable) -> None:
        """
        Register a callback for capacity alerts.
        
        Args:
            callback: Function to call when alerts are triggered
        """
        self._alert_callbacks.append(callback)
    
    def unregister_alert_callback(self, callback: callable) -> None:
        """
        Unregister an alert callback.
        
        Args:
            callback: Function to remove from callbacks
        """
        if callback in self._alert_callbacks:
            self._alert_callbacks.remove(callback)
    
    async def _start_datastore_monitoring(self, datastore_id: str) -> None:
        """
        Start background monitoring for a specific datastore.
        
        Args:
            datastore_id: ID of the datastore to monitor
        """
        if datastore_id in self._monitoring_tasks:
            # Already monitoring this datastore
            return
        
        async def monitor_loop():
            """Background monitoring loop for a datastore."""
            while True:
                try:
                    await self.update_datastore_capacity(datastore_id)
                    
                    # Get datastore to check monitoring interval
                    result = await self.db_session.execute(
                        select(Datastore).where(Datastore.id == datastore_id)
                    )
                    datastore = result.scalar_one_or_none()
                    
                    if not datastore or datastore.status == DatastoreStatus.INACTIVE:
                        break
                    
                    # Wait for next check
                    await asyncio.sleep(datastore.capacity_check_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in datastore monitoring loop for {datastore_id}: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
        
        # Start monitoring task
        task = asyncio.create_task(monitor_loop())
        self._monitoring_tasks[datastore_id] = task
        logger.info(f"Started monitoring for datastore {datastore_id}")
    
    async def _stop_datastore_monitoring(self, datastore_id: str) -> None:
        """
        Stop background monitoring for a specific datastore.
        
        Args:
            datastore_id: ID of the datastore to stop monitoring
        """
        if datastore_id in self._monitoring_tasks:
            task = self._monitoring_tasks.pop(datastore_id)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"Stopped monitoring for datastore {datastore_id}")
    
    async def start_monitoring_all_datastores(self) -> None:
        """Start monitoring for all active datastores."""
        try:
            result = await self.db_session.execute(
                select(Datastore.id).where(
                    Datastore.status.in_([DatastoreStatus.ACTIVE, DatastoreStatus.FULL])
                )
            )
            datastore_ids = [row[0] for row in result.fetchall()]
            
            for datastore_id in datastore_ids:
                await self._start_datastore_monitoring(datastore_id)
                
            logger.info(f"Started monitoring for {len(datastore_ids)} datastores")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring all datastores: {e}")
            raise DatastoreManagerError(f"Failed to start monitoring: {e}") from e
    
    async def stop_monitoring_all_datastores(self) -> None:
        """Stop monitoring for all datastores."""
        try:
            datastore_ids = list(self._monitoring_tasks.keys())
            
            for datastore_id in datastore_ids:
                await self._stop_datastore_monitoring(datastore_id)
                
            logger.info(f"Stopped monitoring for {len(datastore_ids)} datastores")
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring all datastores: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources and stop all monitoring tasks."""
        await self.stop_monitoring_all_datastores()
        self._alert_callbacks.clear()
        logger.info("Datastore manager cleanup completed")