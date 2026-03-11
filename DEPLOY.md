# PCM - Deployment Guide

## Deployment no Servidor 192.168.130.10

### Pré-requisitos

- Servidor: 192.168.130.10
- Python 3.12+
- Node.js 20+
- PostgreSQL 18
- Redis 7

### 1. Preparar Ambiente

```bash
# Instalar dependências do sistema
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip nodejs npm postgresql redis-server

# Configurar PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE pcmdata;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '2020Tra';"
```

### 2. Deploy Backend

```bash
# Clonar repositório
cd /opt
git clone https://github.com/rsdenck/pcm.git
cd pcm

# Configurar backend
cd pcm
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com configurações de produção

# Executar migrations
alembic upgrade head

# Testar backend
python run.py
```

### 3. Deploy Frontend

```bash
# Configurar frontend
cd /opt/pcm/pcm-frontend
npm install

# Configurar .env
cp .env.example .env
echo "NUXT_PUBLIC_API_BASE=http://192.168.130.10:8000/api/v1" > .env

# Build para produção
npm run build

# Testar frontend
npm run preview -- --host 192.168.130.10 --port 9000
```

### 4. Configurar Serviços Systemd

#### Backend Service

```bash
sudo nano /etc/systemd/system/pcm-backend.service
```

```ini
[Unit]
Description=PCM Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/pcm/pcm
Environment="PATH=/opt/pcm/pcm/venv/bin"
ExecStart=/opt/pcm/pcm/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Frontend Service

```bash
sudo nano /etc/systemd/system/pcm-frontend.service
```

```ini
[Unit]
Description=PCM Frontend
After=network.target pcm-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/pcm/pcm-frontend
Environment="NUXT_PUBLIC_API_BASE=http://192.168.130.10:8000/api/v1"
ExecStart=/usr/bin/npm run dev -- --host 192.168.130.10 --port 9000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Habilitar e Iniciar Serviços

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviços
sudo systemctl enable pcm-backend
sudo systemctl enable pcm-frontend

# Iniciar serviços
sudo systemctl start pcm-backend
sudo systemctl start pcm-frontend

# Verificar status
sudo systemctl status pcm-backend
sudo systemctl status pcm-frontend
```

### 5. Inicializar Cluster de Laboratório

```bash
cd /opt/pcm
source pcm/venv/bin/activate
python init-lab-cluster.py
```

### 6. Verificar Deployment

```bash
# Testar API
curl http://192.168.130.10:8000/api/v1/health

# Testar Dashboard
curl http://192.168.130.10:8000/api/v1/dashboard

# Acessar frontend
# Abrir navegador: http://192.168.130.10:9000
```

### 7. Logs

```bash
# Logs do backend
sudo journalctl -u pcm-backend -f

# Logs do frontend
sudo journalctl -u pcm-frontend -f

# Logs do PostgreSQL
sudo journalctl -u postgresql -f
```

## Firewall

```bash
# Permitir portas
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 9000/tcp  # Frontend
sudo ufw allow 5432/tcp  # PostgreSQL (apenas rede local)
sudo ufw allow 6379/tcp  # Redis (apenas rede local)
```

## Backup

```bash
# Backup do banco de dados
pg_dump -U postgres pcmdata > /backup/pcmdata-$(date +%Y%m%d).sql

# Backup da aplicação
tar -czf /backup/pcm-$(date +%Y%m%d).tar.gz /opt/pcm
```

## Troubleshooting

### Backend não inicia

```bash
# Verificar logs
sudo journalctl -u pcm-backend -n 50

# Verificar PostgreSQL
sudo systemctl status postgresql

# Verificar Redis
sudo systemctl status redis
```

### Frontend não carrega

```bash
# Verificar logs
sudo journalctl -u pcm-frontend -n 50

# Verificar se backend está respondendo
curl http://192.168.130.10:8000/api/v1/health
```

### Erro de conexão com Proxmox

```bash
# Testar conectividade
ping 192.168.130.20

# Testar API Proxmox
curl -k https://192.168.130.20:8006/api2/json/version
```

## Acesso

- **Frontend:** http://192.168.130.10:9000
- **API:** http://192.168.130.10:8000
- **API Docs:** http://192.168.130.10:8000/docs
- **ReDoc:** http://192.168.130.10:8000/redoc

## Credenciais Padrão

- **Tenant:** default
- **Cluster:** PROXMON Development Cluster
- **Proxmox:** 192.168.130.20:8006
