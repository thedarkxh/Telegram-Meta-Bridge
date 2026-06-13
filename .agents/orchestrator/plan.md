# Project Plan: Self-Assessment Portal

## Overview
This document outlines the execution plan for building the static web-based Self-Assessment Portal. We will use a Dual-Track Project Pattern with an **Implementation Track** (M1 to M5) and an **E2E Testing Track** running in parallel.

## Milestones and Dependencies

```
+-----------------------------------+
|  E2E Testing Track (Parallel)    |
|  - Setup Vitest/JSDOM tests       |
|  - Implement Tier 1-4 Test Cases |
|  - Publish TEST_READY.md          |
+-----------------------------------+
                  |
                  v
+-----------------------------------------------------------+
|  M1: Scaffolding (Vite + React + TS + Tailwind + Vitest)  |
+-----------------------------------------------------------+
                  |
                  v
+-----------------------------------------------------------+
|  M2: Note-taking CRUD (Notes editor, tags, search)        |
+-----------------------------------------------------------+
                  |
                  v
+-----------------------------------------------------------+
|  M3: Quiz & Flashcards (Study mode, scoring, mastery)     |
+-----------------------------------------------------------+
                  |
                  v
+-----------------------------------------------------------+
|  M4: Dashboard & UI (Charts, premium glassmorphism theme) |
+-----------------------------------------------------------+
                  |
                  v
+-----------------------------------------------------------+
|  M5: E2E Integration & Adversarial Hardening              |
|  - Run and pass E2E tests                                 |
|  - Challenger-led Tier 5 hardening                        |
+-----------------------------------------------------------+
```

## Track Details

### 1. Implementation Track
We will spawn subagents for each milestone sequentially:
- **M1 (Scaffolding)**: Setup directories, package.json, webpack/vite configs, tailwind setup, basic Router, and local storage base module.
- **M2 (CRUD)**: Notes view, edit form (markdown format), deletion, tag/category management, dynamic search/filter, and auto-save (debounce mechanism).
- **M3 (Quiz & Flashcards)**: Quiz engine to generate questions from markdown notes (e.g. parsing `# Q:` headers or flashcard notations, or simple fill-in-the-blanks). A view for active quiz taking, card flip interactive micro-interactions, scoring mechanism, and mastery rating update modal/slider.
- **M4 (Dashboard)**: A learning metrics dashboard. Interactive charts (using Tailwind/SVG elements or lightweight canvas/SVG charting) showing mastery distribution, number of notes per category, study session logs, and history charts.
- **M5 (E2E Integration & Hardening)**: Integrate test runners, fix edge cases identified by E2E testing, and run adversarial review to ensure total test coverage.

### 2. E2E Testing Track
We will spawn a testing orchestrator to run parallel E2E test developments:
- Define requirements-driven test cases (Tiers 1-4).
- Tier 1: Feature coverage (CRUD operations, note search/filter, taking a quiz, scoring, updating mastery rating).
- Tier 2: Boundary conditions (empty titles, massive content, extremely large study history, empty tag lists, zero/max quiz score).
- Tier 3: Pairwise combinations (filtering notes then taking a quiz, deleting notes active in quiz).
- Tier 4: Real-world workflow (user logs in, imports notes, takes quizzes on multiple notes, verifies dashboard updates correctly).
- Publish `TEST_READY.md` containing the E2E test commands and structure.

## Execution Strategy
- We will spawn an **E2E Testing Track sub-orchestrator** first.
- In parallel, we will spawn subagents for the **Implementation Track milestones** (starting with M1).
- We will use `self` subagents to act as track/milestone orchestrators or workers.
- Each milestone will follow the cycle: Explorer(s) analyze -> Worker implements -> Reviewer(s) verify -> Challenger/Auditor checks -> Gate.
- Liveness will be checked via `progress.md` updates every 10 minutes.
- Integrity verification will be enforced in every iteration by a Forensic Auditor in 'development' mode.
