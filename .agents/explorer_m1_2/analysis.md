# Analysis Report: Project Scaffolding (Milestone 1)

## Summary of Core Findings
The local environment is fully prepared for offline/local scaffolding with Node `v22.22.3`, npm `10.9.8`, and pre-cached `create-vite` packages. A complete Blueprint has been designed to initialize Vite + React + TypeScript + Tailwind CSS and configure Vitest with JSDOM for robust component testing and local persistence.

---

## Environment Investigation Results

| Metric | Value / Status | Verification Command | Notes |
|---|---|---|---|
| **Node.js Version** | `v22.22.3` | `node -v` | Fully supported for modern Vite configurations. |
| **npm Version** | `10.9.8` | `npm -v` | Active lockfile v3 compatibility. |
| **npx Version** | `10.9.8` | `npx -v` | Offline package resolution ready. |
| **Offline Cache Status**| Functional | `npm install --dry-run --prefer-offline lucide-react` | Command successfully completed dry run, proving packages resolve locally. |
| **Pre-cached Templates**| Available | `find_by_name` on `~/.npm/_npx` | Found pre-cached versions of `create-vite` in npx directory. |

---

## 1. Project Initialization Blueprint

To scaffold the project in `/home/samar/self-assessment-portal/` (which contains existing `.agents/` and metadata files):

1. **Scaffold Vite Core Project**
   Run the standard command in the root folder. Since the directory is non-empty, select the **"Ignore files and continue"** option when prompted by the CLI.
   ```bash
   npx create-vite@latest . --template react-ts
   ```

2. **Install Core Dependencies**
   Install the necessary UI icons library:
   ```bash
   npm install lucide-react
   ```

3. **Install Development Dependencies**
   Install the styling and testing ecosystem:
   ```bash
   npm install -D tailwindcss postcss autoprefixer vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @types/node @tailwindcss/typography
   ```

4. **Initialize Tailwind Configuration**
   Generate `tailwind.config.js` and `postcss.config.js` in the root:
   ```bash
   npx tailwindcss init -p
   ```

5. **Establish Directory Hierarchy**
   Align the project directory structure with `PROJECT.md`:
   ```bash
   mkdir -p src/components src/context src/utils tests
   ```

---

## 2. Premium Dark-Mode & Glassmorphism Styling

The portal visual identity uses a premium glassmorphic dark-mode palette.

### 2.1 Tailwind CSS Configuration (`tailwind.config.js`)
Use the ESM format matching Vite's `"type": "module"` in `package.json`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // support class-based dark mode (default premium dark mode)
  theme: {
    extend: {
      colors: {
        darkBg: '#090d16',
        darkCard: 'rgba(17, 24, 39, 0.65)',
        darkBorder: 'rgba(255, 255, 255, 0.08)',
        accentPrimary: '#6366f1',   // Indigo
        accentSecondary: '#a855f7', // Purple
        success: '#10b981',         // Emerald (mastery)
        warning: '#f59e0b',         // Amber (average progress)
        danger: '#ef4444',          // Red
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-inset': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.05)',
      },
    },
  },
  plugins: [
    // Typography plugin for styling parsed markdown content
    require('@tailwindcss/typography'),
  ],
}
```

### 2.2 Global Utilities (`src/index.css`)
Define standard classes for premium glassmorphism:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-[#090d16] text-slate-100 font-sans antialiased min-h-screen selection:bg-indigo-500/30;
  }
}

@layer utilities {
  .glass-panel {
    background: rgba(17, 24, 39, 0.65);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 0 1px 1px 0 rgba(255, 255, 255, 0.05);
  }
  
  .glass-input {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    @apply transition-all duration-200 focus:outline-none focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/25 text-slate-100 placeholder-slate-500 rounded-lg px-4 py-2;
  }

  .glass-button-primary {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(168, 85, 247, 0.8) 100%);
    @apply text-white font-medium px-4 py-2 rounded-lg transition-all duration-200 hover:brightness-110 active:scale-95 shadow-md shadow-indigo-500/10 hover:shadow-indigo-500/20 border border-white/10;
  }

  .glass-button-secondary {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    @apply text-slate-200 font-medium px-4 py-2 rounded-lg transition-all duration-200 hover:bg-white/5 active:scale-95;
  }

  .glass-card-interactive {
    @apply glass-panel transition-all duration-300 hover:-translate-y-1 hover:border-indigo-500/30 hover:shadow-indigo-500/5 cursor-pointer;
  }
}
```

