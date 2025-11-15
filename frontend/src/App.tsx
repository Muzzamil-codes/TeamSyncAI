import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import Header from './components/Header';
import UploadPage from './pages/UploadPage';
import TodoPage from './pages/TodoPage';
import CalendarPage from './pages/CalendarPage';
import ChatPage from './pages/ChatPage';
import { Todo, CalendarEvent, ChatMessage, UploadedFile } from './types';
import './styles/globals.css';

const API_BASE_URL = 'http://localhost:8000/api/v1/agent';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [todos, setTodos] = useState<Todo[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 1, sender: 'ai', text: 'Hello! I\'m TeamSync AI. Upload a chat file to get started.', timestamp: new Date().toISOString() }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch todos from backend
  const fetchTodos = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/todos`);
      const data = await response.json();
      const formattedTodos: Todo[] = data.todos.map((t: any, idx: number) => ({
        id: idx + 1,
        title: t.task,
        completed: false,
        priority: t.priority,
        dueDate: new Date().toISOString().split('T')[0],
        description: t.task
      }));
      setTodos(formattedTodos);
    } catch (error) {
      console.error('Error fetching todos:', error);
    }
  };

  // Fetch calendar events from backend
  const fetchCalendarEvents = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/calendar`);
      const data = await response.json();
      const formattedEvents: CalendarEvent[] = data.dates.map((d: any, idx: number) => ({
        id: idx + 1,
        title: d.event,
        date: d.date,
        time: '12:00 PM',
        description: d.description
      }));
      setEvents(formattedEvents);
    } catch (error) {
      console.error('Error fetching calendar events:', error);
    }
  };

  // Fetch uploaded files from backend
  const fetchUploadedFiles = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/files`);
      const data = await response.json();
      const formattedFiles: UploadedFile[] = data.files.map((f: any) => ({
        id: f.file_name,
        name: f.file_name,
        size: f.message_count,
        uploadedAt: f.uploaded_at
      }));
      setUploadedFiles(formattedFiles);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  // Refresh data on mount
  useEffect(() => {
    fetchUploadedFiles();
    fetchTodos();
    fetchCalendarEvents();
  }, []);

  const handleFileUpload = async (files: File[]) => {
    setIsLoading(true);
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/upload`, {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const data = await response.json();
          const newFile: UploadedFile = {
            id: data.file_name,
            name: data.file_name,
            size: data.message_count,
            uploadedAt: new Date().toISOString()
          };
          setUploadedFiles([...uploadedFiles, newFile]);
          
          // Refresh todos and calendar after upload
          setTimeout(() => {
            fetchTodos();
            fetchCalendarEvents();
          }, 1000);
        }
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleTodo = (id: number) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const handleDeleteTodo = (id: number) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  const handleDeleteFile = async (fileName: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/files/${fileName}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        // Remove from uploaded files list
        setUploadedFiles(uploadedFiles.filter(file => file.name !== fileName));
        
        // Refresh todos and calendar after deletion
        setTimeout(() => {
          fetchTodos();
          fetchCalendarEvents();
        }, 500);
      }
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  const handleSendMessage = async (text: string) => {
    setIsLoading(true);
    const userMessage: ChatMessage = {
      id: messages.length + 1,
      sender: 'user',
      text,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    // Create AI message placeholder
    const aiMessageId = messages.length + 2;
    const aiMessage: ChatMessage = {
      id: aiMessageId,
      sender: 'ai',
      text: '',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, aiMessage]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
      });

      if (response.ok && response.body) {
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.chunk) {
                  fullResponse += data.chunk;
                  // Update the AI message with streamed content
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === aiMessageId
                        ? { ...msg, text: fullResponse }
                        : msg
                    )
                  );
                }
              } catch (e) {
                console.error('Error parsing stream:', e);
              }
            }
          }
        }
      } else {
        // Fallback error message
        const errorResponse: ChatMessage = {
          id: aiMessageId,
          sender: 'ai',
          text: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString()
        };
        setMessages(prev =>
          prev.map(msg =>
            msg.id === aiMessageId ? errorResponse : msg
          )
        );
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorResponse: ChatMessage = {
        id: aiMessageId,
        sender: 'ai',
        text: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev =>
        prev.map(msg =>
          msg.id === aiMessageId ? errorResponse : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'upload' && (
          <UploadPage
            onFilesUpload={handleFileUpload}
            uploadedFiles={uploadedFiles}
            onDeleteFile={handleDeleteFile}
            isLoading={isLoading}
          />
        )}
        {activeTab === 'todos' && (
          <TodoPage
            todos={todos}
            onToggleTodo={handleToggleTodo}
            onDeleteTodo={handleDeleteTodo}
          />
        )}
        {activeTab === 'calendar' && <CalendarPage events={events} />}
        {activeTab === 'chat' && (
          <ChatPage
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        )}
      </main>
    </div>
  );
};

export default App;
