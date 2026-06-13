# Milestone 1: Project Scaffolding Analysis and Design Blueprint

## 1. Executive Summary
This report provides a complete, production-grade technical blueprint for initializing and configuring the **Self-Assessment Portal** under Milestone 1 (Project Scaffolding). The project targets an offline-first Single Page Application (SPA) utilizing Vite, React, TypeScript, Tailwind CSS, and Vitest. Based on our environment check, the system is fully prepared with Node.js `v22.22.3` and npm `10.9.8` with direct access to the registry.

---

## 2. Environment Investigation
A check of the local development environment returned the following details:
- **Node.js**: `v22.22.3` (Supports latest features and stable runtime)
- **npm**: `10.9.8`
- **npx**: `10.9.8`
- **Registry**: `https://registry.npmjs.org/`
- **Connectivity**: Verified. Remote queries (e.g. `npm info`) are functional, enabling package installations directly.

---

## 3. Project Scaffolding Blueprint
To initialize the project in `/home/samar/self-assessment-portal` while preserving existing files (e.g. the `.agents/` folder and metadata), we must not let `npm create` clear the directory. 

### Step-by-Step Initialization Command
1. Create a temporary scaffolding directory:
   ```bash
   npx create-vite@latest temp-scaffold --template react-ts
   ```
2. Move the generated files into the root project directory:
   ```bash
   mv temp-scaffold/* /home/samar/self-assessment-portal/
   mv temp-scaffold/.* /home/samar/self-assessment-portal/ 2>/dev/null || true
   rm -rf temp-scaffold
   ```
3. Initialize Tailwind CSS and PostCSS configuration:
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

### Target Folder Structure
Following the project layout conventions from `PROJECT.md`, the layout will be structured as:
```text
/home/samar/self-assessment-portal/
├── .agents/                    # Agent metadata (Read-only)
├── public/                     # Static assets
├── src/
│   ├── components/             # Reusable UI components (Dashboard, NotesList, NoteEditor, QuizView)
│   ├── context/                # React context for state management (NoteContext, etc.)
│   ├── utils/                  # Helper utilities (storage.ts, quizGenerator.ts)
│   ├── types.ts                # Shared TypeScript interfaces
│   ├── App.tsx                 # Core App layout & state routing
│   ├── main.tsx                # React DOM entrypoint
│   ├── index.css               # Global Tailwind CSS and glassmorphism styling
│   └── vite-env.d.ts           # Vite TypeScript declarations
├── tests/
│   ├── setup.ts                # Vitest global testing setup
│   └── App.test.tsx            # Smoke and rendering tests
├── index.html                  # HTML entrypoint
├── package.json                # Project scripts and dependencies
├── postcss.config.js           # PostCSS configuration
├── tailwind.config.js          # Tailwind CSS customization
├── tsconfig.json               # TS compilation config
└── vite.config.ts              # Vite & Vitest configuration
```

---

## 4. Tailwind CSS Dark-Mode & Glassmorphism Design
To achieve a premium dark-mode theme, we will utilize custom background colors, translucent border overlays, and backdrop-blur gradients (glassmorphism).

