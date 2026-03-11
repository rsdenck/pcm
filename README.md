<div align="center">

<img src="https://raw.githubusercontent.com/rsdenck/pcm/main/assets/pcm-logo.png" alt="PCM Logo" width="800"/>

<table>
<tr>
<td align="center" width="100%">

# PCM – Proxmox Center Manager

**Plano de Controle Cloud para Infraestrutura Proxmox Enterprise**

_"Transformando Proxmox em uma plataforma cloud completa."_

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

**[🇧🇷 Português](#visão-geral)** • **[🇺🇸 English](README.en.md)**

[Recursos](#recursos) • [Arquitetura](#arquitetura) • [Início Rápido](#início-rápido) • [Documentação](#documentação) • [Laboratório](#configuração-do-laboratório)

</td>
</tr>
</table>

</div>

---

## Visão Geral

PCM (Proxmox Center Manager) é um **Plano de Controle Cloud de nível enterprise** que transforma a infraestrutura Proxmox VE em uma plataforma cloud completa. Construído para implantações em larga escala com gerenciamento multi-cluster, multi-tenancy e automação completa.

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                 PLANO DE CONTROLE (PCM)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   API    │  │Agendador │  │ Tenant   │  │Observ.   │     │
│  │ Gateway  │  │  Tarefas │  │ Manager  │  │  Stack   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   PLANO DE COMPUTAÇÃO                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Cluster 1 │  │Cluster 2 │  │Cluster 3 │  │Cluster N │     │
│  │ PVE/PBS  │  │ PVE/PBS  │  │ PVE/PBS  │  │ PVE/PBS  │     │
│  │   PMG    │  │   PMG    │  │   PMG    │  │   PMG    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

</div>

---

## Recursos

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

### Capacidades Principais

![Multi-Cluster](https://img.shields.io/badge/-Gerenciamento_Multi--Cluster-000000?style=for-the-badge&logo=server&logoColor=ff7a00)

Controle centralizado de múltiplos clusters Proxmox em diferentes sites e regiões.

![Multi-Tenancy](https://img.shields.io/badge/-Multi--Tenancy-000000?style=for-the-badge&logo=users&logoColor=ff7a00)

Isolamento completo de tenants com controle de acesso baseado em funções (RBAC).

![Automation](https://img.shields.io/badge/-Provisionamento_Automatizado-000000?style=for-the-badge&logo=robot&logoColor=ff7a00)

Deploy assíncrono de VMs/Containers com gerenciamento inteligente de filas.

![Observability](https://img.shields.io/badge/-Observabilidade_Unificada-000000?style=for-the-badge&logo=grafana&logoColor=ff7a00)

Agregação de métricas, traces e logs baseada em OpenTelemetry.

</td>
<td valign="top" width="50%">

### Recursos da Plataforma

![SDN](https://img.shields.io/badge/-Integração_SDN-000000?style=for-the-badge&logo=cisco&logoColor=ff7a00)

Suporte nativo para Software-Defined Networking.

![Ceph](https://img.shields.io/badge/-Storage_Ceph-000000?style=for-the-badge&logo=ceph&logoColor=ff7a00)

Gerenciamento e monitoramento de storage Ceph de primeira classe.

![API](https://img.shields.io/badge/-API_RESTful-000000?style=for-the-badge&logo=fastapi&logoColor=ff7a00)

Cobertura completa de API com documentação OpenAPI.

![UI](https://img.shields.io/badge/-Dashboard_Moderno-000000?style=for-the-badge&logo=vue.js&logoColor=ff7a00)

Interface web responsiva construída com Nuxt 3.

</td>
</tr>
</table>

</div>

---

## Stack Tecnológica

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
![Vite](https://img.shields.io/badge/Vite-000000?style=for-the-badge&logo=vite&logoColor=ff7a00)

**Infraestrutura**

![PostgreSQL](https://img.shields.io/badge/PostgreSQL_18-000000?style=for-the-badge&logo=postgresql&logoColor=ff7a00)
![Redis](https://img.shields.io/badge/Redis_7-000000?style=for-the-badge&logo=redis&logoColor=ff7a00)

</td>
</tr>
</table>

</div>

---

## Arquitetura

<div align="center">

### Design de Microserviços

| Serviço | Propósito | Tecnologia |
|---------|-----------|------------|
| ![API](https://img.shields.io/badge/-API_Gateway-000000?style=flat-square&logo=fastapi&logoColor=ff7a00) | API Principal & WebSocket | FastAPI |
| ![Scheduler](https://img.shields.io/badge/-Agendador-000000?style=flat-square&logo=clockify&logoColor=ff7a00) | Agendamento de Tarefas | Celery Beat |
| ![Tenant](https://img.shields.io/badge/-Gerenciador_Tenant-000000?style=flat-square&logo=users&logoColor=ff7a00) | Multi-tenancy | FastAPI |
| ![Compute](https://img.shields.io/badge/-Gerenciador_Compute-000000?style=flat-square&logo=server&logoColor=ff7a00) | Operações VM/Container | AsyncIO |
| ![Storage](https://img.shields.io/badge/-Gerenciador_Storage-000000?style=flat-square&logo=database&logoColor=ff7a00) | Operações de Storage | Ceph API |
| ![Network](https://img.shields.io/badge/-Gerenciador_Network-000000?style=flat-square&logo=cisco&logoColor=ff7a00) | Gerenciamento SDN | Proxmox SDN |
| ![Telemetry](https://img.shields.io/badge/-Telemetria-000000?style=flat-square&logo=grafana&logoColor=ff7a00) | Coleta de Métricas | OTEL |

</div>

---

## Início Rápido

<div align="center">

### Pré-requisitos

![Python](https://img.shields.io/badge/Python-3.12+-000000?style=flat-square&logo=python&logoColor=ff7a00)
![Node](https://img.shields.io/badge/Node.js-20+-000000?style=flat-square&logo=node.js&logoColor=ff7a00)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-000000?style=flat-square&logo=postgresql&logoColor=ff7a00)
![Redis](https://img.shields.io/badge/Redis-7-000000?style=flat-square&logo=redis&logoColor=ff7a00)
![Proxmox](https://img.shields.io/badge/Proxmox-VE_8+-000000?style=flat-square&logo=proxmox&logoColor=ff7a00)

</div>

### Instalação (Windows)

```bash
# 1. Setup Backend
setup-backend.bat

# 2. Configurar ambiente
# Editar pcm/.env com suas configurações

# 3. Executar migrations
cd pcm
venv\Scripts\activate
alembic upgrade head

# 4. Setup Frontend
setup-frontend.bat

# 5. Iniciar todos os serviços
start-all.bat
```

### Pontos de Acesso

<div align="center">

| Serviço | URL | Descrição |
|---------|-----|-----------|
| ![Frontend](https://img.shields.io/badge/-Frontend-000000?style=flat-square&logo=vue.js&logoColor=ff7a00) | http://192.168.130.10:9000 | Dashboard Web |
| ![API](https://img.shields.io/badge/-API-000000?style=flat-square&logo=fastapi&logoColor=ff7a00) | http://192.168.130.10:8000 | REST API |
| ![Docs](https://img.shields.io/badge/-API_Docs-000000?style=flat-square&logo=swagger&logoColor=ff7a00) | http://192.168.130.10:8000/docs | Swagger UI |
| ![ReDoc](https://img.shields.io/badge/-ReDoc-000000?style=flat-square&logo=readthedocs&logoColor=ff7a00) | http://192.168.130.10:8000/redoc | Documentação API |

</div>

---

## Configuração do Laboratório

<div align="center">

### Configuração do Cluster de Desenvolvimento

**Cluster de Desenvolvimento PROXMON**

| Node | IP | Função | Status |
|------|-----|--------|--------|
| ![PVE-01](https://img.shields.io/badge/-PVE--01-000000?style=flat-square&logo=proxmox&logoColor=ff7a00) | 192.168.130.20 | Primário | ![Online](https://img.shields.io/badge/-Online-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) |
| ![PVE-02](https://img.shields.io/badge/-PVE--02-000000?style=flat-square&logo=proxmox&logoColor=ff7a00) | 192.168.130.21 | Secundário | ![Online](https://img.shields.io/badge/-Online-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) |
| ![PVE-03](https://img.shields.io/badge/-PVE--03-000000?style=flat-square&logo=proxmox&logoColor=ff7a00) | 192.168.130.22 | Terciário | ![Online](https://img.shields.io/badge/-Online-000000?style=flat-square&logo=checkmarx&logoColor=00ff00) |

</div>

### Inicializar Cluster de Laboratório

```bash
cd pcm
venv\Scripts\activate
python ../init-lab-cluster.py
```

Veja [LAB.md](LAB.md) para detalhes completos da configuração do laboratório.

---

## Documentação

<div align="center">

| Documento | Descrição |
|-----------|-----------|
| ![Quick Start](https://img.shields.io/badge/-Início_Rápido-000000?style=flat-square&logo=rocket&logoColor=ff7a00) | [QUICKSTART.md](QUICKSTART.md) |
| ![Setup Guide](https://img.shields.io/badge/-Guia_Setup-000000?style=flat-square&logo=book&logoColor=ff7a00) | [SETUP.md](SETUP.md) |
| ![Deployment](https://img.shields.io/badge/-Deployment-000000?style=flat-square&logo=kubernetes&logoColor=ff7a00) | [DEPLOY.md](DEPLOY.md) |
| ![Migration](https://img.shields.io/badge/-Migração-000000?style=flat-square&logo=git&logoColor=ff7a00) | [MIGRATION.md](MIGRATION.md) |
| ![Lab Config](https://img.shields.io/badge/-Config_Lab-000000?style=flat-square&logo=proxmox&logoColor=ff7a00) | [LAB.md](LAB.md) |

</div>

---

## Funções de Usuário

<div align="center">

| Função | Permissões | Badge |
|--------|------------|-------|
| Provider Admin | Acesso completo à plataforma | ![Admin](https://img.shields.io/badge/-Provider_Admin-000000?style=flat-square&logo=shield&logoColor=ff7a00) |
| Tenant Admin | Gerenciamento nível tenant | ![Tenant](https://img.shields.io/badge/-Tenant_Admin-000000?style=flat-square&logo=users&logoColor=ff7a00) |
| Tenant User | Consumo de recursos | ![User](https://img.shields.io/badge/-Tenant_User-000000?style=flat-square&logo=user&logoColor=ff7a00) |

</div>

---

## Roadmap

<div align="center">

<table>
<tr>
<td valign="top" width="50%">

### Concluído

- [x] Implementação da API core
- [x] Suporte multi-cluster
- [x] Gerenciamento de tenants
- [x] Provisionamento assíncrono
- [x] Gerenciamento de storage
- [x] Sincronização VM/Container
- [x] Dashboard UI moderno

</td>
<td valign="top" width="50%">

### Em Progresso

- [ ] RBAC avançado
- [ ] Integração billing (Lago)
- [ ] Automação de backup
- [ ] Visualização topologia rede
- [ ] Analytics de custos
- [ ] Provider Terraform
- [ ] Integração Kubernetes

</td>
</tr>
</table>

</div>

---

## Estrutura do Projeto

```
pcm/
├── services/          # Microserviços
│   ├── api/          # API principal
│   ├── scheduler/    # Agendamento tarefas
│   ├── tenant/       # Gerenciamento tenant
│   ├── compute/      # Operações VM/Container
│   ├── storage/      # Gerenciamento storage
│   └── network/      # Gerenciamento rede
├── core/             # Componentes core
│   ├── database/     # Configuração DB
│   ├── config/       # Configurações
│   ├── auth/         # Autenticação
│   └── events/       # Sistema eventos
├── workers/          # Workers background
│   ├── provisioning/ # Tarefas provisioning
│   ├── monitoring/   # Health checks
│   └── telemetry/    # Coleta métricas
└── sdk/              # SDKs
    └── proxmox/      # Cliente API Proxmox

pcmfe/                # Aplicação Nuxt 3
├── pages/            # Rotas
├── components/       # Componentes Vue
├── layouts/          # Layouts
└── assets/           # Assets estáticos
```

---

## Contribuindo

<div align="center">

Contribuições são bem-vindas! Por favor, siga estes passos:

1. Fork o repositório
2. Crie uma branch de feature (`git checkout -b feature/recurso-incrivel`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona recurso incrível'`)
4. Push para a branch (`git push origin feature/recurso-incrivel`)
5. Abra um Pull Request

</div>

---

## Licença

<div align="center">

[![License](https://img.shields.io/badge/License-MIT-000000?style=for-the-badge&logo=opensourceinitiative&logoColor=ff7a00)](LICENSE)

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

</div>

---

## Suporte

<div align="center">

[![Issues](https://img.shields.io/badge/-Issues-000000?style=for-the-badge&logo=github&logoColor=ff7a00)](https://github.com/rsdenck/pcm/issues)
[![Discussions](https://img.shields.io/badge/-Discussions-000000?style=for-the-badge&logo=github&logoColor=ff7a00)](https://github.com/rsdenck/pcm/discussions)

</div>

---

## Agradecimentos

<div align="center">

Construído com tecnologias modernas e inspirado por plataformas cloud enterprise:

![VMware](https://img.shields.io/badge/-VMware_vCloud-000000?style=flat-square&logo=vmware&logoColor=ff7a00)
![OpenStack](https://img.shields.io/badge/-OpenStack-000000?style=flat-square&logo=openstack&logoColor=ff7a00)
![Proxmox](https://img.shields.io/badge/-Proxmox_VE-000000?style=flat-square&logo=proxmox&logoColor=ff7a00)

</div>

---

<div align="center">

### Filosofia

_"Se não é monitorado, não existe."_

_"Se é repetitivo, deve ser automatizado."_

_"Infraestrutura não é arte. É engenharia."_

---

**[Website](https://github.com/rsdenck/pcm)** • **[Documentação](SETUP.md)** • **[Referência API](http://192.168.130.10:8000/docs)**

Feito com precisão para gerenciamento de infraestrutura enterprise

[![GitHub](https://img.shields.io/badge/-rsdenck-000000?style=for-the-badge&logo=github&logoColor=ff7a00)](https://github.com/rsdenck)

</div>
