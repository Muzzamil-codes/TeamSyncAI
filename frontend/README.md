# TeamSync Frontend

A modern React frontend for TeamSync, powered by Vite, TypeScript, and Tailwind CSS. The application features a minimal black theme and is built to work with the FARM Stack backend.

## Features

- **Upload Management** - Upload WhatsApp chats, Google Meet transcriptions, and other documents
- **Task Management** - AI-generated tasks with priority levels and due dates
- **Event Calendar** - Visual calendar displaying important meetings and deadlines
- **AI Chat** - Chat interface powered by Gemini AI with RAG capabilities
- **Minimal Black Theme** - Clean, modern UI with dark aesthetic

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Lightning-fast build tool
- **Lucide React** - Beautiful SVG icons

## Getting Started

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Preview

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Header.tsx       # Main header
│   │   └── Navigation.tsx   # Tab navigation
│   ├── pages/               # Page components
│   │   ├── UploadPage.tsx   # File upload interface
│   │   ├── TodoPage.tsx     # Task list and management
│   │   ├── CalendarPage.tsx # Event calendar
│   │   └── ChatPage.tsx     # AI chatbot interface
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── styles/              # Global styles
│   │   └── globals.css
│   ├── App.tsx              # Main app component
│   └── main.tsx             # Entry point
├── public/
│   └── index.html           # HTML template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Color Scheme (Minimal Black)

- **Primary Background**: `#0a0a0a`
- **Secondary Background**: `#1a1a1a`
- **Tertiary Background**: `#2d2d2d`
- **Text Primary**: `#ffffff`
- **Text Secondary**: `#b0b0b0`
- **Accent**: `#3b82f6` (Blue)

## API Integration

The frontend is configured to proxy API requests to `http://localhost:8000/api` during development. Update the `vite.config.ts` to change the backend URL.

## Component Overview

### Navigation
- Tab-based navigation for all main sections
- Active tab highlighting with blue accent

### Upload Page
- Drag-and-drop file upload
- File type detection (WhatsApp, transcripts, etc.)
- Upload history with file metadata

### Todo Page
- Task display with priority badges
- Filter by status (all/active/completed)
- Filter by priority (all/high/medium/low)
- Quick task toggle and deletion

### Calendar Page
- Monthly calendar view
- Event indicators on calendar dates
- Upcoming events sidebar
- Navigate between months

### Chat Page
- Message history with sender identification
- User and AI message differentiation
- Auto-scroll to latest message
- Keyboard shortcuts (Enter to send, Shift+Enter for newline)

## Development Notes

- The app uses React 18 with TypeScript for type safety
- Tailwind CSS is configured with custom color palette for the minimal black theme
- Icons are sourced from lucide-react for consistency
- The layout is responsive and works on desktop, tablet, and mobile

## Next Steps

1. Connect to backend API endpoints
2. Implement file upload functionality
3. Integrate Gemini AI for task generation
4. Implement RAG for chat context
5. Add user authentication
6. Deploy to production

---

Built with ❤️ for productivity
