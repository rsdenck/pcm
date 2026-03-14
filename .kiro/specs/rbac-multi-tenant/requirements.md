# RBAC Multi-Tenant System - Requirements

## Overview
Implementar um sistema completo de RBAC (Role-Based Access Control) com isolamento multi-tenant, similar ao vCloud Director da VMware, onde cada tenant é um cliente isolado com seus próprios recursos e usuários.

## Business Requirements

### BR-001: Hierarquia de Permissões
O sistema deve suportar 4 níveis de acesso:
1. **PROVIDER_ADMIN** - Admin Global do Sistema
2. **TENANT_ADMIN** - Admin de um Tenant específico
3. **TENANT_MANAGER** - Gerente de recursos do Tenant
4. **TENANT_USER** - Usuário com acesso read-only

### BR-002: Isolamento Multi-Tenant
- Cada tenant deve ser completamente isolado
- Usuários de um tenant NÃO podem acessar recursos de outros tenants
- Apenas PROVIDER_ADMIN pode navegar entre tenants
- Cada tenant funciona como um cliente independente

### BR-003: Gerenciamento de Usuários
- PROVIDER_ADMIN pode criar usuários em qualquer tenant
- PROVIDER_ADMIN pode alterar senhas de qualquer usuário
- PROVIDER_ADMIN pode atribuir roles a qualquer usuário
- TENANT_ADMIN pode criar usuários apenas no seu tenant
- TENANT_ADMIN pode gerenciar roles dentro do seu tenant

### BR-004: Gerenciamento de Recursos
- PROVIDER_ADMIN tem acesso total a todos os recursos
- TENANT_ADMIN tem acesso total aos recursos do seu tenant
- TENANT_MANAGER pode criar/editar recursos mas não usuários
- TENANT_USER tem acesso read-only

## Functional Requirements

### FR-001: Database Schema
Implementar as seguintes tabelas:
- `organizations` - Organizações (nível mais alto)
- `tenants` - Tenants/Clientes (já existe, precisa ajustes)
- `projects` - Projetos dentro de tenants
- `users` - Usuários (já existe, precisa ajustes)
- `groups` - Grupos de usuários
- `roles` - Papéis/Roles
- `permissions` - Permissões granulares
- `role_permissions` - Relacionamento N:N
- `user_roles` - Relacionamento N:N
- `user_groups` - Relacionamento N:N
- `acl_entries` - Access Control List

### FR-002: Backend Services
Criar services para:
- Organization Management
- Project Management
- Group Management
- Role Management
- Permission Management
- ACL Management
- Enhanced User Management
- Enhanced Tenant Management

### FR-003: Backend API Routes
Criar rotas REST para:
- `/api/v1/organizations` - CRUD de organizações
- `/api/v1/projects` - CRUD de projetos
- `/api/v1/groups` - CRUD de grupos
- `/api/v1/roles` - CRUD de roles
- `/api/v1/permissions` - CRUD de permissões
- `/api/v1/users` - CRUD completo de usuários
- `/api/v1/users/{id}/roles` - Gerenciar roles de usuário
- `/api/v1/users/{id}/password` - Resetar senha
- `/api/v1/acl` - Gerenciar ACL

### FR-004: Frontend - Admin Global
Criar interfaces para PROVIDER_ADMIN:
- Dashboard de gerenciamento de usuários
- Interface de criação de usuários
- Interface de atribuição de roles
- Interface de gerenciamento de permissões
- Interface de reset de senhas
- Navegação entre tenants
- Gerenciamento de organizações

### FR-005: Frontend - Tenant Admin
Criar interfaces para TENANT_ADMIN:
- Dashboard do tenant
- Gerenciamento de usuários do tenant
- Gerenciamento de VMs
- Gerenciamento de redes
- Gerenciamento de firewalls
- Configuração de NAT/CGNAT
- Gerenciamento de projetos

### FR-006: Frontend - Tenant Manager
Criar interfaces para TENANT_MANAGER:
- Dashboard de recursos
- Criação/edição de VMs
- Criação/edição de redes
- Criação/edição de firewalls
- Configuração de regras de firewall

