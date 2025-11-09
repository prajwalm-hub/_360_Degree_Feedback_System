@echo off
echo ========================================
echo Starting NewsScope India - Backend
echo ========================================
echo.

cd /d "%~dp0backend"

echo Starting FastAPI backend on port 8000...
py -3.10 run_server.py

pause
