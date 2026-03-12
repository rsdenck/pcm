"""
Script completo: cria usuário, database e tabelas
Execute como administrador do Windows
"""
import subprocess
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from pcm.core.database.base import Base
from pcm.core.models import *

def run_sql_as_postgres(sql_commands):
    """Executa SQL usando psql com autenticação do Windows"""
    psql_path = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"
    
    for sql in sql_commands:
        print(f"Executando: {sql[:50]}...")
        try:
            result = subprocess.run(
                [psql_path, "-U", "postgres", "-h", "localhost", "-c", sql],
                capture_output=True,
                text=True,
                input="2020Tra##\n"  # Tenta com a senha
            )
            if result.returncode != 0:
                print(f"Aviso: {result.stderr}")
            else:
                print(f"OK: {result.stdout}")
        except Exception as e:
            print(f"Erro: {e}")

async def create_tables_direct():
    """Cria tabelas diretamente usando SQLAlchemy"""
    print("\n" + "=" * 60)
    print("Criando tabelas no database...")
    print("=" * 60)
    
    # Usar usuário pcm_user
    database_url = "postgresql+asyncpg://pcm_user:pcm123@localhost:5432/pcmdata_db"
    
    try:
        engine = create_async_engine(database_url, echo=True)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("\n" + "=" * 60)
        print("SUCESSO! Tabelas criadas!")
        print("=" * 60)
        print("\nTabelas criadas:")
        print("  - tenants")
        print("  - users")
        print("  - proxmox_clusters")
        print("  - proxmox_nodes")
        print("  - virtual_machines")
        print("  - storage_pools")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"\nErro ao criar tabelas: {e}")
        return False

def main():
    print("=" * 60)
    print("PCM - Setup Completo do Database")
    print("=" * 60)
    print()
    
    # Tentar criar usuário via SQL
    print("Tentando criar usuário pcm_user...")
    sql_commands = [
        "DROP USER IF EXISTS pcm_user;",
        "CREATE USER pcm_user WITH PASSWORD 'pcm123';",
        "GRANT ALL PRIVILEGES ON DATABASE pcmdata_db TO pcm_user;",
    ]
    
    run_sql_as_postgres(sql_commands)
    
    print("\n" + "=" * 60)
    print("IMPORTANTE!")
    print("=" * 60)
    print("\nSe o comando acima falhou, execute manualmente no pgAdmin:")
    print("\n1. Abra pgAdmin")
    print("2. Conecte ao PostgreSQL 18")
    print("3. Query Tool e execute:")
    print("\n   DROP USER IF EXISTS pcm_user;")
    print("   CREATE USER pcm_user WITH PASSWORD 'pcm123';")
    print("   GRANT ALL PRIVILEGES ON DATABASE pcmdata_db TO pcm_user;")
    print("\n4. Conecte ao database pcmdata_db e execute:")
    print("\n   GRANT ALL ON SCHEMA public TO pcm_user;")
    print("   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pcm_user;")
    print("   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pcm_user;")
    print("   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pcm_user;")
    print("   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pcm_user;")
    print("\n" + "=" * 60)
    
    input("\nPressione Enter depois de executar os comandos no pgAdmin...")
    
    # Criar tabelas
    success = asyncio.run(create_tables_direct())
    
    if success:
        print("\n" + "=" * 60)
        print("TUDO PRONTO!")
        print("=" * 60)
        print("\nAgora você pode:")
        print("1. Iniciar o backend: python run.py")
        print("2. Acessar: http://192.168.130.10:9000")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("FALHOU!")
        print("=" * 60)
        print("\nVerifique se executou os comandos SQL no pgAdmin")

if __name__ == "__main__":
    main()
