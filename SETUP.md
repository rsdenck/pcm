# PCM - Setup Guide

## Pré-requisitos

- Python 3.12+
- Node.js 20+
- PostgreSQL 18
- Redis 7
## Setup Local

### 1. Backend (FastAPI)

```bash
cd pcm

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Criar database
# O PostgreSQL deve estar rodando com:
# USER: postgres
# PASSWORD: 2020Tra
# HOST: localhost

# Executar migrations
alembic upgrade head

# Iniciar API
uvicorn pcm.services.api.main:app --reload --host 0.0.0.0 --port 8000
```

API estará disponível em: http://localhost:8000

### 2. Frontend (Nuxt)

```bash
cd pcm-frontend

cd pcmfendências
npm install

# Configurar variáveis de ambiente
cp .env.example .env

# Iniciar dev server
npm run dev
```

Frontend estará disponível em: http://localhost:3000

### 3. Workers (Celery)
### 3. Workers (Celery)

```bash
cd pcm

# Iniciar worker
celery -A pcm.workers.celery_app worker --loglevel=info

# Iniciar beat (scheduler)
celery -A pcm.workers.celery_app beat --loglevel=info
```

## Serviços Disponíveis
## Criar Database
### Backend
```bash
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health
```

### Frontend
Abrir navegador em: http://localhost:3000

## Estrutura de Serviços

```
PCM Control Plane
├── API (FastAPI)          → :8000
├── Frontend (Nuxt)        → :3000
├── PostgreSQL             → :5432
├── Redis                  → :6379
└── Workers (Celery)       → Background
```

```bashr primeiro tenant
2. Adicionar cluster Proxmox
3. Configurar autenticação
4. Configurar observabilidade

## Troubleshooting

### Erro de conexão com PostgreSQL
- Verificar se PostgreSQL está rodando
- Verificar credenciais no .env
- Verificar se database 'pcmdata' existe

### Erro de conexão com Redis
- Verificar se Redis está rodando
- Verificar URL no .env

### Erro no frontend
- Verificar se API está rodando
- Verificar NUXT_PUBLIC_API_BASE no .env
- Limpar cache: `rm -rf .nuxt node_modules && npm install`

## Documentação da API

Swagger UI disponível em: http://localhost:8000/docs
ReDoc disponível em: http://localhost:8000/redoc
