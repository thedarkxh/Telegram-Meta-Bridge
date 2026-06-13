# Scope: Milestone 1 - Project Scaffolding

## Architecture
- Tech Stack: Vite + React + TypeScript + Tailwind CSS + Vitest + JSDOM
- Local persistence helper functions in `src/utils/storage.ts`
- Basic layout and routing/views in `src/App.tsx` and related components

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1.1 | Project Scaffolding | Setup Vite + React + TS + Tailwind CSS in project | None | PLANNED |
| 1.2 | Tailwind CSS Config | Configure Tailwind with dark-mode palette & glassmorphism | 1.1 | PLANNED |
| 1.3 | Vitest Configuration | Configure Vitest with JSDOM support and add package.json scripts | 1.1 | PLANNED |
| 1.4 | Local Persistence API | Set up localStorage helpers for notes, study history/quiz sessions | 1.1 | PLANNED |
| 1.5 | Basic App Structure | Define basic App components/views (Dashboard, Notes List, Note Editor, Quiz View) and layout | 1.4 | PLANNED |
| 1.6 | Verification | Verify build (npm run build) and a basic smoke test | 1.5 | PLANNED |

## Interface Contracts
See root `PROJECT.md` for definitions of:
- `Note`
- `QuizQuestion`
- `QuizSession`
- Local persistence API signatures (to be detailed during implementation)
