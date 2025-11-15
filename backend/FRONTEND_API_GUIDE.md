# Frontend-Optimized API Documentation

## Overview

The API has been restructured to support your 4-section React SPA:
1. **Upload Section** - Upload WhatsApp chat files
2. **Todo List Section** - View extracted todos
3. **Calendar Section** - View important dates
4. **Chat Section** - Chat with the AI agent about the files

All sections use a **common data storage** that persists across the entire session.

---

## API Endpoints

### 1. Upload Chat File
**Endpoint:** `POST /api/v1/agent/upload`

Upload a WhatsApp chat export. This is the main entry point that populates the common storage.

**Request:**
```
Content-Type: multipart/form-data
Body: file (WhatsApp .txt export)
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Successfully uploaded chat.txt with 150 messages",
  "file_name": "chat.txt",
  "message_count": 150,
  "todos": [
    "- Follow up with John on project",
    "- Submit Q3 report by Friday",
    "- Schedule meeting with team"
  ],
  "important_dates": [
    {
      "date": "TBD",
      "event": "Submit Q3 report by Friday",
      "description": "Extracted from todo items"
    }
  ]
}
```

**Frontend Usage:**
```javascript
// Upload Section
const handleFileUpload = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/v1/agent/upload', {
    method: 'POST',
    body: formData,
  });
  
  const data = await response.json();
  // Display todos in Todo List section
  // Display dates in Calendar section
};
```

---

### 2. Get Todos
**Endpoint:** `GET /api/v1/agent/todos`

Retrieve all todos extracted from uploaded chat files. Uses common storage.

**Response (200 OK):**
```json
{
  "todos": [
    {
      "task": "Follow up with John on project",
      "priority": "medium",
      "status": "pending"
    },
    {
      "task": "Submit Q3 report by Friday",
      "priority": "medium",
      "status": "pending"
    }
  ],
  "count": 2,
  "last_updated": "2025-11-15T10:30:00.000000"
}
```

**Frontend Usage:**
```javascript
// Todo List Section
const fetchTodos = async () => {
  const response = await fetch('/api/v1/agent/todos');
  const data = await response.json();
  
  setTodos(data.todos);
  setLastUpdated(data.last_updated);
};
```

---

### 3. Get Calendar Events
**Endpoint:** `GET /api/v1/agent/calendar`

Retrieve important dates and events extracted from uploaded chats. Uses common storage.

**Response (200 OK):**
```json
{
  "dates": [
    {
      "date": "TBD",
      "event": "Submit Q3 report by Friday",
      "description": "Extracted from todo items"
    },
    {
      "date": "2025-11-25",
      "event": "Project Q4 Launch",
      "description": "Mentioned in chat discussion"
    }
  ],
  "count": 2,
  "last_updated": "2025-11-15T10:30:00.000000"
}
```

**Frontend Usage:**
```javascript
// Calendar Section
const fetchCalendarEvents = async () => {
  const response = await fetch('/api/v1/agent/calendar');
  const data = await response.json();
  
  setEvents(data.dates);
  setLastUpdated(data.last_updated);
};
```

---

### 4. Chat with AI Agent
**Endpoint:** `POST /api/v1/agent/chat`

Send a message to the AI agent. The agent has access to all uploaded chat content from common storage.

**Request:**
```json
{
  "question": "What are the main decisions discussed?"
}
```

**Response (200 OK):**
```json
{
  "answer": "Based on the uploaded chats, the main decisions include: 1) Project launch scheduled for Q4, 2) Team expansion planned, 3) Q3 targets exceeded by 15%"
}
```

**Frontend Usage:**
```javascript
// Chat Section
const sendMessage = async (message) => {
  const response = await fetch('/api/v1/agent/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: message }),
  });
  
  const data = await response.json();
  addMessageToChat(data.answer);
};
```

---

### 5. List Uploaded Files
**Endpoint:** `GET /api/v1/agent/files`

Get information about all uploaded files in the common storage.

**Response (200 OK):**
```json
{
  "files": [
    {
      "file_name": "group_chat.txt",
      "uploaded_at": "2025-11-15T10:15:00.000000",
      "message_count": 150,
      "todo_count": 5,
      "date_count": 2
    },
    {
      "file_name": "project_chat.txt",
      "uploaded_at": "2025-11-15T10:30:00.000000",
      "message_count": 200,
      "todo_count": 8,
      "date_count": 3
    }
  ],
  "total_files": 2
}
```

**Frontend Usage:**
```javascript
// File Management
const listFiles = async () => {
  const response = await fetch('/api/v1/agent/files');
  const data = await response.json();
  
  setUploadedFiles(data.files);
};
```

---

### 6. Delete File
**Endpoint:** `DELETE /api/v1/agent/files/{file_name}`

Remove a file from common storage.

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "File group_chat.txt deleted successfully"
}
```

**Frontend Usage:**
```javascript
// Remove file from common storage
const deleteFile = async (fileName) => {
  const response = await fetch(`/api/v1/agent/files/${fileName}`, {
    method: 'DELETE',
  });
  
  const data = await response.json();
  // Refresh todos, calendar, and chat context
};
```

---

### 7. Get System Status
**Endpoint:** `GET /api/v1/agent/status`

Get current status of the system including file counts and total extracted data.

**Response (200 OK):**
```json
{
  "files_uploaded": 2,
  "total_messages": 350,
  "total_todos": 13,
  "total_calendar_events": 5,
  "is_ready": true
}
```

**Frontend Usage:**
```javascript
// Status Bar / Dashboard
const getStatus = async () => {
  const response = await fetch('/api/v1/agent/status');
  const data = await response.json();
  
  setSystemStatus(data);
  if (!data.is_ready) {
    showMessage("Please upload a chat file first");
  }
};
```

---

## Common Data Storage Architecture

### How It Works:

```
Frontend Upload Section
         ↓
    Upload Chat File
         ↓
