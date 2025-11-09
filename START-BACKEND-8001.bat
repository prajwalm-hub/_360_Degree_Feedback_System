@echo off
REM Start NewsScope India Backend on port 8001
echo Starting NewsScope India Backend...
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
