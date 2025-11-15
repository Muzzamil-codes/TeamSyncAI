# TeamSync AI - WhatsApp Chat Analysis & Productivity Assistant

A powerful AI-driven productivity application that analyzes WhatsApp group chats, extracts actionable todos, identifies important dates, and enables intelligent conversations with your chat data.

## 🎯 Features

### Core Capabilities
- **Chat Analysis**: Upload WhatsApp chat exports and analyze conversations with AI
- **Todo Extraction**: Automatically identifies action items and tasks from chat messages
- **Calendar Integration**: Extracts dates and deadlines from chat content
- **Intelligent Chat**: Ask questions about your chats with context-aware responses
- **Conversation Memory**: AI remembers previous questions in the same session
- **Real-time Streaming**: See responses as they're generated (no long waits)
- **Persistent Storage**: All uploads persist during the session

### Advanced Features
- **Multiple Date Formats**: Recognizes various date formats (Nov 15, 11/15/25, 2025-11-15, etc.)
- **Dual Date Extraction**: Uses both regex patterns and AI-assisted extraction
- **Future Dates Only**: Calendar filters to show only upcoming events
- **File Management**: Delete uploaded files and associated todos/events
- **Minimalistic Design**: Clean, dark-themed UI for better focus

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI with Uvicorn ASGI server
- **AI Model**: Google Gemini 2.5-Flash with streaming support
- **LLM Library**: LangChain 0.2+
- **Language**: Python 3.8+
- **Port**: 8000

### Frontend Stack
- **Framework**: React 18.2 with TypeScript
- **Styling**: Tailwind CSS 3.3
- **Build Tool**: Vite 4.4
- **HTTP Client**: Axios 1.6
- **Icons**: Lucide React 0.263
- **Port**: 5173

## 📦 Project Structure

```
TeamSyncAI/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── rag_agent.py          # Core AI Agent with streaming
│   │   ├── routers/
│   │   │   └── llm_agent.py          # 7 API endpoints
│   │   └── main.py                   # FastAPI app setup
│   ├── pyproject.toml                # Python dependencies
│   └── .env                          # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx            # App header & branding
│   │   │   └── Navigation.tsx        # Tab navigation
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx        # File upload with drag-drop
│   │   │   ├── TodoPage.tsx          # Todo list display
│   │   │   ├── CalendarPage.tsx      # Calendar events
│   │   │   └── ChatPage.tsx          # AI chat interface
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript interfaces
│   │   ├── styles/
│   │   │   └── globals.css           # Tailwind + custom styles
│   │   ├── App.tsx                   # Main app component
│   │   └── main.tsx                  # React entry point
│   ├── package.json                  # Node dependencies
│   ├── tsconfig.json                 # TypeScript config
│   ├── tailwind.config.js            # Tailwind config
│   ├── vite.config.ts                # Vite config
│   └── index.html                    # HTML entry point
│
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google API Key for Gemini (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create environment file**
   ```bash
   # Create .env file
   echo GOOGLE_API_KEY=your_api_key_here > .env
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # OR using uv (faster)
   uv sync
   ```

4. **Run the server**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Server will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   App will be available at `http://localhost:5173`

## 📚 API Endpoints

All endpoints are prefixed with `/api/v1/agent`

### 1. **POST /upload**
Upload a WhatsApp chat file
- **Request**: Form data with `file` field (.txt file)
- **Response**: File info, auto-extracted todos and dates
- **Purpose**: Process chat and populate storage

### 2. **GET /todos**
Get all extracted todos from all uploads
- **Response**: List of todos with task and priority
- **Purpose**: Display actionable items in app

### 3. **GET /calendar**
Get all extracted dates and events
- **Response**: List of events grouped by date
- **Purpose**: Display upcoming events in calendar

### 4. **POST /chat**
Chat with AI about uploaded content
- **Request**: `{ "question": "string" }`
- **Response**: Streamed response in NDJSON format
- **Purpose**: Ask questions with context and memory

### 5. **GET /files**
List all uploaded files
- **Response**: File names, message counts, upload timestamps
- **Purpose**: Show upload history

### 6. **DELETE /files/{file_name}**
Delete a specific file and associated data
- **Response**: Confirmation of deletion
- **Purpose**: Clean up old uploads

### 7. **GET /status**
Get system status
- **Response**: Server info and statistics
- **Purpose**: Health check

## 🎨 UI Components

### Upload Section
- Drag-and-drop file upload
- Accept .txt files (WhatsApp exports)
- Display uploaded files with message counts
- Delete functionality for each file

### Todo Section
- Statistics: Total, Active, Completed counts
- Filter buttons: All, Active, Completed
- Todo items with priority badges
- Mark as complete/incomplete
- Delete individual todos

