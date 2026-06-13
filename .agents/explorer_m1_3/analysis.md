# Milestone 1 Blueprint & Environment Analysis: Self-Assessment Portal

## Executive Summary
This report details the scaffolding blueprint for Milestone 1 (Project Scaffolding) of the Self-Assessment Portal. Following a thorough investigation of the workspace and system environment, we have designed a robust scaffolding procedure, a Tailwind CSS v4 premium dark-mode theme, a JSDOM-powered Vitest testing structure, data persistence layers, view routing, and an automated smoke test suite optimized to function under the system's current offline package constraints.

---

## Environment Analysis

### 1. Toolchain Availability
System commands show that the modern Node.js and NPM toolchain is installed and fully functional:
* **Node.js**: `v22.22.3`
* **NPM**: `10.9.8`
* **NPX**: `10.9.8`

### 2. Dependency Cache Analysis
The environment is operating in a sandboxed, offline environment (`CODE_ONLY` network mode). An npm install test revealed the following cache states:
* **Pre-cached and Fully Offline Installable**:
  * Core React stack: `react` (19.2.7), `react-dom` (19.2.7), `typescript` (6.0.3), `vite` (8.0.16), `@types/react` (19.2.17), `@types/react-dom` (19.2.3), `@vitejs/plugin-react` (6.0.2).
  * Tailwind CSS Stack: `tailwindcss` (4.3.0), `postcss` (8.5.15), `autoprefixer` (10.5.0).
* **Missing from Cache (Resolving Offline Fails with `ENOTCACHED`)**:
  * Vitest & JSDOM: `vitest`, `jsdom`.
  * Tailwind Vite Integration: `@tailwindcss/vite` (requires `@tailwindcss/oxide-wasm32-wasi` which is uncached).
  * Testing Libraries: `@testing-library/react`, `@testing-library/jest-dom`.

### 3. Mitigation Strategies for Scaffolding
* **Scaffolding Tailwind CSS v4**: Rather than using the Vite plugin `@tailwindcss/vite` (which lacks cached offline WASM binaries), use the **PostCSS integration for Tailwind CSS v4**, which is fully cached and offline-installable.
* **Vitest / JSDOM Offline Installation**: The blueprint defines all package configurations. However, because `vitest` and `jsdom` are not in the local npm cache, they must either be installed when network connectivity is restored, mapped to a local package path, or run in an environment that has pre-installed Vitest.
* **Testing Library Fallback**: In the event that `@testing-library/jest-dom` is unavailable offline, the test blueprint utilizes **standard DOM assertions** (`not.toBeNull()`, `.textContent`) that execute directly on standard elements returned by `@testing-library/react` and JSDOM, eliminating the hard dependency on custom matchers.

---

## 1. Project Scaffolding Blueprint

### A. Non-Destructive Scaffolding Command Sequence
Because the repository root already contains `.agents/` and `PROJECT.md`, running `npx create-vite .` directly with `--overwrite` would wipe out the project metadata. The implementer should execute this non-destructive setup:

```bash
# 1. Create Vite project in a temporary subdirectory
npx create-vite temp-project --template react-ts --no-interactive

# 2. Copy the scaffolded files to the root directory without overwriting metadata
cp -rn temp-project/* .
cp -rn temp-project/.* . 2>/dev/null || true

# 3. Clean up the temporary project folder
rm -rf temp-project
```

### B. Scaffold Configuration Files

#### `postcss.config.js`
Enable Tailwind CSS v4 compilation via PostCSS since the PostCSS plugins are fully cached:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

#### `vite.config.ts`
Vite configuration incorporating Vitest and JSDOM test settings:
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

---

## 2. Premium Dark-Mode Tailwind CSS Configuration
Tailwind CSS v4 is configured CSS-first inside `src/index.css` using the `@theme` and `@utility` directives.

