"""
API routes for tenant management.

This module provides REST API endpoints for comprehensive tenant management
including creation, updates, quota management, and statistics.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator

from pcm.core.database.session import get_db
from pcm.services.tenant_service import TenantService, TenantNotFoundError, TenantServiceError
from pcm.core.models.tenant import TenantStatus, BillingPlan


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenants", tags=["tenants"])


# Pydantic models for request/response
class TenantCreateRequest(BaseModel):
    """Request model for tenant creation."""
    name: str = Field(..., min_length=1, max_length=255, description="Tenant name")
    organization: str = Field(..., min_length=1, max_length=255, description="Organization name")
    owner: str = Field(..., min_length=1, max_length=255, description="Owner name")
    description: Optional[str] = Field(None, max_length=1000, description="Tenant description")
    region: Optional[str] = Field(None, max_length=100, description="Region")
    datacenter: Optional[str] = Field(None, max_length=100, description="Datacenter")
    billing_plan: Optional[BillingPlan] = Field(None, description="Billing plan")
    
    # Default infrastructure
    default_cluster_id: Optional[str] = Field(None, description="Default cluster ID")
    default_network: Optional[str] = Field(None, description="Default network")
    default_storage: Optional[str] = Field(None, description="Default storage")
    
    # Compute quotas
    cpu_limit: Optional[int] = Field(None, ge=0, description="CPU limit in vCPU cores")
    ram_limit: Optional[int] = Field(None, ge=0, description="RAM limit in GB")
    max_vms: Optional[int] = Field(None, ge=0, description="Maximum VMs")
    max_containers: Optional[int] = Field(None, ge=0, description="Maximum containers")
    
    # Storage quotas
    max_storage_capacity: Optional[int] = Field(None, ge=0, description="Maximum storage in GB")
    max_volumes: Optional[int] = Field(None, ge=0, description="Maximum volumes")
    snapshot_limit: Optional[int] = Field(None, ge=0, description="Snapshot limit")
    
    # Network quotas
    max_networks: Optional[int] = Field(None, ge=0, description="Maximum networks")
    max_floating_ips: Optional[int] = Field(None, ge=0, description="Maximum floating IPs")
    max_load_balancers: Optional[int] = Field(None, ge=0, description="Maximum load balancers")
    max_vlans: Optional[int] = Field(None, ge=0, description="Maximum VLANs")
    
    # Configuration
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuration")
    tenant_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata")
    network_isolation: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Network isolation config")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class TenantResponse(BaseModel):
    """Response model for tenant data."""
    id: str
    name: str
    slug: str
    tenant_id: str
    organization: str
    owner: str
    description: Optional[str]
    region: Optional[str]
    datacenter: Optional[str]
    status: str
    billing_plan: Optional[str]
    created_at: str
    updated_at: str
    quotas: Dict[str, Any]
    quota_status: Dict[str, Any]


# API Endpoints
@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreateRequest,
    db: AsyncSession = Depends(get_db)
) -> TenantResponse:
    """
    Create a new tenant with comprehensive configuration.
    
    Creates a new tenant with the specified configuration including
    quotas, default infrastructure settings, and metadata.
    """
    try:
        tenant_service = TenantService(db)
        tenant = await tenant_service.create_tenant(tenant_data.dict(exclude_unset=True))
        await db.commit()
        
        logger.info(f"Created tenant: {tenant.name} (ID: {tenant.id})")
        return TenantResponse(**tenant.to_dict())
        
    except TenantServiceError as e:
        logger.error(f"Failed to create tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating tenant: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    status_filter: Optional[TenantStatus] = Query(None, alias="status"),
    organization: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[TenantResponse]:
    """
    List tenants with optional filtering and pagination.
    
    Returns a paginated list of tenants with optional filtering
    by status and organization.
    """
    try:
        tenant_service = TenantService(db)
        tenants = await tenant_service.list_tenants(
            status=status_filter,
            organization=organization,
            limit=limit,
            offset=offset
        )
        
        return [TenantResponse(**tenant.to_dict()) for tenant in tenants]
        
    except Exception as e:
        logger.error(f"Failed to list tenants: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> TenantResponse:
    """
    Get a specific tenant by ID.
    
    Returns detailed information about a tenant including
    quotas, usage statistics, and configuration.
    """
    try:
        tenant_service = TenantService(db)
        tenant = await tenant_service.get_tenant(tenant_id)
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return TenantResponse(**tenant.to_dict())
        
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    except Exception as e:
        logger.error(f"Failed to get tenant {tenant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantCreateRequest,
    db: AsyncSession = Depends(get_db)
) -> TenantResponse:
    """
    Update an existing tenant.
    
    Updates tenant information including quotas,
    configuration, and metadata.
    """
    try:
        tenant_service = TenantService(db)
        tenant = await tenant_service.update_tenant(tenant_id, tenant_data.dict(exclude_unset=True))
        await db.commit()
        
        logger.info(f"Updated tenant: {tenant.name} (ID: {tenant.id})")
        return TenantResponse(**tenant.to_dict())
        
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    except Exception as e:
        logger.error(f"Failed to update tenant {tenant_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/templates/list")
async def get_tenant_templates(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get predefined tenant templates.
    
    Returns a list of predefined tenant templates with
    recommended quotas and configurations.
    """
    try:
        tenant_service = TenantService(db)
        templates = await tenant_service.get_tenant_templates()
        
        return templates
        
    except Exception as e:
        logger.error(f"Failed to get tenant templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )