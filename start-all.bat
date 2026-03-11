@echo off
echo ========================================
echo PCM - Proxmox Center Manager
echo Starting All Services
echo ========================================
echo.

echo Starting Backend API...
start "PCM Backend" cmd /k "cd pcm && venv\Scripts\activate && python run.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend...
start "PCM Frontend" cmd /k "cd pcm-frontend && npm run dev -- --host 192.168.130.10 --port 9000"

echo.
echo ========================================
echo Services Started!
echo.
echo Backend API: http://192.168.130.10:8000
echo Frontend: http://192.168.130.10:9000
echo API Docs: http://192.168.130.10:8000/docs
echo ========================================
