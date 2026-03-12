"""
Script para criar tabelas diretamente no database
"""
import asyncio
import getpass
from sqlalchemy.ext.asyncio import create_async_engine
from pcm.core.database.base import Base
from pcm.core.models import *

async def create_tables():
    print("=" * 60)
    print("PCM - Criacao de Tabelas no Database")
    print("=" * 60)
    print()
    
    # Solicitar credenciais
    db_host = input("Host do PostgreSQL [localhost]: ").strip() or "localhost"
    db_port = input("Porta [5432]: ").strip() or "5432"
    db_user = input("Usuario [postgres]: ").strip() or "postgres"
    db_password = getpass.getpass("Senha: ")
    db_name = input("Nome do Database [pcmdata_db]: ").strip() or "pcmdata_db"
    
    print()
    print("Conectando ao database...")
    
    # Construir URL do database
    database_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        # Criar engine
        engine = create_async_engine(database_url, echo=True)
        
        print()
        print("Criando tabelas...")
        print()
        
        # Criar todas as tabelas
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print()
        print("=" * 60)
        print("SUCESSO! Tabelas criadas!")
        print("=" * 60)
        print()
        print("Tabelas criadas:")
        print("  - tenants")
        print("  - users")
        print("  - proxmox_clusters")
        print("  - proxmox_nodes")
        print("  - virtual_machines")
        print("  - storage_pools")
        print("  - pbs_servers")
        print("  - datastores")
        print()
        
        await engine.dispose()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("ERRO ao criar tabelas!")
        print("=" * 60)
        print(f"Erro: {e}")
        print()
        raise

if __name__ == "__main__":
    asyncio.run(create_tables())
