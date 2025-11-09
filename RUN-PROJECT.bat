@echo off
echo ========================================
echo Starting NewsScope India Project
echo ========================================
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d "%~dp0backend\python-service" && set DATABASE_URL=sqlite:///.wrangler/state/v3/d1/miniflare-D1DatabaseObject/0a63475064ba0fef38489ee0454cb2d789b28a906ef12161e40ea6ea13385173.sqlite && py -3.10 api_server.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d "%~dp0" && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================
echo.
echo Press any key to exit this window (servers will keep running)
pause >nul
