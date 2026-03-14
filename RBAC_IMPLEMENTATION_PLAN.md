# Plano de Implementação RBAC Multi-Tenant

## Visão Geral
Sistema completo de RBAC (Role-Based Access Control) com isolamento multi-tenant, similar ao vCloud Director da VMware.

## Hierarquia de Permissões

### 1. PROVIDER_ADMIN (Admin Global)
- Acesso total ao sistema
- Pode criar/editar/deletar qualquer recurso
- Pode navegar em qualquer tenant
- Pode criar e gerenciar tenants
- Pode criar e gerenciar usuários de qualquer tenant
- Pode definir admins de tenants
- Pode alterar senhas de qualquer usuário
- Pode alocar/remover/deletar tenants

### 2. TENANT_ADMIN (Admin do Tenant)
- Acesso total APENAS ao seu tenant
- Pode criar/editar/deletar recursos do seu tenant
- Pode criar usuários dentro do seu tenant
- Pode gerenciar VMs, redes, firewalls do seu tenant
- NÃO pode acessar outros tenants
- NÃO pode criar novos tenants

### 3. TENANT_MANAGER (Gerente do Tenant)
- Pode gerenciar recursos do tenant
- Pode criar VMs, redes, firewalls
- Pode configurar regras de firewall, NAT, CGNAT
- NÃO pode criar usuários
- NÃO pode alterar configurações do tenant

### 4. TENANT_USER (Usuário do Tenant)
- Acesso somente leitura aos recursos do tenant
- Pode visualizar VMs, redes, firewalls
- NÃO pode criar ou modificar recursos

## Estrutura do Banco de Dados

### Tabelas Necessárias

```sql
-- Organizações (nível mais alto)
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tenants (clientes)
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    -- ... (já existe)
);

-- Projetos dentro de tenants
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usuários (já existe, precisa ajustes)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    -- ... (já existe)
);

-- Grupos de usuários
CREATE TABLE groups (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- Roles (papéis)
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- Permissões
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Relacionamento Role-Permission
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Relacionamento User-Role
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Relacionamento User-Group
CREATE TABLE user_groups (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    group_id UUID REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);

-- ACL Entries (Access Control List)
CREATE TABLE acl_entries (
    id UUID PRIMARY KEY,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID NOT NULL,
    principal_type VARCHAR(50) NOT NULL, -- 'user', 'group', 'role'
    principal_id UUID NOT NULL,
    permission VARCHAR(100) NOT NULL,
    allow BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX(resource_type, resource_id),
    INDEX(principal_type, principal_id)
);
```

## Fases de Implementação

### FASE 1: Database Models (Backend)
- [ ] Criar modelos SQLAlchemy para todas as tabelas
- [ ] Criar migrations Alembic
- [ ] Criar seeds para permissões padrão

### FASE 2: Backend Services
- [ ] Service para Organizations
- [ ] Service para Projects
- [ ] Service para Groups
- [ ] Service para Roles
- [ ] Service para Permissions
- [ ] Service para ACL
- [ ] Atualizar User Service com RBAC completo
- [ ] Atualizar Tenant Service com isolamento

### FASE 3: Backend API Routes
- [ ] Routes para Organizations
- [ ] Routes para Projects
- [ ] Routes para Groups
- [ ] Routes para Roles
- [ ] Routes para Permissions
- [ ] Routes para User Management (CRUD completo)
- [ ] Middleware de autorização por tenant

### FASE 4: Frontend - Admin Global
- [ ] Página de gerenciamento de usuários
- [ ] Página de gerenciamento de roles
- [ ] Página de gerenciamento de permissões
- [ ] Página de gerenciamento de groups
- [ ] Interface para atribuir roles a usuários
- [ ] Interface para criar usuários em tenants
- [ ] Interface para resetar senhas

### FASE 5: Frontend - Tenant Admin
- [ ] Dashboard específico do tenant
- [ ] Gerenciamento de usuários do tenant
- [ ] Gerenciamento de VMs
- [ ] Gerenciamento de redes
- [ ] Gerenciamento de firewalls
- [ ] Configuração de NAT/CGNAT

### FASE 6: Frontend - Tenant User
- [ ] Dashboard read-only
- [ ] Visualização de recursos
- [ ] Limitações de acesso

## Recursos por Role

### PROVIDER_ADMIN pode:
- ✅ Criar/editar/deletar tenants
- ✅ Criar/editar/deletar usuários de qualquer tenant
- ✅ Atribuir roles a qualquer usuário
- ✅ Criar/editar/deletar clusters
- ✅ Navegar entre tenants
- ✅ Alterar senhas de usuários
- ✅ Gerenciar organizações
- ✅ Gerenciar permissões globais

### TENANT_ADMIN pode:
- ✅ Criar/editar/deletar usuários do seu tenant
- ✅ Atribuir roles dentro do seu tenant
- ✅ Criar/editar/deletar VMs
- ✅ Criar/editar/deletar redes
- ✅ Criar/editar/deletar firewalls
- ✅ Configurar NAT/CGNAT
- ✅ Gerenciar projetos do tenant
- ❌ Acessar outros tenants
- ❌ Criar novos tenants

### TENANT_MANAGER pode:
- ✅ Criar/editar/deletar VMs
- ✅ Criar/editar/deletar redes
- ✅ Criar/editar/deletar firewalls
- ✅ Configurar NAT/CGNAT
- ❌ Criar usuários
- ❌ Alterar configurações do tenant

### TENANT_USER pode:
- ✅ Visualizar VMs
- ✅ Visualizar redes
- ✅ Visualizar firewalls
- ❌ Criar ou modificar recursos

## Prioridades Imediatas

1. **Criar modelos de banco de dados** (organizations, projects, groups, roles, permissions, acl_entries)
2. **Criar migrations**
3. **Criar seeds de permissões padrão**
4. **Implementar services básicos**
5. **Criar rotas de API para gerenciamento de usuários**
6. **Criar interface de gerenciamento de usuários no frontend**

## Estimativa de Tempo
- Fase 1: 2-3 horas
- Fase 2: 4-5 horas
- Fase 3: 3-4 horas
- Fase 4: 5-6 horas
- Fase 5: 6-8 horas
- Fase 6: 3-4 horas

**Total: ~25-30 horas de desenvolvimento**

## Próximos Passos
Começar pela Fase 1 - criar os modelos de banco de dados e migrations.
