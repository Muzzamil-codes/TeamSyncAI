# MongoDB Migration Summary

## Database Switch: SQLite → MongoDB

The TeamSync AI backend has been successfully migrated from SQLite (SQL) to MongoDB (NoSQL).

### What Changed

#### 1. **Database Configuration** (`app/core/database.py`)
- **Before**: SQLAlchemy ORM with SQLite
  ```python
  DATABASE_URL = "sqlite:///./teamsync.db"
  engine = create_engine(DATABASE_URL, ...)
  SessionLocal = sessionmaker(bind=engine)
  ```

- **After**: Motor (async MongoDB driver)
  ```python
  MONGODB_URL = "mongodb://localhost:27017"
  client = AsyncClient(MONGODB_URL)
  database = client["teamsync"]
  ```

**Benefits**:
- ✅ Async/await support for better performance
- ✅ Horizontal scaling capabilities
- ✅ Better for modern Python applications
- ✅ Collection-based (document-oriented) storage

#### 2. **Data Models** (`app/models.py`)
- **Before**: SQLAlchemy ORM classes with relationships
  ```python
  class User(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True)
      username = Column(String(50), unique=True)
  ```

- **After**: Pydantic models with MongoDB ObjectId
  ```python
  class User(BaseModel):
      id: Optional[PyObjectId] = Field(alias="_id", default=None)
      username: str
  ```

**Benefits**:
- ✅ Simpler data definitions
- ✅ Built-in validation
- ✅ Better JSON serialization
- ✅ Natural MongoDB ObjectId support

#### 3. **Authentication Router** (`app/routers/auth.py`)
- Migrated from SQLAlchemy session queries to async MongoDB queries
- Changed from `db.query(User).filter()` to `db["users"].find_one({...})`
- All endpoints now use `async/await`

#### 4. **LLM Agent Router** (`app/routers/llm_agent.py`)
- **CRITICAL: Unique File Storage Per User**
  - Files with the same name uploaded by the same user **overwrite** the previous version
  - Implemented with compound unique index: `(user_id, filename)`
  ```python
  # Database index
  await database["uploaded_files"].create_index(
      [("user_id", 1), ("filename", 1)], 
      unique=True
  )
  ```

- All CRUD operations converted to async MongoDB calls
- ObjectId handling for document references

#### 5. **Background Processing** (`app/tasks.py`)
- Celery tasks now work with MongoDB using asyncio integration
- Async helper functions for Celery sync context
- Process pool fallback still works for non-blocking file processing

#### 6. **Main Application** (`app/main.py`)
- Updated startup/shutdown events to use async database initialization
- Version bumped to 0.3.0

### Installation Requirements

Added MongoDB-specific packages to `requirements.txt`:
```
motor==3.3.0          # Async MongoDB driver
pymongo==4.5.0        # MongoDB Python driver
dnspython==2.4.2      # DNS resolution for MongoDB Atlas
```

Install with:
```bash
pip install motor pymongo dnspython
```

### Configuration

Update `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key
MONGODB_URL=mongodb://localhost:27017
```

For MongoDB Atlas (Cloud):
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### Database Collections

Automatically created with proper indexes:
- `users` - User accounts
- `uploaded_files` - Chat files (unique per user)
- `todos` - Todo items
- `calendar_events` - Calendar events

### Running the Backend

```bash
cd d:\KMIT\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### Key Differences to Remember

| Aspect | SQLite | MongoDB |
|--------|--------|---------|
| Queries | `db.query(Model).filter()` | `await db["collection"].find()` |
| ID Type | Integer | ObjectId (BSON) |
| Relationships | Foreign keys | Document references |
| Transactions | ACID | Per-document |
| Scaling | Single file | Distributed |
| File Uniqueness | By ID | By user + filename |

### Migration Complete ✅

All features should work exactly the same from the frontend's perspective. The backend now uses MongoDB with:
- ✅ Unique file storage per user
- ✅ Async/await throughout
- ✅ Better scalability
- ✅ Proper indexes for performance
- ✅ Fallback processing without Redis
