@echo off
echo ========================================
echo NewsScope India - Hybrid Collection System
echo ========================================
echo.
echo Starting all collectors...
echo.

echo [1/4] Starting RSS Collector (every 15 minutes)...
start "RSS Collector" cmd /k "cd /d "%~dp0backend" && py -3.10 run_rss_collector.py --interval 15"
timeout /t 2 /nobreak >nul

echo [2/4] Starting Web Scraper (every 15 minutes)...
start "Web Scraper" cmd /k "cd /d "%~dp0backend" && py -3.10 run_enhanced_scraper.py --interval 15"
timeout /t 2 /nobreak >nul

echo [3/4] Starting Backend API (port 8000)...
start "Backend API" cmd /k "cd /d "%~dp0backend" && py -3.10 run_server.py"
timeout /t 5 /nobreak >nul

echo [4/4] Starting Frontend (port 5173)...
start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Services running:
echo   1. RSS Collector (Terminal 1)
echo   2. Web Scraper (Terminal 2)
echo   3. Backend API (Terminal 3) - http://localhost:8000
echo   4. Frontend (Terminal 4) - http://localhost:5173
echo.
echo Press any key to exit this launcher...
pause >nul
