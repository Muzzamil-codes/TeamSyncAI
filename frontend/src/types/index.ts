// Types for TeamSync application
export interface Todo {
  id: number;
  title: string;
  completed: boolean;
  priority: 'high' | 'medium' | 'low';
  dueDate: string;
  description?: string;
}

export interface CalendarEvent {
  id: number;
  title: string;
  date: string;
  time: string;
  description?: string;
}

export interface ChatMessage {
  id: number;
  sender: 'user' | 'ai';
  text: string;
  timestamp?: string;
}

export interface UploadedFile {
  id: string;
  name: string;
  type: 'whatsapp' | 'transcript' | 'other';
  uploadedAt: string;
  size: number;
}

export interface AIResponse {
  todos?: Todo[];
  events?: CalendarEvent[];
  insights?: string;
}
