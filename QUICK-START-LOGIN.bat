@echo off
echo ========================================
echo NewsScope India - Quick Start (Login Fix)
echo ========================================
echo.

echo Step 1: Checking Backend...
echo.

REM Check if backend is running
curl -s http://localhost:8000/api/health >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend is already running!
    echo.
) else (
    echo [INFO] Backend is not running. Starting it now...
    echo.
    
    REM Start backend in a new window
    start "NewsScope Backend" cmd /k "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    echo Waiting for backend to start (10 seconds)...
    timeout /t 10 /nobreak >nul
    
    REM Check again
    curl -s http://localhost:8000/api/health >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Backend started successfully!
    ) else (
        echo [ERROR] Backend failed to start. Please check the backend window for errors.
        pause
        exit /b 1
    )
)

echo.
echo Step 2: Initializing Database Users...
echo.

cd backend
python init_admin.py
cd ..

echo.
echo Step 3: Starting Frontend...
echo.

REM Check if frontend is already running
curl -s http://localhost:5173 >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [OK] Frontend is already running!
) else (
    echo [INFO] Starting frontend...
    start "NewsScope Frontend" cmd /k "cd frontend && npm run dev"
    
    echo Waiting for frontend to start (5 seconds)...
    timeout /t 5 /nobreak >nul
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo ========================================
echo Demo Login Credentials:
echo ========================================
echo.
echo PIB Officer (Delhi):
echo   Username: pib_delhi
echo   Password: officer123
echo.
echo PIB Officer (Mumbai):
echo   Username: pib_mumbai
echo   Password: officer123
echo.
echo Admin:
echo   Username: admin
echo   Password: admin123
echo.
echo ========================================
echo.
echo Opening frontend in browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173
echo.
echo Press any key to exit...
pause >nul
