# ROADMAP.md

# PCM — Proxmox Center Manager
Cloud Control Plane for Proxmox Infrastructure

Version: 0.1  
Status: Architecture Definition

---------------------------------------------------------------------

# 1. INTRODUÇÃO

PCM (Proxmox Center Manager) é uma plataforma de **Control Plane Cloud** projetada para gerenciar grandes ambientes baseados em Proxmox.

O objetivo do PCM é transformar clusters do Proxmox em uma **infraestrutura cloud multi-tenant**, semelhante ao que plataformas como VMware vCloud Director, Apache CloudStack e OpenStack fazem.

O PCM atua como uma camada superior de orquestração e gerenciamento, permitindo:

- Multi-tenancy real
- Orquestração de recursos
- Observabilidade completa
- Balanceamento automático
- Gestão multi-datacenter
- Automação de infraestrutura
- Scheduler inteligente
- Catálogo de serviços
- Integração com Ceph
- Integração com Proxmox SDN
- Billing baseado em uso

Arquitetura conceitual:

```
Users
│
▼
PCM (Control Plane)
│
▼
Proxmox Clusters (Compute Plane)
```

---------------------------------------------------------------------

# 2. OBJETIVO DO PCM

Resolver limitações atuais do Proxmox:

- ausência de control plane cloud
- ausência de multi-tenant avançado
- falta de scheduler inteligente
- falta de observabilidade unificada
- ausência de billing
- ausência de gestão multi datacenter

O PCM adiciona uma camada que permite:

- orquestração global
- governança de infraestrutura
- automação cloud-native

---------------------------------------------------------------------

# 3. STACK TECNOLÓGICA

## Backend
- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy 2

## Database
- PostgreSQL 18

## Message Queue
- Redis ou NATS

## Workers
- Celery

## Observabilidade
- OpenTelemetry

## Frontend
- Nuxt Framework
- Nuxt UI
- Vue
- Tailwind CSS

## Billing
- Lago

## Infraestrutura
- Proxmox VE
- Ceph Storage
- Proxmox SDN

---------------------------------------------------------------------

# 4. MODELO DE ARQUITETURA

O PCM separa dois planos fundamentais:

- CONTROL PLANE
- Compute Plane

Arquitetura geral:

```
USERS
│
▼
PCM UI
(Nuxt + Tailwind)
│
▼
PCM API
│
┌────────────┼────────────┐
│            │            │
Scheduler   Observability   Automation
│            │            │
└────────────┼────────────┘
│
Resource Manager
│
Proxmox API
│
Proxmox Clusters
(Compute Plane)
```

---------------------------------------------------------------------

# 5. COMPONENTES PRINCIPAIS

## PCM API

Interface central da plataforma.

Responsável por:
- autenticação
- gerenciamento de tenants
- gerenciamento de clusters
- orquestração de recursos

---------------------------------------------------------------------

## Scheduler

Responsável por escolher onde executar workloads.

Critérios:
- cpu load
- ram disponível
- latência de storage
- latência de rede
- afinidade de tenant
- anti-affinity

Fluxo:
```
User
→ PCM API
→ Scheduler
→ Node escolhido
→ Proxmox API
```

---------------------------------------------------------------------

## Resource Manager

Cérebro da plataforma.

Responsável por:
- ciclo de vida de recursos
- validação de quotas
- execução de workflows
- orquestração de serviços

Recursos gerenciados:
- VMs
- Volumes
- Snapshots
- Networks
- Floating IPs
- Templates

---------------------------------------------------------------------

## Observability Service

Baseado em OpenTelemetry.

Coleta:
- vm cpu
- vm ram
- disk io
- network throughput
- ceph usage
- node health
- cluster status

Pipeline:
```
Proxmox Nodes
↓
OTEL Agents
↓
OTEL Collector
↓
PCM Telemetry
```

Permite:
- capacity planning
- anomaly detection
- alerting

---------------------------------------------------------------------

## Automation Engine

Executa workflows automatizados.

Exemplos:
- create_vm
- resize_disk
- snapshot
- migration

Todas operações são executadas como **tasks assíncronas**.

---------------------------------------------------------------------

## Patch Manager

Responsável por atualização automatizada de nodes.

Workflow:
1. drain node
2. migrate VMs
3. apply updates
4. reboot node
5. restore node

