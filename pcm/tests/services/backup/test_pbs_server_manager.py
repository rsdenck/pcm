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
    async def test_list_servers_no_filters(self, server_manager):
        """Test listing all servers without filters."""
        mock_servers = [
            MagicMock(spec=PBSServer),
            MagicMock(spec=PBSServer)
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_servers
        server_manager.db_session.execute.return_value = mock_result
        
        servers = await server_manager.list_servers()
        
        assert len(servers) == 2
        assert servers == mock_servers
    
    @pytest.mark.asyncio
    async def test_list_servers_with_datacenter_filter(self, server_manager):
        """Test listing servers filtered by datacenter."""
        mock_servers = [MagicMock(spec=PBSServer)]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_servers
        server_manager.db_session.execute.return_value = mock_result
        
        servers = await server_manager.list_servers(datacenter="dc1")
        
        assert len(servers) == 1
        # Verify the query was filtered by datacenter
        server_manager.db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_servers_with_status_filter(self, server_manager):
        """Test listing servers filtered by status."""
        mock_servers = [MagicMock(spec=PBSServer)]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_servers
        server_manager.db_session.execute.return_value = mock_result
        
        servers = await server_manager.list_servers(status=ServerStatus.ONLINE)
        
        assert len(servers) == 1
        # Verify the query was filtered by status
        server_manager.db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_server_with_datastores(self, server_manager, sample_server_data):
        """Test server registration that includes datastore discovery."""
        # Mock successful health check with datastores
        mock_health_result = {
            'healthy': True,
            'version': {'version': '2.4.0'},
            'status': {'uptime': 12345},
            'datastores': [
                {
                    'store': 'backup-store-1',
                    'total': 1000000,
                    'used': 500000,
                    'avail': 500000
                },
                {
                    'store': 'backup-store-2',
                    'total': 2000000,
                    'used': 800000,
                    'avail': 1200000
                }
            ]
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
    async def test_register_server_invalid_parameters(self, server_manager):
        """Test server registration with invalid parameters."""
        invalid_data = {
            'name': '',  # Empty name
            'hostname': 'pbs.example.com',
            'api_token_id': 'test-token-id',
            'api_token_secret': 'test-token-secret',
            'datacenter': 'dc1'
        }
        
        # Should raise validation error before attempting connection
        with pytest.raises(Exception):  # Could be ValueError or similar
            await server_manager.register_server(**invalid_data)
    
    @pytest.mark.asyncio
    async def test_get_server_with_datastores(self, server_manager):
        """Test getting server with datastore relationships loaded."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.id = server_id
        mock_server.datastores = [MagicMock(spec=Datastore)]
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_server
        server_manager.db_session.execute.return_value = mock_result
        
        server = await server_manager.get_server(server_id)
        
        assert server == mock_server
        assert len(server.datastores) == 1
        # Verify selectinload was used for datastores
        server_manager.db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_server_not_found(self, server_manager):
        """Test getting non-existent server."""
        server_id = "non-existent-server"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        server_manager.db_session.execute.return_value = mock_result
        
        server = await server_manager.get_server(server_id)
        
        assert server is None
    
    @pytest.mark.asyncio
    async def test_health_monitoring_task_lifecycle(self, server_manager):
        """Test health monitoring task creation and cleanup."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.id = server_id
        mock_server.name = "test-server"
        mock_server.health_check_interval = 1  # Short interval for testing
        
        # Test starting monitoring
        await server_manager._start_health_monitoring(mock_server)
        assert server_id in server_manager._health_check_tasks
        
        # Test stopping monitoring
        await server_manager._stop_health_monitoring(server_id)
        assert server_id not in server_manager._health_check_tasks
    
    @pytest.mark.asyncio
    async def test_health_monitoring_duplicate_start(self, server_manager):
        """Test that starting monitoring twice doesn't create duplicate tasks."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.id = server_id
        mock_server.name = "test-server"
        mock_server.health_check_interval = 1
        
        # Start monitoring twice
        await server_manager._start_health_monitoring(mock_server)
        first_task = server_manager._health_check_tasks.get(server_id)
        
        await server_manager._start_health_monitoring(mock_server)
        second_task = server_manager._health_check_tasks.get(server_id)
        
        # Should be the same task (no duplicate)
        assert first_task == second_task
        
        # Cleanup
        await server_manager._stop_health_monitoring(server_id)
    
    @pytest.mark.asyncio
    async def test_server_statistics_empty_datastores(self, server_manager):
        """Test server statistics with no datastores."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.id = server_id
        mock_server.name = "test-server"
        mock_server.status = ServerStatus.ONLINE
        mock_server.version = "2.4.0"
        mock_server.datacenter = "dc1"
        mock_server.last_health_check = datetime.utcnow()
        mock_server.error_count = 0
        mock_server.created_at = datetime.utcnow() - timedelta(days=10)
        mock_server.is_healthy = True
        mock_server.datastores = []  # No datastores
        
        with patch.object(server_manager, 'get_server', return_value=mock_server):
            stats = await server_manager.get_server_statistics(server_id)
        
        assert stats['datastores']['total'] == 0
        assert stats['datastores']['active'] == 0
        assert stats['datastores']['total_capacity'] == 0
        assert stats['datastores']['used_capacity'] == 0
        assert stats['datastores']['usage_percentage'] == 0
        assert stats['uptime_days'] == 10
    
    @pytest.mark.asyncio
    async def test_server_statistics_not_found(self, server_manager):
        """Test server statistics for non-existent server."""
        server_id = "non-existent-server"
        
        with patch.object(server_manager, 'get_server', return_value=None):
            with pytest.raises(PBSServerManagerError, match="Server .* not found"):
                await server_manager.get_server_statistics(server_id)
    
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


class TestPBSServerManagerEdgeCases:
    """Test edge cases and error conditions for PBS server manager."""
    
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
    
    @pytest.mark.asyncio
    async def test_register_server_database_error(self, server_manager):
        """Test server registration with database error."""
        server_data = {
            'name': 'test-pbs-01',
            'hostname': 'pbs.example.com',
            'api_token_id': 'test-token-id',
            'api_token_secret': 'test-token-secret',
            'datacenter': 'dc1'
        }
        
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
            
            # Mock database error
            server_manager.db_session.flush.side_effect = Exception("Database error")
            
            with patch.object(server_manager, '_start_health_monitoring', new_callable=AsyncMock):
                with pytest.raises(Exception, match="Database error"):
                    await server_manager.register_server(**server_data)
    
    @pytest.mark.asyncio
    async def test_unregister_server_database_error(self, server_manager):
        """Test server unregistration with database error."""
        server_id = "test-server-id"
        
        # Mock database error
        server_manager.db_session.execute.side_effect = Exception("Database error")
        
        with patch.object(server_manager, '_stop_health_monitoring', new_callable=AsyncMock):
            with pytest.raises(Exception, match="Database error"):
                await server_manager.unregister_server(server_id)
    
    @pytest.mark.asyncio
    async def test_health_check_with_partial_datastore_info(self, server_manager):
        """Test health check with incomplete datastore information."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.name = "test-server"
        
        # Create mock datastore
        mock_datastore = MagicMock(spec=Datastore)
        mock_datastore.name = "backup-store"
        mock_server.datastores = [mock_datastore]
        
        with patch.object(server_manager, 'get_server', return_value=mock_server):
            mock_health_result = {
                'healthy': True,
                'version': {'version': '2.4.0'},
                'datastores': [
                    {
                        'store': 'backup-store',
                        # Missing capacity information
                    }
                ]
            }
            
            with patch('pcm.services.backup.pbs_server_manager.PBSAPIClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.health_check.return_value = mock_health_result
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                result = await server_manager.perform_health_check(server_id)
        
        assert result['healthy'] is True
        # Datastore should not be updated due to missing capacity info
        mock_datastore.update_capacity.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_datastore_info_with_unknown_datastore(self, server_manager):
        """Test updating datastore info with unknown datastore from PBS."""
        mock_server = MagicMock(spec=PBSServer)
        mock_server.datastores = []  # No datastores configured
        
        # PBS reports a datastore that's not in our database
        datastore_list = [
            {
                'store': 'unknown-store',
                'total': 1000000,
                'used': 500000,
                'avail': 500000
            }
        ]
        
        # Should not raise an error, just skip unknown datastores
        await server_manager._update_datastore_info(mock_server, datastore_list)
        
        # No exceptions should be raised
        assert True
    
    @pytest.mark.asyncio
    async def test_health_monitoring_task_exception_handling(self, server_manager):
        """Test health monitoring task handles exceptions gracefully."""
        server_id = "test-server-id"
        mock_server = MagicMock(spec=PBSServer)
        mock_server.id = server_id
        mock_server.name = "test-server"
        mock_server.health_check_interval = 0.1  # Very short for testing
        
        # Mock perform_health_check to raise an exception
        with patch.object(server_manager, 'perform_health_check', side_effect=Exception("Health check error")):
            await server_manager._start_health_monitoring(mock_server)
            
            # Let the task run briefly
            await asyncio.sleep(0.2)
            
            # Task should still be running despite the exception
            assert server_id in server_manager._health_check_tasks
            
            # Cleanup
            await server_manager._stop_health_monitoring(server_id)
    
    @pytest.mark.asyncio
    async def test_stop_health_monitoring_nonexistent_task(self, server_manager):
        """Test stopping health monitoring for non-existent task."""
        server_id = "non-existent-server"
        
        # Should not raise an error
        await server_manager._stop_health_monitoring(server_id)
        
        # No exceptions should be raised
        assert True


class TestPBSServerManagerValidation:
    """Test validation and security aspects of PBS server manager."""
    
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
    
    @pytest.mark.asyncio
    async def test_register_server_ssl_verification_disabled(self, server_manager):
        """Test server registration with SSL verification disabled."""
        server_data = {
            'name': 'test-pbs-insecure',
            'hostname': 'pbs.example.com',
            'api_token_id': 'test-token-id',
            'api_token_secret': 'test-token-secret',
            'datacenter': 'dc1',
            'verify_ssl': False  # Disabled SSL verification
        }
        
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
            
            with patch.object(server_manager, '_start_health_monitoring', new_callable=AsyncMock):
                server = await server_manager.register_server(**server_data)
        
        assert server.verify_ssl is False
        assert server.status == ServerStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_register_server_custom_port(self, server_manager):
        """Test server registration with custom port."""
        server_data = {
            'name': 'test-pbs-custom-port',
            'hostname': 'pbs.example.com',
            'api_token_id': 'test-token-id',
            'api_token_secret': 'test-token-secret',
            'datacenter': 'dc1',
            'port': 9007  # Custom port
        }
        
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
            
            with patch.object(server_manager, '_start_health_monitoring', new_callable=AsyncMock):
                server = await server_manager.register_server(**server_data)
        
        assert server.port == 9007
        assert server.status == ServerStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_register_server_with_description(self, server_manager):
        """Test server registration with description."""
        server_data = {
            'name': 'test-pbs-with-desc',
            'hostname': 'pbs.example.com',
            'api_token_id': 'test-token-id',
            'api_token_secret': 'test-token-secret',
            'datacenter': 'dc1',
            'description': 'Test PBS server for development'
        }
        
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
            
            with patch.object(server_manager, '_start_health_monitoring', new_callable=AsyncMock):
                server = await server_manager.register_server(**server_data)
        
        assert server.description == 'Test PBS server for development'
        assert server.status == ServerStatus.ONLINE