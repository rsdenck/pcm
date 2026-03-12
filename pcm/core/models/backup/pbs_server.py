from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
from enum import Enum
from pcm.core.database.base import Base


class ServerStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class PBSServer(Base):
    """
    Proxmox Backup Server model for managing PBS instances.
    
    Stores connection details, authentication credentials, and health status
    for PBS servers across datacenters. Supports multi-tenant backup operations
    with proper isolation and monitoring.
    """
    __tablename__ = "pbs_servers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=8007, nullable=False)
    
    # Authentication credentials
    api_token_id: Mapped[str] = mapped_column(String(255), nullable=False)
    api_token_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Connection settings
    verify_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    timeout: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    
    # Location and organization
    datacenter: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Health and status monitoring
    status: Mapped[ServerStatus] = mapped_column(
        SQLEnum(ServerStatus, native_enum=False), 
        default=ServerStatus.OFFLINE, 
        nullable=False
    )
    last_health_check: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    health_check_interval: Mapped[int] = mapped_column(Integer, default=300, nullable=False)  # seconds
    
    # Version and capabilities
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    capabilities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Error tracking
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    datastores: Mapped[list["Datastore"]] = relationship(
        back_populates="pbs_server", 
        cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        """Initialize PBSServer with proper defaults."""
        # Set defaults for fields that might not be set by SQLAlchemy in tests
        if 'port' not in kwargs:
            kwargs['port'] = 8007
        if 'verify_ssl' not in kwargs:
            kwargs['verify_ssl'] = True
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30
        if 'health_check_interval' not in kwargs:
            kwargs['health_check_interval'] = 300
        if 'status' not in kwargs:
            kwargs['status'] = ServerStatus.OFFLINE
        if 'error_count' not in kwargs:
            kwargs['error_count'] = 0
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.utcnow()
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = datetime.utcnow()
        
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<PBSServer(id={self.id}, name={self.name}, hostname={self.hostname}, status={self.status})>"

    @property
    def is_healthy(self) -> bool:
        """Check if the PBS server is in a healthy state."""
        return self.status == ServerStatus.ONLINE

    @property
    def connection_url(self) -> str:
        """Get the full connection URL for the PBS server."""
        protocol = "https" if self.verify_ssl else "http"
        port = self.port or 8007  # Default PBS port
        return f"{protocol}://{self.hostname}:{port}"

    def mark_offline(self, error_message: str | None = None) -> None:
        """Mark the server as offline and optionally record an error."""
        self.status = ServerStatus.OFFLINE
        self.last_health_check = datetime.utcnow()
        if error_message:
            self.last_error = error_message
            if self.error_count is None:
                self.error_count = 0
            self.error_count += 1

    def mark_online(self, version: str | None = None, capabilities: dict | None = None) -> None:
        """Mark the server as online and update version/capabilities."""
        self.status = ServerStatus.ONLINE
        self.last_health_check = datetime.utcnow()
        self.last_error = None
        if self.error_count is None:
            self.error_count = 0
        else:
            self.error_count = 0
        if version:
            self.version = version
        if capabilities:
            self.capabilities = capabilities