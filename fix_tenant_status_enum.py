"""
Script para corrigir o enum de status dos tenants no banco de dados.
O banco tem valores em MAIÚSCULO mas o modelo Python usa minúsculo.
"""
import asyncio
from sqlalchemy import text
from pcm.core.database import engine


async def fix_tenant_status():
    """Corrige os valores de status dos tenants para maiúsculo."""
    async with engine.begin() as conn:
        # Primeiro, vamos ver quantos tenants existem
        result = await conn.execute(text("SELECT COUNT(*) FROM tenants"))
        count = result.scalar()
        print(f"Total de tenants no banco: {count}")
        
        if count == 0:
            print("Nenhum tenant encontrado. Nada a fazer.")
            return
        
        # Verificar os status atuais
        result = await conn.execute(text("SELECT id, name, status FROM tenants"))
        tenants = result.fetchall()
        
        print("\nStatus atuais:")
        for tenant in tenants:
            print(f"  - {tenant.name}: {tenant.status}")
        
        # Atualizar status para maiúsculo
        print("\nAtualizando status para maiúsculo...")
        
        # Mapear valores minúsculos para maiúsculos
        status_map = {
            'active': 'ACTIVE',
            'suspended': 'SUSPENDED',
            'pending': 'PENDING',
            'archived': 'ARCHIVED'
        }
        
        for old_status, new_status in status_map.items():
            result = await conn.execute(
                text(f"UPDATE tenants SET status = '{new_status}' WHERE status = '{old_status}'")
            )
            if result.rowcount > 0:
                print(f"  ✓ Atualizados {result.rowcount} tenants de '{old_status}' para '{new_status}'")
        
        # Verificar resultado
        result = await conn.execute(text("SELECT id, name, status FROM tenants"))
        tenants = result.fetchall()
        
        print("\nStatus após atualização:")
        for tenant in tenants:
            print(f"  - {tenant.name}: {tenant.status}")
        
        print("\n✓ Status dos tenants corrigidos com sucesso!")


if __name__ == "__main__":
    asyncio.run(fix_tenant_status())
