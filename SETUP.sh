#!/bin/bash
# Quick Installation & Setup Script for TeamSync AI with Database, Auth & Celery

echo "=========================================="
echo "TeamSync AI - Full Stack Setup"
echo "=========================================="
echo ""

# Step 1: Install Redis
echo "[1/5] Installing Redis..."
echo "For Windows:"
echo "  Option A: choco install redis-64"
echo "  Option B: Download from https://github.com/microsoftarchive/redis/releases"
echo "  Option C: docker run -d -p 6379:6379 redis:latest"
echo ""
echo "For macOS:"
echo "  brew install redis"
echo ""
echo "For Linux:"
echo "  sudo apt-get install redis-server"
echo ""

# Step 2: Backend Setup
echo "[2/5] Setting up backend..."
cd backend || exit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Initializing database..."
python -c "from app.core.database import init_db; init_db()"

echo "Backend ready!"
echo ""

cd ..

# Step 3: Frontend Setup
echo "[3/5] Setting up frontend..."
cd frontend || exit

echo "Installing Node dependencies..."
npm install

echo "Frontend ready!"
echo ""

cd ..

# Step 4: Environment Setup
echo "[4/5] Creating .env file..."

if [ ! -f backend/.env ]; then
  echo "Creating backend/.env..."
  cp backend/.env.example backend/.env
  
  echo "⚠️  IMPORTANT: Edit backend/.env and set:"
  echo "  - GOOGLE_API_KEY (required)"
  echo "  - SECRET_KEY (for production, change the default)"
  echo "  - DATABASE_URL (if not using SQLite)"
  echo "  - REDIS_URL (default is fine if Redis on localhost)"
fi

echo ""

# Step 5: Summary
echo "[5/5] Setup Complete!"
echo ""
echo "=========================================="
echo "To start the application:"
echo "=========================================="
echo ""
echo "Terminal 1 - Redis:"
echo "  redis-server"
echo ""
echo "Terminal 2 - Celery Worker:"
echo "  cd backend"
echo "  celery -A app.tasks worker --loglevel=info"
echo ""
echo "Terminal 3 - Backend API:"
echo "  cd backend"
echo "  python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "Terminal 4 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then visit: http://localhost:5173"
echo ""
echo "=========================================="
echo "Quick Test:"
echo "=========================================="
echo "1. Register: /register"
echo "2. Login: /login"
echo "3. Upload chat file"
echo "4. Check todos & calendar"
echo ""
echo "=========================================="
echo ""
