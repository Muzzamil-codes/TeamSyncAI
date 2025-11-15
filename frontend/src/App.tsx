import React, { useState } from 'react';
import Navigation from './components/Navigation';
import Header from './components/Header';
import UploadPage from './pages/UploadPage';
import TodoPage from './pages/TodoPage';
import CalendarPage from './pages/CalendarPage';
import ChatPage from './pages/ChatPage';
import { Todo, CalendarEvent, ChatMessage, UploadedFile } from './types';
import './styles/globals.css';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [todos, setTodos] = useState<Todo[]>([
    {
      id: 1,
      title: 'Review Q4 marketing proposal',
      completed: false,
      priority: 'high',
      dueDate: '2025-11-20',
      description: 'Review and provide feedback on the Q4 marketing proposal'
    },
    {
      id: 2,
      title: 'Prepare slides for client meeting',
      completed: false,
      priority: 'medium',
      dueDate: '2025-11-18'
    },
    {
      id: 3,
      title: 'Update project documentation',
      completed: true,
      priority: 'low',
      dueDate: '2025-11-16'
    }
  ]);

  const [events, setEvents] = useState<CalendarEvent[]>([
    { id: 1, title: 'Team Standup', date: '2025-11-15', time: '09:00 AM', description: 'Daily team sync' },
    { id: 2, title: 'Client Presentation', date: '2025-11-18', time: '02:00 PM', description: 'Q4 project presentation' },
    { id: 3, title: 'Sprint Planning', date: '2025-11-20', time: '10:00 AM', description: 'Plan next sprint' }
  ]);

  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 1, sender: 'ai', text: 'Hello! I\'m TeamSync AI. I can help you organize your tasks, analyze your meetings, and answer questions about your uploaded documents. What can I help you with today?', timestamp: new Date().toISOString() }
  ]);

  const handleFileUpload = (files: UploadedFile[]) => {
    setUploadedFiles([...uploadedFiles, ...files]);
  };

  const handleToggleTodo = (id: number) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const handleDeleteTodo = (id: number) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  const handleSendMessage = (text: string) => {
    const userMessage: ChatMessage = {
      id: messages.length + 1,
      sender: 'user',
      text,
      timestamp: new Date().toISOString()
    };

    setMessages([...messages, userMessage]);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: messages.length + 2,
        sender: 'ai',
        text: 'I\'ve received your message. This is a prototype response. In production, this would be powered by the Gemini AI backend with RAG capabilities.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-black-custom-900">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'upload' && (
          <UploadPage
            onFilesUpload={handleFileUpload}
            uploadedFiles={uploadedFiles}
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
          />
        )}
      </main>
    </div>
  );
};

export default App;