### `tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable class-based dark mode switching
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#080C14',       // Deep rich dark blue-gray background
          panel: '#0F1626',    // Secondary dark for cards/panels
          border: '#1E293B',   // Border highlight
        },
        brand: {
          primary: '#7C3AED',  // Violet-600
          success: '#10B981',  // Emerald-500
          warning: '#F59E0B',  // Amber-500
          info: '#06B6D4',     // Cyan-500
        }
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-glow': '0 0 20px rgba(124, 58, 237, 0.15)',
      }
    },
  },
  plugins: [],
}
```

### `src/index.css`
Append custom utilities for premium glassmorphism classes to `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer utilities {
  /* Premium Translucent Glass Panel */
  .glass-panel {
    background: rgba(15, 22, 38, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  /* Hover state for glass cards with subtle glow */
  .glass-card {
    background: rgba(30, 41, 59, 0.3);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .glass-card:hover {
    background: rgba(30, 41, 59, 0.45);
    border-color: rgba(124, 58, 237, 0.3);
    box-shadow: 0 0 25px rgba(124, 58, 237, 0.15);
    transform: translateY(-2px);
  }

  /* Custom Scrollbar for premium feel */
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  ::-webkit-scrollbar-track {
    background: #080C14;
  }
  ::-webkit-scrollbar-thumb {
    background: #1E293B;
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: #7C3AED;
  }
}
```

---

## 5. Vitest & JSDOM Testing Suite Design
To ensure unit and integration tests render React components inside a headless environment correctly, we configure Vitest with JSDOM.

### `package.json` DevDependencies & Scripts
Add the following additions to your `package.json`:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.0.1",
    "@testing-library/user-event": "^14.5.2",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "jsdom": "^25.0.1",
    "typescript": "^5.6.3",
    "vite": "^6.0.1",
    "vitest": "^2.1.8"
  }
}
```

### `vite.config.ts`
Vite configuration modified with testing parameters:
```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    include: ['tests/**/*.{test,spec}.{ts,tsx}'],
  },
});
```

### `tests/setup.ts`
Standard test environment configuration:
```typescript
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Automatically unmount elements from the DOM after each test case
afterEach(() => {
  cleanup();
});
```

---

## 6. LocalStorage Persistence API
Create `src/types.ts` to host standard interfaces matching `PROJECT.md`:

### `src/types.ts`
```typescript
export interface Note {
  id: string;
  title: string;
  content: string; // Markdown supported
  tags: string[];
  category: string;
  masteryRating: number; // 0-5 (0 means unrated)
  createdAt: string;
  updatedAt: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  answer: string;
  options: string[]; // For multiple choice
}

export interface QuizSession {
  id: string;
  noteId: string;
  score: number;
  totalQuestions: number;
  timestamp: string;
}
```

### `src/utils/storage.ts`
Implementation of the LocalStorage data layer helper functions:
```typescript
import { Note, QuizSession } from '../types';

const NOTES_KEY = 'self_assessment_notes';
const QUIZ_SESSIONS_KEY = 'self_assessment_quiz_sessions';

/**
 * Fetch all notes stored in LocalStorage.
 */
export const getNotes = (): Note[] => {
  try {
    const data = localStorage.getItem(NOTES_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to parse notes from storage:', error);
    return [];
  }
};

/**
 * Save or update a note in storage.
 */
export const saveNote = (note: Note): void => {
  try {
    const notes = getNotes();
    const index = notes.findIndex(n => n.id === note.id);
    const timestamp = new Date().toISOString();

    if (index >= 0) {
      // Update existing note
      notes[index] = {
        ...note,
        updatedAt: timestamp,
      };
    } else {
      // Create new note
      notes.push({
        ...note,
        createdAt: note.createdAt || timestamp,
        updatedAt: timestamp,
      });
    }

    localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
  } catch (error) {
    console.error('Failed to save note to storage:', error);
  }
};

/**
 * Delete a note and its associated quiz history.
 */
export const deleteNote = (id: string): void => {
  try {
    const notes = getNotes();
    const filteredNotes = notes.filter(n => n.id !== id);
    localStorage.setItem(NOTES_KEY, JSON.stringify(filteredNotes));

    // Delete associated quiz sessions to keep storage clean
    const sessions = getQuizSessions();
    const filteredSessions = sessions.filter(s => s.noteId !== id);
    localStorage.setItem(QUIZ_SESSIONS_KEY, JSON.stringify(filteredSessions));
  } catch (error) {
    console.error('Failed to delete note from storage:', error);
  }
};

/**
 * Fetch all quiz sessions.
 */
export const getQuizSessions = (): QuizSession[] => {
  try {
    const data = localStorage.getItem(QUIZ_SESSIONS_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to parse quiz sessions from storage:', error);
    return [];
  }
};

/**
 * Record a completed quiz session.
 */
export const saveQuizSession = (session: QuizSession): void => {
  try {
    const sessions = getQuizSessions();
    sessions.push({
      ...session,
      timestamp: session.timestamp || new Date().toISOString(),
    });
    localStorage.setItem(QUIZ_SESSIONS_KEY, JSON.stringify(sessions));
  } catch (error) {
    console.error('Failed to save quiz session to storage:', error);
  }
};

/**
 * Fetch quiz sessions for a particular note.
 */
export const getQuizSessionsByNote = (noteId: string): QuizSession[] => {
  return getQuizSessions().filter(s => s.noteId === noteId);
};
```

---

## 7. Views Architecture & Routing Setup
To avoid routing setup overhead or complex sync bugs during testing, we will implement a light state-based layout router directly in `src/App.tsx`.

### Simple Router Layout
- **Views**:
  - `dashboard`: Show global charts, aggregate mastery metrics, and recent activities.
  - `notes-list`: Browse, search, filter by tag/category, and delete notes.
  - `note-editor`: Markdown note editing, tag assignment, category configuration, and mastery selection.
  - `quiz`: Run assessment interface for the selected note.

### `src/App.tsx`
```typescript
import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import NotesList from './components/NotesList';
import NoteEditor from './components/NoteEditor';
import QuizView from './components/QuizView';

export type View = 'dashboard' | 'notes-list' | 'note-editor' | 'quiz';

export default function App() {
  const [view, setView] = useState<View>('dashboard');
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);

  const navigateTo = (nextView: View, noteId: string | null = null) => {
    setView(nextView);
    setSelectedNoteId(noteId);
  };

  return (
    <div className="min-h-screen bg-[#080C14] text-slate-100 flex font-sans selection:bg-violet-500/30 selection:text-violet-200">
      {/* Premium Sidebar Navigation */}
      <aside className="w-64 border-r border-slate-800 bg-[#0F1626]/80 backdrop-blur-md p-6 flex flex-col justify-between">
        <div className="flex flex-col gap-8">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-violet-600 to-cyan-400 flex items-center justify-center font-bold text-white shadow-glass-glow">
              S
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
              Self-Assess
            </span>
          </div>

          <nav className="flex flex-col gap-2">
            <button
              onClick={() => navigateTo('dashboard')}
              className={`w-full text-left px-4 py-2.5 rounded-lg transition-all text-sm font-medium ${
                view === 'dashboard'
                  ? 'bg-violet-600/20 text-violet-400 border border-violet-500/30 shadow-glass-glow'
                  : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => navigateTo('notes-list')}
              className={`w-full text-left px-4 py-2.5 rounded-lg transition-all text-sm font-medium ${
                view === 'notes-list' || view === 'note-editor'
                  ? 'bg-violet-600/20 text-violet-400 border border-violet-500/30 shadow-glass-glow'
                  : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
              }`}
            >
              My Notes
            </button>
          </nav>
        </div>

        <div className="text-xs text-slate-500 border-t border-slate-800 pt-4">
          Status: Local Storage Sync Active
        </div>
      </aside>

      {/* View Container */}
      <main className="flex-1 p-8 overflow-y-auto max-h-screen">
        <div className="max-w-6xl mx-auto">
          {view === 'dashboard' && <Dashboard onNavigate={navigateTo} />}
          {view === 'notes-list' && <NotesList onNavigate={navigateTo} />}
          {view === 'note-editor' && <NoteEditor noteId={selectedNoteId} onNavigate={navigateTo} />}
          {view === 'quiz' && <QuizView noteId={selectedNoteId} onNavigate={navigateTo} />}
        </div>
      </main>
    </div>
  );
}
```

---

## 8. Smoke Testing Verification
A Vitest + JSDOM smoke test configuration to verify UI elements mounting.

### `tests/App.test.tsx`
```typescript
import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../src/App';

// Mock child view components to isolate the App shell smoke test
vi.mock('../src/components/Dashboard', () => ({
  default: () => <div data-testid="dashboard-view">Dashboard Mock Content</div>
}));
vi.mock('../src/components/NotesList', () => ({
  default: () => <div data-testid="notes-list-view">Notes List Mock Content</div>
}));
vi.mock('../src/components/NoteEditor', () => ({
  default: () => <div data-testid="note-editor-view">Note Editor Mock Content</div>
}));
vi.mock('../src/components/QuizView', () => ({
  default: () => <div data-testid="quiz-view">Quiz Mock Content</div>
}));

describe('App Scaffolding & Routing Smoke Test', () => {
  it('renders side navigation bar successfully', () => {
    render(<App />);

    // Verify App Brand and Navigation buttons exist in Document
    expect(screen.getByText('Self-Assess')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /my notes/i })).toBeInTheDocument();
  });

  it('renders Dashboard as default active view', () => {
    render(<App />);

    // Check if default view mounts successfully
    expect(screen.getByTestId('dashboard-view')).toBeInTheDocument();
    expect(screen.queryByTestId('notes-list-view')).not.toBeInTheDocument();
  });
});
```
