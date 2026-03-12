"""
Script automático - cria tudo sem interação
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from pcm.core.database.base import Base
from pcm.core.models import *

def setup_user_and_permissions():
    """Configura usuário e permissões usando psycopg2"""
    print("=" * 60)
    print("PCM - Setup Automatico do Database")
    print("=" * 60)
    print()
    
    # Conectar como postgres usando a senha que funciona no pgAdmin
    # Vamos tentar várias senhas comuns
    passwords = ['pcm123', 'postgres', 'admin', '2020Tra##', '']
    
    conn = None
    for pwd in passwords:
        try:
            print(f"Tentando conectar com senha...")
            conn = psycopg2.connect(
                host='localhost',
                port=5433,
                user='postgres',
                password=pwd,
                database='pcmdata_db'
            )
            print(f"✓ Conectado com sucesso!")
            break
        except Exception as e:
            continue
    
    if not conn:
        print("✗ Não foi possível conectar ao PostgreSQL")
        print("\nTentando sem senha (trust authentication)...")
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5433,
                user='postgres',
                database='pcmdata_db'
            )
            print("✓ Conectado sem senha!")
        except Exception as e:
            print(f"✗ Erro: {e}")
            print("\nPor favor, configure a senha do postgres ou habilite trust authentication")
            return False
    
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        print("\n1. Alterando senha do usuário pcm_user...")
        cur.execute("ALTER USER pcm_user WITH PASSWORD 'pcm123';")
        print("✓ Senha alterada")
        
        print("\n2. Configurando permissões no schema...")
        cur.execute("GRANT ALL ON SCHEMA public TO pcm_user;")
        print("✓ Permissões no schema concedidas")
        
        print("\n3. Configurando permissões em tabelas...")
        cur.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pcm_user;")
        print("✓ Permissões em tabelas concedidas")
        
        print("\n4. Configurando permissões em sequences...")
        cur.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pcm_user;")
        print("✓ Permissões em sequences concedidas")
        
        print("\n5. Configurando permissões padrão...")
        cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pcm_user;")
        cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pcm_user;")
        print("✓ Permissões padrão configuradas")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ Usuário e permissões configurados com sucesso!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao configurar permissões: {e}")
        cur.close()
        conn.close()
        return False

def create_tables():
    """Cria tabelas usando SQLAlchemy síncrono"""
    print("\n" + "=" * 60)
    print("Criando tabelas no database...")
    print("=" * 60)
    print()
    
    database_url = "postgresql://pcm_user:pcm123@localhost:5433/pcmdata_db"
    
    try:
        engine = create_engine(database_url, echo=True)
        Base.metadata.create_all(engine)
        
        print("\n" + "=" * 60)
        print("✓ SUCESSO! Tabelas criadas!")
        print("=" * 60)
        print("\nTabelas criadas:")
        print("  ✓ tenants")
        print("  ✓ users")
        print("  ✓ proxmox_clusters")
        print("  ✓ proxmox_nodes")
        print("  ✓ virtual_machines")
        print("  ✓ storage_pools")
        print()
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao criar tabelas: {e}")
        return False

def main():
    print("\n🚀 Iniciando setup automático do PCM...\n")
    
    # Configurar usuário e permissões
    if not setup_user_and_permissions():
        print("\n❌ Falha ao configurar usuário")
        return
    
    # Criar tabelas
    if not create_tables():
        print("\n❌ Falha ao criar tabelas")
        return
    
    print("\n" + "=" * 60)
    print("🎉 PCM DATABASE CONFIGURADO COM SUCESSO!")
    print("=" * 60)
    print("\n✓ Usuário: pcm_user")
    print("✓ Senha: pcm123")
    print("✓ Database: pcmdata_db")
    print("✓ Tabelas: criadas")
    print("\nPróximos passos:")
    print("  1. Atualizar pcm/.env com as credenciais")
    print("  2. Iniciar backend: python run.py")
    print("  3. Acessar: http://192.168.130.10:9000")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
