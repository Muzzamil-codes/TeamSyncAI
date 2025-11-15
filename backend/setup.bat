@echo off
REM Setup Script for Backend Integration
REM This script sets up the integrated FastAPI backend with Gemini AI Agent

echo ===================================
echo FastAPI Backend Setup Script
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

echo [1/5] Python version check: OK
echo.

REM Install requirements
echo [2/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Check .env file
echo [3/5] Checking environment configuration...
if exist .env (
    echo .env file found
    REM Check if API key is set
    findstr /r "GOOGLE_API_KEY" .env >nul
    if errorlevel 1 (
        echo WARNING: GOOGLE_API_KEY not found in .env
        echo Please add: GOOGLE_API_KEY=your_api_key_to_.env
    ) else (
        echo GOOGLE_API_KEY is configured
    )
) else (
    echo ERROR: .env file not found
    echo Please create .env file with: GOOGLE_API_KEY=your_api_key
    exit /b 1
)
echo.

REM Test imports
echo [4/5] Testing imports...
python -c "from app.core import ChatAnalysisAgent, get_agent; print('✓ Core modules imported successfully')"
if errorlevel 1 (
    echo ERROR: Failed to import core modules
    exit /b 1
)
echo.

REM Display next steps
echo [5/5] Setup complete!
echo.
echo ===================================
echo NEXT STEPS:
echo ===================================
echo.
echo To start the backend server:
echo   uvicorn app.main:app --reload --port 8000
echo.
echo Then access:
echo   - API Docs: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo   - API Health: http://localhost:8000/
echo.
echo For integration details, see: API_INTEGRATION_GUIDE.md
echo.
pause
