"""
Unit tests for Health Monitoring Service.

Tests centralized health monitoring for PBS servers.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
from pcm.services.backup.health_monitor import HealthMonitoringService
from pcm.services.backup.pbs_server_manager import PBSServerManager


class TestHealthMonitoringService:
    """Test cases for HealthMonitoringService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session
    
    @pytest.fixture
    def health_monitor(self, mock_db_session):
        """Create HealthMonitoringService instance."""
        return HealthMonitoringService(mock_db_session)
    
    @pytest.fixture
    def mock_servers(self):
        """Create mock PBS servers."""
        server1 = MagicMock(spec=PBSServer)
        server1.id = "server1"
        server1.name = "pbs-01"
        server1.status = ServerStatus.ONLINE
        server1.health_check_interval = 300
        server1.last_health_check = datetime.utcnow() - timedelta(seconds=400)
        server1.error_count = 0
        
        server2 = MagicMock(spec=PBSServer)
        server2.id = "server2"
        server2.name = "pbs-02"
        server2.status = ServerStatus.OFFLINE
        server2.health_check_interval = 300
        server2.last_health_check = None
        server2.error_count = 2
        
        return [server1, server2]
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, health_monitor):
        """Test starting the monitoring service."""
        assert not health_monitor._is_running
        assert health_monitor._monitoring_task is None
        
        with patch.object(health_monitor, '_monitoring_loop', new_callable=AsyncMock) as mock_loop:
            await health_monitor.start_monitoring()
            
            assert health_monitor._is_running is True
            assert health_monitor._monitoring_task is not None
    
    @pytest.mark.asyncio
    async def test_start_monitoring_already_running(self, health_monitor):
        """Test starting monitoring when already running."""
        health_monitor._is_running = True
        
        with patch.object(health_monitor, '_monitoring_loop', new_callable=AsyncMock):
            await health_monitor.start_monitoring()
            
            # Should not create new task
            assert health_monitor._monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, health_monitor):
        """Test stopping the monitoring service."""
        # Set up running state
        health_monitor._is_running = True
        mock_task = AsyncMock()
        health_monitor._monitoring_task = mock_task
        
        with patch.object(health_monitor.server_manager, 'cleanup', new_callable=AsyncMock) as mock_cleanup:
            await health_monitor.stop_monitoring()
            
            assert health_monitor._is_running is False
            mock_task.cancel.assert_called_once()
            mock_cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_servers_needing_check(self, health_monitor, mock_servers):
        """Test getting servers that need health checks."""
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_servers
        health_monitor.db_session.execute.return_value = mock_result
        
        servers = await health_monitor._get_servers_needing_check()
        
        assert len(servers) == 2
        assert servers == mock_servers
        
        # Verify query was executed
        health_monitor.db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_perform_server_health_check_success(self, health_monitor):
        """Test successful server health check."""
        mock_server = MagicMock(spec=PBSServer)
        mock_server.name = "test-server"
        mock_server.status = ServerStatus.OFFLINE
        
        mock_health_result = {
            'healthy': True,
            'version': {'version': '2.4.0'}
        }
        
        with patch.object(health_monitor.server_manager, 'perform_health_check', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = mock_health_result
            
            result = await health_monitor._perform_server_health_check(mock_server)
            
            assert result == mock_health_result
            mock_check.assert_called_once_with(mock_server.id)
    
    @pytest.mark.asyncio
    async def test_perform_server_health_check_failure(self, health_monitor):
        """Test server health check with failure."""
        mock_server = MagicMock(spec=PBSServer)
        mock_server.name = "test-server"
        mock_server.status = ServerStatus.ONLINE
        
        with patch.object(health_monitor.server_manager, 'perform_health_check', new_callable=AsyncMock) as mock_check:
            mock_check.side_effect = Exception("Health check failed")
            
            result = await health_monitor._perform_server_health_check(mock_server)
            
            assert result['healthy'] is False
            assert 'Health check failed' in result['error']
    
    @pytest.mark.asyncio
    async def test_check_servers_health(self, health_monitor, mock_servers):
        """Test checking health of multiple servers."""
        with patch.object(health_monitor, '_get_servers_needing_check', new_callable=AsyncMock) as mock_get_servers:
            with patch.object(health_monitor, '_perform_server_health_check', new_callable=AsyncMock) as mock_check:
                mock_get_servers.return_value = mock_servers
                mock_check.return_value = {'healthy': True}
                
                await health_monitor._check_servers_health()
                
                # Verify all servers were checked
                assert mock_check.call_count == len(mock_servers)
                mock_check.assert_any_call(mock_servers[0])
                mock_check.assert_any_call(mock_servers[1])
    
    @pytest.mark.asyncio
    async def test_check_servers_health_no_servers(self, health_monitor):
        """Test checking health when no servers need checking."""
        with patch.object(health_monitor, '_get_servers_needing_check', new_callable=AsyncMock) as mock_get_servers:
            mock_get_servers.return_value = []
            
            await health_monitor._check_servers_health()
            
            # Should return early without performing checks
            mock_get_servers.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_monitoring_status(self, health_monitor, mock_servers):
        """Test getting monitoring service status."""
        health_monitor._is_running = True
        
        with patch.object(health_monitor.server_manager, 'list_servers', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_servers
            
            status = await health_monitor.get_monitoring_status()
            
            assert status['service_status'] == 'running'
            assert status['total_servers'] == 2
            assert status['server_status_counts'][ServerStatus.ONLINE.value] == 1
            assert status['server_status_counts'][ServerStatus.OFFLINE.value] == 1
            assert status['health_summary']['healthy_servers'] == 1
            assert status['health_summary']['unhealthy_servers'] == 1
            assert status['health_summary']['health_percentage'] == 50.0
            assert status['servers_with_errors'] == 1  # server2 has error_count > 0
    
    @pytest.mark.asyncio
    async def test_get_monitoring_status_no_servers(self, health_monitor):
        """Test getting monitoring status with no servers."""
        health_monitor._is_running = False
        
        with patch.object(health_monitor.server_manager, 'list_servers', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []
            
            status = await health_monitor.get_monitoring_status()
            
            assert status['service_status'] == 'stopped'
            assert status['total_servers'] == 0
            assert status['health_summary']['health_percentage'] == 100
            assert status['servers_with_errors'] == 0
    
    @pytest.mark.asyncio
    async def test_force_check_all_servers(self, health_monitor, mock_servers):
        """Test forcing health check of all servers."""
        with patch.object(health_monitor.server_manager, 'list_servers', new_callable=AsyncMock) as mock_list:
            with patch.object(health_monitor, '_perform_server_health_check', new_callable=AsyncMock) as mock_check:
                mock_list.return_value = mock_servers
                mock_check.side_effect = [
                    {'healthy': True},  # server1 success
                    {'healthy': False, 'error': 'Connection failed'}  # server2 failure
                ]
                
                result = await health_monitor.force_check_all_servers()
                
                assert result['total_servers'] == 2
                assert result['successful_checks'] == 1
                assert result['failed_checks'] == 1
                assert len(result['results']['successful']) == 1
                assert len(result['results']['failed']) == 1
                assert result['results']['successful'][0]['server_id'] == 'server1'
                assert result['results']['failed'][0]['server_id'] == 'server2'
    
    @pytest.mark.asyncio
    async def test_force_check_all_servers_no_servers(self, health_monitor):
        """Test forcing health check with no servers."""
        with patch.object(health_monitor.server_manager, 'list_servers', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []
            
            result = await health_monitor.force_check_all_servers()
            
            assert result['total_servers'] == 0
            assert result['summary'] == 'No servers to check'
    
    @pytest.mark.asyncio
    async def test_force_check_all_servers_with_exception(self, health_monitor, mock_servers):
        """Test forcing health check with exception during check."""
        with patch.object(health_monitor.server_manager, 'list_servers', new_callable=AsyncMock) as mock_list:
            with patch.object(health_monitor, '_perform_server_health_check', new_callable=AsyncMock) as mock_check:
                mock_list.return_value = mock_servers
                mock_check.side_effect = [
                    {'healthy': True},  # server1 success
                    Exception('Network error')  # server2 exception
                ]
                
                result = await health_monitor.force_check_all_servers()
                
                assert result['total_servers'] == 2
                assert result['successful_checks'] == 1
                assert result['failed_checks'] == 1
                assert result['results']['failed'][0]['error'] == 'Network error'


class TestHealthMonitoringServiceIntegration:
    """Integration tests for health monitoring service."""
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_integration(self):
        """Test the monitoring loop with mocked components."""
        mock_db_session = AsyncMock(spec=AsyncSession)
        health_monitor = HealthMonitoringService(mock_db_session)
        health_monitor._check_interval = 0.1  # Fast interval for testing
        
        check_count = 0
        
        async def mock_check_servers():
            nonlocal check_count
            check_count += 1
            if check_count >= 3:  # Stop after 3 checks
                health_monitor._is_running = False
        
        with patch.object(health_monitor, '_check_servers_health', side_effect=mock_check_servers):
            await health_monitor.start_monitoring()
            
            # Wait for monitoring to complete
            if health_monitor._monitoring_task:
                try:
                    await health_monitor._monitoring_task
                except asyncio.CancelledError:
                    pass
        
        assert check_count == 3
        assert not health_monitor._is_running