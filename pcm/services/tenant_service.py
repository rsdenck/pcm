"""
Tenant Service for multi-tenant infrastructure management.

This service provides comprehensive tenant management including:
- Tenant creation and lifecycle management
- Quota enforcement and monitoring
- Resource isolation
- RBAC integration
- Billing integration
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func as sa_func
from sqlalchemy.orm import selectinload

from pcm.core.models.tenant import Tenant, TenantStatus, BillingPlan
from pcm.core.models.user import User
from pcm.core.models.cluster import ProxmoxCluster


logger = logging.getLogger(__name__)


class TenantServiceError(Exception):
    """Base exception for tenant service errors."""
    pass


class TenantNotFoundError(TenantServiceError):
    """Raised when tenant is not found."""
    pass


class TenantQuotaExceededError(TenantServiceError):
    """Raised when tenant quota is exceeded."""
    pass


class TenantService:
    """
    Service for managing tenants in the PCM system.
    
    Provides comprehensive tenant management including creation,
    quota enforcement, resource tracking, and lifecycle management.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize tenant service."""
        self.db_session = db_session
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Tenant:
        """
        Create a new tenant with comprehensive configuration.
        
        Args:
            tenant_data: Tenant configuration data
            
        Returns:
            Created tenant instance
            
        Raises:
            TenantServiceError: If creation fails
        """
        try:
            # Generate tenant_id if not provided
            if 'tenant_id' not in tenant_data:
                tenant_data['tenant_id'] = self._generate_tenant_id(tenant_data['name'])
            
            # Generate slug if not provided
            if 'slug' not in tenant_data:
                tenant_data['slug'] = self._generate_slug(tenant_data['name'])
            
            # Set default values
            tenant_data.setdefault('status', TenantStatus.ACTIVE)
            tenant_data.setdefault('current_usage', {})
            tenant_data.setdefault('configuration', {})
            tenant_data.setdefault('tenant_metadata', {})
            
            # Create tenant instance
            tenant = Tenant(**tenant_data)
            
            # Add to session
            self.db_session.add(tenant)
            await self.db_session.flush()
            await self.db_session.refresh(tenant)
            
            logger.info(f"Created tenant: {tenant.name} (ID: {tenant.id})")
            return tenant
            
        except Exception as e:
            logger.error(f"Failed to create tenant: {e}")
            raise TenantServiceError(f"Failed to create tenant: {str(e)}")
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Tenant instance or None if not found
        """
        result = await self.db_session.execute(
            select(Tenant)
            .options(
                selectinload(Tenant.users),
                selectinload(Tenant.clusters)
            )
            .where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tenant_by_tenant_id(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by tenant_id field.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant instance or None if not found
        """
        result = await self.db_session.execute(
            select(Tenant)
            .options(
                selectinload(Tenant.users),
                selectinload(Tenant.clusters)
            )
            .where(Tenant.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def list_tenants(
        self, 
        status: Optional[TenantStatus] = None,
        organization: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Tenant]:
        """
        List tenants with optional filtering.
        
        Args:
            status: Filter by status
            organization: Filter by organization
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of tenant instances
        """
        query = select(Tenant).options(
            selectinload(Tenant.users),
            selectinload(Tenant.clusters)
        )
        
        if status:
            query = query.where(Tenant.status == status)
        
        if organization:
            query = query.where(Tenant.organization.ilike(f"%{organization}%"))
        
        query = query.order_by(Tenant.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
    
    async def update_tenant(self, tenant_id: str, update_data: Dict[str, Any]) -> Tenant:
        """
        Update tenant configuration.
        
        Args:
            tenant_id: Tenant ID
            update_data: Data to update
            
        Returns:
            Updated tenant instance
            
        Raises:
            TenantNotFoundError: If tenant not found
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        
        tenant.updated_at = datetime.utcnow()
        await self.db_session.flush()
        await self.db_session.refresh(tenant)
        
        logger.info(f"Updated tenant: {tenant.name} (ID: {tenant.id})")
        return tenant
    
    async def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete tenant and all associated resources.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            TenantNotFoundError: If tenant not found
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        
        # Archive instead of hard delete for audit purposes
        tenant.status = TenantStatus.ARCHIVED
        tenant.updated_at = datetime.utcnow()
        
        await self.db_session.flush()
        
        logger.info(f"Archived tenant: {tenant.name} (ID: {tenant.id})")
        return True
    
    async def check_quota(self, tenant_id: str, resource_type: str, requested: int) -> bool:
        """
        Check if tenant has quota available for requested resource.
        
        Args:
            tenant_id: Tenant ID
            resource_type: Type of resource (cpu, ram, vms, etc.)
            requested: Amount requested
            
        Returns:
            True if quota available, False otherwise
            
        Raises:
            TenantNotFoundError: If tenant not found
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        
        return tenant.check_quota_limit(resource_type, requested)
    
    async def update_usage(self, tenant_id: str, resource_type: str, value: int) -> None:
        """
        Update resource usage for tenant.
        
        Args:
            tenant_id: Tenant ID
            resource_type: Type of resource
            value: New usage value
            
        Raises:
            TenantNotFoundError: If tenant not found
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        
        tenant.update_usage(resource_type, value)
        await self.db_session.flush()
        
        logger.debug(f"Updated usage for tenant {tenant.name}: {resource_type} = {value}")
    
    async def get_quota_status(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get comprehensive quota status for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Quota status dictionary
            
        Raises:
            TenantNotFoundError: If tenant not found
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        
        return tenant.get_quota_status()
    
    async def activate_tenant(self, tenant_id: str) -> Tenant:
        """
        Activate a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Updated tenant instance
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        
        tenant.activate()
        await self.db_session.flush()
        
        logger.info(f"Activated tenant: {tenant.name}")
        return tenant
    
    async def suspend_tenant(self, tenant_id: str) -> Tenant:
        """
        Suspend a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Updated tenant instance
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        
        tenant.suspend()
        await self.db_session.flush()
        
        logger.info(f"Suspended tenant: {tenant.name}")
        return tenant
    
    async def get_tenant_statistics(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Statistics dictionary
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        
        # Get counts of associated resources
        user_count = len(tenant.users)
        cluster_count = len(tenant.clusters)
        vm_count = len(tenant.vms)
        
        return {
            'tenant_info': tenant.to_dict(),
            'resource_counts': {
                'users': user_count,
                'clusters': cluster_count,
                'vms': vm_count
            },
            'quota_status': tenant.get_quota_status(),
            'usage_summary': tenant.get_quota_usage()
        }
    
    def _generate_tenant_id(self, name: str) -> str:
        """Generate tenant ID from name."""
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        tenant_id = name.lower().replace(' ', '-')
        tenant_id = ''.join(c for c in tenant_id if c.isalnum() or c == '-')
        return tenant_id[:50]  # Limit length
    
    def _generate_slug(self, name: str) -> str:
        """Generate slug from name."""
        return self._generate_tenant_id(name)
    
    async def get_tenant_templates(self) -> List[Dict[str, Any]]:
        """
        Get predefined tenant templates.
        
        Returns:
            List of tenant templates
        """
        return [
            {
                'name': 'Small Business',
                'description': 'Template for small businesses with basic needs',
                'billing_plan': BillingPlan.BASIC,
                'quotas': {
                    'cpu_limit': 16,
                    'ram_limit': 64,
                    'max_vms': 10,
                    'max_containers': 20,
                    'max_storage_capacity': 500,
                    'max_volumes': 50,
                    'snapshot_limit': 100,
                    'max_networks': 5,
                    'max_floating_ips': 5,
                    'max_load_balancers': 2,
                    'max_vlans': 10
                }
            },
            {
                'name': 'Medium Enterprise',
                'description': 'Template for medium enterprises with moderate needs',
                'billing_plan': BillingPlan.STANDARD,
                'quotas': {
                    'cpu_limit': 64,
                    'ram_limit': 256,
                    'max_vms': 50,
                    'max_containers': 100,
                    'max_storage_capacity': 2000,
                    'max_volumes': 200,
                    'snapshot_limit': 500,
                    'max_networks': 20,
                    'max_floating_ips': 20,
                    'max_load_balancers': 10,
                    'max_vlans': 50
                }
            },
            {
                'name': 'Large Enterprise',
                'description': 'Template for large enterprises with extensive needs',
                'billing_plan': BillingPlan.PREMIUM,
                'quotas': {
                    'cpu_limit': 256,
                    'ram_limit': 1024,
                    'max_vms': 200,
                    'max_containers': 500,
                    'max_storage_capacity': 10000,
                    'max_volumes': 1000,
                    'snapshot_limit': 2000,
                    'max_networks': 100,
                    'max_floating_ips': 100,
                    'max_load_balancers': 50,
                    'max_vlans': 200
                }
            },
            {
                'name': 'Development Team',
                'description': 'Template optimized for development teams',
                'billing_plan': BillingPlan.STANDARD,
                'quotas': {
                    'cpu_limit': 32,
                    'ram_limit': 128,
                    'max_vms': 25,
                    'max_containers': 50,
                    'max_storage_capacity': 1000,
                    'max_volumes': 100,
                    'snapshot_limit': 300,
                    'max_networks': 10,
                    'max_floating_ips': 10,
                    'max_load_balancers': 5,
                    'max_vlans': 25
                }
            }
        ]