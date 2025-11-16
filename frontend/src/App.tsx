import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import Header from './components/Header';
import UploadPage from './pages/UploadPage';
import TodoPage from './pages/TodoPage';
import CalendarPage from './pages/CalendarPage';
import ChatPage from './pages/ChatPage';
import { Todo, CalendarEvent, ChatMessage, UploadedFile } from './types';
import './styles/globals.css';

const API_BASE_URL = 'http://localhost:8001/api/v1/agent';

// Helper to get auth header
const getAuthHeader = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

const App: React.FC = () => {
  const navigate = useNavigate();
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
      const response = await fetch(`${API_BASE_URL}/todos`, {
        headers: getAuthHeader()
      });
      if (response.status === 401 || response.status === 403) {
        navigate('/login');
        return;
      }
      const data = await response.json();
      // Filter todos to only show today's todos
      const today = new Date().toISOString().split('T')[0];
      const todaysTodos = data.filter((t: any) => {
        const dueDate = t.due_date || new Date().toISOString().split('T')[0];
        return dueDate === today;
      });
      const formattedTodos: Todo[] = todaysTodos.map((t: any, idx: number) => ({
        id: idx + 1,
        title: t.task,
        completed: t.completed || false,
        priority: t.priority,
        dueDate: t.due_date || today,
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
      const response = await fetch(`${API_BASE_URL}/calendar`, {
        headers: getAuthHeader()
      });
      if (response.status === 401 || response.status === 403) {
        navigate('/login');
        return;
      }
      const data = await response.json();
      const formattedEvents: CalendarEvent[] = data.map((d: any, idx: number) => ({
        id: idx + 1,
        title: d.title,
        date: d.event_date,
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
      const response = await fetch(`${API_BASE_URL}/files`, {
        headers: getAuthHeader()
      });
      if (response.status === 401 || response.status === 403) {
        navigate('/login');
        return;
      }
      const data = await response.json();
      const formattedFiles: UploadedFile[] = data.map((f: any) => ({
        id: f.id,
        name: f.filename,
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
    console.log('Upload started with', files.length, 'files');
    setIsLoading(true);
    try {
      for (const file of files) {
        console.log('Processing file:', file.name, 'Size:', file.size);
        const formData = new FormData();
        formData.append('file', file);
        
        const token = localStorage.getItem('auth_token');
        console.log('Token available:', !!token);
        
        if (!token) {
          console.error('No auth token found');
          navigate('/login');
          return;
        }
        
        try {
          console.log('Sending upload request to:', `${API_BASE_URL}/upload`);
          const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: formData
          });
          
          console.log('Upload response status:', response.status);
          
          if (response.status === 401 || response.status === 403) {
            console.error('Auth error on upload');
            navigate('/login');
            return;
          }

          if (response.ok) {
            console.log('Upload successful, parsing response');
            const data = await response.json();
            console.log('Response data:', data);
            const newFile: UploadedFile = {
              id: data.file_id,
              name: data.file_name,
              size: 0,
              uploadedAt: new Date().toISOString()
            };
            setUploadedFiles([...uploadedFiles, newFile]);
            
            // Refresh todos and calendar after upload with longer delay for processing
            // Polling every 2 seconds for up to 30 seconds
            console.log('Starting polling for processed data');
            let attempts = 0;
            const pollInterval = setInterval(async () => {
              attempts++;
              console.log('Poll attempt', attempts);
              try {
                await fetchTodos();
                await fetchCalendarEvents();
              } catch (e) {
                console.error('Error polling:', e);
              }
              
              if (attempts >= 15) {
                console.log('Polling complete');
                clearInterval(pollInterval);
              }
            }, 2000);
            
          } else {
            const errorText = await response.text();
            console.error('Upload failed with status:', response.status, 'Response:', errorText);
          }
        } catch (fetchError) {
          console.error('Fetch error during upload:', fetchError);
          // Try to refresh data anyway after a delay
          setTimeout(() => {
            fetchTodos();
            fetchCalendarEvents();
          }, 3000);
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
      // Find file ID from uploadedFiles
      const file = uploadedFiles.find(f => f.name === fileName);
      if (!file) return;

      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_BASE_URL}/files/${file.id}`, {
        method: 'DELETE',
        headers: getAuthHeader()
      });

      if (response.status === 401 || response.status === 403) {
        navigate('/login');
        return;
      }

      if (response.ok) {
        // Remove from uploaded files list
        setUploadedFiles(uploadedFiles.filter(f => f.id !== file.id));
        
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
      const token = localStorage.getItem('auth_token');
      // Get the most recent uploaded file ID (if any)
      const fileId = uploadedFiles.length > 0 ? uploadedFiles[0].id : undefined;
      
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          question: text,
          file_id: fileId
        })
      });

      if (response.status === 401 || response.status === 403) {
        navigate('/login');
        return;
      }

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
