# Project: Self-Assessment Portal

## Architecture
- Tech Stack: Vite + React + TypeScript + Tailwind CSS + Vitest
- Persistence: LocalStorage-based state/data layer
- Code Layout:
  - `src/components/`: Reusable UI components (buttons, cards, dashboard charts, layout)
  - `src/context/`: React context for global state management (NoteContext, AssessmentContext)
  - `src/utils/`: Helper utilities (storage API, quiz generator)
  - `src/types.ts`: TypeScript interfaces for Notes, Quizzes, History, Dashboard
  - `src/App.tsx` & `main.tsx`: Entry points
  - `tests/`: E2E, integration, and unit tests

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Scaffolding | Setup Vite + React + TS + Tailwind + Vitest, create base layout & Storage API | None | IN_PROGRESS (2b607ccd-5409-40b0-b298-a4de3e355102) |
| 2 | M2: Note-taking CRUD | Implement Notes CRUD, markdown viewer, categories/tags, search, auto-save | M1 | PLANNED |
| 3 | M3: Quiz & Flashcards | Implement quiz/flashcard generation, study mode, scoring, mastery setting | M2 | PLANNED |
| 4 | M4: Dashboard & UI | Metrics dashboard with charts, premium dark-mode styling, glassmorphism, animations | M3 | PLANNED |
| 5 | M5: E2E Integration | Integration of E2E test suite, bug fixing, adversarial coverage (Tier 5) | M4, E2E-Ready | PLANNED |

## Interface Contracts
### Data Models
- Note:
  ```typescript
  interface Note {
    id: string;
    title: string;
    content: string; // Markdown supported
    tags: string[];
    category: string;
    masteryRating: number; // 0-5 (0 means unrated)
    createdAt: string;
    updatedAt: string;
  }
  ```
- QuizQuestion:
  ```typescript
  interface QuizQuestion {
    id: string;
    question: string;
    answer: string;
    options: string[]; // For multiple choice
  }
  ```
- QuizSession:
  ```typescript
  interface QuizSession {
    id: string;
    noteId: string;
    score: number;
    totalQuestions: number;
    timestamp: string;
  }
  ```
