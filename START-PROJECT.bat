@echo off
echo ========================================
echo Starting NewsScope India
echo ========================================
echo.
echo This will open 2 terminal windows:
echo 1. Backend (FastAPI) - Port 8000
echo 2. Frontend (React) - Port 5173
echo.
echo Press any key to start...
pause >nul

start "NewsScope Backend" cmd /k "%~dp0start-backend.bat"
timeout /t 3 /nobreak >nul
start "NewsScope Frontend" cmd /k "%~dp0start-frontend.bat"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173 (or 5174 if 5173 is busy)
echo API Docs: http://localhost:8000/docs
echo.
echo Keep both terminal windows open!
echo.
pause
