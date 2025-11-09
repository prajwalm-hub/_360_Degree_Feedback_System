@echo off
echo ================================================
echo NewsScope India - RAG Assistant Quick Start
echo ================================================
echo.

echo Step 1: Installing RAG dependencies...
cd backend
pip install langchain==0.1.0 langchain-community==0.0.13 faiss-cpu==1.7.4 chromadb==0.4.22 tiktoken==0.5.2
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up RAG system...
python setup_rag.py

echo.
echo ================================================
echo RAG Assistant Setup Complete!
echo ================================================
echo.
echo To use the RAG assistant:
echo 1. Make sure backend is running (START-BACKEND-8001.bat)
echo 2. Access the assistant at: http://localhost:8000
echo 3. Navigate to the "AI Assistant" tab
echo.
echo API Documentation: http://localhost:8000/docs
echo.
pause
