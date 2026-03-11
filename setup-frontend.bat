@echo off
echo ========================================
echo PCM - Proxmox Center Manager
echo Frontend Setup
echo ========================================
echo.

cd pcmfe

echo Instalando dependencias...
call npm install

echo.
echo Configurando variaveis de ambiente...
if not exist .env (
    copy .env.example .env
    echo Arquivo .env criado!
) else (
    echo Arquivo .env ja existe.
)

echo.
echo ========================================
echo Setup concluido!
echo.
echo Proximos passos:
echo 1. Execute: start-frontend.bat
echo ========================================
pause
