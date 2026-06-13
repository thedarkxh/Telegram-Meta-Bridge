# Original User Request

## Initial Request — 2026-06-13T22:39:38+05:30

A production-ready self-assessment portal structured as a GitHub repository subfolder, containing full note-taking features (creating, editing, organizing notes) along with self-assessment capabilities.

Working directory: /home/samar/self-assessment-portal
Integrity mode: development

## Requirements

### R1. Note-taking Engine
The portal must support standard note-taking capabilities, including creating, reading, updating, and deleting (CRUD) notes, rich-text or markdown editing, organizing notes by category/tags, searching, and auto-saving.

### R2. Self-Assessment Module
Users must be able to conduct self-assessments on their notes:
- Generate interactive quizzes or flashcards based on note content.
- Set a confidence score/mastery status (e.g., Red/Yellow/Green or 1-5 scale) for each note.
- View a progress dashboard showing overall learning metrics, mastery distribution, and study history.

### R3. Premium Visual Interface
A visually stunning, responsive user interface with rich aesthetics:
- Dark-mode optimized palette (sleek dark colors, smooth gradients, glassmorphism).
- Modern typography.
- Smooth transitions and micro-animations for interactive elements (hover effects, card flips, loading states).

### R4. Local Data Persistence
All notes, tags, quiz history, and confidence scores must be persistently saved (e.g., in the browser's `localStorage` or `IndexedDB`) so data is retained across browser sessions and page reloads.

### R5. Static Build and Testing
The project must be buildable as a static frontend application (e.g., suitable for GitHub Pages deployment). It must include a robust automated test suite (using Vitest, Jest, or Cypress/Playwright) verifying the note CRUD operations and quiz logic.

## Acceptance Criteria

### Note-taking & UI
- [ ] Notes can be created, edited, categorized, and deleted with instant UI updates.
- [ ] User can search notes by title/content and filter by tags/categories.
- [ ] Notes and state persist across page reloads.
- [ ] Page features a premium dark-mode theme, custom fonts, glassmorphic card styles, and hover animations.

### Self-Assessment & Quizzes
- [ ] An interactive quiz or flashcard interface can be opened for any note.
- [ ] Quizzes score user answers and display results with feedback.
- [ ] User can manually set and update a mastery rating for each note, which updates the dashboard metrics.
- [ ] Dashboard displays at least two charts or visual metrics (e.g. total notes mastered, quiz completion rate).

### Technical & Testing
- [ ] Build command (e.g. `npm run build` or equivalent) compiles the project successfully without errors.
- [ ] Automated tests cover at least 3 core functionalities (CRUD, search, quiz scoring) and pass successfully.
