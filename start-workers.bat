@echo off
echo ========================================
echo PCM - Proxmox Center Manager
echo Celery Workers Startup
echo ========================================
echo.

cd pcm

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Iniciando Celery Workers...
echo.

celery -A pcm.workers.celery_app worker --loglevel=info --pool=solo
