# Database, Authentication & Background Processing Setup Guide

## Overview

Your TeamSync AI application has been enhanced with three critical features:

1. **Persistent Database Storage** - SQLite (dev) / PostgreSQL (prod)
2. **JWT Authentication** - Secure user login/registration
3. **Background Processing** - Celery + Redis for async tasks

---

## 1. DATABASE SETUP (SQLAlchemy)

### Architecture

```
Database Models:
├── User (authentication)
├── UploadedFile (chat files)
├── TodoItem (extracted todos)
└── CalendarEvent (extracted dates)
```

### Files Created

- `backend/app/core/database.py` - Database configuration & session management
- `backend/app/models.py` - SQLAlchemy ORM models
- `backend/migrations/` - (Optional) Alembic migrations folder

### Configuration

Edit `backend/.env`:

```bash
# SQLite (Development - Default)
DATABASE_URL=sqlite:///./teamsync.db

# PostgreSQL (Production)
# DATABASE_URL=postgresql://username:password@localhost:5432/teamsync
```

### Initialize Database

```bash
cd backend
python -c "from app.core.database import init_db; init_db()"
```

### Models Overview

**User Model**
- Stores user credentials and metadata
- One-to-many relationship with UploadedFile, TodoItem, CalendarEvent
- Cascading delete for user cleanup

**UploadedFile Model**
- Links files to specific users
- Stores content, message count, timestamps
- Cascading delete removes todos/calendar events

**TodoItem Model**
- Extracted action items with priority levels
- Priority enum: LOW, MEDIUM, HIGH
- Linked to user and source file

**CalendarEvent Model**
- Extracted dates and events
- Supports scheduled/unscheduled (TBD) events
- Future-date filtering in endpoints

---

## 2. AUTHENTICATION (JWT)

### Architecture

```
Flow:
1. User registers/logs in → POST /api/v1/auth/register | /login
2. Server returns access_token (JWT)
3. Client stores token in localStorage
4. Client sends token in Authorization header
5. Server validates token via get_current_user dependency
```

### Files Created

- `backend/app/core/security.py` - JWT token creation/validation, password hashing
- `backend/app/routers/auth.py` - Auth endpoints (login, register, logout, me)
- `frontend/src/context/AuthContext.tsx` - React context for auth state
- `frontend/src/pages/LoginPage.tsx` - Login UI
- `frontend/src/pages/RegisterPage.tsx` - Registration UI

### Configuration

Edit `backend/.env`:

```bash
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ IMPORTANT**: Change `SECRET_KEY` before production deployment!

### Endpoints

**POST /api/v1/auth/register**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```
Returns: `{ access_token, token_type, user }`

**POST /api/v1/auth/login**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```
Returns: `{ access_token, token_type, user }`

**GET /api/v1/auth/me**
- Requires: Bearer token
- Returns: Current user info

**POST /api/v1/auth/logout**
- Client-side: Remove token from localStorage

### Protected Endpoints

All endpoints now require authentication:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/agent/upload
```

### Frontend Integration

1. Wrap app with `AuthProvider` in `main.tsx`:
```tsx
import { AuthProvider } from './context/AuthContext';

ReactDOM.render(
  <AuthProvider>
    <App />
  </AuthProvider>,
  document.getElementById('root')
);
```

2. Use in components:
```tsx
import { useAuth } from '../context/AuthContext';

function MyComponent() {
  const { user, login, logout } = useAuth();
  // ...
}
```

3. Protect routes:
```tsx
import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
}
```

---

## 3. BACKGROUND PROCESSING (Celery + Redis)

### Architecture

```
Flow:
1. User uploads file → /api/v1/agent/upload
2. File stored in DB with user_id
3. Task queued: process_uploaded_file.delay(file_id, user_id)
4. Celery worker processes in background
5. Extracts todos/dates, stores in DB
6. Response returns task_id for monitoring
```

### Files Created

- `backend/app/core/celery_config.py` - Celery configuration
- `backend/app/tasks.py` - Background tasks

### Configuration

Install Redis:

```bash
# Windows (using Chocolatey)
choco install redis-64

# macOS (using Homebrew)
brew install redis

# Linux (Ubuntu/Debian)
sudo apt-get install redis-server

# Docker
docker run -d -p 6379:6379 redis:latest
```

Start Redis:
```bash
redis-server
```

Edit `backend/.env`:
```bash
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Running Celery Worker

```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

### Tasks Available

**process_uploaded_file**
```python
@celery_app.task(bind=True, max_retries=3)
def process_uploaded_file(self, file_id: int, user_id: int):
    """
    Async file processing:
    - Extract todos via AI
    - Extract calendar events
    - Store in database
    - Auto-retry on failure (3x)
    """
```

