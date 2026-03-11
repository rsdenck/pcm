@echo off
echo ========================================
echo PCM - Proxmox Center Manager
echo Frontend Startup
echo ========================================
echo.

cd pcmfe

echo Iniciando Nuxt dev server...
echo Frontend disponivel em: http://localhost:3000
echo.

npm run dev
