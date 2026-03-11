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

**[🇧🇷 Português](README.md)** • **[🇺🇸 English](#overview)**

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
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API    │  │Scheduler │  │ Tenant   │  │Observ.   │   │
│  │ Gateway  │  │ Engine   │  │ Manager  │  │  Stack   │   │
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

</div>

---

## Features

- **Multi-Cluster Management** – Centralized control of multiple Proxmox clusters
- **Multi-Tenancy** – Complete tenant isolation with RBAC
- **Automated Provisioning** – Async VM/Container deployment
- **Unified Observability** – OpenTelemetry-based metrics and tracing
- **SDN Integration** – Native Software-Defined Networking
- **Ceph Storage** – First-class Ceph storage management
- **RESTful API** – Complete API coverage with OpenAPI docs
- **Modern UI** – Responsive dashboard built with Nuxt 3

---

## Quick Start

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

| Service | URL |
|---------|-----|
| Frontend | http://192.168.130.10:9000 |
| API | http://192.168.130.10:8000 |
| API Docs | http://192.168.130.10:8000/docs |

---

## Lab Setup

**PROXMON Development Cluster**

| Node | IP | Role |
|------|-----|------|
| PVE-01 | 192.168.130.20 | Primary |
| PVE-02 | 192.168.130.21 | Secondary |
| PVE-03 | 192.168.130.22 | Tertiary |

See [LAB.md](LAB.md) for complete lab configuration.

---

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Setup Guide](SETUP.md)
- [Deployment Guide](DEPLOY.md)
- [Migration Guide](MIGRATION.md)
- [Lab Configuration](LAB.md)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**[Website](https://github.com/rsdenck/pcm)** • **[Documentation](SETUP.md)** • **[API Reference](http://192.168.130.10:8000/docs)**

Made with precision for enterprise infrastructure management

[![GitHub](https://img.shields.io/badge/-rsdenck-000000?style=for-the-badge&logo=github&logoColor=ff7a00)](https://github.com/rsdenck)

</div>
