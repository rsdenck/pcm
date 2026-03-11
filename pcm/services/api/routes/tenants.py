from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from pcm.core.database import get_db
from pcm.core.models import Tenant

router = APIRouter()


class TenantCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[TenantResponse])
async def list_tenants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).where(Tenant.is_active == True))
    tenants = result.scalars().all()
    return tenants


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(tenant_data: TenantCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).where(Tenant.slug == tenant_data.slug))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this slug already exists"
        )
    
    tenant = Tenant(**tenant_data.model_dump())
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant
