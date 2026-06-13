# Scope: E2E Testing Track

## Architecture
- Framework: Vitest + JSDOM
- Helpers: `@testing-library/react`, `@testing-library/user-event`
- Target: `/home/samar/self-assessment-portal`
- Code Layout:
  - All E2E and integration tests will be located under `src/tests/` or a dedicated `tests/` directory as scaffolded by the project.
  - Test files will be grouped by tier:
    - `tests/tier1_features.test.tsx` (>= 30 tests covering Note CRUD, Tag Management, Search/Filter, Quiz Generation, Scoring, Mastery)
    - `tests/tier2_boundaries.test.tsx` (>= 30 tests covering empty/extreme inputs, quiz score limits, empty storage)
    - `tests/tier3_combinations.test.tsx` (>= 6 tests covering cross-feature interactions like search-then-quiz, delete active quiz note)
    - `tests/tier4_scenarios.test.tsx` (>= 5 tests covering complete user workflow/study flows)

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|-------------|--------|
| 1 | M1: E2E Test Infra Setup | Configure Vitest, JSDOM, package.json test scripts, and test helpers in the repository | None (Coordinating with Implementation M1) | DONE |
| 2 | M2: Tier 1 Feature Coverage | Implement >= 30 test cases for core CRUD, tags, search/filter, quiz, scoring, mastery ratings | M1 | IN_PROGRESS (58a7ec29-eeb9-4c3e-8c82-bb6773d095ff) |
| 3 | M3: Tier 2 Boundaries & Corners | Implement >= 30 test cases for edge cases, extreme inputs, and limits | M2 | IN_PROGRESS (e5bfacb1-a770-4876-ba73-5a8c1a4327d6) |
| 4 | M4: Tier 3 Cross-feature Combinations | Implement >= 6 test cases for cross-feature interaction scenarios | M3 | IN_PROGRESS (d76e20e2-dc28-4dde-8923-905b90c24e4f) |
| 5 | M5: Tier 4 Real-world Scenarios | Implement >= 5 test cases for full user workflows / study sessions | M4 | IN_PROGRESS (d76e20e2-dc28-4dde-8923-905b90c24e4f) |
| 6 | M6: Test Integration & TEST_READY | Run the entire suite, verify clean run, publish TEST_READY.md at project root | M5 | PLANNED |

## Interface Contracts
The tests will interact with the application by mounting the main `<App />` component in JSDOM, or by interacting with the DOM elements rendered by it, as defined in `PROJECT.md`.
Key DOM query attributes/selectors:
- Note management: UI buttons for creating, saving, editing notes, categories, tags.
- Search/filter: Search input, tag dropdowns, category filters.
- Quiz interface: Flashcard flippers, answer options, submit buttons, next buttons, score display.
- Dashboard: Mastery sliders/ratings, charts/stats containers.
