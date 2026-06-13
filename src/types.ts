/**
 * Core data contracts for the Self‑Assessment Portal.
 * No implementation details – pure shape definitions.
 */

export interface Note {
  id: string;                     // UUID
  title: string;
  content: string;                // Markdown
  tags: string[];                 // Optional tags
  category: string;               // Optional category
  masteryRating: number;          // 0‑5 (0 = unrated)
  createdAt: string;              // ISO timestamp
  updatedAt: string;              // ISO timestamp
}

/** Simple quiz question extracted from a note. */
export interface QuizQuestion {
  id: string;
  question: string;               // Prompt
  answer: string;                 // Correct answer
  options?: string[];             // Multiple‑choice options (optional)
}

/** One quiz session linked to a note. */
export interface QuizSession {
  id: string;
  noteId: string;
  score: number;                  // 0‑100%
  totalQuestions: number;
  timestamp: string;              // ISO timestamp
}
