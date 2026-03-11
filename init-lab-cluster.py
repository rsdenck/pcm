"""
Script para inicializar o cluster de laboratório no PCM
"""
import asyncio
import httpx

API_BASE = "http://192.168.130.10:8000/api/v1"

# Configuração do cluster de laboratório
LAB_CLUSTER = {
    "name": "PROXMON Development Cluster",
    "hostname": "192.168.130.20",
    "port": 8006,
    "cluster_type": "pve",
    "api_token_id": "root@pam!pvetoken",
    "api_token_secret": "b8e4d593-9fe8-4c10-ae15-881c9873cb63",
    "verify_ssl": False,
    "description": "Cluster de desenvolvimento e testes - 3 nodes (PVE-01, PVE-02, PVE-03)",
    "tenant_id": "default-tenant-id"  # Será criado automaticamente
}

# Tenant padrão
DEFAULT_TENANT = {
    "name": "Default Organization",
    "slug": "default",
    "description": "Organização padrão para desenvolvimento"
}


async def create_tenant():
    """Cria o tenant padrão"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/tenants",
                json=DEFAULT_TENANT,
                timeout=30.0
            )
            response.raise_for_status()
            tenant = response.json()
            print(f"✓ Tenant criado: {tenant['name']} (ID: {tenant['id']})")
            return tenant['id']
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # Tenant já existe, buscar ID
                response = await client.get(f"{API_BASE}/tenants")
                tenants = response.json()
                for tenant in tenants:
                    if tenant['slug'] == DEFAULT_TENANT['slug']:
                        print(f"✓ Tenant já existe: {tenant['name']} (ID: {tenant['id']})")
                        return tenant['id']
            raise


async def create_cluster(tenant_id: str):
    """Cria o cluster de laboratório"""
    LAB_CLUSTER['tenant_id'] = tenant_id
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/clusters",
                json=LAB_CLUSTER,
                timeout=30.0
            )
            response.raise_for_status()
            cluster = response.json()
            print(f"✓ Cluster criado: {cluster['name']} (ID: {cluster['id']})")
            print(f"  Status: {cluster['status']}")
            print(f"  Hostname: {cluster['hostname']}:{cluster['port']}")
            return cluster['id']
        except httpx.HTTPStatusError as e:
            print(f"✗ Erro ao criar cluster: {e.response.text}")
            raise


async def sync_cluster(cluster_id: str):
    """Sincroniza dados do cluster"""
    async with httpx.AsyncClient() as client:
        try:
            print(f"\nSincronizando cluster...")
            response = await client.get(
                f"{API_BASE}/clusters/{cluster_id}/sync",
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Cluster sincronizado com sucesso!")
            print(f"  Última sincronização: {result.get('last_sync')}")
            
            # Obter estatísticas
            stats_response = await client.get(
                f"{API_BASE}/clusters/{cluster_id}/stats",
                timeout=30.0
            )
            stats = stats_response.json()
            print(f"\nEstatísticas do Cluster:")
            print(f"  Nodes: {stats.get('online_nodes')}/{stats.get('total_nodes')}")
            print(f"  VMs: {stats.get('running_vms')}/{stats.get('total_vms')}")
            print(f"  Containers: {stats.get('total_containers')}")
            print(f"  Storage: {stats.get('available_storage')}/{stats.get('total_storage')}")
            
        except httpx.HTTPStatusError as e:
            print(f"✗ Erro ao sincronizar cluster: {e.response.text}")
            raise


async def main():
    print("=" * 60)
    print("PCM - Inicialização do Cluster de Laboratório")
    print("=" * 60)
    print()
    
    try:
        # Criar tenant
        print("1. Criando tenant padrão...")
        tenant_id = await create_tenant()
        print()
        
        # Criar cluster
        print("2. Adicionando cluster de laboratório...")
        cluster_id = await create_cluster(tenant_id)
        print()
        
        # Sincronizar cluster
        print("3. Sincronizando dados do cluster...")
        await sync_cluster(cluster_id)
        print()
        
        print("=" * 60)
        print("✓ Inicialização concluída com sucesso!")
        print()
        print("Acesse o PCM em: http://192.168.130.10:9000")
        print("API Docs: http://192.168.130.10:8000/docs")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Erro durante inicialização: {str(e)}")
        print("=" * 60)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
