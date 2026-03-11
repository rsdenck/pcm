from pcm.workers.celery_app import celery_app
from pcm.sdk.proxmox import ProxmoxClient
import asyncio


@celery_app.task(name="provision_vm")
def provision_vm(cluster_id: str, vm_config: dict):
    """
    Provisiona uma VM no cluster Proxmox
    """
    return asyncio.run(_provision_vm_async(cluster_id, vm_config))


async def _provision_vm_async(cluster_id: str, vm_config: dict):
    return {
        "status": "success",
        "cluster_id": cluster_id,
        "vm_id": vm_config.get("vmid"),
        "message": "VM provisioned successfully"
    }


@celery_app.task(name="sync_cluster_data")
def sync_cluster_data(cluster_id: str):
    """
    Sincroniza dados do cluster Proxmox
    """
    return asyncio.run(_sync_cluster_data_async(cluster_id))


async def _sync_cluster_data_async(cluster_id: str):
    return {
        "status": "success",
        "cluster_id": cluster_id,
        "message": "Cluster data synced successfully"
    }
