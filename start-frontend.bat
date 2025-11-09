@echo off
echo ========================================
echo Starting NewsScope India - Frontend
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Starting Vite dev server...
npm run dev

pause