POST /api/v1/agent/upload
         ↓
┌─────────────────────────┐
│   Common Data Storage   │
│  (_data_store dict)     │
├─────────────────────────┤
│ ┌────────────────────┐  │
│ │  File 1: chat.txt  │  │
│ │  - Content         │  │
│ │  - Extracted Todos │  │
│ │  - Important Dates │  │
│ └────────────────────┘  │
│                         │
│ ┌────────────────────┐  │
│ │  File 2: group.txt │  │
│ │  - Content         │  │
│ │  - Extracted Todos │  │
│ │  - Important Dates │  │
│ └────────────────────┘  │
└─────────────────────────┘
     ↙        ↓        ↖
    /         |         \
GET /todos  GET /chat  GET /calendar
   ↓          ↓          ↓
Todo List   Chat Box   Calendar
```

### Key Characteristics:

1. **Persistent During Session** - Data stays in memory for the duration of the session
2. **Cumulative** - Multiple files can be uploaded and their data combined
3. **Unified Context** - Chat endpoint has access to all uploaded content
4. **Automatic Extraction** - Todos and dates are automatically extracted on upload

---

## Error Handling

### 400 Bad Request
```json
{
  "detail": "No chat files uploaded. Please upload a chat file first using the /upload endpoint."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error processing chat: [error details]"
}
```

---

## Frontend Integration Guide

### Step 1: Upload Implementation
```javascript
const Upload = () => {
  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await fetch('/api/v1/agent/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      
      // Display success
      console.log(`Uploaded: ${data.file_name}`);
      console.log(`Todos: ${data.todos.length}`);
      console.log(`Dates: ${data.important_dates.length}`);
      
      // Refresh other sections
      refreshTodos();
      refreshCalendar();
      
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };
  
  return (
    <input 
      type="file" 
      onChange={(e) => handleUpload(e.target.files[0])}
    />
  );
};
```

### Step 2: Todo List Implementation
```javascript
const TodoList = () => {
  const [todos, setTodos] = useState([]);
  
  useEffect(() => {
    fetchTodos();
  }, []);
  
  const fetchTodos = async () => {
    try {
      const res = await fetch('/api/v1/agent/todos');
      const data = await res.json();
      setTodos(data.todos);
    } catch (error) {
      console.error('Failed to fetch todos:', error);
    }
  };
  
  return (
    <div>
      {todos.map((todo) => (
        <div key={todo.task}>
          <input type="checkbox" />
          <span>{todo.task}</span>
          <span className="priority">{todo.priority}</span>
        </div>
      ))}
    </div>
  );
};
```

### Step 3: Calendar Implementation
```javascript
const Calendar = () => {
  const [events, setEvents] = useState([]);
  
  useEffect(() => {
    fetchCalendar();
  }, []);
  
  const fetchCalendar = async () => {
    try {
      const res = await fetch('/api/v1/agent/calendar');
      const data = await res.json();
      setEvents(data.dates);
    } catch (error) {
      console.error('Failed to fetch calendar:', error);
    }
  };
  
  return (
    <div>
      {events.map((event) => (
        <div key={event.event}>
          <span className="date">{event.date}</span>
          <span className="event">{event.event}</span>
        </div>
      ))}
    </div>
  );
};
```

### Step 4: Chat Implementation
```javascript
const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const sendMessage = async () => {
    try {
      const res = await fetch('/api/v1/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });
      
      const data = await res.json();
      setMessages([...messages, 
        { role: 'user', text: input },
        { role: 'assistant', text: data.answer }
      ]);
      setInput('');
      
    } catch (error) {
      console.error('Chat failed:', error);
    }
  };
  
  return (
    <div>
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>
            {msg.text}
          </div>
        ))}
      </div>
      <input 
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};
```

---

## Summary of Changes

### Old API (Separate Operations)
- `/build` - Index chat
- `/query` - Ask question
- `/todos` - Extract todos
- `/summary` - Get summary

**Problem:** Required sequential calls, no persistent storage

### New API (Unified Storage)
- `/upload` - Upload and auto-extract
- `/chat` - Chat (uses all uploaded files)
- `/todos` - Get todos (from all files)
- `/calendar` - Get dates (from all files)
- `/files` - Manage uploads
- `/status` - System status

**Benefits:** 
✓ Single upload populates all sections  
✓ Common storage shared across endpoints  
✓ Multiple files supported  
✓ Auto-extraction of todos and dates  
✓ Persistent during session  

---

## Testing the API

### Using cURL:

```bash
# 1. Upload file
curl -X POST "http://localhost:8000/api/v1/agent/upload" \
  -F "file=@chat.txt"

# 2. Get todos
curl -X GET "http://localhost:8000/api/v1/agent/todos"

# 3. Get calendar
curl -X GET "http://localhost:8000/api/v1/agent/calendar"

# 4. Chat
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What were the main points?"}'

# 5. List files
curl -X GET "http://localhost:8000/api/v1/agent/files"

# 6. Get status
curl -X GET "http://localhost:8000/api/v1/agent/status"
```

---

**Status:** ✅ Ready for Frontend Integration