Permite atualizações sem downtime.

---------------------------------------------------------------------

# 6. MODELO MULTI-TENANT

Hierarquia principal:

```
Provider
├── Tenants
│       ├── Projects
│       ├── Users
│       └── Quotas
│
└── Infrastructure
    ├── Proxmox Clusters
    ├── Nodes
    ├── Ceph Storage
    └── SDN
```

---------------------------------------------------------------------

# 7. TENANTS

Representam organizações ou empresas.

Propriedades:
- tenant_name
- tenant_id
- cpu_quota
- ram_quota
- storage_quota
- network_quota
- billing_account

Configurações adicionais:
- allowed_templates
- allowed_regions
- allowed_storage_classes

---------------------------------------------------------------------

# 8. PROJECTS (Virtual Datacenters)

Cada tenant pode possuir múltiplos projetos.

Exemplo:
```
Tenant: EmpresaX
Projects
  - Production
  - Development
  - Testing
```

Cada project define quotas próprias:
- cpu quota
- ram quota
- storage quota
- network quota

---------------------------------------------------------------------

# 9. USERS

Usuários pertencem a tenants.

Campos:
- username
- email
- password
- roles
- 2FA
- api_tokens
- ssh_keys

---------------------------------------------------------------------

# 10. RBAC

Controle de acesso baseado em roles.

Roles:
- provider_admin
- tenant_admin
- project_admin
- developer
- viewer

Permissões:
- create_vm
- delete_vm
- manage_network
- view_metrics
- create_snapshot

Modelo:
```
Role
└ permissions

User
└ role

Role
└ scope
```

Scopes:
- global
- tenant
- project
- resource

---------------------------------------------------------------------

# 11. CATÁLOGO

Catálogo de serviços.

Contém:
- VM Templates
- Container Images
- OS Images

També pode definir:

Instance Types
- small
  - 2 CPU
  - 4 GB RAM
- medium
  - 4 CPU
  - 8 GB RAM
- large
  - 8 CPU
  - 16 GB RAM

---------------------------------------------------------------------

# 12. QUOTAS

Sistema essencial para multi-tenant.

Tipos:
- cpu quota
- ram quota
- vm limit
- disk quota
- network quota

Aplicação:
- Tenant
- Project

---------------------------------------------------------------------

# 13. TASK SYSTEM

Todas operações são assíncronas.

Exemplos:
- create vm
- resize disk
- snapshot
- migration

Modelo de task:
- task_id
- status
- progress
- logs
- result

Status possíveis:
- pending
- running
- completed
- failed

---------------------------------------------------------------------

# 14. OBSERVABILIDADE

Dados coletados:
- vm cpu
- vm ram
- disk io
- network throughput
- ceph usage
- node health

Com suporte a:
- metrics
- logs
- traces
- alerts

Tecnologia:
- OpenTelemetry

---------------------------------------------------------------------

# 15. MULTI DATACENTER

Estrutura global:

```
Provider
└ Regions
  └ Datacenters
    └ Clusters
      └ Nodes
```

Exemplo:
```
Region: Brazil
  - DC: SP1
  - DC: RJ1
```

Permite:
- failover
- geo-distribution
- global resource pools

---------------------------------------------------------------------

# 16. GLOBAL RESOURCE POOL

Todos clusters podem ser agregados.

Exemplo:
```
Datacenter A
  - Cluster A1
  - Cluster A2

Datacenter B
  - Cluster B1
```

Para o usuário:
```
Global Cloud Pool
```

O scheduler decide onde executar.

---------------------------------------------------------------------

# 17. BILLING

Integração com Lago.

Cobrança baseada em:
- cpu hours
- ram hours
- storage usage
- network traffic

---------------------------------------------------------------------

# 18. BANCO DE DADOS

Principais tabelas:

- providers
- regions
- datacenters
- clusters
- nodes
- tenants
- projects
- users
- roles
- permissions
- vms
- volumes
- snapshots
- images
- templates
- networks
- floating_ips
- storage_pools
- instance_types
- catalog_items
- quotas
- tasks
- events
- metrics
- billing_usage

---------------------------------------------------------------------

# 19. MICROSERVIÇOS

Arquitetura baseada em serviços.

