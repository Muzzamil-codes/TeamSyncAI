# React SPA Frontend Integration Guide

## 🎯 Overview

Your 4-section React SPA now has a perfectly matched backend API. Here's how to integrate each section:

### Frontend Architecture:
```
React SPA
├── Upload Section    ← POST /api/v1/agent/upload
├── Todo List Section ← GET /api/v1/agent/todos
├── Calendar Section  ← GET /api/v1/agent/calendar
└── Chat Section      ← POST /api/v1/agent/chat
```

### Backend Architecture:
```
Common Data Storage
├── File 1 Content + Auto-Extracted Todos + Auto-Extracted Dates
├── File 2 Content + Auto-Extracted Todos + Auto-Extracted Dates
└── File N Content + Auto-Extracted Todos + Auto-Extracted Dates
```

---

## 📤 Section 1: Upload Component

This is the entry point. When a user uploads a file, everything is automatically extracted and stored.

### Component Code:

```javascript
import React, { useState } from 'react';

const Upload = ({ onUploadSuccess, onTodosExtracted, onDatesExtracted }) => {
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Call backend upload endpoint
      const response = await fetch('/api/v1/agent/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();

      // Update UI with extraction results
      console.log('✓ File uploaded:', data.file_name);
      console.log('✓ Messages parsed:', data.message_count);
      console.log('✓ Todos extracted:', data.todos.length);
      console.log('✓ Dates extracted:', data.important_dates.length);

      // Add to uploaded files list
      setUploadedFiles([...uploadedFiles, data.file_name]);

      // Notify parent components
      onUploadSuccess(data);
      onTodosExtracted(data.todos);
      onDatesExtracted(data.important_dates);

      // Show success message
      alert(`Successfully uploaded ${data.file_name}\n\nExtracted:\n- ${data.todos.length} todos\n- ${data.important_dates.length} dates`);

    } catch (err) {
      setError(err.message);
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-section">
      <h2>📤 Upload Chat</h2>
      
      <div className="upload-area">
        <input
          type="file"
          accept=".txt"
          onChange={handleFileUpload}
          disabled={loading}
          id="file-input"
        />
        <label htmlFor="file-input">
          {loading ? 'Uploading...' : 'Click to upload WhatsApp chat'}
        </label>
      </div>

      {error && <div className="error">{error}</div>}

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h3>Uploaded Files ({uploadedFiles.length}):</h3>
          <ul>
            {uploadedFiles.map((file) => (
              <li key={file}>{file}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Upload;
```

---

## ✅ Section 2: Todo List Component

Displays all extracted todos from uploaded files. Can mark as complete.

### Component Code:

```javascript
import React, { useState, useEffect } from 'react';

const TodoList = () => {
  const [todos, setTodos] = useState([]);
  const [completedTodos, setCompletedTodos] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchTodos();
    
    // Refresh todos every 5 seconds
    const interval = setInterval(fetchTodos, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchTodos = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/agent/todos');
      const data = await response.json();

      setTodos(data.todos);
      setLastUpdated(data.last_updated);
      
    } catch (error) {
      console.error('Failed to fetch todos:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleTodo = (task) => {
    const newCompleted = new Set(completedTodos);
    if (newCompleted.has(task)) {
      newCompleted.delete(task);
    } else {
      newCompleted.add(task);
    }
    setCompletedTodos(newCompleted);
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ff6b6b';
      case 'medium': return '#ffd93d';
      case 'low': return '#6bcf7f';
      default: return '#999';
    }
  };

  return (
    <div className="todo-section">
      <h2>✅ Todo List</h2>
      
      {loading && todos.length === 0 && <p>Loading todos...</p>}

      {todos.length === 0 && !loading && (
        <p className="empty">No todos yet. Upload a chat file to extract todos.</p>
      )}

      <div className="todos-container">
        {todos.map((todo, index) => (
          <div key={index} className="todo-item">
            <input
              type="checkbox"
              checked={completedTodos.has(todo.task)}
              onChange={() => toggleTodo(todo.task)}
            />
            <span 
              className={completedTodos.has(todo.task) ? 'completed' : ''}
            >
              {todo.task}
            </span>
            <span 
              className="priority-badge"
              style={{ backgroundColor: getPriorityColor(todo.priority) }}
            >
              {todo.priority}
            </span>
          </div>
        ))}
      </div>

      <div className="stats">
        <span>Total: {todos.length}</span>
        <span>Completed: {completedTodos.size}</span>
        {lastUpdated && (
          <span className="timestamp">
            Last updated: {new Date(lastUpdated).toLocaleTimeString()}
          </span>
        )}
      </div>
    </div>
  );
};

export default TodoList;
```

