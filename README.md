# PCM – Proxmox Center Manager

Cloud Control Plane para Infraestruturas Proxmox em larga escala

## 🎯 Visão do Projeto

O PCM é um Control Plane completo para grandes infraestruturas baseadas em clusters Proxmox, transformando o Proxmox em uma plataforma cloud completa.

```
Infraestrutura Base (Proxmox + Ceph + Networking)
                    ↓
    PCM – Proxmox Center Manager (Control Plane)
                    ↓
Tenants / Projects / VMs / Networks / Storage / Observability
```

## 🏗️ Arquitetura

### Separação de Planos

**CONTROL PLANE**
- PCM API
- PCM Scheduler
- PCM Tenant Manager
- PCM Database (PostgreSQL 18)
- PCM Observability
- OTEL Collector

**COMPUTE PLANE**
- Proxmox Cluster 1
- Proxmox Cluster 2
- Proxmox Cluster N

## 🚀 Stack Tecnológica

### Backend
- **Framework:** FastAPI (Python 3.12+)
- **Database:** PostgreSQL 18
- **ORM:** SQLAlchemy 2
- **Queue:** Redis/NATS
- **Workers:** Celery/Dramatiq
- **Observability:** OpenTelemetry

### Frontend
- **Framework:** Nuxt 3
- **UI Framework:** Nuxt UI
- **Styling:** Tailwind CSS
- **Build:** Vite

### Infraestrutura
- **Storage:** Ceph
- **Networking:** SDN
- **Billing:** Lago (Open Source)

## 📦 Repositório

GitHub: https://github.com/rsdenck/pcm

## 📁 Estrutura do Projeto

```
pcm/
├── services/
│   ├── api/              # PCM API principal
│   ├── scheduler/        # Agendador de tarefas
│   ├── tenant/           # Gerenciamento de tenants
│   ├── compute/          # Gerenciamento de VMs
│   ├── storage/          # Gerenciamento de storage
│   └── network/          # Gerenciamento de redes
├── core/
│   ├── database/         # Configuração do banco
│   ├── config/           # Configurações globais
│   ├── auth/             # Autenticação
│   └── events/           # Sistema de eventos
├── workers/
│   ├── provisioning/     # Workers de provisionamento
│   ├── monitoring/       # Workers de monitoramento
│   └── telemetry/        # Workers de telemetria
├── sdk/
│   └── proxmox/          # SDK para Proxmox API
└── frontend/             # Nuxt application
```

## 🎨 Design System

### Brand Colors
- `brand-orange`: #ff7a00
- `brand-black`: #000000
- `brand-dark`: #0a0a0a
- `brand-card`: #111111

## 👥 Tipos de Usuários

- **Provider Admin:** Administrador da plataforma
- **Tenant Admin:** Administrador do tenant
- **Tenant User:** Usuário do tenant

## 🔄 Fluxo de Provisionamento

```
User → PCM UI → PCM API → Scheduler → Node → Proxmox API → VM criada
```

## 📊 Microserviços

- `pcm-api`: API principal
- `pcm-scheduler`: Agendador
- `pcm-tenant`: Gerenciamento de tenants
- `pcm-compute`: Gerenciamento de compute
- `pcm-storage`: Gerenciamento de storage
- `pcm-network`: Gerenciamento de redes
- `pcm-telemetry`: Telemetria
- `pcm-auth`: Autenticação

## 🎯 Objetivo Final

Transformar o Proxmox em uma plataforma cloud completa, similar a:
- VMware vCloud Director
- OpenStack Control Plane

Com recursos de:
- Multi-Cluster Management
- Multi-Tenant Cloud
- Ceph Native Storage
- Observabilidade nativa
- Provisionamento automatizado
- Controle centralizado de infraestrutura

---

Desenvolvido com foco em escalabilidade, performance e isolamento enterprise.