---

## 3. Vitest & JSDOM Testing Setup

### 3.1 Vite Test Configuration (`vite.config.ts`)
Modify the default `vite.config.ts` to integrate Vitest config:

```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    css: true,
  },
});
```

### 3.2 Testing Setup Script (`src/setupTests.ts`)
Inject the custom Jest DOM matcher suite:

```typescript
import '@testing-library/jest-dom';
```

### 3.3 TypeScript Configuration Adjustments
Add the `vitest/globals` to type definitions inside `tsconfig.app.json` or `tsconfig.json`:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

### 3.4 Scripts in `package.json`
Add testing tasks to run tests interactively or in headless environment:

```json
"scripts": {
  "dev": "vite",
  "build": "tsc -b && vite build",
  "lint": "eslint .",
  "preview": "vite preview",
  "test": "vitest",
  "test:run": "vitest run",
  "test:coverage": "vitest run --coverage"
}
```

---

## 4. LocalStorage Data Persistence Layer

Implement TypeScript type definitions and a robust local storage persistence service.

### 4.1 Interface Contracts (`src/types.ts`)
Extracted from `PROJECT.md` contracts:

```typescript
export interface Note {
  id: string;
  title: string;
  content: string; // Markdown supported
  tags: string[];
  category: string;
  masteryRating: number; // 0-5 (0 = unrated)
  createdAt: string;
  updatedAt: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  answer: string;
  options: string[]; // For multiple choice options
}

export interface QuizSession {
  id: string;
  noteId: string;
  score: number;
  totalQuestions: number;
  timestamp: string;
}
```

### 4.2 Storage Service Layer (`src/utils/storage.ts`)
A secure utility with safety fallbacks to handle parse/write exceptions:

```typescript
import { Note, QuizSession } from '../types';

const NOTES_KEY = 'sp_notes';
const SESSIONS_KEY = 'sp_quiz_sessions';

/**
 * Safely parses data from localStorage.
 */
const safeParse = <T>(key: string, defaultValue: T): T => {
  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : defaultValue;
  } catch (error) {
    console.error(`Error parsing localStorage key "${key}":`, error);
    return defaultValue;
  }
};

/**
 * Safely writes data to localStorage.
 */
const safeWrite = (key: string, value: any): void => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Error writing to localStorage key "${key}":`, error);
  }
};

/**
 * Notes CRUD Persistence
 */
export const getNotes = (): Note[] => {
  return safeParse<Note[]>(NOTES_KEY, []);
};

export const saveNotes = (notes: Note[]): void => {
  safeWrite(NOTES_KEY, notes);
};

export const saveNote = (note: Note): void => {
  const notes = getNotes();
  const index = notes.findIndex(n => n.id === note.id);
  const now = new Date().toISOString();
  
  if (index >= 0) {
    notes[index] = { 
      ...note, 
      updatedAt: now 
    };
  } else {
    notes.push({
      ...note,
      createdAt: note.createdAt || now,
      updatedAt: now
    });
  }
  saveNotes(notes);
};

export const deleteNote = (id: string): void => {
  const notes = getNotes();
  const filtered = notes.filter(n => n.id !== id);
  saveNotes(filtered);
};

/**
 * Quiz Session History Persistence
 */
export const getQuizSessions = (): QuizSession[] => {
  return safeParse<QuizSession[]>(SESSIONS_KEY, []);
};

export const saveQuizSession = (session: QuizSession): void => {
  const sessions = getQuizSessions();
  sessions.push({
    ...session,
    timestamp: session.timestamp || new Date().toISOString()
  });
  safeWrite(SESSIONS_KEY, sessions);
};

export const getQuizSessionsByNote = (noteId: string): QuizSession[] => {
  return getQuizSessions().filter(s => s.noteId === noteId);
};
```

---

## 5. App Layout & State-based Routing

Rather than using complex external routers which add unnecessary testing surface, a lightweight state-based view switcher handles view toggling seamlessly.

### 5.1 Main App Shell (`src/App.tsx`)
```tsx
import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import NotesList from './components/NotesList';
import NoteEditor from './components/NoteEditor';
import QuizView from './components/QuizView';

