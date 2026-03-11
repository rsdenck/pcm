from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pcm.core.database import get_db
from pcm.core.models import ProxmoxCluster, ProxmoxNode, VirtualMachine, Tenant
from pcm.core.models.cluster import ClusterStatus
from pcm.core.models.vm import VMStatus, VMType

router = APIRouter()


@router.get("")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Retorna estatísticas gerais do dashboard"""
    
    # Total de clusters
    clusters_result = await db.execute(select(func.count(ProxmoxCluster.id)))
    total_clusters = clusters_result.scalar()
    
    # Clusters online
    online_clusters_result = await db.execute(
        select(func.count(ProxmoxCluster.id)).where(
            ProxmoxCluster.status == ClusterStatus.ONLINE
        )
    )
    online_clusters = online_clusters_result.scalar()
    
    # Total de nodes
    nodes_result = await db.execute(select(func.count(ProxmoxNode.id)))
    total_nodes = nodes_result.scalar()
    
    # Nodes online
    online_nodes_result = await db.execute(
        select(func.count(ProxmoxNode.id)).where(ProxmoxNode.status == "online")
    )
    online_nodes = online_nodes_result.scalar()
    
    # Total de VMs
    vms_result = await db.execute(
        select(func.count(VirtualMachine.id)).where(
            VirtualMachine.vm_type == VMType.QEMU
        )
    )
    total_vms = vms_result.scalar()
    
    # VMs rodando
    running_vms_result = await db.execute(
        select(func.count(VirtualMachine.id)).where(
            VirtualMachine.vm_type == VMType.QEMU,
            VirtualMachine.status == VMStatus.RUNNING
        )
    )
    running_vms = running_vms_result.scalar()
    
    # Total de containers
    containers_result = await db.execute(
        select(func.count(VirtualMachine.id)).where(
            VirtualMachine.vm_type == VMType.LXC
        )
    )
    total_containers = containers_result.scalar()
    
    # Containers rodando
    running_containers_result = await db.execute(
        select(func.count(VirtualMachine.id)).where(
            VirtualMachine.vm_type == VMType.LXC,
            VirtualMachine.status == VMStatus.RUNNING
        )
    )
    running_containers = running_containers_result.scalar()
    
    # Total de tenants
    tenants_result = await db.execute(select(func.count(Tenant.id)))
    total_tenants = tenants_result.scalar()
    
    # Clusters recentes
    recent_clusters_result = await db.execute(
        select(ProxmoxCluster).order_by(ProxmoxCluster.created_at.desc()).limit(5)
    )
    recent_clusters = recent_clusters_result.scalars().all()
    
    return {
        "stats": {
            "total_clusters": total_clusters or 0,
            "online_clusters": online_clusters or 0,
            "total_nodes": total_nodes or 0,
            "online_nodes": online_nodes or 0,
            "total_vms": total_vms or 0,
            "running_vms": running_vms or 0,
            "total_containers": total_containers or 0,
            "running_containers": running_containers or 0,
            "total_tenants": total_tenants or 0,
        },
        "clusters": [
            {
                "id": cluster.id,
                "name": cluster.name,
                "hostname": cluster.hostname,
                "port": cluster.port,
                "status": cluster.status.value,
                "cluster_type": cluster.cluster_type.value,
                "last_sync": cluster.last_sync.isoformat() if cluster.last_sync else None,
            }
            for cluster in recent_clusters
        ]
    }
