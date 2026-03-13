from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from typing import Dict, Any, Optional
from pcm.core.database.base import Base


class TenantStatus(str, Enum):
    """Status do tenant."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    ARCHIVED = "archived"


class BillingPlan(str, Enum):
    """Planos de billing disponíveis."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class Tenant(Base):
    """
    Tenant model for multi-tenant infrastructure management.
    
    A Tenant is an isolated logical domain within the Proxmox Control Plane
    used to group infrastructure resources, users, policies, and quotas.
    """
    __tablename__ = "tenants"

    # Primary identification
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Organization details
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Location and infrastructure
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    datacenter: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Status and billing
    status: Mapped[TenantStatus] = mapped_column(
        SQLEnum(TenantStatus, native_enum=False), 
        default=TenantStatus.ACTIVE, 
        nullable=False
    )
    billing_plan: Mapped[BillingPlan | None] = mapped_column(
        SQLEnum(BillingPlan, native_enum=False), 
        nullable=True
    )
    
    # Default infrastructure settings
    default_cluster_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    default_network: Mapped[str | None] = mapped_column(String(255), nullable=True)
    default_storage: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Compute resource limits
    cpu_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # vCPU cores
    ram_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # GB
    max_vms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_containers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Storage limits
    max_storage_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)  # GB
    max_volumes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    snapshot_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Network limits
    max_networks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_floating_ips: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_load_balancers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_vlans: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Configuration and metadata
    configuration: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tenant_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Network isolation settings
    network_isolation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Current usage tracking (for quota enforcement)
    current_usage: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    users: Mapped[list["User"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    clusters: Mapped[list["ProxmoxCluster"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    vms: Mapped[list["VirtualMachine"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    backup_policies: Mapped[list["BackupPolicy"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    roles: Mapped[list["Role"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name={self.name}, organization={self.organization})>"
    
    @property
    def is_active(self) -> bool:
        """Check if tenant is active."""
        return self.status == TenantStatus.ACTIVE
    
    def get_quota_usage(self) -> Dict[str, Any]:
        """Get current quota usage statistics."""
        return self.current_usage or {}
    
    def update_usage(self, resource_type: str, value: int) -> None:
        """Update resource usage for quota tracking."""
        if not self.current_usage:
            self.current_usage = {}
        self.current_usage[resource_type] = value
    
    def check_quota_limit(self, resource_type: str, requested: int) -> bool:
        """Check if requested resource amount is within quota limits."""
        current = self.get_quota_usage().get(resource_type, 0)
        
        limit_map = {
            'cpu': self.cpu_limit,
            'ram': self.ram_limit,
            'vms': self.max_vms,
            'containers': self.max_containers,
            'storage': self.max_storage_capacity,
            'volumes': self.max_volumes,
            'snapshots': self.snapshot_limit,
            'networks': self.max_networks,
            'floating_ips': self.max_floating_ips,
            'load_balancers': self.max_load_balancers,
            'vlans': self.max_vlans
        }
        
        limit = limit_map.get(resource_type)
        if limit is None:
            return True  # No limit set
        
        return (current + requested) <= limit
    
    def get_quota_status(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive quota status for all resources."""
        usage = self.get_quota_usage()
        
        resources = {
            'cpu': {'limit': self.cpu_limit, 'unit': 'vCPU'},
            'ram': {'limit': self.ram_limit, 'unit': 'GB'},
            'vms': {'limit': self.max_vms, 'unit': 'count'},
            'containers': {'limit': self.max_containers, 'unit': 'count'},
            'storage': {'limit': self.max_storage_capacity, 'unit': 'GB'},
            'volumes': {'limit': self.max_volumes, 'unit': 'count'},
            'snapshots': {'limit': self.snapshot_limit, 'unit': 'count'},
            'networks': {'limit': self.max_networks, 'unit': 'count'},
            'floating_ips': {'limit': self.max_floating_ips, 'unit': 'count'},
            'load_balancers': {'limit': self.max_load_balancers, 'unit': 'count'},
            'vlans': {'limit': self.max_vlans, 'unit': 'count'}
        }
        
        status = {}
        for resource, config in resources.items():
            current = usage.get(resource, 0)
            limit = config['limit']
            
            if limit is not None:
                percentage = (current / limit * 100) if limit > 0 else 0
                status[resource] = {
                    'current': current,
                    'limit': limit,
                    'percentage': round(percentage, 2),
                    'unit': config['unit'],
                    'available': limit - current
                }
            else:
                status[resource] = {
                    'current': current,
                    'limit': None,
                    'percentage': 0,
                    'unit': config['unit'],
                    'available': 'unlimited'
                }
        
        return status
    
    def activate(self) -> None:
        """Activate the tenant."""
        self.status = TenantStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def suspend(self) -> None:
        """Suspend the tenant."""
        self.status = TenantStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
    
    def archive(self) -> None:
        """Archive the tenant."""
        self.status = TenantStatus.ARCHIVED
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'tenant_id': self.tenant_id,
            'organization': self.organization,
            'owner': self.owner,
            'description': self.description,
            'region': self.region,
            'datacenter': self.datacenter,
            'status': self.status.value,
            'billing_plan': self.billing_plan.value if self.billing_plan else None,
            'default_cluster_id': self.default_cluster_id,
            'default_network': self.default_network,
            'default_storage': self.default_storage,
            'quotas': {
                'compute': {
                    'cpu_limit': self.cpu_limit,
                    'ram_limit': self.ram_limit,
                    'max_vms': self.max_vms,
                    'max_containers': self.max_containers
                },
                'storage': {
                    'max_storage_capacity': self.max_storage_capacity,
                    'max_volumes': self.max_volumes,
                    'snapshot_limit': self.snapshot_limit
                },
                'network': {
                    'max_networks': self.max_networks,
                    'max_floating_ips': self.max_floating_ips,
                    'max_load_balancers': self.max_load_balancers,
                    'max_vlans': self.max_vlans
                }
            },
            'quota_status': self.get_quota_status(),
            'configuration': self.configuration,
            'metadata': self.tenant_metadata,
            'network_isolation': self.network_isolation,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
