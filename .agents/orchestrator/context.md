# Project Context: Self-Assessment Portal

## Technical Design Decisions
- **Framework**: Vite + React + TypeScript
  - React provides a robust declarative UI.
  - TypeScript provides type safety for data models like Notes and QuizHistory.
  - Vite offers extremely fast compilation and static build features.
- **Styling**: Tailwind CSS
  - Premium visual interface requires custom dark-mode colors, glassmorphic layout, backdrop blurs, and hover animations, all of which are easily done with Tailwind.
- **State Management**: React Context
  - NoteContext and AssessmentContext will store active state and wrap local storage persistent calls.
- **Local Persistence**: `localStorage`
  - A clean localStorage wrapper with auto-save feature (debounced input handler).
- **Test Framework**: Vitest with JSDOM
  - High speed, Jest-compatible APIs, natively supported by Vite.
  - Used for unit and integration/E2E test simulation.

## Integrity Mode
- **Mode**: `development`
  - Forensic Auditor will enforce static and runtime checks to ensure genuine, non-fabricated code implementations and test results.

## Working Directories Directory Map
- Root: `/home/samar/self-assessment-portal`
- Agent metadata: `.agents/`
  - Orchestrator: `.agents/orchestrator/`
  - E2E Test Track: `.agents/testing_track/` (planned)
  - M1 Scaffolding: `.agents/m1_scaffolding/` (planned)
  - M2 Note-taking CRUD: `.agents/m2_crud/` (planned)
  - M3 Quiz & Flashcards: `.agents/m3_quiz/` (planned)
  - M4 Dashboard & UI: `.agents/m4_dashboard/` (planned)
  - M5 E2E Integration: `.agents/m5_e2e_integration/` (planned)