### Calendar Section
- Events grouped by date
- Long-format date display (e.g., "Monday, November 15, 2025")
- Separate "To Be Scheduled" section for TBD dates
- Event descriptions and times

### Chat Section
- Message history with user/AI distinction
- Real-time streaming responses
- Input field with multi-line support
- Loading indicators
- Auto-scroll to latest messages

## 💾 Data Storage

### Memory Buffer (Conversation)
- Stores last 10 user-AI exchanges
- Used for context in responses
- Resets on app reload

### Data Store (Uploads)
- Dictionary-based in-memory storage
- Persists during current session
- Cleared on backend restart
- Contains:
  - File name
  - File content
  - Upload timestamp
  - Extracted todos
  - Important dates

## 🤖 AI Features

### Conversation Chain with Memory
- Remembers previous questions in session
- References past conversation for context
- Natural, conversational responses
- No repetitive greetings

### Dual Date Extraction
- **Regex Patterns**: Matches multiple date formats
  - `November 15th, 2025`
  - `11/15/25` and `11-15-2025`
  - `2025-11-15`
  - Chat timestamps: `[11/15/25, 2:30 PM]`
- **AI-Assisted**: Uses Gemini to identify dates mentioned casually

### Smart Prompts
- Detects if chat data is available
- Adapts responses accordingly
- Guides users to upload data when needed
- Maintains conversation continuity

### Streaming Responses
- Uses LangChain's `.stream()` for real-time output
- NDJSON format for chunk delivery
- Frontend updates message as chunks arrive
- No waiting for full response completion

## 🔧 Configuration

### Environment Variables
```env
# Backend
GOOGLE_API_KEY=your_gemini_api_key

# Frontend (in .env or hardcoded in App.tsx)
VITE_API_BASE_URL=http://localhost:8000/api/v1/agent
```

### Customization

**Change Model**:
Edit `backend/app/core/rag_agent.py`:
```python
self.llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Change here
    ...
)
```

**Adjust Memory Size**:
Edit `backend/app/core/rag_agent.py`:
```python
self.memory_buffer: deque = deque(maxlen=10)  # Change maxlen
```

**Modify UI Colors**:
Edit `frontend/tailwind.config.js` or component classes (all use `gray-950`, `gray-900`, `gray-800`, white/gray theme)

## 🧪 Testing

### Backend Testing
```bash
# Test API endpoints
curl http://localhost:8000/api/v1/agent/status

# Test upload
curl -X POST -F "file=@chat.txt" http://localhost:8000/api/v1/agent/upload

# Test chat (streaming)
curl -X POST -H "Content-Type: application/json" \
  -d '{"question":"What are the todos?"}' \
  http://localhost:8000/api/v1/agent/chat
```

### Frontend Testing
- Upload a WhatsApp chat file
- Check todos and calendar extraction
- Ask questions in the chat
- Verify streaming responses
- Test file deletion

## 📝 WhatsApp Export Format

To use this app, export your WhatsApp chat:

1. Open WhatsApp group
2. Tap menu (⋮) → More → Export chat
3. Choose "Without media"
4. Save as .txt file
5. Upload to TeamSync

Expected format:
```
[11/15/25, 2:30 PM] User Name: Message content here
[11/15/25, 2:35 PM] Another User: Reply here
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Verify GOOGLE_API_KEY in .env
- Check port 8000 isn't in use: `netstat -ano | findstr :8000`

### Frontend won't start
- Check Node version: `node --version` (need 16+)
- Delete node_modules and run `npm install` again
- Check port 5173 isn't in use

### Chat returns 400 error
- Make sure backend is running on port 8000
- Check CORS is enabled (should be by default)
- Try refreshing the page

### Todos/Calendar not showing
- Upload a chat file first
- Wait a moment for processing
- Check browser console for errors

## 📄 License

This project is created for educational and productivity purposes.

## 👨‍💻 Developer Notes

### Key Improvements Made
1. ✅ Streaming responses instead of long waits
2. ✅ Conversation memory for context
3. ✅ Dual date extraction (regex + AI)
4. ✅ Natural conversational tone
5. ✅ Works with or without uploaded data
6. ✅ Minimalistic, clean UI design
7. ✅ Real-time message updates
8. ✅ Persistent session storage

### Future Enhancements
- Database persistence (SQLite/PostgreSQL)
- User authentication
- Custom prompts/instructions
- Bulk file uploads
- Export todos to calendar apps
- Dark/Light theme toggle
- Mobile responsive design
- Email notifications for deadlines

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review browser console for errors
3. Check terminal output from backend
4. Verify all dependencies are installed

---

**TeamSync AI** - Making productivity AI accessible to everyone 🚀

