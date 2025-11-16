# MongoDB Setup Instructions

## Prerequisites

You need MongoDB running locally or accessible via network.

### Option 1: MongoDB Community Edition (Local)

#### Windows

1. **Download MongoDB Community Edition**
   - Go to https://www.mongodb.com/try/download/community
   - Download the Windows installer
   - Run the installer and follow the setup wizard

2. **Verify Installation**
   ```powershell
   mongod --version
   ```

3. **Start MongoDB Service**
   - MongoDB should start automatically as a Windows service
   - Or manually start: 
     ```powershell
     mongod --dbpath "C:\data\db"
     ```

4. **Verify MongoDB is Running**
   ```powershell
   mongosh
   ```
   This opens the MongoDB shell. Type `exit` to quit.

#### macOS

```bash
# Install via Homebrew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Verify
mongosh
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt-get install -y mongodb

# Start service
sudo systemctl start mongod

# Verify
mongosh
```

### Option 2: MongoDB Atlas (Cloud)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free account
3. Create a new project and cluster
4. Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)
5. Update `.env` file:
   ```env
   MONGODB_URL=mongodb+srv://your_username:your_password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

### Option 3: Docker

```bash
# Run MongoDB in Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Verify
docker ps
```

## Verify MongoDB Connection

After starting MongoDB, test the connection:

```powershell
# In the backend directory
python -c "from motor.motor_asyncio import AsyncClient; import asyncio; client = AsyncClient('mongodb://localhost:27017'); print('✓ MongoDB connected!')"
```

## Common Issues

### "Connection refused" error
- Make sure MongoDB is running (check `mongod` process)
- Verify MONGODB_URL in `.env` is correct
- Default local: `mongodb://localhost:27017`

### "Authentication failed" error (MongoDB Atlas)
- Check username and password in connection string
- Ensure IP address is whitelisted in Atlas

### Permission denied on Windows
- Run PowerShell as Administrator
- Or use the MongoDB Service Manager (Ctrl+Alt+Del → Services)

## Next Steps

Once MongoDB is running:
1. Start the backend: `python -m uvicorn app.main:app --reload --port 8001`
2. The backend will automatically create indexes on startup
3. Your data will persist in MongoDB

## Database Location

- **Local Installation**: `C:\Program Files\MongoDB\Server\<version>\data` (Windows)
- **Docker**: Inside container at `/data/db`
- **Cloud (Atlas)**: Hosted MongoDB servers
