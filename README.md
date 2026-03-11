<div align="center">

# PCM – Proxmox Center Manager

**Cloud Control Plane for Enterprise Proxmox Infrastructure**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Nuxt](https://img.shields.io/badge/Nuxt-3.x-00DC82.svg)](https://nuxt.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791.svg)](https://www.postgresql.org/)

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## Overview

PCM (Proxmox Center Manager) is an enterprise-grade **Cloud Control Plane** designed to transform Proxmox VE infrastructure into a fully-featured cloud platform. Built for large-scale deployments, PCM provides centralized management, multi-tenancy, automation, and observability across multiple Proxmox clusters.

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROL PLANE (PCM)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API    │  │Scheduler │  │ Tenant   │  │Observ.   │   │
│  │ Gateway  │  │ Engine   │  │ Manager  │  │ Stack    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    COMPUTE PLANE                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Cluster 1 │  │Cluster 2 │  │Cluster 3 │  │Cluster N │   │
│  │ PVE/PBS  │  │ PVE/PBS  │  │ PVE/PBS  │  │ PVE/PBS  │   │
│  │   PMG    │  │   PMG    │  │   PMG    │  │   PMG    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Core Capabilities

- **Multi-Cluster Management** – Centralized control of multiple Proxmox clusters
- **Multi-Tenancy** – Complete tenant isolation with RBAC
- **Automated Provisioning** – Async VM/Container deployment with queue management
- **Unified Observability** – OpenTelemetry-based metrics and tracing
- **SDN Integration** – Native Software-Defined Networking support
- **Ceph Storage** – First-class Ceph storage management
- **RESTful API** – Complete API coverage with OpenAPI documentation
- **Modern UI** – Responsive dashboard built with Nuxt 3

### Platform Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Gateway** | FastAPI | RESTful API & WebSocket support |
| **Database** | PostgreSQL 18 | Persistent data storage |
| **Cache/Queue** | Redis 7 | Caching & async task queue |
| **Workers** | Celery | Background job processing |
| **Frontend** | Nuxt 3 + Nuxt UI | Modern web interface |
| **Observability** | OpenTelemetry | Metrics, traces, logs |

## Architecture

### Technology Stack

#### Backend
```
Python 3.12+
├── FastAPI          # Web framework
├── SQLAlchemy 2     # ORM
├── Pydantic         # Data validation
├── Celery           # Task queue
├── AsyncIO          # Async operations
└── OpenTelemetry    # Observability
```

#### Frontend
```
Node.js 20+
├── Nuxt 3           # Vue framework
├── Nuxt UI          # Component library
├── Tailwind CSS     # Styling
└── TypeScript       # Type safety
```

#### Infrastructure
```
PostgreSQL 18        # Primary database
Redis 7              # Cache & queue
Proxmox VE 8+        # Compute platform
Ceph                 # Storage backend
```

### Microservices Architecture

```
pcm/
├── services/
│   ├── api/              # Main API service
│   ├── scheduler/        # Task scheduling
│   ├── tenant/           # Tenant management
│   ├── compute/          # VM/Container ops
│   ├── storage/          # Storage management
│   └── network/          # Network management
├── core/
│   ├── database/         # DB configuration
│   ├── config/           # Settings
│   ├── auth/             # Authentication
│   └── events/           # Event system
├── workers/
│   ├── provisioning/     # Provisioning tasks
│   ├── monitoring/       # Health checks
│   └── telemetry/        # Metrics collection
└── sdk/
    └── proxmox/          # Proxmox API client
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 18
- Redis 7
- Proxmox VE 8+ cluster

### Installation

#### 1. Backend Setup

```bash
# Run automated setup
setup-backend.bat

# Configure environment
# Edit pcm/.env with your settings

# Run database migrations
cd pcm
venv\Scripts\activate
alembic upgrade head
```

#### 2. Frontend Setup

```bash
# Run automated setup
setup-frontend.bat
```

#### 3. Start Services

```bash
# Terminal 1 - Backend API
start-backend.bat

# Terminal 2 - Frontend
start-frontend.bat

# Terminal 3 - Workers (optional)
start-workers.bat
```

### Access Points

- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Configuration

### Environment Variables

#### Backend (`pcm/.env`)
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/pcmdata
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

#### Frontend (`pcm-frontend/.env`)
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

### Proxmox Cluster Configuration

Add your Proxmox clusters via API or UI:

```bash
POST /api/v1/clusters
{
  "name": "Production Cluster",
  "hostname": "192.168.130.20",
  "port": 8006,
  "api_token_id": "root@pam!pcm",
  "api_token_secret": "your-token-secret",
  "cluster_type": "pve"
}
```

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Setup Guide](SETUP.md)
- [Migration Guide](MIGRATION.md)
- [API Documentation](http://localhost:8000/docs)

## User Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Provider Admin** | Full platform access | Platform operators |
| **Tenant Admin** | Tenant-level management | Organization admins |
| **Tenant User** | Resource consumption | End users |

## Roadmap

- [x] Core API implementation
- [x] Multi-cluster support
- [x] Tenant management
- [x] Async provisioning
- [ ] Advanced RBAC
- [ ] Billing integration (Lago)
- [ ] Backup automation
- [ ] Network topology visualization
- [ ] Cost analytics
- [ ] Terraform provider

## Contributing

We welcome contributions! Please see our contributing guidelines.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/rsdenck/pcm/issues)
- **Discussions:** [GitHub Discussions](https://github.com/rsdenck/pcm/discussions)

## Acknowledgments

Built with modern technologies and inspired by enterprise cloud platforms:
- VMware vCloud Director
- OpenStack
- Proxmox VE

---

<div align="center">

**[Website](https://github.com/rsdenck/pcm)** • **[Documentation](SETUP.md)** • **[API Reference](http://localhost:8000/docs)**

Made with precision for enterprise infrastructure management

</div>
