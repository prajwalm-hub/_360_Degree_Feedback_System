@echo off
REM Quick Start Script for NewsScope India Automated Collection
REM Run this to test the complete system

echo ============================================================
echo   NewsScope India - Automated News Collection System
echo   Quick Start Test
echo ============================================================
echo.

echo [1/5] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
echo.

echo [2/5] Installing dependencies...
cd backend
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
)
echo.

echo [3/5] Testing RSS collection (dry run)...
python collect_news_enhanced.py --dry-run --language en
if errorlevel 1 (
    echo ERROR: Collection test failed!
    pause
    exit /b 1
)
echo.

echo [4/5] Running actual collection (RSS only)...
python collect_news_enhanced.py --language hi
if errorlevel 1 (
    echo ERROR: Collection failed!
    pause
    exit /b 1
)
echo.

echo [5/5] Starting FastAPI server...
echo.
echo ============================================================
echo   Collection Complete!
echo   Starting API server on http://localhost:8000
echo   Dashboard available at http://localhost:5173
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