**cleanup_old_files**
```python
@celery_app.task(bind=True)
def cleanup_old_files(self, days: int = 30):
    """
    Daily cleanup task (scheduled via Celery Beat)
    Removes files older than N days
    """
```

**analyze_chat_async**
```python
@celery_app.task(bind=True)
def analyze_chat_async(self, file_id: int, user_id: int, question: str):
    """
    Heavy LLM analysis (optional)
    Offloads expensive inference to background
    """
```

### Optional: Celery Beat (Scheduler)

For periodic tasks, start Celery Beat:

```bash
celery -A app.tasks beat --loglevel=info
```

This will run `cleanup_old_files` daily at 2 AM.

### Monitoring Celery Tasks

**Option 1: Flower (Celery Web UI)**

```bash
pip install flower
celery -A app.tasks flower
```

Visit: http://localhost:5555

**Option 2: Celery Shell**

```bash
celery -A app.tasks inspect active
celery -A app.tasks inspect scheduled
celery -A app.tasks inspect stats
```

---

## 4. UPDATED ENDPOINTS

All endpoints now:
- Require JWT authentication
- Use database for persistence
- Support per-user data isolation
- Queue background tasks where needed

### Upload Endpoint

**POST /api/v1/agent/upload**

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "file=@chat.txt" \
  http://localhost:8000/api/v1/agent/upload
```

Response:
```json
{
  "status": "success",
  "message": "File uploaded. Processing in background.",
  "file_id": 42,
  "file_name": "chat.txt",
  "task_id": "celery-task-uuid"
}
```

### Get Todos

**GET /api/v1/agent/todos?file_id=42**

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/agent/todos
```

### Get Calendar Events

**GET /api/v1/agent/calendar?file_id=42**

### Chat Endpoint

**POST /api/v1/agent/chat**

```json
{
  "question": "What are the action items?",
  "file_id": 42
}
```

Returns: Streaming NDJSON response

---

## 5. STARTUP SEQUENCE

### Terminal 1: Redis
```bash
redis-server
```

### Terminal 2: Celery Worker
```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

### Terminal 3: Backend API
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 4: Frontend
```bash
cd frontend
npm run dev
```

Then visit: http://localhost:5173

---

## 6. DATABASE MIGRATIONS (Optional)

For production, use Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add User model"

# Apply migration
alembic upgrade head
```

---

## 7. PRODUCTION DEPLOYMENT

### Environment Variables

Create `backend/.env.production`:

```bash
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/teamsync
SECRET_KEY=your-very-secret-key-here
REDIS_URL=redis://:password@prod-redis-host:6379/0
GOOGLE_API_KEY=your-google-api-key
ENVIRONMENT=production
```

### Database Setup (PostgreSQL)

```bash
# Install PostgreSQL, create database
createdb teamsync

# Run migrations
alembic upgrade head
```

### Security Checklist

- [ ] Change `SECRET_KEY` to random string
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS/SSL
- [ ] Update CORS origins in `main.py`
- [ ] Set strong Redis password
- [ ] Use environment variables (not hardcoded)
- [ ] Enable password reset flow
- [ ] Implement rate limiting
- [ ] Add audit logging

---

## 8. TROUBLESHOOTING

### "No module named 'sqlalchemy'"
```bash
pip install -r requirements.txt
```

### "Redis connection refused"
- Ensure Redis is running: `redis-cli ping`
- Check `REDIS_URL` in `.env`

### "JWT token invalid"
- Token expired: User needs to login again
- Wrong secret: Ensure `SECRET_KEY` matches

### Database locked (SQLite)
```bash
# Remove the DB and start fresh
rm teamsync.db
python -c "from app.core.database import init_db; init_db()"
```

### Celery tasks not processing
- Check worker is running
- Check Redis is running
- Check logs for errors: `celery -A app.tasks worker --loglevel=debug`

---

## 9. TESTING

### Create Test User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Upload File

```bash
TOKEN="<access_token_from_register>"

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@chat.txt" \
  http://localhost:8000/api/v1/agent/upload
```

### Monitor Task

```bash
celery -A app.tasks inspect active
```

---

## 10. NEXT STEPS

1. **Frontend Routing**: Update `App.tsx` to include `/login` and `/register` routes
2. **Error Handling**: Add error boundaries and toast notifications
3. **Token Refresh**: Implement refresh token flow for long sessions
4. **Password Reset**: Add forgot password endpoint
5. **User Settings**: Create user profile/settings page
6. **API Documentation**: Add Swagger docs (`/docs`)

---

## Summary

✅ **Persistent Storage**: All data survives process restarts
✅ **Authentication**: Secure user accounts with JWT
✅ **Background Processing**: Heavy tasks don't block API
✅ **Production Ready**: Database, caching, and async patterns implemented
✅ **Scalable**: Architecture supports multi-worker deployment

Questions? Check the code comments or review the original issue tracker.