### FR-007: Frontend - Tenant User
Criar interfaces para TENANT_USER:
- Dashboard read-only
- Visualização de VMs
- Visualização de redes
- Visualização de firewalls

## Non-Functional Requirements

### NFR-001: Security
- Todas as operações devem ser autenticadas
- Todas as operações devem ser autorizadas via RBAC
- Senhas devem ser hasheadas com bcrypt
- Tokens JWT devem expirar em 60 minutos
- Isolamento de tenant deve ser garantido em nível de banco de dados

### NFR-002: Performance
- Queries devem usar índices apropriados
- Cache de permissões deve ser implementado
- Paginação deve ser implementada em todas as listagens

### NFR-003: Auditability
- Todas as operações críticas devem ser logadas
- Logs devem incluir: usuário, ação, timestamp, tenant

### NFR-004: Usability
- Interface deve ser intuitiva
- Feedback visual para todas as operações
- Mensagens de erro claras
- Design consistente com Proxmox (laranja #E57000)

## Permissions Matrix

### PROVIDER_ADMIN
| Resource | Create | Read | Update | Delete | Manage |
|----------|--------|------|--------|--------|--------|
| Tenants | ✅ | ✅ | ✅ | ✅ | ✅ |
| Users (All) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Clusters | ✅ | ✅ | ✅ | ✅ | ✅ |
| VMs (All) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Networks (All) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Firewalls (All) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Organizations | ✅ | ✅ | ✅ | ✅ | ✅ |
| Roles | ✅ | ✅ | ✅ | ✅ | ✅ |
| Permissions | ✅ | ✅ | ✅ | ✅ | ✅ |

### TENANT_ADMIN
| Resource | Create | Read | Update | Delete | Manage |
|----------|--------|------|--------|--------|--------|
| Tenants | ❌ | ✅ (own) | ✅ (own) | ❌ | ❌ |
| Users (Tenant) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Clusters | ❌ | ✅ (own) | ❌ | ❌ | ❌ |
| VMs (Tenant) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Networks (Tenant) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Firewalls (Tenant) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Projects | ✅ | ✅ | ✅ | ✅ | ✅ |

### TENANT_MANAGER
| Resource | Create | Read | Update | Delete | Manage |
|----------|--------|------|--------|--------|--------|
| Users | ❌ | ✅ | ❌ | ❌ | ❌ |
| VMs (Tenant) | ✅ | ✅ | ✅ | ✅ | ❌ |
| Networks (Tenant) | ✅ | ✅ | ✅ | ✅ | ❌ |
| Firewalls (Tenant) | ✅ | ✅ | ✅ | ✅ | ❌ |
| NAT/CGNAT | ✅ | ✅ | ✅ | ✅ | ❌ |

### TENANT_USER
| Resource | Create | Read | Update | Delete | Manage |
|----------|--------|------|--------|--------|--------|
| VMs (Tenant) | ❌ | ✅ | ❌ | ❌ | ❌ |
| Networks (Tenant) | ❌ | ✅ | ❌ | ❌ | ❌ |
| Firewalls (Tenant) | ❌ | ✅ | ❌ | ❌ | ❌ |

## Success Criteria

1. ✅ PROVIDER_ADMIN pode criar usuários em qualquer tenant
2. ✅ PROVIDER_ADMIN pode alterar senhas de qualquer usuário
3. ✅ PROVIDER_ADMIN pode navegar entre tenants
4. ✅ TENANT_ADMIN pode gerenciar apenas seu tenant
5. ✅ TENANT_ADMIN NÃO pode acessar outros tenants
6. ✅ TENANT_MANAGER pode criar recursos mas não usuários
7. ✅ TENANT_USER tem acesso read-only
8. ✅ Isolamento de tenant é garantido
9. ✅ Todas as operações são auditadas
10. ✅ Interface é intuitiva e responsiva

## Out of Scope (Future Phases)
- LDAP/AD integration avançada
- Multi-factor authentication
- API rate limiting
- Advanced audit reports
- Billing integration
- Resource quotas automáticos