export type ViewType = 'dashboard' | 'notes' | 'editor' | 'quiz';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);

  const handleEditNote = (noteId: string) => {
    setSelectedNoteId(noteId);
    setCurrentView('editor');
  };

  const handleCreateNote = () => {
    setSelectedNoteId(null);
    setCurrentView('editor');
  };

  const handleStartQuiz = (noteId: string) => {
    setSelectedNoteId(noteId);
    setCurrentView('quiz');
  };

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-64 glass-panel border-r border-slate-800 p-6 flex flex-col gap-6">
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Self-Assessment Portal
          </h1>
          <p className="text-xs text-slate-500 mt-1">Milestone 1 Dev Scaffolding</p>
        </div>
        
        <nav className="flex flex-col gap-2">
          <button 
            onClick={() => setCurrentView('dashboard')}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all ${
              currentView === 'dashboard' 
                ? 'bg-indigo-600/30 border border-indigo-500/50 text-indigo-200' 
                : 'hover:bg-white/5 text-slate-400'
            }`}
          >
            <span>Dashboard</span>
          </button>
          <button 
            onClick={() => setCurrentView('notes')}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all ${
              currentView === 'notes' || currentView === 'editor'
                ? 'bg-indigo-600/30 border border-indigo-500/50 text-indigo-200' 
                : 'hover:bg-white/5 text-slate-400'
            }`}
          >
            <span>My Notes</span>
          </button>
        </nav>
      </aside>

      {/* Main Viewport */}
      <main className="flex-1 p-8 overflow-y-auto">
        {currentView === 'dashboard' && (
          <Dashboard 
            onCreateNote={handleCreateNote}
            onEditNote={handleEditNote}
            onStartQuiz={handleStartQuiz}
          />
        )}
        {currentView === 'notes' && (
          <NotesList 
            onEditNote={handleEditNote}
            onStartQuiz={handleStartQuiz}
            onCreateNote={handleCreateNote}
          />
        )}
        {currentView === 'editor' && (
          <NoteEditor 
            noteId={selectedNoteId} 
            onClose={() => setCurrentView('notes')} 
          />
        )}
        {currentView === 'quiz' && (
          <QuizView 
            noteId={selectedNoteId!} 
            onClose={() => setCurrentView('dashboard')} 
          />
        )}
      </main>
    </div>
  );
};

export default App;
```

---

## 6. Rendering Smoke Test

### 6.1 App Smoke Test (`tests/App.test.tsx`)
Verify basic DOM rendering, default fallback view routing, and local storage safety inside the JSDOM sandbox.

```tsx
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import App from '../src/App';

// Mock components to isolate router smoke test from implementation details
vi.mock('../src/components/Dashboard', () => ({
  default: ({ onCreateNote }: any) => (
    <div data-testid="dashboard-view">
      <h2>Dashboard Panel</h2>
      <button onClick={onCreateNote}>Create Note</button>
    </div>
  )
}));
vi.mock('../src/components/NotesList', () => ({
  default: () => <div data-testid="notes-list-view">Notes List Panel</div>
}));
vi.mock('../src/components/NoteEditor', () => ({
  default: () => <div data-testid="note-editor-view">Note Editor Panel</div>
}));
vi.mock('../src/components/QuizView', () => ({
  default: () => <div data-testid="quiz-view">Quiz View Panel</div>
}));

describe('App Scaffolding & Smoke Test Suite', () => {
  beforeEach(() => {
    // In-memory Mock LocalStorage setup
    const localStorageMock = (() => {
      let store: Record<string, string> = {};
      return {
        getItem: (key: string) => store[key] || null,
        setItem: (key: string, value: string) => {
          store[key] = value.toString();
        },
        clear: () => {
          store = {};
        },
        removeItem: (key: string) => {
          delete store[key];
        }
      };
    })();

    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true
    });
  });

  it('renders application sidebar and default dashboard view on mount', () => {
    render(<App />);
    
    // Verify application brand displays in sidebar
    expect(screen.getByText('Self-Assessment Portal')).toBeInTheDocument();
    
    // Verify default view matches dashboard
    expect(screen.getByTestId('dashboard-view')).toBeInTheDocument();
    expect(screen.getByText('Dashboard Panel')).toBeInTheDocument();
  });
});
```
