<div align="center">

<img src="https://raw.githubusercontent.com/rsdenck/pcm/main/assets/pcm-logo.png" alt="PCM Logo" width="800"/>

<table>
<tr>
<td align="center" width="100%">

# PCM – Proxmox Center Manager

**Cloud Control Plane for Enterprise Proxmox Infrastructure**

_"Transforming Proxmox into a complete cloud platform."_

</td>
</tr>
</table>

<table>
<tr>
<td align="center">

[![License](https://img.shields.io/badge/License-MIT-000000?style=for-the-badge&logo=opensourceinitiative&logoColor=ff7a00)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-000000?style=for-the-badge&logo=python&logoColor=ff7a00)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-000000?style=for-the-badge&logo=fastapi&logoColor=ff7a00)](https://fastapi.tiangolo.com/)
[![Nuxt](https://img.shields.io/badge/Nuxt-3.x-000000?style=for-the-badge&logo=nuxt.js&logoColor=ff7a00)](https://nuxt.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-000000?style=for-the-badge&logo=postgresql&logoColor=ff7a00)](https://www.postgresql.org/)
[![Proxmox](https://img.shields.io/badge/Proxmox-VE_8+-000000?style=for-the-badge&logo=proxmox&logoColor=ff7a00)](https://www.proxmox.com/)

</td>
</tr>
</table>

<table>
<tr>
<td align="center">

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Lab Setup](#lab-setup)

</td>
</tr>
</table>

</div>

---

## Overview

PCM (Proxmox Center Manager) is an **enterprise-grade Cloud Control Plane** that transforms Proxmox VE infrastructure into a fully-featured cloud platform. Built for large-scale deployments with multi-cluster management, multi-tenancy, and complete automation.

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROL PLANE (PCM)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   API    │  │Scheduler │  │ Tenant   │  │Observ.   │     │
│  │ Gateway  │  │ Engine   │  │ Manager  │  │ Stack    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    COMPUTE PLANE                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Cluster 1 │  │Cluster 2 │  │Cluster 3 │  │Cluster N │     │
│  │ PVE/PBS  │  │ PVE/PBS  │  │ PVE/PBS  │  │ PVE/PBS  │     │
│  │   PMG    │  │   PMG    │  │   PMG    │  │   PMG    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

</div>

---

## Features

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

### Core Capabilities

![Multi-Cluster](https://img.shields.io/badge/-Multi--Cluster_Management-000000?style=for-the-badge&logo=server&logoColor=ff7a00)

Centralized control of multiple Proxmox clusters across different sites and regions.

![Multi-Tenancy](https://img.shields.io/badge/-Multi--Tenancy-000000?style=for-the-badge&logo=users&logoColor=ff7a00)

Complete tenant isolation with role-based access control (RBAC).

![Automation](https://img.shields.io/badge/-Automated_Provisioning-000000?style=for-the-badge&logo=robot&logoColor=ff7a00)

Async VM/Container deployment with intelligent queue management.

![Observability](https://img.shields.io/badge/-Unified_Observability-000000?style=for-the-badge&logo=grafana&logoColor=ff7a00)

OpenTelemetry-based metrics, traces, and logs aggregation.

</td>
<td valign="top" width="50%">

### Platform Features

![SDN](https://img.shields.io/badge/-SDN_Integration-000000?style=for-the-badge&logo=cisco&logoColor=ff7a00)

Native Software-Defined Networking support.

![Ceph](https://img.shields.io/badge/-Ceph_Storage-000000?style=for-the-badge&logo=ceph&logoColor=ff7a00)

First-class Ceph storage management and monitoring.

![API](https://img.shields.io/badge/-RESTful_API-000000?style=for-the-badge&logo=fastapi&logoColor=ff7a00)

Complete API coverage with OpenAPI documentation.

![UI](https://img.shields.io/badge/-Modern_Dashboard-000000?style=for-the-badge&logo=vue.js&logoColor=ff7a00)

Responsive web interface built with Nuxt 3.

</td>
</tr>
</table>

</div>

---

## Technology Stack

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

### Backend Stack

![Python](https://img.shields.io/badge/Python_3.12+-000000?style=for-the-badge&logo=python&logoColor=ff7a00)
![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=for-the-badge&logo=fastapi&logoColor=ff7a00)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy_2-000000?style=for-the-badge&logo=python&logoColor=ff7a00)
![Pydantic](https://img.shields.io/badge/Pydantic-000000?style=for-the-badge&logo=python&logoColor=ff7a00)
![Celery](https://img.shields.io/badge/Celery-000000?style=for-the-badge&logo=celery&logoColor=ff7a00)
![AsyncIO](https://img.shields.io/badge/AsyncIO-000000?style=for-the-badge&logo=python&logoColor=ff7a00)

**Observability**

![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000000?style=for-the-badge&logo=opentelemetry&logoColor=ff7a00)
![Prometheus](https://img.shields.io/badge/Prometheus-000000?style=for-the-badge&logo=prometheus&logoColor=ff7a00)

</td>
<td valign="top" width="50%">

### Frontend Stack

![Nuxt](https://img.shields.io/badge/Nuxt_3-000000?style=for-the-badge&logo=nuxt.js&logoColor=ff7a00)
![Vue](https://img.shields.io/badge/Vue_3-000000?style=for-the-badge&logo=vue.js&logoColor=ff7a00)
![Nuxt_UI](https://img.shields.io/badge/Nuxt_UI-000000?style=for-the-badge&logo=nuxt.js&logoColor=ff7a00)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-000000?style=for-the-badge&logo=tailwindcss&logoColor=ff7a00)
![TypeScript](https://img.shields.io/badge/TypeScript-000000?style=for-the-badge&logo=typescript&logoColor=ff7a00)
![Vite](https://img.shields.io/badge/Vite-000000?style=for-the-badge&logo=vite&logoColor=ff7a00)

**Infrastructure**

![PostgreSQL](https://img.shields.io/badge/PostgreSQL_18-000000?style=for-the-badge&logo=postgresql&logoColor=ff7a00)
![Redis](https://img.shields.io/badge/Redis_7-000000?style=for-the-badge&logo=redis&logoColor=ff7a00)

</td>
</tr>
</table>

</div>

---

## Architecture

<div align="center">

### Microservices Design

| Service | Purpose | Technology |
|---------|---------|------------|
| ![API](https://img.shields.io/badge/-API_Gateway-000000?style=flat-square&logo=fastapi&logoColor=ff7a00) | Main API & WebSocket | FastAPI |
| ![Scheduler](https://img.shields.io/badge/-Scheduler-000000?style=flat-square&logo=clockify&logoColor=ff7a00) | Task Scheduling | Celery Beat |
| ![Tenant](https://img.shields.io/badge/-Tenant_Manager-000000?style=flat-square&logo=users&logoColor=ff7a00) | Multi-tenancy | FastAPI |
| ![Compute](https://img.shields.io/badge/-Compute_Manager-000000?style=flat-square&logo=server&logoColor=ff7a00) | VM/Container Ops | AsyncIO |
| ![Storage](https://img.shields.io/badge/-Storage_Manager-000000?style=flat-square&logo=database&logoColor=ff7a00) | Storage Ops | Ceph API |
| ![Network](https://img.shields.io/badge/-Network_Manager-000000?style=flat-square&logo=cisco&logoColor=ff7a00) | SDN Management | Proxmox SDN |
| ![Telemetry](https://img.shields.io/badge/-Telemetry-000000?style=flat-square&logo=grafana&logoColor=ff7a00) | Metrics Collection | OTEL |

</div>

---

## Quick Start

<div align="center">

### Prerequisites

![Python](https://img.shields.io/badge/Python-3.12+-000000?style=flat-square&logo=python&logoColor=ff7a00)
![Node](https://img.shields.io/badge/Node.js-20+-000000?style=flat-square&logo=node.js&logoColor=ff7a00)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-000000?style=flat-square&logo=postgresql&logoColor=ff7a00)
![Redis](https://img.shields.io/badge/Redis-7-000000?style=flat-square&logo=redis&logoColor=ff7a00)
![Proxmox](https://img.shields.io/badge/Proxmox-VE_8+-000000?style=flat-square&logo=proxmox&logoColor=ff7a00)

</div>

### Installation (Windows)

```bash
# 1. Backend Setup
setup-backend.bat

# 2. Configure environment
# Edit pcm/.env with your settings

# 3. Run migrations
cd pcm
venv\Scripts\activate
alembic upgrade head

# 4. Frontend Setup
setup-frontend.bat

# 5. Start all services
start-all.bat
```

### Access Points

<div align="center">

| Service | URL | Description |
|---------|-----|-------------|
| ![Frontend](https://img.shields.io/badge/-Frontend-000000?style=flat-square&logo=vue.js&logoColor=ff7a00) | http://192.168.130.10:9000 | Web Dashboard |
| ![API](https://img.shields.io/badge/-API-000000?style=flat-square&logo=fastapi&logoColor=ff7a00) | http://192.168.130.10:8000 | REST API |
| ![Docs](https://img.shields.io/badge/-API_Docs-000000?style=flat-square&logo=swagger&logoColor=ff7a00) | http://192.168.130.10:8000/docs | Swagger UI |
| ![ReDoc](https://img.shields.io/badge/-ReDoc-000000?style=flat-square&logo=readthedocs&logoColor=ff7a00) | http://192.168.130.10:8000/redoc | API Documentation |

</div>

---

## Lab Setup

<div align="center">

### Development Cluster Configuration

**PROXMON Development Cluster**

| Node | IP | Role | Status |
|------|-----|------|--------|
| ![PVE-01](https://img.shields.io/badge/-PVE--01-000000?style=flat-square&logo=proxmox&logoColor=ff7a00) | 192.168.130.20 | Primary | ![Online](https://img.shields.io/badge/-Online-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) |
| ![PVE-02](https://img.shields.io/badge/-PVE--02-000000?style=flat-square&logo=proxmox&logoColor=ff7a00) | 192.168.130.21 | Secondary | ![Online](https://img.shields.io/badge/-Online-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) |
| ![PVE-03](https://img.shields.io/badge/-PVE--03-000000?style=flat-square&logo=proxmox&logoColor=ff7a00) | 192.168.130.22 | Tertiary | ![Online](https://img.shields.io/badge/-Online-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) |

</div>

### Initialize Lab Cluster

```bash
cd pcm
venv\Scripts\activate
python ../init-lab-cluster.py
```

See [LAB.md](LAB.md) for complete lab configuration details.

---

## Documentation

<div align="center">

| Document | Description |
|----------|-------------|
| ![Quick Start](https://img.shields.io/badge/-Quick_Start-000000?style=flat-square&logo=rocket&logoColor=ff7a00) | [QUICKSTART.md](QUICKSTART.md) |
| ![Setup Guide](https://img.shields.io/badge/-Setup_Guide-000000?style=flat-square&logo=book&logoColor=ff7a00) | [SETUP.md](SETUP.md) |
| ![Deployment](https://img.shields.io/badge/-Deployment-000000?style=flat-square&logo=kubernetes&logoColor=ff7a00) | [DEPLOY.md](DEPLOY.md) |
| ![Migration](https://img.shields.io/badge/-Migration-000000?style=flat-square&logo=git&logoColor=ff7a00) | [MIGRATION.md](MIGRATION.md) |
| ![Lab Config](https://img.shields.io/badge/-Lab_Config-000000?style=flat-square&logo=proxmox&logoColor=ff7a00) | [LAB.md](LAB.md) |

</div>

---

## User Roles

<div align="center">

| Role | Permissions | Badge |
|------|-------------|-------|
| Provider Admin | Full platform access | ![Admin](https://img.shields.io/badge/-Provider_Admin-000000?style=flat-square&logo=shield&logoColor=ff7a00) |
| Tenant Admin | Tenant-level management | ![Tenant](https://img.shields.io/badge/-Tenant_Admin-000000?style=flat-square&logo=users&logoColor=ff7a00) |
| Tenant User | Resource consumption | ![User](https://img.shields.io/badge/-Tenant_User-000000?style=flat-square&logo=user&logoColor=ff7a00) |

</div>

---

## Roadmap

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

### Completed

- [x] Core API implementation
- [x] Multi-cluster support
- [x] Tenant management
- [x] Async provisioning
- [x] Storage management
- [x] VM/Container sync
- [x] Modern UI dashboard

</td>
<td valign="top" width="50%">

### In Progress

- [ ] Advanced RBAC
- [ ] Billing integration (Lago)
- [ ] Backup automation
- [ ] Network topology viz
- [ ] Cost analytics
- [ ] Terraform provider
- [ ] Kubernetes integration

</td>
</tr>
</table>

</div>

---

## Project Structure

```
pcm/
├── services/          # Microservices
│   ├── api/          # Main API
│   ├── scheduler/    # Task scheduling
│   ├── tenant/       # Tenant management
│   ├── compute/      # VM/Container ops
│   ├── storage/      # Storage management
│   └── network/      # Network management
├── core/             # Core components
│   ├── database/     # DB configuration
│   ├── config/       # Settings
│   ├── auth/         # Authentication
│   └── events/       # Event system
├── workers/          # Background workers
│   ├── provisioning/ # Provisioning tasks
│   ├── monitoring/   # Health checks
│   └── telemetry/    # Metrics collection
└── sdk/              # SDKs
    └── proxmox/      # Proxmox API client

pcmfe/                # Nuxt 3 application (Frontend)
├── pages/            # Routes
├── components/       # Vue components
├── layouts/          # Layouts
└── assets/           # Static assets
```

---

## Contributing

<div align="center">

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

</div>

---

## License

<div align="center">

[![License](https://img.shields.io/badge/License-MIT-000000?style=for-the-badge&logo=opensourceinitiative&logoColor=ff7a00)](LICENSE)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

</div>

---

## Support

<div align="center">

[![Issues](https://img.shields.io/badge/-Issues-000000?style=for-the-badge&logo=github&logoColor=ff7a00)](https://github.com/rsdenck/pcm/issues)
[![Discussions](https://img.shields.io/badge/-Discussions-000000?style=for-the-badge&logo=github&logoColor=ff7a00)](https://github.com/rsdenck/pcm/discussions)

</div>

---

## Acknowledgments

<div align="center">

Built with modern technologies and inspired by enterprise cloud platforms:

![VMware](https://img.shields.io/badge/-VMware_vCloud-000000?style=flat-square&logo=vmware&logoColor=ff7a00)
![OpenStack](https://img.shields.io/badge/-OpenStack-000000?style=flat-square&logo=openstack&logoColor=ff7a00)
![Proxmox](https://img.shields.io/badge/-Proxmox_VE-000000?style=flat-square&logo=proxmox&logoColor=ff7a00)

</div>

---

<div align="center">

### Philosophy

_"If it's not monitored, it doesn't exist."_

_"If it's repetitive, it must be automated."_

_"Infrastructure is not art. It's engineering."_

---

**[Website](https://github.com/rsdenck/pcm)** • **[Documentation](SETUP.md)** • **[API Reference](http://192.168.130.10:8000/docs)**

Made with precision for enterprise infrastructure management

[![GitHub](https://img.shields.io/badge/-rsdenck-000000?style=for-the-badge&logo=github&logoColor=ff7a00)](https://github.com/rsdenck)

</div>
