<div align="center">

<img src="https://raw.githubusercontent.com/rsdenck/pcm/main/assets/pcm-logo.png" alt="PCM Logo" width="800"/>

<table>
<tr>
<td align="center" width="100%">

# PCM – Roadmap & Architecture

**Plano de Desenvolvimento e Arquitetura da Plataforma**

_"Transformando Proxmox em uma plataforma cloud completa."_

</td>
</tr>
</table>

<table>
<tr>
<td align="center">

[![Version](https://img.shields.io/badge/Version-0.1.0-000000?style=for-the-badge&logo=git&logoColor=ff7a00)](https://github.com/rsdenck/pcm)
[![Status](https://img.shields.io/badge/Status-Fase_2_Em_Andamento-000000?style=for-the-badge&logo=rocket&logoColor=ff7a00)](https://github.com/rsdenck/pcm)
[![Architecture](https://img.shields.io/badge/Architecture-Microserviços-000000?style=for-the-badge&logo=kubernetes&logoColor=ff7a00)](https://github.com/rsdenck/pcm)
[![License](https://img.shields.io/badge/License-MIT-000000?style=for-the-badge&logo=opensourceinitiative&logoColor=ff7a00)](LICENSE)

</td>
</tr>
</table>

</div>

---

## 🎯 Introdução

<div align="center">

![Cloud Control Plane](https://img.shields.io/badge/-Cloud_Control_Plane-000000?style=for-the-badge&logo=cloud&logoColor=ff7a00)

</div>

PCM (Proxmox Center Manager) é uma plataforma de **Control Plane Cloud** projetada para gerenciar grandes ambientes baseados em Proxmox.

O objetivo do PCM é transformar clusters do Proxmox em uma **infraestrutura cloud multi-tenant**, semelhante ao que plataformas como VMware vCloud Director, Apache CloudStack e OpenStack fazem.

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                    USERS & TENANTS                          │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 PCM CONTROL PLANE                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   API    │  │Scheduler │  │ Resource │  │Observ.   │     │
│  │ Gateway  │  │  Engine  │  │ Manager  │  │  Stack   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                PROXMOX COMPUTE PLANE                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Cluster 1 │  │Cluster 2 │  │Cluster 3 │  │Cluster N │     │
│  │ PVE/PBS  │  │ PVE/PBS  │  │ PVE/PBS  │  │ PVE/PBS  │     │
│  │   PMG    │  │   PMG    │  │   PMG    │  │   PMG    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

</div>

### Capacidades Principais

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

![Multi-Tenant](https://img.shields.io/badge/-Multi--Tenancy_Real-000000?style=for-the-badge&logo=users&logoColor=ff7a00)

Isolamento completo de tenants com controle de acesso baseado em funções (RBAC).

![Orchestration](https://img.shields.io/badge/-Orquestração_Global-000000?style=for-the-badge&logo=kubernetes&logoColor=ff7a00)

Orquestração de recursos distribuídos em múltiplos clusters e datacenters.

![Automation](https://img.shields.io/badge/-Automação_Completa-000000?style=for-the-badge&logo=robot&logoColor=ff7a00)

Automação de infraestrutura com workflows inteligentes e scheduler avançado.

</td>
<td valign="top" width="50%">

![Observability](https://img.shields.io/badge/-Observabilidade_Unificada-000000?style=for-the-badge&logo=grafana&logoColor=ff7a00)

Agregação de métricas, traces e logs baseada em OpenTelemetry.

![Multi-DC](https://img.shields.io/badge/-Multi--Datacenter-000000?style=for-the-badge&logo=server&logoColor=ff7a00)

Gestão multi-datacenter com failover automático e geo-distribuição.

![Billing](https://img.shields.io/badge/-Billing_Inteligente-000000?style=for-the-badge&logo=creditcard&logoColor=ff7a00)

Sistema de billing baseado em uso real com integração Lago.

</td>
</tr>
</table>

</div>

---

## 🎯 Objetivo do PCM

<div align="center">

### Problemas Resolvidos

<table>
<tr>
<td valign="top" width="50%">

### Limitações Atuais do Proxmox

![Problem](https://img.shields.io/badge/-Ausência_Control_Plane-000000?style=flat-square&logo=x&logoColor=ff0000)

Falta de camada de orquestração cloud nativa

![Problem](https://img.shields.io/badge/-Multi--Tenant_Limitado-000000?style=flat-square&logo=x&logoColor=ff0000)

Isolamento básico sem governança avançada

![Problem](https://img.shields.io/badge/-Scheduler_Simples-000000?style=flat-square&logo=x&logoColor=ff0000)

Ausência de scheduler inteligente para workloads

![Problem](https://img.shields.io/badge/-Observabilidade_Fragmentada-000000?style=flat-square&logo=x&logoColor=ff0000)

Métricas e logs não unificados

</td>
<td valign="top" width="50%">

### Soluções do PCM

![Solution](https://img.shields.io/badge/-Control_Plane_Enterprise-000000?style=flat-square&logo=checkmarx&logoColor=00ff00)

Orquestração global com governança completa

![Solution](https://img.shields.io/badge/-Multi--Tenancy_Avançado-000000?style=flat-square&logo=checkmarx&logoColor=00ff00)

Isolamento completo com RBAC granular

![Solution](https://img.shields.io/badge/-Scheduler_Inteligente-000000?style=flat-square&logo=checkmarx&logoColor=00ff00)

Alocação automática baseada em ML e métricas

![Solution](https://img.shields.io/badge/-Observabilidade_Unificada-000000?style=flat-square&logo=checkmarx&logoColor=00ff00)

Stack completo com OpenTelemetry

</td>
</tr>
</table>

</div>

---

## 🛠️ Stack Tecnológica

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

### Stack Backend

![Python](https://img.shields.io/badge/Python_3.12+-000000?style=for-the-badge&logo=python&logoColor=ff7a00)
![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=for-the-badge&logo=fastapi&logoColor=ff7a00)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy_2-000000?style=for-the-badge&logo=python&logoColor=ff7a00)
![Pydantic](https://img.shields.io/badge/Pydantic-000000?style=for-the-badge&logo=python&logoColor=ff7a00)
![Celery](https://img.shields.io/badge/Celery-000000?style=for-the-badge&logo=celery&logoColor=ff7a00)
![AsyncIO](https://img.shields.io/badge/AsyncIO-000000?style=for-the-badge&logo=python&logoColor=ff7a00)

**Observabilidade**

![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000000?style=for-the-badge&logo=opentelemetry&logoColor=ff7a00)
![Prometheus](https://img.shields.io/badge/Prometheus-000000?style=for-the-badge&logo=prometheus&logoColor=ff7a00)

</td>
<td valign="top" width="50%">

### Stack Frontend

![Nuxt](https://img.shields.io/badge/Nuxt_3-000000?style=for-the-badge&logo=nuxt.js&logoColor=ff7a00)
![Vue](https://img.shields.io/badge/Vue_3-000000?style=for-the-badge&logo=vue.js&logoColor=ff7a00)
![Nuxt_UI](https://img.shields.io/badge/Nuxt_UI-000000?style=for-the-badge&logo=nuxt.js&logoColor=ff7a00)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-000000?style=for-the-badge&logo=tailwindcss&logoColor=ff7a00)
![TypeScript](https://img.shields.io/badge/TypeScript-000000?style=for-the-badge&logo=typescript&logoColor=ff7a00)

**Infraestrutura**

![PostgreSQL](https://img.shields.io/badge/PostgreSQL_18-000000?style=for-the-badge&logo=postgresql&logoColor=ff7a00)
![Redis](https://img.shields.io/badge/Redis_7-000000?style=for-the-badge&logo=redis&logoColor=ff7a00)
![Lago](https://img.shields.io/badge/Lago_Billing-000000?style=for-the-badge&logo=creditcard&logoColor=ff7a00)

</td>
</tr>
</table>

</div>

---

## 🏗️ Arquitetura de Microserviços

<div align="center">

### Design de Separação de Planos

| Plano | Responsabilidade | Tecnologia |
|-------|------------------|------------|
| ![Control Plane](https://img.shields.io/badge/-Control_Plane-000000?style=flat-square&logo=kubernetes&logoColor=ff7a00) | Orquestração, Governança, APIs | PCM Stack |
| ![Compute Plane](https://img.shields.io/badge/-Compute_Plane-000000?style=flat-square&logo=server&logoColor=ff7a00) | Execução de Workloads | Proxmox VE |

</div>

### Arquitetura Geral

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                      USERS                                  │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   PCM UI                                    │
│              (Nuxt + Tailwind)                              │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   PCM API                                   │
└─────┬─────────────┬─────────────┬─────────────┬─────────────┘
      ▼             ▼             ▼             ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Scheduler │ │Observ.   │ │Automation│ │ Resource │
│  Engine  │ │  Stack   │ │  Engine  │ │ Manager  │
└─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘
      └─────────────┼─────────────┼─────────────┘
                    ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                 Proxmox API                                 │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Proxmox Clusters                               │
│                (Compute Plane)                              │
└─────────────────────────────────────────────────────────────┘
```

</div>

### Microserviços PCM

<div align="center">

| Serviço | Propósito | Tecnologia | Status |
|---------|-----------|------------|--------|
| ![API](https://img.shields.io/badge/-API_Gateway-000000?style=flat-square&logo=fastapi&logoColor=ff7a00) | API Principal & WebSocket | FastAPI | ✅ |
| ![Auth](https://img.shields.io/badge/-Auth_Service-000000?style=flat-square&logo=shield&logoColor=ff7a00) | Autenticação & RBAC | FastAPI | ✅ |
| ![Tenant](https://img.shields.io/badge/-Tenant_Manager-000000?style=flat-square&logo=users&logoColor=ff7a00) | Multi-tenancy | FastAPI | ✅ |
| ![Scheduler](https://img.shields.io/badge/-Scheduler-000000?style=flat-square&logo=clockify&logoColor=ff7a00) | Agendamento Inteligente | Celery Beat | ⏳ |
| ![Resource](https://img.shields.io/badge/-Resource_Manager-000000?style=flat-square&logo=server&logoColor=ff7a00) | Operações VM/Container | AsyncIO | ⏳ |
| ![Storage](https://img.shields.io/badge/-Storage_Manager-000000?style=flat-square&logo=database&logoColor=ff7a00) | Operações de Storage | Ceph API | ⏳ |
| ![Network](https://img.shields.io/badge/-Network_Manager-000000?style=flat-square&logo=cisco&logoColor=ff7a00) | Gerenciamento SDN | Proxmox SDN | ⏳ |
| ![Backup](https://img.shields.io/badge/-Backup_Manager-000000?style=flat-square&logo=shield&logoColor=ff7a00) | Backup & Recovery | PBS API | ✅ |
| ![Telemetry](https://img.shields.io/badge/-Telemetry-000000?style=flat-square&logo=grafana&logoColor=ff7a00) | Coleta de Métricas | OTEL | ⏳ |

</div>

---



## 🚀 Roadmap de Desenvolvimento

<div align="center">

### Status Atual: **Fase 2 - Infrastructure Integration** ⏳

![Progress](https://img.shields.io/badge/Progresso_Geral-65%25-000000?style=for-the-badge&logo=rocket&logoColor=ff7a00)

</div>

### Fase 1 — Core Platform ✅ **CONCLUÍDO**

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

#### Backend Core ✅

![API](https://img.shields.io/badge/-API_FastAPI-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Auth](https://img.shields.io/badge/-Autenticação-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Tenant](https://img.shields.io/badge/-Tenant_Management-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![RBAC](https://img.shields.io/badge/-RBAC-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Database](https://img.shields.io/badge/-Database_Schema-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

</td>
<td valign="top" width="50%">

#### Frontend Core ✅

![Frontend](https://img.shields.io/badge/-Frontend_Nuxt_3-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![UI](https://img.shields.io/badge/-Nuxt_UI-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Dashboard](https://img.shields.io/badge/-Dashboard_Principal-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![CI/CD](https://img.shields.io/badge/-CI/CD_GitHub_Actions-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

</td>
</tr>
</table>

</div>

### Fase 2 — Infrastructure Integration ⏳ **EM ANDAMENTO**

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

#### Integração Proxmox ✅

![Proxmox](https://img.shields.io/badge/-Integração_Proxmox_API-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Clusters](https://img.shields.io/badge/-Gestão_de_Clusters-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Nodes](https://img.shields.io/badge/-Gestão_de_Nodes-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Storage](https://img.shields.io/badge/-Gestão_de_Storage-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

</td>
<td valign="top" width="50%">

#### Módulo de Backup ✅

![PBS](https://img.shields.io/badge/-PBS_Integration-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Models](https://img.shields.io/badge/-Modelos_de_Dados-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Tests](https://img.shields.io/badge/-Property_Tests-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Unit Tests](https://img.shields.io/badge/-110+_Unit_Tests-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Config](https://img.shields.io/badge/-Sistema_Configuração-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

![Health](https://img.shields.io/badge/-Monitoramento_Saúde-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) **Completo**

</td>
</tr>
</table>

</div>

#### Frontend Security & Authentication ⏳

<div align="center">

| Task | Descrição | Status |
|------|-----------|--------|
| ![Task](https://img.shields.io/badge/-1.1-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) | Authentication Infrastructure & Services | ✅ **CONCLUÍDO** |
| ![Task](https://img.shields.io/badge/-1.2-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) | Login & Authentication UI | ✅ **CONCLUÍDO** |
| ![Task](https://img.shields.io/badge/-1.3-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) | Protected Routes & Access Control | ✅ **CONCLUÍDO** |
| ![Task](https://img.shields.io/badge/-1.4-000000?style=flat-square&logo=code&logoColor=ff7a00) | Role-Based Access Control (RBAC) | ⏳ **EM PROGRESSO** |
| ![Task](https://img.shields.io/badge/-1.5-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) | Input Validation & Sanitization | ⏳ **PENDENTE** |

</div>

#### Próximas Tasks do Módulo de Backup ⏳

<div align="center">

| Task | Descrição | Status |
|------|-----------|--------|
| ![Task](https://img.shields.io/badge/-3.2-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) | Property test para configuration round-trip | ✅ **CONCLUÍDO** |
| ![Task](https://img.shields.io/badge/-5.3-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) | Property test para PBS server health monitoring | ✅ **CONCLUÍDO** |
| ![Task](https://img.shields.io/badge/-5.4-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) | Unit tests para PBS server management | ✅ **CONCLUÍDO** |
| ![Task](https://img.shields.io/badge/-6.2-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) | Implementar backup job execution | ✅ **CONCLUÍDO** |
| ![Task](https://img.shields.io/badge/-6.3-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) | Property test para backup scheduling | ✅ **CONCLUÍDO** |
| ![Task](https://img.shields.io/badge/-6.4-000000?style=flat-square&logo=code&logoColor=ff7a00) | Unit tests para backup scheduler | ⏳ **PRÓXIMO** |

</div>

### Fase 3 — Resource Management ⏳ **PRÓXIMO**

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

#### VM Management ⏳

![VM Create](https://img.shields.io/badge/-Criação_de_VMs-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![VM Lifecycle](https://img.shields.io/badge/-Ciclo_de_Vida_VM-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Templates](https://img.shields.io/badge/-Templates-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

</td>
<td valign="top" width="50%">

#### Storage & Network ⏳

![Volumes](https://img.shields.io/badge/-Volumes-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Snapshots](https://img.shields.io/badge/-Snapshots-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Networking](https://img.shields.io/badge/-Networking-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

</td>
</tr>
</table>

</div>

### Fase 4 — Scheduler ⏳

<div align="center">

![Scheduler](https://img.shields.io/badge/-Alocação_Automática-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Load Balancing](https://img.shields.io/badge/-Balanceamento_de_Carga-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Migration](https://img.shields.io/badge/-Migração_Automática-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

</div>

### Fase 5 — Observability ⏳

<div align="center">

![OTEL](https://img.shields.io/badge/-OpenTelemetry-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Metrics](https://img.shields.io/badge/-Métricas-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Dashboards](https://img.shields.io/badge/-Dashboards-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

</div>

### Fase 6 — Multi Datacenter ⏳

<div align="center">

![Regions](https://img.shields.io/badge/-Regions-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Datacenters](https://img.shields.io/badge/-Datacenters-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Resource Pools](https://img.shields.io/badge/-Resource_Pools-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

</div>

### Fase 7 — Automation ⏳

<div align="center">

![Workflows](https://img.shields.io/badge/-Workflows-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Tasks](https://img.shields.io/badge/-Tasks-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Events](https://img.shields.io/badge/-Event_System-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

</div>

### Fase 8 — Billing ⏳

<div align="center">

![Lago](https://img.shields.io/badge/-Integração_Lago-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

![Usage](https://img.shields.io/badge/-Métricas_de_Consumo-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) **Pendente**

</div>

---

## 📊 Status Atual do Projeto

<div align="center">

<table>
<tr>
<td align="center" width="100%">

**Versão**: 0.1.0 | **Data**: Março 2026 | **Status**: Fase 2 em Andamento

</td>
</tr>
</table>

</div>

### ✅ O que está funcionando:

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

#### Core Platform ✅

![Backend](https://img.shields.io/badge/-Backend_API_Completo-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) FastAPI

![Database](https://img.shields.io/badge/-PostgreSQL_18_Configurado-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Database

![Frontend](https://img.shields.io/badge/-Frontend_Nuxt_3-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) + Nuxt UI

![Auth](https://img.shields.io/badge/-Sistema_Autenticação-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Completo

![Tenants](https://img.shields.io/badge/-Gerenciamento_Tenants-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Multi-tenant

![Clusters](https://img.shields.io/badge/-Gerenciamento_Clusters-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Proxmox

![Dashboard](https://img.shields.io/badge/-Dashboard_Métricas-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Enterprise

![Integration](https://img.shields.io/badge/-Integração_Proxmox_API-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Completa

</td>
<td valign="top" width="50%">

#### Módulo de Backup ✅

![PBS](https://img.shields.io/badge/-Integração_PBS_Nativa-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Proxmox Backup Server

![Multi-Tenant](https://img.shields.io/badge/-Backup_Multi--Tenant-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Isolamento Completo

![Policies](https://img.shields.io/badge/-Políticas_Automatizadas-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Agendamento

![Health](https://img.shields.io/badge/-Monitoramento_Tempo_Real-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Health Checks

![Property Tests](https://img.shields.io/badge/-Property--Based_Testing-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Validação

![Unit Tests](https://img.shields.io/badge/-110+_Casos_de_Teste-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Cobertura

![CI/CD](https://img.shields.io/badge/-CI/CD_GitHub_Actions-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Completo

![Security](https://img.shields.io/badge/-Análise_Segurança-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) Automatizada

</td>
</tr>
</table>

</div>

### ⏳ Próximos Passos:

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

#### Backup Module (Continuação) ⏳

1. ![Task](https://img.shields.io/badge/-Property_Tests-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) Configuration round-trip
2. ![Task](https://img.shields.io/badge/-Agendador_Backup-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) Scheduler engine
3. ![Task](https://img.shields.io/badge/-Monitoramento_Alertas-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) Monitoring system
4. ![Task](https://img.shields.io/badge/-Operações_Restore-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) Restore operations
5. ![Task](https://img.shields.io/badge/-Catálogo_Busca-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) Backup catalog

</td>
<td valign="top" width="50%">

#### Resource Management ⏳

6. ![Task](https://img.shields.io/badge/-Endpoints_API_REST-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) REST API endpoints
7. ![Task](https://img.shields.io/badge/-Interface_Web_Backup-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) Web interface
8. ![Task](https://img.shields.io/badge/-Criação_VMs_Interface-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) VM creation
9. ![Task](https://img.shields.io/badge/-Gerenciamento_Volumes-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) Volume management
10. ![Task](https://img.shields.io/badge/-Scheduler_Inteligente-000000?style=flat-square&logo=hourglass&logoColor=ff7a00) Smart scheduler

</td>
</tr>
</table>

</div>

---

## 🎯 Visão Final

<div align="center">

### Transformação Completa

PCM transforma o Proxmox em uma **plataforma cloud enterprise completa**.

```
┌─────────────────────────────────────────────────────────────┐
│                      USERS                                  │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   PCM UI                                    │
│              (Cloud Dashboard)                              │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               PCM Control Plane                             │
│    (Orquestração + Governança + Automação)                  │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            Proxmox Infrastructure                           │
│         (Clusters + Ceph + SDN + PBS)                       │
└─────────────────────────────────────────────────────────────┘
```

### Posicionamento

![Cloud Control Plane](https://img.shields.io/badge/-Cloud_Control_Plane_for_Proxmox_Infrastructure-000000?style=for-the-badge&logo=cloud&logoColor=ff7a00)

</div>

---

<div align="center">

### Filosofia do Projeto

_"Se não é monitorado, não existe."_

_"Se é repetitivo, deve ser automatizado."_

_"Infraestrutura não é arte. É engenharia."_

---

**[Repositório](https://github.com/rsdenck/pcm)** • **[Documentação](SETUP.md)** • **[API Reference](http://192.168.130.10:8000/docs)**

Construído com precisão para gerenciamento de infraestrutura enterprise

[![GitHub](https://img.shields.io/badge/-rsdenck-000000?style=for-the-badge&logo=github&logoColor=ff7a00)](https://github.com/rsdenck)

</div>
