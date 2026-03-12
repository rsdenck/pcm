"""
PBS API Client for communicating with Proxmox Backup Server instances.

This module provides a client for interacting with PBS servers, including
authentication, health checks, and datastore management operations.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from urllib.parse import urljoin

from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus


logger = logging.getLogger(__name__)


class PBSClientError(Exception):
    """Base exception for PBS client errors."""
    pass


class PBSAuthenticationError(PBSClientError):
    """Raised when PBS authentication fails."""
    pass


class PBSConnectionError(PBSClientError):
    """Raised when PBS connection fails."""
    pass


class PBSAPIClient:
    """
    Asynchronous client for Proxmox Backup Server API.
    
    Provides methods for server communication, health checks,
    and datastore management operations.
    """
    
    def __init__(self, pbs_server: PBSServer):
        """
        Initialize PBS API client.
        
        Args:
            pbs_server: PBSServer model instance with connection details
        """
        self.pbs_server = pbs_server
        self.base_url = pbs_server.connection_url
        self.api_token_id = pbs_server.api_token_id
        self.api_token_secret = pbs_server.api_token_secret
        self.verify_ssl = pbs_server.verify_ssl
        self.timeout = pbs_server.timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
    
    async def _create_session(self) -> None:
        """Create aiohttp session with proper configuration."""
        connector = aiohttp.TCPConnector(
            verify_ssl=self.verify_ssl,
            limit=10,
            limit_per_host=5
        )
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        headers = {
            'Authorization': f'PBSAPIToken={self.api_token_id}:{self.api_token_secret}',
            'Content-Type': 'application/json'
        }
        
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
    
    async def _close_session(self) -> None:
        """Close aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to PBS API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            API response data
            
        Raises:
            PBSConnectionError: If connection fails
            PBSAuthenticationError: If authentication fails
            PBSClientError: For other API errors
        """
        if not self._session:
            await self._create_session()
        
        url = urljoin(self.base_url, f"/api2/json/{endpoint.lstrip('/')}")
        
        try:
            async with self._session.request(
                method=method,
                url=url,
                params=params,
                json=data
            ) as response:
                
                if response.status == 401:
                    raise PBSAuthenticationError(
                        f"Authentication failed for PBS server {self.pbs_server.name}"
                    )
                
                if response.status >= 400:
                    error_text = await response.text()
                    raise PBSClientError(
                        f"PBS API error {response.status}: {error_text}"
                    )
                
                response_data = await response.json()
                return response_data.get('data', {})
                
        except aiohttp.ClientError as e:
            raise PBSConnectionError(
                f"Connection failed to PBS server {self.pbs_server.name}: {str(e)}"
            ) from e
        except asyncio.TimeoutError as e:
            raise PBSConnectionError(
                f"Timeout connecting to PBS server {self.pbs_server.name}"
            ) from e
    
    async def get_version(self) -> Dict[str, Any]:
        """
        Get PBS server version information.
        
        Returns:
            Version information including version string and capabilities
        """
        return await self._request('GET', 'version')
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get PBS server status information.
        
        Returns:
            Server status including uptime, memory, and disk usage
        """
        return await self._request('GET', 'nodes/localhost/status')
    
    async def list_datastores(self) -> List[Dict[str, Any]]:
        """
        List all datastores on the PBS server.
        
        Returns:
            List of datastore information
        """
        response = await self._request('GET', 'admin/datastore')
        return response if isinstance(response, list) else []
    
    async def get_datastore_status(self, datastore_name: str) -> Dict[str, Any]:
        """
        Get status information for a specific datastore.
        
        Args:
            datastore_name: Name of the datastore
            
        Returns:
            Datastore status including capacity and usage
        """
        return await self._request('GET', f'admin/datastore/{datastore_name}/status')
    
    async def create_datastore(
        self, 
        name: str, 
        path: str, 
        **options
    ) -> Dict[str, Any]:
        """
        Create a new datastore on the PBS server.
        
        Args:
            name: Datastore name
            path: Storage path
            **options: Additional datastore options
            
        Returns:
            Creation result
        """
        data = {
            'name': name,
            'path': path,
            **options
        }
        return await self._request('POST', 'config/datastore', data=data)
    
    async def delete_datastore(self, name: str) -> Dict[str, Any]:
        """
        Delete a datastore from the PBS server.
        
        Args:
            name: Datastore name
            
        Returns:
            Deletion result
        """
        return await self._request('DELETE', f'config/datastore/{name}')
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of the PBS server.
        
        Returns:
            Health check results including version, status, and datastores
        """
        try:
            # Get version and basic status
            version_info = await self.get_version()
            status_info = await self.get_status()
            datastores = await self.list_datastores()
            
            return {
                'healthy': True,
                'version': version_info,
                'status': status_info,
                'datastores': datastores,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed for PBS server {self.pbs_server.name}: {e}")
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }