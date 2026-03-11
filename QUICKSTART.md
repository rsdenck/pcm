# PCM - Quick Start Guide

## 🚀 Início Rápido (Windows)

### Passo 1: Pré-requisitos

Certifique-se de ter instalado:
- ✅ Python 3.12+
- ✅ Node.js 20+
- ✅ PostgreSQL 18 (rodando em localhost:5432)
- ✅ Redis 7 (rodando em localhost:6379)

### Passo 2: Configurar PostgreSQL

Credenciais necessárias:
- **User:** postgres
- **Password:** 2020Tra
- **Host:** localhost
- **Port:** 5432

Criar database:
```bash
# PowerShell
$env:PGPASSWORD="2020Tra"
psql -U postgres -h localhost -c "CREATE DATABASE pcmdata;"
```

### Passo 3: Setup Backend

```bash
# 1. Executar setup
setup-backend.bat

# 2. Configurar .env (já está configurado por padrão)
# Arquivo: pcm/.env

# 3. Executar migrations
cd pcm
venv\Scripts\activate
alembic upgrade head
cd ..
```

### Passo 4: Setup Frontend

```bash
# Executar setup
setup-frontend.bat
```

### Passo 5: Iniciar Aplicação

Abra 2 terminais:

**Terminal 1 - Backend:**
```bash
start-backend.bat
```

**Terminal 2 - Frontend:**
```bash
start-frontend.bat
```

### Passo 6: Acessar

- 🌐 **Frontend:** http://localhost:3000
- 🔌 **API:** http://localhost:8000
- 📚 **Docs:** http://localhost:8000/docs

## 🎯 Próximos Passos

1. Criar primeiro tenant via API
2. Adicionar cluster Proxmox
3. Configurar workers (opcional)

## 🔧 Workers (Opcional)

Para processamento assíncrono:
```bash
start-workers.bat
```

## 📝 Estrutura de Comandos

```
setup-backend.bat      → Configura backend (uma vez)
setup-frontend.bat     → Configura frontend (uma vez)
start-backend.bat      → Inicia API
start-frontend.bat     → Inicia frontend
start-workers.bat      → Inicia workers Celery
```

## ⚠️ Troubleshooting

### PostgreSQL não conecta
- Verificar se está rodando: `psql -U postgres -h localhost`
- Verificar senha: 2020Tra
- Verificar se database existe: `\l` no psql

### Redis não conecta
- Verificar se está rodando
- Windows: Instalar via WSL ou usar Redis Windows port

### Erro no frontend
- Limpar cache: `cd pcmfe && rm -rf .nuxt node_modules && npm install`

### Erro no backend
- Recriar venv: `cd pcm && rm -rf venv && python -m venv venv`
- Reinstalar: `venv\Scripts\activate && pip install -r requirements.txt`

## 📊 Verificar Status

### Backend
```bash
curl http://localhost:8000/api/v1/health
```

### Frontend
Abrir: http://localhost:3000

## 🎨 Repositório

GitHub: https://github.com/rsdenck/pcm
