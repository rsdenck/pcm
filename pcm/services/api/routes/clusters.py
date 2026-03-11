from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from pcm.core.database import get_db
from pcm.core.models import ProxmoxCluster, ClusterType, ClusterStatus
from pcm.sdk.proxmox import ProxmoxClient

router = APIRouter()


class ClusterCreate(BaseModel):
    name: str
    hostname: str
    port: int = 8006
    cluster_type: ClusterType = ClusterType.PVE
    api_token_id: str
    api_token_secret: str
    verify_ssl: bool = False
    description: str | None = None
    tenant_id: str


class ClusterResponse(BaseModel):
    id: str
    name: str
    hostname: str
    port: int
    cluster_type: ClusterType
    status: ClusterStatus
    description: str | None
    tenant_id: str
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ClusterResponse])
async def list_clusters(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProxmoxCluster))
    clusters = result.scalars().all()
    return clusters


@router.post("", response_model=ClusterResponse, status_code=status.HTTP_201_CREATED)
async def create_cluster(cluster_data: ClusterCreate, db: AsyncSession = Depends(get_db)):
    try:
        client = ProxmoxClient(
            host=cluster_data.hostname,
            port=cluster_data.port,
            token_id=cluster_data.api_token_id,
            token_secret=cluster_data.api_token_secret,
            verify_ssl=cluster_data.verify_ssl,
        )
        
        await client.get_version()
        initial_status = ClusterStatus.ONLINE
    except Exception:
        initial_status = ClusterStatus.OFFLINE
    
    cluster = ProxmoxCluster(
        **cluster_data.model_dump(),
        status=initial_status
    )
    db.add(cluster)
    await db.commit()
    await db.refresh(cluster)
    return cluster


@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(cluster_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProxmoxCluster).where(ProxmoxCluster.id == cluster_id))
    cluster = result.scalar_one_or_none()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found"
        )
    
    return cluster


@router.get("/{cluster_id}/nodes")
async def get_cluster_nodes(cluster_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProxmoxCluster).where(ProxmoxCluster.id == cluster_id))
    cluster = result.scalar_one_or_none()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found"
        )
    
    try:
        client = ProxmoxClient(
            host=cluster.hostname,
            port=cluster.port,
            token_id=cluster.api_token_id,
            token_secret=cluster.api_token_secret,
            verify_ssl=cluster.verify_ssl,
        )
        
        nodes_data = await client.get_nodes()
        return nodes_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to cluster: {str(e)}"
        )