```css
@import "tailwindcss";

@theme {
  /* Premium Dark Mode Colors */
  --color-slate-900: #0f172a;
  --color-slate-950: #020617;
  
  --color-brand-dark: #09090b;
  --color-brand-card: rgba(18, 18, 24, 0.65);
  --color-brand-border: rgba(255, 255, 255, 0.08);
  --color-brand-glow: rgba(139, 92, 246, 0.15);
  
  /* Mastery Status Colors (0-5 Rating scale) */
  --color-mastery-0: #6b7280; /* Gray (Unrated) */
  --color-mastery-1: #ef4444; /* Red (Beginning) */
  --color-mastery-2: #f97316; /* Orange (Developing) */
  --color-mastery-3: #f59e0b; /* Yellow (Approaching) */
  --color-mastery-4: #3b82f6; /* Blue (Proficient) */
  --color-mastery-5: #10b981; /* Emerald (Mastered) */

  --backdrop-blur-glass: 12px;
}

/* Custom Glassmorphism Utility Classes */
@utility glass-card {
  background-color: var(--color-brand-card);
  backdrop-filter: blur(var(--backdrop-blur-glass));
  -webkit-backdrop-filter: blur(var(--backdrop-blur-glass));
  border: 1px solid var(--color-brand-border);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@utility glass-card-hover {
  &:hover {
    border-color: rgba(139, 92, 246, 0.3);
    box-shadow: 0 8px 32px 0 rgba(139, 92, 246, 0.15), 0 0 1px 1px rgba(139, 92, 246, 0.25);
    transform: translateY(-2px);
  }
}

@utility text-glow-indigo {
  text-shadow: 0 0 8px rgba(99, 102, 241, 0.5);
}

@utility glow-ring {
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.25);
}
```

---

## 3. Vitest & JSDOM Scaffolding

### A. devDependencies and scripts (`package.json`)
The following configuration should be merged into `package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:run": "vitest run"
  },
  "devDependencies": {
    "vitest": "^3.0.0",
    "jsdom": "^26.0.0",
    "@types/node": "^24.12.3",
    "@testing-library/react": "^16.2.0",
    "@testing-library/jest-dom": "^6.6.3"
  }
}
```

### B. Environment Setup (`tests/setup.ts`)
Creates a setup file that configures React element cleaning after each test:
```typescript
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Optional import: if @testing-library/jest-dom is successfully installed, uncomment:
// import '@testing-library/jest-dom';

afterEach(() => {
  cleanup();
});
```

---

## 4. LocalStorage Persistence API Blueprint
Create the storage utilities under `src/utils/storage.ts`. To make functions robust and testable in JSDOM/Node without hard mocking, an in-memory fallback store is integrated directly.

```typescript
import { Note, QuizSession } from '../types';

// In-memory fallback for environments without a native localStorage (e.g. basic Node tests)
class InMemoryStorage implements Storage {
  private store: Record<string, string> = {};

  get length(): number {
    return Object.keys(this.store).length;
  }

  clear(): void {
    this.store = {};
  }

  getItem(key: string): string | null {
    return this.store[key] || null;
  }

  key(index: number): string | null {
    return Object.keys(this.store)[index] || null;
  }

  removeItem(key: string): void {
    delete this.store[key];
  }

  setItem(key: string, value: string): void {
    this.store[key] = value;
  }
}

const fallbackStorage = new InMemoryStorage();

const getStorage = (): Storage => {
  if (typeof window !== 'undefined' && window.localStorage) {
    return window.localStorage;
  }
  return fallbackStorage;
};

// Storage Keys
const NOTES_KEY = 'sap_notes';
const QUIZ_SESSIONS_KEY = 'sap_quiz_sessions';

/**
 * Notes Storage API
 */
export const getNotes = (): Note[] => {
  try {
    const storage = getStorage();
    const data = storage.getItem(NOTES_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load notes from localStorage:', error);
    return [];
  }
};

export const saveNote = (note: Note): void => {
  try {
    const storage = getStorage();
    const notes = getNotes();
    const existingIndex = notes.findIndex(n => n.id === note.id);
    
    if (existingIndex > -1) {
      notes[existingIndex] = { ...note, updatedAt: new Date().toISOString() };
    } else {
      notes.push(note);
    }
    
    storage.setItem(NOTES_KEY, JSON.stringify(notes));
  } catch (error) {
    console.error('Failed to save note to localStorage:', error);
  }
};

export const deleteNote = (id: string): void => {
  try {
    const storage = getStorage();
    const notes = getNotes();
    const updatedNotes = notes.filter(n => n.id !== id);
    storage.setItem(NOTES_KEY, JSON.stringify(updatedNotes));
  } catch (error) {
    console.error('Failed to delete note from localStorage:', error);
  }
};

export const getNoteById = (id: string): Note | undefined => {
  return getNotes().find(n => n.id === id);
};

/**
 * Quiz Sessions Storage API
 */
export const getQuizSessions = (): QuizSession[] => {
  try {
    const storage = getStorage();
    const data = storage.getItem(QUIZ_SESSIONS_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load quiz sessions from localStorage:', error);
    return [];
  }
};

export const saveQuizSession = (session: QuizSession): void => {
  try {
    const storage = getStorage();
    const sessions = getQuizSessions();
    sessions.push(session);
    storage.setItem(QUIZ_SESSIONS_KEY, JSON.stringify(sessions));
  } catch (error) {
    console.error('Failed to save quiz session to localStorage:', error);
  }
};

export const getQuizSessionsForNote = (noteId: string): QuizSession[] => {
  return getQuizSessions().filter(s => s.noteId === noteId);
};
```

