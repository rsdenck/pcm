from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from pcm.core.models import ProxmoxCluster, ProxmoxNode, Storage, VirtualMachine
from pcm.core.models.cluster import ClusterStatus
from pcm.core.models.storage import StorageType, StorageStatus
from pcm.core.models.vm import VMType, VMStatus
from pcm.sdk.proxmox import ProxmoxClient
from datetime import datetime


class ClusterService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """Sincroniza dados do cluster Proxmox"""
        result = await self.db.execute(
            select(ProxmoxCluster).where(ProxmoxCluster.id == cluster_id)
        )
        cluster = result.scalar_one_or_none()
        
        if not cluster:
            raise ValueError(f"Cluster {cluster_id} not found")

        client = ProxmoxClient(
            host=cluster.hostname,
            port=cluster.port,
            token_id=cluster.api_token_id,
            token_secret=cluster.api_token_secret,
            verify_ssl=cluster.verify_ssl,
        )

        try:
            # Verificar conexão
            await client.get_version()
            cluster.status = ClusterStatus.ONLINE
            
            # Sincronizar nodes
            await self._sync_nodes(cluster, client)
            
            # Sincronizar storage
            await self._sync_storage(cluster, client)
            
            # Sincronizar VMs
            await self._sync_vms(cluster, client)
            
            cluster.last_sync = datetime.utcnow()
            await self.db.commit()
            
            return {
                "status": "success",
                "cluster_id": cluster_id,
                "last_sync": cluster.last_sync.isoformat()
            }
            
        except Exception as e:
            cluster.status = ClusterStatus.OFFLINE
            await self.db.commit()
            raise Exception(f"Failed to sync cluster: {str(e)}")

    async def _sync_nodes(self, cluster: ProxmoxCluster, client: ProxmoxClient):
        """Sincroniza nodes do cluster"""
        nodes_data = await client.get_nodes()
        
        for node_info in nodes_data.get("data", []):
            node_name = node_info.get("node")
            
            # Buscar node existente
            result = await self.db.execute(
                select(ProxmoxNode).where(
                    ProxmoxNode.cluster_id == cluster.id,
                    ProxmoxNode.node_id == node_name
                )
            )
            node = result.scalar_one_or_none()
            
            # Obter status detalhado do node
            try:
                node_status = await client.get_node_status(node_name)
                node_data = node_status.get("data", {})
                
                if not node:
                    # Criar novo node
                    node = ProxmoxNode(
                        name=node_name,
                        node_id=node_name,
                        cluster_id=cluster.id,
                        status=node_info.get("status", "unknown"),
                        uptime=node_data.get("uptime"),
                        cpu_cores=node_data.get("cpuinfo", {}).get("cpus"),
                        cpu_usage=node_data.get("cpu"),
                        memory_total=node_data.get("memory", {}).get("total"),
                        memory_used=node_data.get("memory", {}).get("used"),
                    )
                    self.db.add(node)
                else:
                    # Atualizar node existente
                    node.status = node_info.get("status", "unknown")
                    node.uptime = node_data.get("uptime")
                    node.cpu_cores = node_data.get("cpuinfo", {}).get("cpus")
                    node.cpu_usage = node_data.get("cpu")
                    node.memory_total = node_data.get("memory", {}).get("total")
                    node.memory_used = node_data.get("memory", {}).get("used")
                    
            except Exception as e:
                print(f"Error syncing node {node_name}: {str(e)}")
                continue

    async def _sync_storage(self, cluster: ProxmoxCluster, client: ProxmoxClient):
        """Sincroniza storage do cluster"""
        nodes_data = await client.get_nodes()
        
        for node_info in nodes_data.get("data", []):
            node_name = node_info.get("node")
            
            try:
                storage_data = await client.get_storage(node_name)
                
                for storage_info in storage_data.get("data", []):
                    storage_id = storage_info.get("storage")
                    
                    # Buscar storage existente
                    result = await self.db.execute(
                        select(Storage).where(
                            Storage.cluster_id == cluster.id,
                            Storage.storage_id == storage_id
                        )
                    )
                    storage = result.scalar_one_or_none()
                    
                    status = StorageStatus.AVAILABLE if storage_info.get("active") else StorageStatus.UNAVAILABLE
                    
                    if not storage:
                        # Criar novo storage
                        storage = Storage(
                            storage_id=storage_id,
                            name=storage_id,
                            storage_type=StorageType(storage_info.get("type", "dir")),
                            status=status,
                            total=storage_info.get("total"),
                            used=storage_info.get("used"),
                            available=storage_info.get("avail"),
                            enabled=storage_info.get("enabled", True),
                            shared=storage_info.get("shared", False),
                            cluster_id=cluster.id
                        )
                        self.db.add(storage)
                    else:
                        # Atualizar storage existente
                        storage.status = status
                        storage.total = storage_info.get("total")
                        storage.used = storage_info.get("used")
                        storage.available = storage_info.get("avail")
                        
            except Exception as e:
                print(f"Error syncing storage for node {node_name}: {str(e)}")
                continue

    async def _sync_vms(self, cluster: ProxmoxCluster, client: ProxmoxClient):
        """Sincroniza VMs do cluster"""
        nodes_data = await client.get_nodes()
        
        for node_info in nodes_data.get("data", []):
            node_name = node_info.get("node")
            
            # Buscar node no banco
            result = await self.db.execute(
                select(ProxmoxNode).where(
                    ProxmoxNode.cluster_id == cluster.id,
                    ProxmoxNode.node_id == node_name
                )
            )
            node = result.scalar_one_or_none()
            
            if not node:
                continue
            
            try:
                # Sincronizar VMs QEMU
                vms_data = await client.get_vms(node_name)
                for vm_info in vms_data.get("data", []):
                    await self._sync_vm(node, vm_info, VMType.QEMU)
                
                # Sincronizar Containers LXC
                containers_data = await client.get_containers(node_name)
                for container_info in containers_data.get("data", []):
                    await self._sync_vm(node, container_info, VMType.LXC)
                    
            except Exception as e:
                print(f"Error syncing VMs for node {node_name}: {str(e)}")
                continue

    async def _sync_vm(self, node: ProxmoxNode, vm_info: Dict[str, Any], vm_type: VMType):
        """Sincroniza uma VM específica"""
        vmid = vm_info.get("vmid")
        
        # Buscar VM existente
        result = await self.db.execute(
            select(VirtualMachine).where(
                VirtualMachine.node_id == node.id,
                VirtualMachine.vmid == vmid
            )
        )
        vm = result.scalar_one_or_none()
        
        status_map = {
            "running": VMStatus.RUNNING,
            "stopped": VMStatus.STOPPED,
            "paused": VMStatus.PAUSED,
        }
        status = status_map.get(vm_info.get("status", "unknown"), VMStatus.UNKNOWN)
        
        if not vm:
            # Criar nova VM
            vm = VirtualMachine(
                vmid=vmid,
                name=vm_info.get("name", f"VM-{vmid}"),
                vm_type=vm_type,
                status=status,
                cpu_cores=vm_info.get("cpus"),
                cpu_usage=vm_info.get("cpu"),
                memory_total=vm_info.get("maxmem"),
                memory_used=vm_info.get("mem"),
                disk_total=vm_info.get("maxdisk"),
                disk_used=vm_info.get("disk"),
                uptime=vm_info.get("uptime"),
                node_id=node.id,
                tenant_id=node.cluster.tenant_id
            )
            self.db.add(vm)
        else:
            # Atualizar VM existente
            vm.name = vm_info.get("name", vm.name)
            vm.status = status
            vm.cpu_cores = vm_info.get("cpus")
            vm.cpu_usage = vm_info.get("cpu")
            vm.memory_total = vm_info.get("maxmem")
            vm.memory_used = vm_info.get("mem")
            vm.disk_total = vm_info.get("maxdisk")
            vm.disk_used = vm_info.get("disk")
            vm.uptime = vm_info.get("uptime")

    async def get_cluster_stats(self, cluster_id: str) -> Dict[str, Any]:
        """Obtém estatísticas do cluster"""
        # Contar nodes
        nodes_result = await self.db.execute(
            select(ProxmoxNode).where(ProxmoxNode.cluster_id == cluster_id)
        )
        nodes = nodes_result.scalars().all()
        
        # Contar VMs
        vms_result = await self.db.execute(
            select(VirtualMachine).join(ProxmoxNode).where(
                ProxmoxNode.cluster_id == cluster_id
            )
        )
        vms = vms_result.scalars().all()
        
        # Contar storage
        storage_result = await self.db.execute(
            select(Storage).where(Storage.cluster_id == cluster_id)
        )
        storage = storage_result.scalars().all()
        
        return {
            "total_nodes": len(nodes),
            "online_nodes": len([n for n in nodes if n.status == "online"]),
            "total_vms": len([v for v in vms if v.vm_type == VMType.QEMU]),
            "total_containers": len([v for v in vms if v.vm_type == VMType.LXC]),
            "running_vms": len([v for v in vms if v.status == VMStatus.RUNNING]),
            "total_storage": len(storage),
            "available_storage": len([s for s in storage if s.status == StorageStatus.AVAILABLE])
        }
