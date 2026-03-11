# Guia de Migração: PROXMON → PCM

## Mudanças Principais

### Nome do Projeto
- **Antigo:** PROXMON (Proxmon)
- **Novo:** PCM - Proxmox Center Manager

### Stack Backend
- **Antigo:** Laravel 12 (PHP 8.2+)
- **Novo:** FastAPI (Python 3.12+)

### Stack Frontend
- **Antigo:** SvelteKit 1.20.4
- **Novo:** Nuxt 3 + Nuxt UI

### Banco de Dados
- **Antigo:** MySQL 8.0 / SQLite
- **Novo:** PostgreSQL 18

### Arquitetura
- **Antigo:** Multi-tenant com banco por tenant
- **Novo:** Control Plane separado do Compute Plane

## Estrutura de Diretórios

```
Antigo:
saas-platform/
├── backend/        (Laravel)
├── frontend/       (SvelteKit)
└── billing/

Novo:
pcm/
├── services/       (Microserviços FastAPI)
├── core/           (Database, Config, Auth)
├── workers/        (Celery Workers)
└── sdk/            (Proxmox SDK)

pcmfe/       (Nuxt 3)
```

## Modelos de Dados

### Tenants
Mantido com estrutura similar, agora usando SQLAlchemy

### Clusters
- Suporte para PVE, PBS, PMG
- Status tracking melhorado
- API token authentication

### Users
- Roles: Provider Admin, Tenant Admin, Tenant User
- Autenticação JWT

## API Endpoints

### Antigo (Laravel)
```
/api/dashboard
/api/clusters
/api/settings
```

### Novo (FastAPI)
```
/api/v1/health
/api/v1/tenants
/api/v1/clusters
/api/v1/users
```

## Configuração

### Backend
1. Copiar `.env.example` para `.env`
2. Configurar DATABASE_URL com PostgreSQL
3. Executar migrations: `alembic upgrade head`
4. Iniciar API: `uvicorn pcm.services.api.main:app --reload`

### Frontend
1. Copiar `.env.example` para `.env`
2. Instalar dependências: `npm install`
3. Iniciar dev server: `npm run dev`

### Docker
```bash
docker-compose up -d
```

## Workers (Novo)

Celery workers para processamento assíncrono:
- Provisionamento de VMs
- Monitoramento de clusters
- Coleta de métricas

Iniciar workers:
```bash
celery -A pcm.workers.celery_app worker --loglevel=info
```

## Design System

Mantido:
- brand-orange: #ff7a00
- brand-black: #000000
- Tailwind CSS
- Dark mode

## Próximos Passos

1. Migrar dados existentes do MySQL para PostgreSQL
2. Implementar autenticação JWT
3. Configurar workers Celery
4. Implementar observabilidade (OpenTelemetry)
5. Adicionar testes automatizados
