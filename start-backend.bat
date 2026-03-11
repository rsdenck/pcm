@echo off
echo ========================================
echo PCM - Proxmox Center Manager
echo Backend API Startup
echo ========================================
echo.

cd pcm

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Iniciando API na porta 8000...
echo API disponivel em: http://localhost:8000
echo Documentacao em: http://localhost:8000/docs
echo.

python run.py
