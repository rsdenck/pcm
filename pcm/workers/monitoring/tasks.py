from pcm.workers.celery_app import celery_app
import asyncio


@celery_app.task(name="collect_metrics")
def collect_metrics(cluster_id: str):
    """
    Coleta métricas do cluster
    """
    return asyncio.run(_collect_metrics_async(cluster_id))


async def _collect_metrics_async(cluster_id: str):
    return {
        "status": "success",
        "cluster_id": cluster_id,
        "metrics": {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "storage_usage": 0.0
        }
    }


@celery_app.task(name="health_check_nodes")
def health_check_nodes(cluster_id: str):
    """
    Verifica saúde dos nodes
    """
    return asyncio.run(_health_check_nodes_async(cluster_id))


async def _health_check_nodes_async(cluster_id: str):
    return {
        "status": "success",
        "cluster_id": cluster_id,
        "nodes_status": []
    }