---

## 5. View Structure and Routing Blueprint
To minimize bundle complexity and avoid issues with routing library offline cached states, a state-based view switching approach is designed for `src/App.tsx`.

### A. Project Views Directory Structure
```
src/
├── types.ts                # TypeScript Interfaces
├── main.tsx                # App Entry point
├── App.tsx                 # Core App layout + State Switcher
├── components/
│   ├── Dashboard.tsx       # Overall metrics, distribution charts, study history
│   ├── NotesList.tsx       # CRUD notes list, search input, tag/category filters
│   ├── NoteEditor.tsx      # Markdown text-editor, categories, tags, mastery rating (0-5)
│   └── QuizView.tsx        # Interactive quiz interface, answers, instant scores, and feedback
└── utils/
    └── storage.ts          # LocalStorage API
```

### B. Routing Switcher (`src/App.tsx`)
```typescript
import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import NotesList from './components/NotesList';
import NoteEditor from './components/NoteEditor';
import QuizView from './components/QuizView';

export type View = 'dashboard' | 'notes-list' | 'note-editor' | 'quiz';

export default function App() {
  const [view, setView] = useState<View>('dashboard');
  const [activeNoteId, setActiveNoteId] = useState<string | null>(null);

  const navigateTo = (newView: View, noteId: string | null = null) => {
    setView(newView);
    setActiveNoteId(noteId);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-violet-500 selection:text-white">
      {/* Navigation Header */}
      <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-slate-950/60 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => navigateTo('dashboard')}>
            <span className="text-xl font-bold bg-gradient-to-r from-violet-400 via-fuchsia-400 to-indigo-400 bg-clip-text text-transparent text-glow-indigo">
              Self-Assessment Portal
            </span>
          </div>
          <nav className="flex space-x-2">
            <button
              id="nav-dashboard"
              onClick={() => navigateTo('dashboard')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${
                view === 'dashboard'
                  ? 'bg-violet-600/20 text-violet-400 border border-violet-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`}
            >
              Dashboard
            </button>
            <button
              id="nav-notes"
              onClick={() => navigateTo('notes-list')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${
                view === 'notes-list' || view === 'note-editor'
                  ? 'bg-violet-600/20 text-violet-400 border border-violet-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`}
            >
              Notes
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area with Route switcher */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {view === 'dashboard' && (
          <Dashboard navigateTo={navigateTo} />
        )}
        {view === 'notes-list' && (
          <NotesList navigateTo={navigateTo} />
        )}
        {view === 'note-editor' && (
          <NoteEditor noteId={activeNoteId} navigateTo={navigateTo} />
        )}
        {view === 'quiz' && activeNoteId && (
          <QuizView noteId={activeNoteId} navigateTo={navigateTo} />
        )}
      </main>
    </div>
  );
}
```

---

## 6. Basic Smoke Test Blueprint
The smoke test is placed in `tests/App.test.tsx` to verify component rendering and view navigation. To avoid test execution crashes in offline settings where `@testing-library/jest-dom` may fail to load, standard element checking assertions (`not.toBeNull()`, `textContent`) are used.

```typescript
import React from 'react';
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../src/App';

describe('Self-Assessment Portal Render Smoke Tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders the header application title successfully', () => {
    render(<App />);
    
    const brandElement = screen.getByText('Self-Assessment Portal');
    expect(brandElement).not.toBeNull();
    expect(brandElement.textContent).toContain('Self-Assessment Portal');
  });

  it('renders the Dashboard view components by default', () => {
    render(<App />);
    
    // The Dashboard component should render a metrics summary or heading
    const dashboardTab = screen.getByRole('button', { name: /Dashboard/i });
    expect(dashboardTab).not.toBeNull();
    
    // Verify Dashboard tab active visual style is applied
    expect(dashboardTab.className).toContain('text-violet-400');
  });

  it('navigates successfully to Notes List view when clicked', () => {
    render(<App />);
    
    const notesTab = screen.getByRole('button', { name: /Notes/i });
    expect(notesTab).not.toBeNull();
    
    // Simulate navigation click
    fireEvent.click(notesTab);
    
    // Notes tab should become active
    expect(notesTab.className).toContain('text-violet-400');
  });
});
```
