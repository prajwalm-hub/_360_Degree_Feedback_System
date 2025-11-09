@echo off
setlocal enabledelayedexpansion

echo ========================================
echo NewsScope India - Setup Verification
echo ========================================
echo.

set PASS=0
set FAIL=0

REM Test 1: Backend Health
echo [1/6] Checking Backend Health...
curl -s http://localhost:8000/api/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Backend is running on http://localhost:8000
    set /a PASS+=1
) else (
    echo [FAIL] Backend is NOT running
    echo        Start with: cd backend ^&^& uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    set /a FAIL+=1
)
echo.

REM Test 2: API Documentation
echo [2/6] Checking API Documentation...
curl -s http://localhost:8000/docs >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] API docs accessible at http://localhost:8000/docs
    set /a PASS+=1
) else (
    echo [FAIL] API docs not accessible
    set /a FAIL+=1
)
echo.

REM Test 3: Login Endpoint
echo [3/6] Testing Login Endpoint...
curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"test\"}" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Login endpoint responding
    set /a PASS+=1
) else (
    echo [FAIL] Login endpoint not responding
    set /a FAIL+=1
)
echo.

REM Test 4: Frontend
echo [4/6] Checking Frontend...
curl -s http://localhost:5173 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Frontend is running on http://localhost:5173
    set /a PASS+=1
) else (
    echo [FAIL] Frontend is NOT running
    echo        Start with: cd frontend ^&^& npm run dev
    set /a FAIL+=1
)
echo.

REM Test 5: Environment Files
echo [5/6] Checking Environment Files...
if exist "backend\.env" (
    echo [PASS] Backend .env file exists
    set /a PASS+=1
) else (
    echo [FAIL] Backend .env file missing
    echo        Copy from: backend\.env.example
    set /a FAIL+=1
)
echo.

REM Test 6: Dependencies
echo [6/6] Checking Dependencies...
if exist "backend\venv" (
    echo [PASS] Backend virtual environment exists
    set /a PASS+=1
) else (
    if exist "backend\.venv" (
        echo [PASS] Backend virtual environment exists
        set /a PASS+=1
    ) else (
        echo [WARN] Backend virtual environment not found
        echo        Create with: python -m venv venv
        set /a FAIL+=1
    )
)
echo.

REM Summary
echo ========================================
echo Verification Summary
echo ========================================
echo Tests Passed: %PASS%/6
echo Tests Failed: %FAIL%/6
echo.

if %FAIL% EQU 0 (
    echo [SUCCESS] All checks passed! ✓
    echo.
    echo You can now login at: http://localhost:5173
    echo.
    echo Demo Credentials:
    echo   Username: pib_delhi
    echo   Password: officer123
    echo.
) else (
    echo [WARNING] Some checks failed!
    echo.
    echo Quick Fix:
    echo   Run: QUICK-START-LOGIN.bat
    echo.
    echo Or manually:
    echo   1. Start backend: cd backend ^&^& uvicorn app.main:app --reload
    echo   2. Start frontend: cd frontend ^&^& npm run dev
    echo   3. Initialize users: cd backend ^&^& python init_admin.py
    echo.
)

echo ========================================
echo.
pause