---

## 📅 Section 3: Calendar Component

Shows important dates and events extracted from chats.

### Component Code:

```javascript
import React, { useState, useEffect } from 'react';

const Calendar = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchCalendarEvents();
    
    // Refresh every 5 seconds
    const interval = setInterval(fetchCalendarEvents, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchCalendarEvents = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/agent/calendar');
      const data = await response.json();

      setEvents(data.dates);
      setLastUpdated(data.last_updated);
      
    } catch (error) {
      console.error('Failed to fetch calendar events:', error);
    } finally {
      setLoading(false);
    }
  };

  const isUpcoming = (dateStr) => {
    if (dateStr === 'TBD') return false;
    const eventDate = new Date(dateStr);
    const today = new Date();
    return eventDate >= today;
  };

  return (
    <div className="calendar-section">
      <h2>📅 Calendar</h2>
      
      {loading && events.length === 0 && <p>Loading calendar events...</p>}

      {events.length === 0 && !loading && (
        <p className="empty">No calendar events yet. Upload a chat file to extract dates.</p>
      )}

      <div className="events-container">
        {events.map((event, index) => (
          <div key={index} className="event-item">
            <div className="event-date">
              {event.date === 'TBD' ? '📌 TBD' : new Date(event.date).toLocaleDateString()}
            </div>
            <div className="event-content">
              <h4>{event.event}</h4>
              {event.description && <p>{event.description}</p>}
            </div>
            {isUpcoming(event.date) && (
              <span className="upcoming-badge">Upcoming</span>
            )}
          </div>
        ))}
      </div>

      {lastUpdated && (
        <div className="timestamp">
          Last updated: {new Date(lastUpdated).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
};

export default Calendar;
```

---

## 💬 Section 4: Chat Component

Chat interface to ask questions about the uploaded chats. AI has access to all uploaded content.

### Component Code:

```javascript
import React, { useState, useRef, useEffect } from 'react';

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Send to backend
      const response = await fetch('/api/v1/agent/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      // Add AI response
      setMessages(prev => [...prev, { role: 'assistant', text: data.answer }]);

    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: `Error: ${err.message}` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-section">
      <h2>💬 Chat with AI</h2>
      
      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <p>👋 Welcome! Upload a chat file and ask me anything about it.</p>
              <p>I can answer questions, summarize discussions, and help you find important information.</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <span className="role">{msg.role === 'user' ? 'You' : 'AI'}</span>
              <p>{msg.text}</p>
            </div>
          ))}

          {loading && (
            <div className="message assistant loading">
              <span className="role">AI</span>
              <p>Thinking... ⏳</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          {error && <div className="error-message">{error}</div>}
          
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about the uploaded chats..."
            disabled={loading}
            rows="3"
          />
          
          <button onClick={sendMessage} disabled={loading || !input.trim()}>
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;
```

---

## 🎨 Main App Component

Combine all 4 sections:

```javascript
import React, { useState } from 'react';
import Upload from './sections/Upload';
import TodoList from './sections/TodoList';
import Calendar from './sections/Calendar';
import ChatBox from './sections/ChatBox';
import './App.css';

function App() {
  const [uploadData, setUploadData] = useState(null);

  const handleUploadSuccess = (data) => {
    setUploadData(data);
  };

  return (
    <div className="app">
      <header>
        <h1>📊 TeamSync AI</h1>
        <p>WhatsApp Chat Analysis with AI</p>
      </header>

      <main className="sections-grid">
        <section className="upload-container">
          <Upload onUploadSuccess={handleUploadSuccess} />
        </section>

        <section className="todos-container">
          <TodoList />
        </section>

        <section className="calendar-container">
          <Calendar />
        </section>

        <section className="chat-container">
          <ChatBox />
        </section>
      </main>
    </div>
  );
}

export default App;
```

