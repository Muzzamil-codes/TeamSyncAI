@echo off
REM Quick Installation & Setup Script for TeamSync AI with Database, Auth & Celery (Windows)

echo ==========================================
echo TeamSync AI - Full Stack Setup (Windows)
echo ==========================================
echo.

REM Step 1: Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
echo Python found!
echo.

REM Step 2: Check Node
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install from https://nodejs.org
    pause
    exit /b 1
)
echo Node.js found!
echo.

REM Step 3: Install Redis
echo [3/6] Installing Redis...
echo Installing Redis for Windows...
echo.
echo Option A: Using Chocolatey
echo   choco install redis-64
echo.
echo Option B: Docker
echo   docker run -d -p 6379:6379 redis:latest
echo.
echo Option C: Download
echo   https://github.com/microsoftarchive/redis/releases
echo.
echo Please install Redis and press Enter to continue...
pause

REM Step 4: Backend Setup
echo [4/6] Setting up backend...
cd backend
echo Installing Python dependencies...
pip install -r requirements.txt

echo Initializing database...
python -c "from app.core.database import init_db; init_db()"
cd ..

echo Backend ready!
echo.

REM Step 5: Frontend Setup
echo [5/6] Setting up frontend...
cd frontend
echo Installing Node dependencies...
call npm install
cd ..

echo Frontend ready!
echo.

REM Step 6: Environment
echo [6/6] Creating .env file...

if not exist "backend\.env" (
    echo Creating backend\.env...
    copy backend\.env.example backend\.env
    
    echo.
    echo ^^!^^! IMPORTANT ^^!^^!
    echo Edit backend\.env and set:
    echo   - GOOGLE_API_KEY (required for LLM)
    echo   - SECRET_KEY (change for production)
    echo   - DATABASE_URL (use SQLite for dev)
    echo   - REDIS_URL (localhost:6379 if Redis locally)
    echo.
    pause
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the application, open 4 terminal windows:
echo.
echo Terminal 1 - Redis:
echo   redis-server
echo.
echo Terminal 2 - Celery Worker:
echo   cd backend
echo   celery -A app.tasks worker --loglevel=info
echo.
echo Terminal 3 - Backend API:
echo   cd backend
echo   python -m uvicorn app.main:app --reload --port 8000
echo.
echo Terminal 4 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Then visit: http://localhost:5173
echo.
echo ==========================================
echo Quick Test:
echo ==========================================
echo 1. Register at /register
echo 2. Login at /login
echo 3. Upload a WhatsApp chat file
echo 4. Check extracted todos and calendar
echo.
echo ==========================================
echo.
pause
