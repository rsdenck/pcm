"""
Unit tests for PBS Server Manager.

Tests server registration, health monitoring, and management operations.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
from pcm.core.models.backup.datastore import Datastore, DatastoreStatus
from pcm.services.backup.pbs_server_manager import (
    PBSServerManager,
    PBSServerManagerError,
    PBSServerRegistrationError
)
from pcm.services.backup.pbs_client import PBSConnectionError, PBSAuthenticationError


class TestPBSServerManager:
    """Test cases for PBSServerManager."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        session.execute = AsyncMock()
        return session
    
    @pytest.fixture
    def server_manager(self, mock_db_session):
        """Create PBSServerManager instance."""
        return PBSServerManager(mock_db_session)
    
    @pytest.fixture
    def sample_server_data(self):
        """Sample server registration data."""
        return {
            'name': 'test-pbs-01',
            'hostname': 'pbs.example.com',
            'api_token_id': 'test-token-id',
            'api_token_secret': 'test-token-secret',
            'datacenter': 'dc1',
            'port': 8007,
            'verify_ssl': True,
            'timeout': 30,
            'description': 'Test PBS server'
        }
    
    @pytest.mark.asyncio
    async def test_register_server_success(self, server_manager, sample_server_data):
        """Test successful server registration."""
        # Mock successful health check
        mock_health_result = {
            'healthy': True,
            'version': {'version': '2.4.0'},
            'status': {'uptime': 12345},
            'datastores': []
        }
        
        with patch('pcm.services.backup.pbs_server_manager.PBSAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.health_check.return_value = mock_health_result
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock start health monitoring
            with patch.object(server_manager, '_start_health_monitoring', new_callable=AsyncMock):
                server = await server_manager.register_server(**sample_server_data)
        
        # Verify server properties
        assert server.name == sample_server_data['name']
        assert server.hostname == sample_server_data['hostname']
        assert server.status == ServerStatus.ONLINE
        assert server.version == '2.4.0'
        
        # Verify database operations
        server_manager.db_session.add.assert_called_once()
        server_manager.db_session.flush.assert_called_once()
        server_manager.db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_server_connection_failure(self, server_manager, sample_server_data):
        """Test server registration with connection failure."""
        with patch('pcm.services.backup.pbs_server_manager.PBSAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.health_check.side_effect = PBSConnectionError("Connection failed")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(PBSServerRegistrationError, match="Failed to validate PBS server"):
                await server_manager.register_server(**sample_server_data)
    
    @pytest.mark.asyncio
    async def test_register_server_authentication_failure(self, server_manager, sample_server_data):
        """Test server registration with authentication failure."""
        with patch('pcm.services.backup.pbs_server_manager.PBSAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.health_check.side_effect = PBSAuthenticationError("Auth failed")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(PBSServerRegistrationError, match="Failed to validate PBS server"):
                await server_manager.register_server(**sample_server_data)
    
    @pytest.mark.asyncio
    async def test_register_server_validation_failure(self, server_manager, sample_server_data):
        """Test server registration with validation failure."""
        mock_health_result = {
            'healthy': False,
            'error': 'Server not responding'
        }
        
        with patch('pcm.services.backup.pbs_server_manager.PBSAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.health_check.return_value = mock_health_result
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(PBSServerRegistrationError, match="Server validation failed"):
                await server_manager.register_server(**sample_server_data)
    
    @pytest.mark.asyncio
    async def test_unregister_server_success(self, server_manager):
        """Test successful server unregistration."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.name = "test-server"
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_server
        server_manager.db_session.execute.return_value = mock_result
        
        # Mock stop health monitoring
        with patch.object(server_manager, '_stop_health_monitoring', new_callable=AsyncMock):
            result = await server_manager.unregister_server(server_id)
        
        assert result is True
        server_manager.db_session.delete.assert_called_once_with(mock_server)
    
    @pytest.mark.asyncio
    async def test_unregister_server_not_found(self, server_manager):
        """Test unregistering non-existent server."""
        server_id = "non-existent-server"
        
        # Mock database query returning None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        server_manager.db_session.execute.return_value = mock_result
        
        with patch.object(server_manager, '_stop_health_monitoring', new_callable=AsyncMock):
            result = await server_manager.unregister_server(server_id)
        
        assert result is False
        server_manager.db_session.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_perform_health_check_success(self, server_manager):
        """Test successful health check."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.name = "test-server"
        mock_server.datastores = []
        
        # Mock get_server
        with patch.object(server_manager, 'get_server', return_value=mock_server):
            mock_health_result = {
                'healthy': True,
                'version': {'version': '2.4.0'},
                'datastores': []
            }
            
            with patch('pcm.services.backup.pbs_server_manager.PBSAPIClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.health_check.return_value = mock_health_result
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                result = await server_manager.perform_health_check(server_id)
        
        assert result['healthy'] is True
        mock_server.mark_online.assert_called_once()
        server_manager.db_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_perform_health_check_failure(self, server_manager):
        """Test health check failure."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.name = "test-server"
        
        # Mock get_server
        with patch.object(server_manager, 'get_server', return_value=mock_server):
            with patch('pcm.services.backup.pbs_server_manager.PBSAPIClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.health_check.side_effect = Exception("Connection error")
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                result = await server_manager.perform_health_check(server_id)
        
        assert result['healthy'] is False
        assert 'Connection error' in result['error']
        mock_server.mark_offline.assert_called_once()
        server_manager.db_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_perform_health_check_server_not_found(self, server_manager):
        """Test health check for non-existent server."""
        server_id = "non-existent-server"
        
        with patch.object(server_manager, 'get_server', return_value=None):
            with pytest.raises(PBSServerManagerError, match="Server .* not found"):
                await server_manager.perform_health_check(server_id)
    
    @pytest.mark.asyncio
    async def test_get_server_statistics(self, server_manager):
        """Test getting server statistics."""
        server_id = "test-server-id"
        
        # Create mock server with datastores
        mock_server = MagicMock(spec=PBSServer)
        mock_server.id = server_id
        mock_server.name = "test-server"
        mock_server.status = ServerStatus.ONLINE
        mock_server.version = "2.4.0"
        mock_server.datacenter = "dc1"
        mock_server.last_health_check = datetime.utcnow()
        mock_server.error_count = 0
        mock_server.created_at = datetime.utcnow() - timedelta(days=30)
        mock_server.is_healthy = True
        
        # Mock datastores
        mock_datastore1 = MagicMock(spec=Datastore)
        mock_datastore1.status = DatastoreStatus.ACTIVE
        mock_datastore1.total_capacity = 1000000
        mock_datastore1.used_capacity = 500000
        
        mock_datastore2 = MagicMock(spec=Datastore)
        mock_datastore2.status = DatastoreStatus.ACTIVE
        mock_datastore2.total_capacity = 2000000
        mock_datastore2.used_capacity = 1000000
        
        mock_server.datastores = [mock_datastore1, mock_datastore2]
        
        with patch.object(server_manager, 'get_server', return_value=mock_server):
            stats = await server_manager.get_server_statistics(server_id)
        
        assert stats['server_id'] == server_id
        assert stats['server_name'] == "test-server"
        assert stats['status'] == ServerStatus.ONLINE.value
        assert stats['datastores']['total'] == 2
        assert stats['datastores']['active'] == 2
        assert stats['datastores']['total_capacity'] == 3000000
        assert stats['datastores']['used_capacity'] == 1500000
        assert stats['datastores']['usage_percentage'] == 50.0
        assert stats['uptime_days'] == 30
        assert stats['is_healthy'] is True
    
    @pytest.mark.asyncio
    async def test_cleanup(self, server_manager):
        """Test cleanup of server manager resources."""
        # Mock some running health monitoring tasks
        server_manager._health_check_tasks = {
            'server1': AsyncMock(),
            'server2': AsyncMock()
        }
        
        with patch.object(server_manager, '_stop_health_monitoring', new_callable=AsyncMock) as mock_stop:
            await server_manager.cleanup()
        
        # Verify all monitoring tasks were stopped
        assert mock_stop.call_count == 2
        mock_stop.assert_any_call('server1')
        mock_stop.assert_any_call('server2')


class TestPBSServerManagerIntegration:
    """Integration tests for PBS server manager with datastore updates."""
    
    @pytest.mark.asyncio
    async def test_update_datastore_info(self):
        """Test updating datastore information from PBS."""
        mock_db_session = AsyncMock(spec=AsyncSession)
        server_manager = PBSServerManager(mock_db_session)
        
        # Create mock server with datastore
        mock_server = MagicMock(spec=PBSServer)
        mock_datastore = MagicMock(spec=Datastore)
        mock_datastore.name = "backup-store"
        mock_server.datastores = [mock_datastore]
        
        # Mock datastore info from PBS
        datastore_list = [
            {
                'store': 'backup-store',
                'total': 1000000,
                'used': 500000,
                'avail': 500000
            }
        ]
        
        await server_manager._update_datastore_info(mock_server, datastore_list)
        
        # Verify datastore was updated
        mock_datastore.update_capacity.assert_called_once_with(1000000, 500000, 500000)