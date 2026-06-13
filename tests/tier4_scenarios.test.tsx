import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import App from '../src/App';
import { getNotes, saveNote, getQuizSessions, deleteNote } from '../src/utils/storage';

describe('Tier 4 Real-World Application Scenarios Test Suite', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  const answerQuizQuestion = (correctAnswer: string) => {
    const quizContainer = screen.getByTestId('quiz-view');
    const optionToClick = within(quizContainer).getByRole('button', { name: correctAnswer });
    fireEvent.click(optionToClick);
    const nextBtn = within(quizContainer).getByRole('button', { name: /next question|finish quiz/i });
    fireEvent.click(nextBtn);
  };

  it('test_full_user_study_flow: Create 3 notes, open Math note, take quiz, score 100%, set mastery to 5, view Dashboard to verify Math note is marked as mastered and overall progress metrics update', () => {
    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Create Math Note
    fireEvent.click(screen.getByRole('button', { name: /create new note/i }));
    fireEvent.change(screen.getByPlaceholderText('Enter note title...'), { target: { value: 'Math Note' } });
    fireEvent.change(screen.getByPlaceholderText('e.g. Science, Languages, History...'), { target: { value: 'Math' } });
    fireEvent.change(screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...'), { target: { value: 'algebra, equations' } });
    fireEvent.change(screen.getByPlaceholderText('Type your study notes here...'), { target: { value: 'Math equations content.' } });
    fireEvent.click(screen.getByRole('button', { name: /save note/i }));

    // Create History Note
    fireEvent.click(screen.getByRole('button', { name: /create new note/i }));
    fireEvent.change(screen.getByPlaceholderText('Enter note title...'), { target: { value: 'History Note' } });
    fireEvent.change(screen.getByPlaceholderText('e.g. Science, Languages, History...'), { target: { value: 'History' } });
    fireEvent.click(screen.getByRole('button', { name: /save note/i }));

    // Create Science Note
    fireEvent.click(screen.getByRole('button', { name: /create new note/i }));
    fireEvent.change(screen.getByPlaceholderText('Enter note title...'), { target: { value: 'Science Note' } });
    fireEvent.change(screen.getByPlaceholderText('e.g. Science, Languages, History...'), { target: { value: 'Science' } });
    fireEvent.click(screen.getByRole('button', { name: /save note/i }));

    // Start Quiz on Math Note
    const mathNoteCard = screen.getAllByText('Math Note')[0].closest('.glass-panel');
    expect(mathNoteCard).toBeInTheDocument();
    const quizBtn = within(mathNoteCard as HTMLElement).getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    // Answer Math Quiz questions
    answerQuizQuestion('Math');
    answerQuizQuestion('algebra');
    answerQuizQuestion('Yes');

    // Score 100%, set mastery to 5
    expect(screen.getByText('100%')).toBeInTheDocument();
    const masteryBtn = screen.getByTestId('mastery-btn-5');
    fireEvent.click(masteryBtn);

    // Navigate to Dashboard
    const dashboardTab = screen.getByRole('button', { name: /^dashboard$/i });
    fireEvent.click(dashboardTab);

    // Verify metrics updated
    expect(screen.getByText('Total Study Notes').parentElement).toHaveTextContent('3');
    expect(screen.getByText('Average Mastery Rating').parentElement).toHaveTextContent('5.0');
    expect(screen.getByText('Completed Assessments').parentElement).toHaveTextContent('1');

    // Verify Math note is listed in mastered section
    const masteredList = screen.getByTestId('mastered-notes-list');
    expect(within(masteredList).getByText('Math Note')).toBeInTheDocument();
  });

  it('test_revision_session_flow: Search/filter by tag "exam", open flashcards on first note, open second note, run a quiz, score 80%, check Dashboard to see revision history and progress', () => {
    // Note 1 has tag exam
    const note1 = {
      id: 'n1',
      title: 'Revision Physics',
      content: 'Physics details.',
      tags: ['exam'],
      category: 'Physics',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    // Note 2 has tag exam and 5 questions in content to score exactly 80% (4/5)
    const note2 = {
      id: 'n2',
      title: 'Revision Chemistry',
      content: 'q: Q1\na: A1\nq: Q2\na: A2\nq: Q3\na: A3\nq: Q4\na: A4\nq: Q5\na: A5',
      tags: ['exam'],
      category: 'Chemistry',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    localStorage.setItem('self_assessment_notes', JSON.stringify([note1, note2]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Filter by tag exam
    const selects = screen.getAllByRole('combobox');
    const tagSelect = selects[1];
    fireEvent.change(tagSelect, { target: { value: 'exam' } });

    // Open flashcards on first note (Revision Physics)
    const note1Card = screen.getAllByText('Revision Physics')[0].closest('.glass-panel');
    const quizBtn1 = within(note1Card as HTMLElement).getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn1);

    // Switch to flashcards mode
    const flashcardTabBtn = screen.getByTestId('mode-flashcards-button');
    fireEvent.click(flashcardTabBtn);

    // Flip card
    const cardEl = screen.getByTestId('flashcard-element');
    fireEvent.click(cardEl);
    expect(screen.getByTestId('flashcard-answer')).toBeInTheDocument();

    // Exit back to My Notes
    fireEvent.click(screen.getByRole('button', { name: /exit flashcards/i }));

    // Open second note (Revision Chemistry) and take the quiz
    const note2Card = screen.getAllByText('Revision Chemistry')[0].closest('.glass-panel');
    const quizBtn2 = within(note2Card as HTMLElement).getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn2);

    // Answer 4 correctly, 1 incorrectly
    answerQuizQuestion('A1'); // correct
    answerQuizQuestion('A2'); // correct
    answerQuizQuestion('A3'); // correct
    answerQuizQuestion('A4'); // correct
    answerQuizQuestion('Alternative A'); // incorrect

    // Score should be 80%
    expect(screen.getByText('80%')).toBeInTheDocument();

    // Go to Dashboard
    fireEvent.click(screen.getByRole('button', { name: /go to dashboard/i }));

    // Check revision history for Revision Chemistry at 80%
    const historyList = screen.getByTestId('revision-history');
    expect(within(historyList).getByText('Revision Chemistry')).toBeInTheDocument();
    expect(within(historyList).getByText('80%')).toBeInTheDocument();
    expect(within(historyList).getByText('Expert')).toBeInTheDocument(); // 80% is Expert
  });

  it('test_content_refactoring_flow: Open note, edit category to "Advanced Math", add tag "calculus", edit content, confirm auto-save triggers, search "calculus", open note, open quiz to verify questions reflect new content', async () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Refactor Note',
      content: 'Original note text.',
      tags: [],
      category: 'Math',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Click Edit
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Change fields
    const categoryInput = screen.getByPlaceholderText('e.g. Science, Languages, History...');
    const tagsInput = screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...');
    const contentInput = screen.getByPlaceholderText('Type your study notes here...');

    fireEvent.change(categoryInput, { target: { value: 'Advanced Math' } });
    fireEvent.change(tagsInput, { target: { value: 'calculus' } });
    fireEvent.change(contentInput, { target: { value: 'q: What is the derivative of x^2?\na: 2x' } });

    // Confirm auto-save triggers
    const autosaveEl = await screen.findByText('Draft autosaved', {}, { timeout: 2000 });
    expect(autosaveEl).toBeInTheDocument();

    // Click Cancel (since it is already auto-saved, cancel goes back to list)
    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));

    // Search for calculus
    const searchInput = screen.getByPlaceholderText('Search title or content...');
    fireEvent.change(searchInput, { target: { value: 'calculus' } });

    // Verify note matches
    expect(screen.getByText('Refactor Note')).toBeInTheDocument();

    // Click Start Quiz
    const startQuizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(startQuizBtn);

    // Verify quiz questions reflect the new parsed content
    expect(screen.getByText('What is the derivative of x^2?')).toBeInTheDocument();
    answerQuizQuestion('2x');

    // Verify score is 100% (only 1 question generated from parsed content)
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('test_reset_and_reassess_flow: Simulate user triggering a reset, checking dashboard returns to zero state, then creating one note, taking quiz, and verifying new progress starts', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Math Note',
      content: 'Study content details.',
      tags: [],
      category: 'Math',
      masteryRating: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));
    localStorage.setItem('self_assessment_quiz_sessions', JSON.stringify([{
      id: 's1',
      noteId: 'n1',
      score: 3,
      totalQuestions: 3,
      timestamp: new Date().toISOString()
    }]));

    render(<App />);

    // Mock confirm dialog
    vi.spyOn(window, 'confirm').mockImplementation(() => true);

    // Click Reset Data
    const resetBtn = screen.getByTestId('reset-data-btn');
    fireEvent.click(resetBtn);

    // Check dashboard metrics are back to zero
    expect(screen.getByText('Total Study Notes').parentElement).toHaveTextContent('0');
    expect(screen.getByText('Average Mastery Rating').parentElement).toHaveTextContent('0.0');
    expect(screen.getByText('Completed Assessments').parentElement).toHaveTextContent('0');

    // Create new note
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);
    fireEvent.click(screen.getByRole('button', { name: /create new note/i }));
    fireEvent.change(screen.getByPlaceholderText('Enter note title...'), { target: { value: 'Post-Reset Note' } });
    fireEvent.change(screen.getByPlaceholderText('e.g. Science, Languages, History...'), { target: { value: 'Biology' } });
    fireEvent.change(screen.getByPlaceholderText('Type your study notes here...'), { target: { value: 'Content' } });
    fireEvent.click(screen.getByRole('button', { name: /save note/i }));

    // Start Quiz
    const startQuizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(startQuizBtn);

    // Take the quiz
    answerQuizQuestion('Biology');
    answerQuizQuestion('None');
    answerQuizQuestion('Yes');

    // Score 100%, set mastery to 4
    expect(screen.getByText('100%')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('mastery-btn-4'));

    // Verify new progress on Dashboard
    fireEvent.click(screen.getByRole('button', { name: /go to dashboard/i }));
    expect(screen.getByText('Total Study Notes').parentElement).toHaveTextContent('1');
    expect(screen.getByText('Average Mastery Rating').parentElement).toHaveTextContent('4.0');
    expect(screen.getByText('Completed Assessments').parentElement).toHaveTextContent('1');
  });

  it('test_multi_note_quiz_progress_milestones: User takes quizzes on 5 different notes, scoring 0%, 25%, 50%, 75%, and 100%. Check dashboard averages match exactly 50% and history shows correct scores and badges', () => {
    // Setup 5 notes each generating 4 questions from content
    const generateNote = (id: string, title: string) => ({
      id,
      title,
      content: 'q: Q1\na: A1\nq: Q2\na: A2\nq: Q3\na: A3\nq: Q4\na: A4',
      tags: [],
      category: 'Math',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });

    localStorage.setItem('self_assessment_notes', JSON.stringify([
      generateNote('n1', 'Note A'),
      generateNote('n2', 'Note B'),
      generateNote('n3', 'Note C'),
      generateNote('n4', 'Note D'),
      generateNote('n5', 'Note E')
    ]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Helper to run quiz and submit specific correct answers
    const runQuizWithCorrectAnswersCount = (noteTitle: string, correctCount: number) => {
      const noteCard = screen.getAllByText(noteTitle)[0].closest('.glass-panel');
      const quizBtn = within(noteCard as HTMLElement).getByRole('button', { name: /start quiz/i });
      fireEvent.click(quizBtn);

      for (let i = 1; i <= 4; i++) {
        if (i <= correctCount) {
          answerQuizQuestion(`A${i}`); // Correct option
        } else {
          answerQuizQuestion('Alternative A'); // Incorrect option
        }
      }

      // Quiz finished screen, go back to My Notes
      const quizContainer = screen.getByTestId('quiz-view');
      fireEvent.click(within(quizContainer).getByRole('button', { name: /my notes/i }));
    };

    // Note A: score 0/4 (0%)
    runQuizWithCorrectAnswersCount('Note A', 0);
    // Note B: score 1/4 (25%)
    runQuizWithCorrectAnswersCount('Note B', 1);
    // Note C: score 2/4 (50%)
    runQuizWithCorrectAnswersCount('Note C', 2);
    // Note D: score 3/4 (75%)
    runQuizWithCorrectAnswersCount('Note D', 3);
    // Note E: score 4/4 (100%)
    runQuizWithCorrectAnswersCount('Note E', 4);

    // Go to Dashboard
    const dashboardTab = screen.getByRole('button', { name: /^dashboard$/i });
    fireEvent.click(dashboardTab);

    // Check Completed Assessments shows 5 completed quizzes, average score 50%
    const quizPanel = screen.getByText('Completed Assessments').parentElement;
    expect(quizPanel).toHaveTextContent('5');
    expect(quizPanel).toHaveTextContent('(50% avg)');

    // Verify history displays correct scores and badges
    const historySection = screen.getByTestId('revision-history');
    
    // Note E: 100%, Master
    expect(within(historySection).getByText('Note E')).toBeInTheDocument();
    expect(within(historySection).getAllByText('100%')[0]).toBeInTheDocument();
    expect(within(historySection).getByText('Master')).toBeInTheDocument();

    // Note D: 75%, Expert
    expect(within(historySection).getByText('Note D')).toBeInTheDocument();
    expect(within(historySection).getAllByText('75%')[0]).toBeInTheDocument();
    expect(within(historySection).getByText('Expert')).toBeInTheDocument();

    // Note C: 50%, Passing
    expect(within(historySection).getByText('Note C')).toBeInTheDocument();
    expect(within(historySection).getAllByText('50%')[0]).toBeInTheDocument();
    expect(within(historySection).getByText('Passing')).toBeInTheDocument();

    // Note B: 25%, Needs Review
    expect(within(historySection).getByText('Note B')).toBeInTheDocument();
    expect(within(historySection).getAllByText('25%')[0]).toBeInTheDocument();

    // Note A: 0%, Needs Review
    expect(within(historySection).getByText('Note A')).toBeInTheDocument();
    expect(within(historySection).getAllByText('0%')[0]).toBeInTheDocument();
    
    expect(within(historySection).getAllByText('Needs Review').length).toBe(2);
  });
});
