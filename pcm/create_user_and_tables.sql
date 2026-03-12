-- Script SQL para criar usuário e database
-- Execute este script no pgAdmin ou psql

-- Criar usuário pcm_user
CREATE USER pcm_user WITH PASSWORD 'pcm2024';

-- Dar permissões no database
GRANT ALL PRIVILEGES ON DATABASE pcmdata_db TO pcm_user;

-- Conectar ao database pcmdata_db e dar permissões no schema
\c pcmdata_db

GRANT ALL ON SCHEMA public TO pcm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pcm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pcm_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pcm_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pcm_user;
