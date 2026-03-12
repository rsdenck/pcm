-- ============================================================
-- PCM - Setup do Database
-- Execute este script no pgAdmin (Query Tool)
-- ============================================================

-- 1. Deletar usuário se existir
DROP USER IF EXISTS pcm_user;

-- 2. Criar usuário com senha simples
CREATE USER pcm_user WITH PASSWORD 'pcm123';

-- 3. Dar permissões no database
GRANT ALL PRIVILEGES ON DATABASE pcmdata_db TO pcm_user;

-- ============================================================
-- Agora conecte ao database 'pcmdata_db' e execute:
-- ============================================================

-- 4. Dar permissões no schema public
GRANT ALL ON SCHEMA public TO pcm_user;

-- 5. Dar permissões em tabelas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pcm_user;

-- 6. Dar permissões em sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pcm_user;

-- 7. Configurar permissões padrão para novas tabelas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pcm_user;

-- 8. Configurar permissões padrão para novas sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pcm_user;

-- ============================================================
-- Pronto! Agora execute:
-- cd pcm
-- .\venv\Scripts\python.exe create_tables.py
-- 
-- Credenciais:
-- Usuario: pcm_user
-- Senha: pcm123
-- ============================================================