- pcm-api
- pcm-auth
- pcm-tenant
- pcm-scheduler
- pcm-resource-manager
- pcm-network
- pcm-storage
- pcm-telemetry
- pcm-automation
- pcm-patch
- pcm-catalog

---------------------------------------------------------------------

# 20. ROADMAP DE DESENVOLVIMENTO

## Fase 1 — Core Platform ✅ (CONCLUÍDO)
- ✅ API FastAPI
- ✅ Auth
- ✅ Tenant management
- ✅ RBAC
- ✅ Database schema
- ✅ Frontend Nuxt + Nuxt UI
- ✅ Dashboard principal

## Fase 2 — Infrastructure Integration (EM ANDAMENTO)
- ✅ integração Proxmox API
- ✅ gestão de clusters
- ✅ gestão de nodes
- ✅ gestão de storage
- ✅ módulo de backup (PBS integration)
  - ✅ modelos de dados (PBS Server, Datastore, Policy, Job, Snapshot)
  - ✅ testes property-based para validação
  - ✅ testes unitários abrangentes (110+ casos)
  - ✅ configuração e validação de políticas
  - ✅ gerenciamento de servidores PBS
  - ✅ monitoramento de saúde
  - ✅ sistema de configuração round-trip

## Fase 3 — Resource Management (PRÓXIMO)
- ⏳ criação de VMs
- ⏳ volumes
- ⏳ snapshots
- ⏳ networking

## Fase 4 — Scheduler
- ⏳ alocação automática
- ⏳ balanceamento de carga
- ⏳ migração automática

## Fase 5 — Observability
- ⏳ OTEL
- ⏳ métricas
- ⏳ dashboards

## Fase 6 — Multi Datacenter
- ⏳ regions
- ⏳ datacenters
- ⏳ resource pools

## Fase 7 — Automation
- ⏳ workflows
- ⏳ tasks
- ⏳ event system

## Fase 8 — Billing
- ⏳ integração Lago
- ⏳ métricas de consumo

---------------------------------------------------------------------

# 21. VISÃO FINAL

PCM transforma o Proxmox em uma plataforma cloud completa.

Arquitetura final:

```
Users
│
▼
PCM UI
│
▼
PCM Control Plane
│
▼
Proxmox Infrastructure
│
▼
Clusters + Ceph + SDN
```

PCM se posiciona como:

**Cloud Control Plane for Proxmox Infrastructure**

---------------------------------------------------------------------

## Status Atual do Projeto

**Versão**: 0.1.0  
**Data**: Março 2026  
**Status**: Fase 1 Concluída, Fase 2 em Andamento

### O que está funcionando:
- ✅ Backend API completo (FastAPI)
- ✅ Database PostgreSQL 18 configurado
- ✅ Frontend Nuxt 3 + Nuxt UI
- ✅ Sistema de autenticação
- ✅ Gerenciamento de Tenants
- ✅ Gerenciamento de Clusters
- ✅ Dashboard com métricas
- ✅ Interface enterprise completa
- ✅ Integração com Proxmox API
- ✅ Módulo de Backup completo
  - ✅ Integração nativa com Proxmox Backup Server (PBS)
  - ✅ Gerenciamento multi-tenant de backups
  - ✅ Políticas de backup automatizadas
  - ✅ Monitoramento de saúde em tempo real
  - ✅ Validação de configuração com property-based testing
  - ✅ Cobertura de testes abrangente (110+ casos de teste)
- ✅ CI/CD completo com GitHub Actions
  - ✅ Testes automatizados (backend/frontend)
  - ✅ Análise de segurança e qualidade de código
  - ✅ Performance monitoring
  - ✅ Deploy automatizado

### Próximos Passos:
1. Continuar implementação do módulo de backup
   - ⏳ Implementar agendador de backup
   - ⏳ Sistema de monitoramento e alertas
   - ⏳ Operações de restore
   - ⏳ Catálogo de backups e busca
   - ⏳ Endpoints da API REST
   - ⏳ Interface web para backup
2. Implementar criação de VMs via interface
3. Adicionar gerenciamento de volumes
4. Implementar snapshots
5. Desenvolver scheduler inteligente
6. Adicionar observabilidade com OpenTelemetry

---------------------------------------------------------------------

**Repositório**: https://github.com/rsdenck/pcm  
**Documentação**: README.md  
**Licença**: MIT