---

## 🎨 Basic CSS Styling

```css
.app {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px 0;
  border-bottom: 2px solid #007bff;
}

header h1 {
  margin: 0;
  color: #333;
}

header p {
  margin: 10px 0 0 0;
  color: #666;
}

.sections-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 30px;
}

/* Upload Section */
.upload-section {
  border: 2px dashed #007bff;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  background: #f8f9fa;
}

.upload-area input {
  display: none;
}

.upload-area label {
  display: block;
  padding: 20px;
  background: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.upload-area label:hover {
  background: #0056b3;
}

/* Todo Section */
.todo-section {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.todos-container {
  max-height: 400px;
  overflow-y: auto;
}

.todo-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #eee;
  gap: 12px;
}

.todo-item input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.todo-item span.completed {
  text-decoration: line-through;
  color: #999;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 4px;
  color: white;
  font-size: 0.8em;
  margin-left: auto;
}

/* Calendar Section */
.calendar-section {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.events-container {
  max-height: 400px;
  overflow-y: auto;
}

.event-item {
  padding: 15px;
  border-left: 4px solid #28a745;
  background: #f8f9fa;
  margin-bottom: 10px;
  border-radius: 4px;
  display: flex;
  gap: 15px;
  align-items: center;
}

.event-date {
  font-weight: bold;
  color: #007bff;
  min-width: 100px;
}

.event-content h4 {
  margin: 0;
  color: #333;
}

.event-content p {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 0.9em;
}

.upcoming-badge {
  background: #ffc107;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  color: #333;
  margin-left: auto;
}

/* Chat Section */
.chat-section {
  grid-column: 1 / -1;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  background: #f8f9fa;
}

.message {
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 4px;
  background: white;
  border-left: 4px solid #007bff;
}

.message.user {
  border-left-color: #28a745;
  background: #e8f5e9;
  margin-left: 20px;
}

.message.assistant {
  border-left-color: #007bff;
  background: #e3f2fd;
  margin-right: 20px;
}

.message.loading {
  font-style: italic;
  color: #999;
}

.message .role {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
  font-size: 0.9em;
}

.message p {
  margin: 0;
}

.input-area {
  display: flex;
  gap: 10px;
}

.input-area textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}

.input-area button {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s;
}

.input-area button:hover:not(:disabled) {
  background: #0056b3;
}

.input-area button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  padding: 10px;
  background: #f8d7da;
  border-radius: 4px;
  margin-bottom: 10px;
}

.empty {
  color: #999;
  text-align: center;
  padding: 20px;
}

.welcome-message {
  color: #666;
  text-align: center;
  padding: 30px;
}

.welcome-message p {
  margin: 10px 0;
}

.timestamp {
  font-size: 0.8em;
  color: #999;
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 1024px) {
  .sections-grid {
    grid-template-columns: 1fr;
  }

  .event-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .upcoming-badge {
    margin-left: 0;
  }
}
```

---

## 🚀 Integration Checklist

- [ ] Backend is running on http://localhost:8000
- [ ] All 7 API endpoints are working
- [ ] Upload component can upload .txt files
- [ ] Todos are automatically extracted and displayed
- [ ] Dates are automatically extracted and displayed
- [ ] Chat interface works with extracted content
- [ ] Multiple files can be uploaded
- [ ] Common storage persists during session
- [ ] CSS styling is applied
- [ ] Error handling is in place
- [ ] Auto-refresh is working (5s intervals)

---

## ✅ API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload` | POST | Upload file & auto-extract todos/dates |
| `/todos` | GET | Get all todos from storage |
| `/calendar` | GET | Get all dates from storage |
| `/chat` | POST | Chat about uploaded content |
| `/files` | GET | List uploaded files |
| `/files/{name}` | DELETE | Delete a file |
| `/status` | GET | Get system status |

---

**Your frontend is now ready to integrate! All 4 sections sync with the unified backend API.** 🎉
