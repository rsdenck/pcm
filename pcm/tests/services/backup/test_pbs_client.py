"""
Unit tests for PBS API Client.

Tests PBS server communication, authentication, and API operations.
"""

import pytest
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
from pcm.services.backup.pbs_client import (
    PBSAPIClient,
    PBSClientError,
    PBSConnectionError,
    PBSAuthenticationError
)


class TestPBSAPIClient:
    """Test cases for PBSAPIClient."""
    
    @pytest.fixture
    def mock_pbs_server(self):
        """Create mock PBS server."""
        server = MagicMock(spec=PBSServer)
        server.connection_url = "https://pbs.example.com:8007"
        server.api_token_id = "test-token-id"
        server.api_token_secret = "test-token-secret"
        server.verify_ssl = True
        server.timeout = 30
        server.name = "test-pbs"
        return server
    
    @pytest.fixture
    def pbs_client(self, mock_pbs_server):
        """Create PBSAPIClient instance."""
        return PBSAPIClient(mock_pbs_server)
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, pbs_client, mock_pbs_server):
        """Test client initialization with server details."""
        assert pbs_client.pbs_server == mock_pbs_server
        assert pbs_client.base_url == "https://pbs.example.com:8007"
        assert pbs_client.api_token_id == "test-token-id"
        assert pbs_client.api_token_secret == "test-token-secret"
        assert pbs_client.verify_ssl is True
        assert pbs_client.timeout == 30
    
    @pytest.mark.asyncio
    async def test_context_manager(self, pbs_client):
        """Test async context manager functionality."""
        with patch.object(pbs_client, '_create_session', new_callable=AsyncMock) as mock_create:
            with patch.object(pbs_client, '_close_session', new_callable=AsyncMock) as mock_close:
                async with pbs_client as client:
                    assert client == pbs_client
                
                mock_create.assert_called_once()
                mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_session(self, pbs_client):
        """Test session creation with proper configuration."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            with patch('aiohttp.TCPConnector') as mock_connector_class:
                with patch('aiohttp.ClientTimeout') as mock_timeout_class:
                    mock_connector = MagicMock()
                    mock_timeout = MagicMock()
                    mock_session = MagicMock()
                    
                    mock_connector_class.return_value = mock_connector
                    mock_timeout_class.return_value = mock_timeout
                    mock_session_class.return_value = mock_session
                    
                    await pbs_client._create_session()
                    
                    # Verify connector configuration
                    mock_connector_class.assert_called_once_with(
                        verify_ssl=True,
                        limit=10,
                        limit_per_host=5
                    )
                    
                    # Verify timeout configuration
                    mock_timeout_class.assert_called_once_with(total=30)
                    
                    # Verify session creation
                    mock_session_class.assert_called_once()
                    call_kwargs = mock_session_class.call_args[1]
                    assert call_kwargs['connector'] == mock_connector
                    assert call_kwargs['timeout'] == mock_timeout
                    assert 'Authorization' in call_kwargs['headers']
                    assert call_kwargs['headers']['Authorization'] == 'PBSAPIToken=test-token-id:test-token-secret'
    
    @pytest.mark.asyncio
    async def test_request_success(self, pbs_client):
        """Test successful API request."""
        mock_response_data = {'data': {'version': '2.4.0'}}
        
        with patch.object(pbs_client, '_create_session', new_callable=AsyncMock):
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data
            mock_session.request.return_value.__aenter__.return_value = mock_response
            pbs_client._session = mock_session
            
            result = await pbs_client._request('GET', 'version')
            
            assert result == {'version': '2.4.0'}
            mock_session.request.assert_called_once_with(
                method='GET',
                url='https://pbs.example.com:8007/api2/json/version',
                params=None,
                json=None
            )
    
    @pytest.mark.asyncio
    async def test_request_authentication_error(self, pbs_client):
        """Test API request with authentication error."""
        with patch.object(pbs_client, '_create_session', new_callable=AsyncMock):
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_session.request.return_value.__aenter__.return_value = mock_response
            pbs_client._session = mock_session
            
            with pytest.raises(PBSAuthenticationError, match="Authentication failed"):
                await pbs_client._request('GET', 'version')
    
    @pytest.mark.asyncio
    async def test_request_client_error(self, pbs_client):
        """Test API request with client error."""
        with patch.object(pbs_client, '_create_session', new_callable=AsyncMock):
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text.return_value = "Internal Server Error"
            mock_session.request.return_value.__aenter__.return_value = mock_response
            pbs_client._session = mock_session
            
            with pytest.raises(PBSClientError, match="PBS API error 500"):
                await pbs_client._request('GET', 'version')
    
    @pytest.mark.asyncio
    async def test_request_connection_error(self, pbs_client):
        """Test API request with connection error."""
        with patch.object(pbs_client, '_create_session', new_callable=AsyncMock):
            mock_session = AsyncMock()
            mock_session.request.side_effect = aiohttp.ClientError("Connection failed")
            pbs_client._session = mock_session
            
            with pytest.raises(PBSConnectionError, match="Connection failed"):
                await pbs_client._request('GET', 'version')
    
    @pytest.mark.asyncio
    async def test_get_version(self, pbs_client):
        """Test getting PBS version information."""
        expected_version = {'version': '2.4.0', 'release': '1'}
        
        with patch.object(pbs_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_version
            
            result = await pbs_client.get_version()
            
            assert result == expected_version
            mock_request.assert_called_once_with('GET', 'version')
    
    @pytest.mark.asyncio
    async def test_get_status(self, pbs_client):
        """Test getting PBS status information."""
        expected_status = {'uptime': 12345, 'memory': {'total': 8000000}}
        
        with patch.object(pbs_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_status
            
            result = await pbs_client.get_status()
            
            assert result == expected_status
            mock_request.assert_called_once_with('GET', 'nodes/localhost/status')
    
    @pytest.mark.asyncio
    async def test_list_datastores(self, pbs_client):
        """Test listing datastores."""
        expected_datastores = [
            {'store': 'backup1', 'path': '/backup1'},
            {'store': 'backup2', 'path': '/backup2'}
        ]
        
        with patch.object(pbs_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_datastores
            
            result = await pbs_client.list_datastores()
            
            assert result == expected_datastores
            mock_request.assert_called_once_with('GET', 'admin/datastore')
    
    @pytest.mark.asyncio
    async def test_list_datastores_empty_response(self, pbs_client):
        """Test listing datastores with empty response."""
        with patch.object(pbs_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}  # Non-list response
            
            result = await pbs_client.list_datastores()
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_datastore_status(self, pbs_client):
        """Test getting datastore status."""
        datastore_name = "backup1"
        expected_status = {
            'total': 1000000,
            'used': 500000,
            'avail': 500000
        }
        
        with patch.object(pbs_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_status
            
            result = await pbs_client.get_datastore_status(datastore_name)
            
            assert result == expected_status
            mock_request.assert_called_once_with('GET', f'admin/datastore/{datastore_name}/status')
    
    @pytest.mark.asyncio
    async def test_create_datastore(self, pbs_client):
        """Test creating a datastore."""
        datastore_name = "new-backup"
        datastore_path = "/mnt/backup"
        options = {'compression': 'zstd'}
        expected_result = {'success': True}
        
        with patch.object(pbs_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await pbs_client.create_datastore(datastore_name, datastore_path, **options)
            
            assert result == expected_result
            mock_request.assert_called_once_with(
                'POST', 
                'config/datastore',
                data={
                    'name': datastore_name,
                    'path': datastore_path,
                    'compression': 'zstd'
                }
            )
    
    @pytest.mark.asyncio
    async def test_delete_datastore(self, pbs_client):
        """Test deleting a datastore."""
        datastore_name = "old-backup"
        expected_result = {'success': True}
        
        with patch.object(pbs_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = expected_result
            
            result = await pbs_client.delete_datastore(datastore_name)
            
            assert result == expected_result
            mock_request.assert_called_once_with('DELETE', f'config/datastore/{datastore_name}')
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, pbs_client):
        """Test successful health check."""
        version_info = {'version': '2.4.0'}
        status_info = {'uptime': 12345}
        datastores_info = [{'store': 'backup1'}]
        
        with patch.object(pbs_client, 'get_version', new_callable=AsyncMock) as mock_version:
            with patch.object(pbs_client, 'get_status', new_callable=AsyncMock) as mock_status:
                with patch.object(pbs_client, 'list_datastores', new_callable=AsyncMock) as mock_datastores:
                    mock_version.return_value = version_info
                    mock_status.return_value = status_info
                    mock_datastores.return_value = datastores_info
                    
                    result = await pbs_client.health_check()
                    
                    assert result['healthy'] is True
                    assert result['version'] == version_info
                    assert result['status'] == status_info
                    assert result['datastores'] == datastores_info
                    assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, pbs_client):
        """Test health check with failure."""
        with patch.object(pbs_client, 'get_version', new_callable=AsyncMock) as mock_version:
            mock_version.side_effect = PBSConnectionError("Connection failed")
            
            result = await pbs_client.health_check()
            
            assert result['healthy'] is False
            assert 'Connection failed' in result['error']
            assert 'timestamp' in result