// src/utils/storage.ts
import { v4 as uuidv4 } from 'uuid';
import type { Note, QuizSession } from '../types';

/* -------------------- NOTE CRUD -------------------- */
const NOTES_KEY = 'sa-portal:notes';

export function getNotes(): Note[] {
  const raw = localStorage.getItem(NOTES_KEY);
  return raw ? JSON.parse(raw) : [];
}

/** Save a new or updated note. */
export function saveNote(note: Partial<Note>): Note {
  const notes = getNotes();
  const now = new Date().toISOString();

  // Update existing?
  const existing = notes.find(n => n.id === note.id);
  if (existing) {
    const updated: Note = {
      ...existing,
      ...note,
      updatedAt: now,
    };
    localStorage.setItem(
      NOTES_KEY,
      JSON.stringify(notes.map(n => (n.id === note.id ? updated : n)))
    );
    return updated;
  }

  // Create new
  const newNote: Note = {
    id: uuidv4(),
    title: note.title ?? 'Untitled',
    content: note.content ?? '',
    tags: note.tags ?? [],
    category: note.category ?? '',
    masteryRating: note.masteryRating ?? 0,
    createdAt: now,
    updatedAt: now,
  };
  notes.push(newNote);
  localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
  return newNote;
}

/** Delete a note by its id. */
export function deleteNote(id: string): void {
  const notes = getNotes().filter(n => n.id !== id);
  localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
}

/* -------------------- QUIZ SESSION -------------------- */
const QUIZ_KEY = 'sa-portal:quizzes';

export function getQuizSessions(): QuizSession[] {
  const raw = localStorage.getItem(QUIZ_KEY);
  return raw ? JSON.parse(raw) : [];
}

/** Record a completed quiz session. */
export function saveQuizSession(
  session: Omit<QuizSession, 'id' | 'timestamp'>
): QuizSession {
  const sessions = getQuizSessions();
  const newSession: QuizSession = {
    id: uuidv4(),
    timestamp: new Date().toISOString(),
    ...session,
  };
  sessions.push(newSession);
  localStorage.setItem(QUIZ_KEY, JSON.stringify(sessions));
  return newSession;
}
