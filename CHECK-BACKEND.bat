@echo off
echo ========================================
echo Checking Backend Server Status
echo ========================================
echo.

echo Testing connection to http://localhost:8000/api/health...
echo.

curl -s http://localhost:8000/api/health

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Backend is running!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ERROR: Backend is NOT running!
    echo ========================================
    echo.
    echo Please start the backend server first:
    echo 1. Open a new terminal
    echo 2. Navigate to: NewsScope_India_Fixed\backend
    echo 3. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    echo.
    echo Or use the quick start script:
    echo    start-backend.bat
    echo ========================================
)

echo.
pause
