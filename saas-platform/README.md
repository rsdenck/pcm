# SaaS Platform Enterprise - Cloud Native

Este é um projeto SaaS completo, arquitetado para escalabilidade, segurança e isolamento físico de dados (Multi-tenant por banco de dados).

## 🚀 Stack Tecnológica

- **Backend:** Laravel 10 (API Only)
- **Frontend:** SvelteKit (SSR + SPA)
- **Database:** MySQL 8.0 (Master + Tenant DBs)
- **Cache/Queue:** Redis 7
- **Billing:** Lago (Open Source)
- **Proxy:** Nginx (no Host) + Cloudflare
- **Infra:** Docker + Docker Compose

## 📁 Estrutura do Projeto

- `backend/`: API Laravel seguindo Service Layer + DDD light.
- `frontend/`: Aplicação SvelteKit com Tailwind CSS.
- `infra/`: Configurações de Nginx, Cloudflare e scripts de automação.
- `billing/`: Configuração do sistema de faturamento Lago.

## ⚙️ Configuração Inicial

### 1. Requisitos
- Docker & Docker Compose
- Nginx instalado no Host
- Domínio configurado na Cloudflare (ver `infra/cloudflare/dns.md`)

### 2. Rodando o Projeto
```bash
# Iniciar Containers
docker-compose up -d

# Configurar Backend
docker exec -it saas_backend composer install
docker exec -it saas_backend php artisan migrate --path=database/migrations/master

# Configurar Billing (Lago)
cd billing/lago && docker-compose up -d
```

### 3. Configuração do Nginx no Host
Copie os arquivos de `infra/nginx/conf.d/` para `/etc/nginx/conf.d/` e reinicie o serviço:
```bash
sudo cp infra/nginx/conf.d/*.conf /etc/nginx/conf.d/
sudo systemctl restart nginx
```

## 🔒 Segurança & Isolamento
- **Tenant Resolution:** Feito via Middleware no Laravel baseado no Host Header.
- **Database Switching:** O `DatabaseSwitcher` altera a conexão dinamicamente para o banco do cliente.
- **Cloudflare:** Atua como WAF e terminação SSL, protegendo o IP da VM.

## 🛠️ Manutenção
- Scripts de backup e restore estão em `infra/scripts/`.
- Migrations de tenants devem ser executadas via `TenantService`.

---
Desenvolvido com foco em alta performance e isolamento enterprise.
