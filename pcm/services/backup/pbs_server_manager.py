"""
PBS Server Manager for managing Proxmox Backup Server lifecycle.

This module provides comprehensive management of PBS servers including
registration, health monitoring, and datastore management.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
from pcm.core.models.backup.datastore import Datastore, DatastoreStatus
from pcm.services.backup.pbs_client import PBSAPIClient, PBSClientError, PBSConnectionError, PBSAuthenticationError


logger = logging.getLogger(__name__)


class PBSServerManagerError(Exception):
    """Base exception for PBS server manager errors."""
    pass


class PBSServerRegistrationError(PBSServerManagerError):
    """Raised when PBS server registration fails."""
    pass


class PBSServerManager:
    """
    Manager for PBS server lifecycle operations.
    
    Handles server registration, health monitoring, datastore management,
    and provides high-level operations for PBS server management.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize PBS server manager.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._health_check_tasks: Dict[str, asyncio.Task] = {}
    
    async def register_server(
        self,
        name: str,
        hostname: str,
        api_token_id: str,
        api_token_secret: str,
        datacenter: str,
        port: int = 8007,
        verify_ssl: bool = True,
        timeout: int = 30,
        description: Optional[str] = None
    ) -> PBSServer:
        """
        Register a new PBS server.
        
        Args:
            name: Server name
            hostname: Server hostname or IP
            api_token_id: PBS API token ID
            api_token_secret: PBS API token secret
            datacenter: Datacenter location
            port: Server port (default: 8007)
            verify_ssl: Whether to verify SSL certificates
            timeout: Connection timeout in seconds
            description: Optional server description
            
        Returns:
            Registered PBSServer instance
            
        Raises:
            PBSServerRegistrationError: If registration fails
        """
        logger.info(f"Registering PBS server: {name} at {hostname}:{port}")
        
        # Create server instance
        server = PBSServer(
            name=name,
            hostname=hostname,
            port=port,
            api_token_id=api_token_id,
            api_token_secret=api_token_secret,
            datacenter=datacenter,
            verify_ssl=verify_ssl,
            timeout=timeout,
            description=description,
            status=ServerStatus.OFFLINE
        )
        
        # Validate connectivity and authentication
        try:
            async with PBSAPIClient(server) as client:
                health_result = await client.health_check()
                
                if health_result['healthy']:
                    # Extract version and capabilities
                    version_info = health_result.get('version', {})
                    server.version = version_info.get('version')
                    server.capabilities = version_info
                    server.mark_online(server.version, server.capabilities)
                    logger.info(f"PBS server {name} validated successfully")
                else:
                    error_msg = health_result.get('error', 'Unknown validation error')
                    raise PBSServerRegistrationError(f"Server validation failed: {error_msg}")
                    
        except (PBSConnectionError, PBSAuthenticationError) as e:
            raise PBSServerRegistrationError(f"Failed to validate PBS server: {str(e)}") from e
        
        # Save to database
        self.db_session.add(server)
        await self.db_session.flush()
        await self.db_session.refresh(server)
        
        # Start health monitoring
        await self._start_health_monitoring(server)
        
        logger.info(f"PBS server {name} registered successfully with ID: {server.id}")
        return server
    
    async def unregister_server(self, server_id: str) -> bool:
        """
        Unregister a PBS server.
        
        Args:
            server_id: Server ID to unregister
            
        Returns:
            True if successful, False if server not found
        """
        logger.info(f"Unregistering PBS server: {server_id}")
        
        # Stop health monitoring
        await self._stop_health_monitoring(server_id)
        
        # Delete from database
        result = await self.db_session.execute(
            select(PBSServer).where(PBSServer.id == server_id)
        )
        server = result.scalar_one_or_none()
        
        if server:
            await self.db_session.delete(server)
            logger.info(f"PBS server {server.name} unregistered successfully")
            return True
        
        logger.warning(f"PBS server {server_id} not found for unregistration")
        return False
    
    async def get_server(self, server_id: str) -> Optional[PBSServer]:
        """
        Get a PBS server by ID.
        
        Args:
            server_id: Server ID
            
        Returns:
            PBSServer instance or None if not found
        """
        result = await self.db_session.execute(
            select(PBSServer)
            .options(selectinload(PBSServer.datastores))
            .where(PBSServer.id == server_id)
        )
        return result.scalar_one_or_none()
    
    async def list_servers(
        self, 
        datacenter: Optional[str] = None,
        status: Optional[ServerStatus] = None
    ) -> List[PBSServer]:
        """
        List PBS servers with optional filtering.
        
        Args:
            datacenter: Filter by datacenter
            status: Filter by server status
            
        Returns:
            List of PBSServer instances
        """
        query = select(PBSServer).options(selectinload(PBSServer.datastores))
        
        if datacenter:
            query = query.where(PBSServer.datacenter == datacenter)
        
        if status:
            query = query.where(PBSServer.status == status)
        
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
    
    async def perform_health_check(self, server_id: str) -> Dict[str, Any]:
        """
        Perform immediate health check on a PBS server.
        
        Args:
            server_id: Server ID to check
            
        Returns:
            Health check results
        """
        server = await self.get_server(server_id)
        if not server:
            raise PBSServerManagerError(f"Server {server_id} not found")
        
        logger.debug(f"Performing health check for PBS server: {server.name}")
        
        try:
            async with PBSAPIClient(server) as client:
                health_result = await client.health_check()
                
                if health_result['healthy']:
                    # Update server status
                    version_info = health_result.get('version', {})
                    server.mark_online(
                        version_info.get('version'),
                        version_info
                    )
                    
                    # Update datastore information
                    await self._update_datastore_info(server, health_result.get('datastores', []))
                    
                else:
                    error_msg = health_result.get('error', 'Health check failed')
                    server.mark_offline(error_msg)
                
                await self.db_session.flush()
                return health_result
                
        except Exception as e:
            error_msg = f"Health check failed: {str(e)}"
            server.mark_offline(error_msg)
            await self.db_session.flush()
            
            logger.error(f"Health check failed for server {server.name}: {e}")
            return {
                'healthy': False,
                'error': error_msg,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _update_datastore_info(self, server: PBSServer, datastore_list: List[Dict[str, Any]]) -> None:
        """
        Update datastore information from PBS server.
        
        Args:
            server: PBSServer instance
            datastore_list: List of datastore info from PBS
        """
        for ds_info in datastore_list:
            ds_name = ds_info.get('store')
            if not ds_name:
                continue
            
            # Find existing datastore
            for datastore in server.datastores:
                if datastore.name == ds_name:
                    # Update capacity information if available
                    if 'total' in ds_info and 'used' in ds_info:
                        total = ds_info['total']
                        used = ds_info['used']
                        available = ds_info.get('avail', total - used)
                        datastore.update_capacity(total, used, available)
                    break
    
    async def _start_health_monitoring(self, server: PBSServer) -> None:
        """
        Start background health monitoring for a server.
        
        Args:
            server: PBSServer instance to monitor
        """
        if server.id in self._health_check_tasks:
            # Already monitoring
            return
        
        async def health_monitor():
            """Background health monitoring task."""
            while True:
                try:
                    await asyncio.sleep(server.health_check_interval)
                    await self.perform_health_check(server.id)
                except asyncio.CancelledError:
                    logger.info(f"Health monitoring stopped for server {server.name}")
                    break
                except Exception as e:
                    logger.error(f"Health monitoring error for server {server.name}: {e}")
                    # Continue monitoring despite errors
        
        task = asyncio.create_task(health_monitor())
        self._health_check_tasks[server.id] = task
        logger.info(f"Started health monitoring for server {server.name}")
    
    async def _stop_health_monitoring(self, server_id: str) -> None:
        """
        Stop background health monitoring for a server.
        
        Args:
            server_id: Server ID to stop monitoring
        """
        if server_id in self._health_check_tasks:
            task = self._health_check_tasks.pop(server_id)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"Stopped health monitoring for server {server_id}")
    
    async def get_server_statistics(self, server_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a PBS server.
        
        Args:
            server_id: Server ID
            
        Returns:
            Server statistics including datastores and health metrics
        """
        server = await self.get_server(server_id)
        if not server:
            raise PBSServerManagerError(f"Server {server_id} not found")
        
        # Calculate datastore statistics
        total_datastores = len(server.datastores)
        active_datastores = sum(1 for ds in server.datastores if ds.status == DatastoreStatus.ACTIVE)
        total_capacity = sum(ds.total_capacity or 0 for ds in server.datastores)
        used_capacity = sum(ds.used_capacity or 0 for ds in server.datastores)
        
        return {
            'server_id': server.id,
            'server_name': server.name,
            'status': server.status.value,
            'version': server.version,
            'datacenter': server.datacenter,
            'last_health_check': server.last_health_check.isoformat() if server.last_health_check else None,
            'error_count': server.error_count,
            'datastores': {
                'total': total_datastores,
                'active': active_datastores,
                'total_capacity': total_capacity,
                'used_capacity': used_capacity,
                'usage_percentage': (used_capacity / total_capacity * 100) if total_capacity > 0 else 0
            },
            'uptime_days': (datetime.utcnow() - server.created_at).days,
            'is_healthy': server.is_healthy
        }
    
    async def cleanup(self) -> None:
        """
        Cleanup resources and stop all health monitoring tasks.
        """
        logger.info("Cleaning up PBS server manager")
        
        # Stop all health monitoring tasks
        for server_id in list(self._health_check_tasks.keys()):
            await self._stop_health_monitoring(server_id)
        
        logger.info("PBS server manager cleanup completed")