import httpx
from typing import Any, Dict, Optional
from urllib.parse import urljoin


class ProxmoxClient:
    def __init__(
        self,
        host: str,
        port: int = 8006,
        token_id: str = "",
        token_secret: str = "",
        verify_ssl: bool = False,
        timeout: int = 30,
    ):
        self.base_url = f"https://{host}:{port}/api2/json"
        self.token_id = token_id
        self.token_secret = token_secret
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        
        self.headers = {
            "Authorization": f"PVEAPIToken={token_id}={token_secret}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url, endpoint)
        
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._request("POST", endpoint, data=data)

    async def put(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._request("PUT", endpoint, data=data)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        return await self._request("DELETE", endpoint)

    async def get_version(self) -> Dict[str, Any]:
        return await self.get("/version")

    async def get_cluster_status(self) -> Dict[str, Any]:
        return await self.get("/cluster/status")

    async def get_nodes(self) -> Dict[str, Any]:
        return await self.get("/nodes")

    async def get_node_status(self, node: str) -> Dict[str, Any]:
        return await self.get(f"/nodes/{node}/status")

    async def get_vms(self, node: str) -> Dict[str, Any]:
        return await self.get(f"/nodes/{node}/qemu")

    async def get_containers(self, node: str) -> Dict[str, Any]:
        return await self.get(f"/nodes/{node}/lxc")

    async def get_storage(self, node: str) -> Dict[str, Any]:
        return await self.get(f"/nodes/{node}/storage")
