"""
PBS Health Monitoring Service.

This module provides centralized health monitoring for all PBS servers,
including periodic health checks, alerting, and status management.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
from pcm.services.backup.pbs_server_manager import PBSServerManager


logger = logging.getLogger(__name__)


class HealthMonitoringService:
    """
    Centralized health monitoring service for PBS servers.
    
    Manages periodic health checks, status updates, and alerting
    for all registered PBS servers.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize health monitoring service.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self.server_manager = PBSServerManager(db_session)
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._check_interval = 60  # Check every minute for servers needing health checks
    
    async def start_monitoring(self) -> None:
        """
        Start the health monitoring service.
        """
        if self._is_running:
            logger.warning("Health monitoring service is already running")
            return
        
        logger.info("Starting PBS health monitoring service")
        self._is_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self) -> None:
        """
        Stop the health monitoring service.
        """
        if not self._is_running:
            return
        
        logger.info("Stopping PBS health monitoring service")
        self._is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        
        # Cleanup server manager
        await self.server_manager.cleanup()
    
    async def _monitoring_loop(self) -> None:
        """
        Main monitoring loop that checks servers periodically.
        """
        logger.info("Health monitoring loop started")
        
        while self._is_running:
            try:
                await self._check_servers_health()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                logger.info("Health monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                # Continue monitoring despite errors
                await asyncio.sleep(self._check_interval)
    
    async def _check_servers_health(self) -> None:
        """
        Check health of all servers that need monitoring.
        """
        try:
            # Get all servers that need health checks
            servers_to_check = await self._get_servers_needing_check()
            
            if not servers_to_check:
                return
            
            logger.debug(f"Checking health of {len(servers_to_check)} PBS servers")
            
            # Perform health checks concurrently
            tasks = [
                self._perform_server_health_check(server)
                for server in servers_to_check
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            successful_checks = sum(1 for r in results if not isinstance(r, Exception))
            failed_checks = len(results) - successful_checks
            
            if failed_checks > 0:
                logger.warning(f"Health checks completed: {successful_checks} successful, {failed_checks} failed")
            else:
                logger.debug(f"All {successful_checks} health checks completed successfully")
                
        except Exception as e:
            logger.error(f"Error checking servers health: {e}")
    
    async def _get_servers_needing_check(self) -> List[PBSServer]:
        """
        Get list of servers that need health checks.
        
        Returns:
            List of servers needing health checks
        """
        now = datetime.utcnow()
        
        # Query servers that haven't been checked recently
        result = await self.db_session.execute(
            select(PBSServer).where(
                (PBSServer.last_health_check.is_(None)) |
                (PBSServer.last_health_check < now - timedelta(seconds=PBSServer.health_check_interval))
            )
        )
        
        return list(result.scalars().all())
    
    async def _perform_server_health_check(self, server: PBSServer) -> Dict[str, Any]:
        """
        Perform health check for a single server.
        
        Args:
            server: PBSServer instance to check
            
        Returns:
            Health check results
        """
        try:
            result = await self.server_manager.perform_health_check(server.id)
            
            # Log status changes
            if result.get('healthy'):
                if server.status != ServerStatus.ONLINE:
                    logger.info(f"PBS server {server.name} is now online")
            else:
                if server.status == ServerStatus.ONLINE:
                    logger.warning(f"PBS server {server.name} is now offline: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Health check failed for server {server.name}: {e}")
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get current monitoring service status.
        
        Returns:
            Monitoring service status and statistics
        """
        # Get server statistics
        all_servers = await self.server_manager.list_servers()
        
        status_counts = {}
        for status in ServerStatus:
            status_counts[status.value] = sum(1 for s in all_servers if s.status == status)
        
        # Calculate health metrics
        total_servers = len(all_servers)
        healthy_servers = status_counts.get(ServerStatus.ONLINE.value, 0)
        unhealthy_servers = total_servers - healthy_servers
        
        # Get servers with recent errors
        servers_with_errors = [s for s in all_servers if s.error_count > 0]
        
        return {
            'service_status': 'running' if self._is_running else 'stopped',
            'check_interval': self._check_interval,
            'total_servers': total_servers,
            'server_status_counts': status_counts,
            'health_summary': {
                'healthy_servers': healthy_servers,
                'unhealthy_servers': unhealthy_servers,
                'health_percentage': (healthy_servers / total_servers * 100) if total_servers > 0 else 100
            },
            'servers_with_errors': len(servers_with_errors),
            'last_check_time': datetime.utcnow().isoformat()
        }
    
    async def force_check_all_servers(self) -> Dict[str, Any]:
        """
        Force immediate health check of all servers.
        
        Returns:
            Results of all health checks
        """
        logger.info("Forcing health check of all PBS servers")
        
        all_servers = await self.server_manager.list_servers()
        
        if not all_servers:
            return {
                'total_servers': 0,
                'results': [],
                'summary': 'No servers to check'
            }
        
        # Perform health checks concurrently
        tasks = [
            self._perform_server_health_check(server)
            for server in all_servers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_checks = []
        failed_checks = []
        
        for i, result in enumerate(results):
            server = all_servers[i]
            if isinstance(result, Exception):
                failed_checks.append({
                    'server_id': server.id,
                    'server_name': server.name,
                    'error': str(result)
                })
            else:
                if result.get('healthy'):
                    successful_checks.append({
                        'server_id': server.id,
                        'server_name': server.name,
                        'status': 'healthy'
                    })
                else:
                    failed_checks.append({
                        'server_id': server.id,
                        'server_name': server.name,
                        'error': result.get('error', 'Unknown error')
                    })
        
        return {
            'total_servers': len(all_servers),
            'successful_checks': len(successful_checks),
            'failed_checks': len(failed_checks),
            'results': {
                'successful': successful_checks,
                'failed': failed_checks
            },
            'timestamp': datetime.utcnow().isoformat()
        }