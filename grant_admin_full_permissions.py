"""
Script para conceder permissões completas ao usuário admin@pcm.local.
O admin deve ter acesso total a todos os recursos do sistema.
"""
import asyncio
import json
from sqlalchemy import text
from pcm.core.database import engine


async def grant_admin_permissions():
    """Concede permissões completas ao admin."""
    async with engine.begin() as conn:
        # Buscar o usuário admin
        result = await conn.execute(
            text("SELECT id, email, role, permissions FROM users WHERE email = 'admin@pcm.local'")
        )
        admin = result.fetchone()
        
        if not admin:
            print("❌ Usuário admin@pcm.local não encontrado!")
            return
        
        print(f"✓ Usuário encontrado: {admin.email}")
        print(f"  Role atual: {admin.role}")
        print(f"  Permissões atuais: {admin.permissions}")
        
        # Definir todas as permissões possíveis
        # Para PROVIDER_ADMIN, todas as permissões devem estar disponíveis
        all_permissions = {
            # Tenant permissions
            "tenant:create": True,
            "tenant:read": True,
            "tenant:update": True,
            "tenant:delete": True,
            "tenant:manage": True,
            
            # Cluster permissions
            "cluster:create": True,
            "cluster:read": True,
            "cluster:update": True,
            "cluster:delete": True,
            "cluster:manage": True,
            "cluster:test_connection": True,
            
            # User permissions
            "user:create": True,
            "user:read": True,
            "user:update": True,
            "user:delete": True,
            "user:manage": True,
            
            # VM permissions
            "vm:create": True,
            "vm:read": True,
            "vm:update": True,
            "vm:delete": True,
            "vm:manage": True,
            "vm:start": True,
            "vm:stop": True,
            "vm:restart": True,
            
            # Container permissions
            "container:create": True,
            "container:read": True,
            "container:update": True,
            "container:delete": True,
            "container:manage": True,
            "container:start": True,
            "container:stop": True,
            "container:restart": True,
            
            # Storage permissions
            "storage:create": True,
            "storage:read": True,
            "storage:update": True,
            "storage:delete": True,
            "storage:manage": True,
            
            # Network permissions
            "network:create": True,
            "network:read": True,
            "network:update": True,
            "network:delete": True,
            "network:manage": True,
            
            # Backup permissions
            "backup:create": True,
            "backup:read": True,
            "backup:update": True,
            "backup:delete": True,
            "backup:manage": True,
            "backup:restore": True,
            
            # Settings permissions
            "settings:read": True,
            "settings:update": True,
            "settings:manage": True,
            
            # Dashboard permissions
            "dashboard:read": True,
            "dashboard:manage": True,
            
            # Statistics permissions
            "statistics:read": True,
            "statistics:manage": True,
            
            # Observability permissions
            "observability:read": True,
            "observability:manage": True,
            
            # System permissions
            "system:read": True,
            "system:update": True,
            "system:manage": True,
            "system:admin": True,
            
            # Global admin flag
            "admin:*": True,
            "*:*": True  # Wildcard - acesso total
        }
        
        # Atualizar permissões do admin
        permissions_json = json.dumps(all_permissions)
        await conn.execute(
            text("""
                UPDATE users 
                SET permissions = :permissions,
                    is_superuser = true,
                    role = 'PROVIDER_ADMIN'
                WHERE email = 'admin@pcm.local'
            """),
            {"permissions": permissions_json}
        )
        
        print("\n✓ Permissões atualizadas com sucesso!")
        print(f"\nPermissões concedidas ({len(all_permissions)} permissões):")
        for perm, value in sorted(all_permissions.items()):
            print(f"  ✓ {perm}: {value}")
        
        # Verificar atualização
        result = await conn.execute(
            text("SELECT email, role, is_superuser, permissions FROM users WHERE email = 'admin@pcm.local'")
        )
        updated_admin = result.fetchone()
        
        print(f"\n✓ Verificação final:")
        print(f"  Email: {updated_admin.email}")
        print(f"  Role: {updated_admin.role}")
        print(f"  Is Superuser: {updated_admin.is_superuser}")
        
        # Verificar se permissions já é um dict ou string
        perms = updated_admin.permissions
        if isinstance(perms, str):
            perms = json.loads(perms)
        print(f"  Total de permissões: {len(perms)}")


if __name__ == "__main__":
    asyncio.run(grant_admin_permissions())
