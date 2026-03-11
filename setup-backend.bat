@echo off
echo ========================================
echo PCM - Proxmox Center Manager
echo Backend Setup
echo ========================================
echo.

cd pcm

echo Criando ambiente virtual...
python -m venv venv

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Configurando variaveis de ambiente...
if not exist .env (
    copy .env.example .env
    echo Arquivo .env criado! Configure suas credenciais.
) else (
    echo Arquivo .env ja existe.
)

echo.
echo ========================================
echo Setup concluido!
echo.
echo Proximos passos:
echo 1. Configure o arquivo pcm/.env
echo 2. Certifique-se que PostgreSQL esta rodando
echo 3. Execute: alembic upgrade head
echo 4. Execute: start-backend.bat
echo ========================================
pause
