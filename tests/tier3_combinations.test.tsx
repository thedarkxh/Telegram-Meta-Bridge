import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import App from '../src/App';
import { getNotes, saveNote, getQuizSessions, deleteNote } from '../src/utils/storage';

describe('Tier 3 Cross-Feature Combinations Test Suite', () => {
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

  it('test_search_filter_then_quiz: Filter notes by a tag/category, open a matching note, take the quiz, check history', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Quantum Physics Notes',
        content: 'Introduction to quantum mechanics.',
        tags: ['quantum'],
        category: 'Physics',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Calculus Notes',
        content: 'Integration and differentiation.',
        tags: ['calculus'],
        category: 'Math',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Verify both notes render initially
    expect(screen.getByText('Quantum Physics Notes')).toBeInTheDocument();
    expect(screen.getByText('Calculus Notes')).toBeInTheDocument();

    // Filter by Category: Physics
    const selects = screen.getAllByRole('combobox');
    const categorySelect = selects[0];
    fireEvent.change(categorySelect, { target: { value: 'Physics' } });

    // Filter by Tag: quantum
    const tagSelect = selects[1];
    fireEvent.change(tagSelect, { target: { value: 'quantum' } });

    // Verify only Note 1 renders
    expect(screen.getByText('Quantum Physics Notes')).toBeInTheDocument();
    expect(screen.queryByText('Calculus Notes')).not.toBeInTheDocument();

    // Click Start Quiz on Quantum Physics Notes
    const startQuizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(startQuizBtn);

    // Take the quiz
    // Question 1: What is the main topic of the note "Quantum Physics Notes"? (Physics)
    answerQuizQuestion('Physics');
    // Question 2: Which of the following tags is associated with "Quantum Physics Notes"? (quantum)
    answerQuizQuestion('quantum');
    // Question 3: Does the content of "Quantum Physics Notes" contain details about the subject matter? (Yes)
    answerQuizQuestion('Yes');

    // Verify quiz finished percentage is 100%
    expect(screen.getByText('100%')).toBeInTheDocument();

    // Click Go to Dashboard
    const dashboardBtn = screen.getByRole('button', { name: /go to dashboard/i });
    fireEvent.click(dashboardBtn);

    // Verify completed assessments count is 1
    const quizPanel = screen.getByText('Completed Assessments').parentElement;
    expect(quizPanel).toHaveTextContent('1');
    expect(quizPanel).toHaveTextContent('(100% avg)');
  });

  it('test_edit_note_content_updates_quiz: Open note, edit its content, then run the quiz and verify questions generated match the updated note', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Original Title',
      content: 'Some original content',
      tags: ['original-tag'],
      category: 'Chemistry',
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

    // Fill new values
    const titleInput = screen.getByPlaceholderText('Enter note title...');
    const categoryInput = screen.getByPlaceholderText('e.g. Science, Languages, History...');
    const tagsInput = screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...');
    const contentInput = screen.getByPlaceholderText('Type your study notes here...');

    fireEvent.change(titleInput, { target: { value: 'Bio Note' } });
    fireEvent.change(categoryInput, { target: { value: 'Biology' } });
    fireEvent.change(tagsInput, { target: { value: 'enzymes' } });
    fireEvent.change(contentInput, { target: { value: '' } }); // empty content!

    // Click Save Note
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Verify updated note is listed
    expect(screen.getByText('Bio Note')).toBeInTheDocument();

    // Click Start Quiz
    const startQuizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(startQuizBtn);

    // Verify and answer questions based on updated values
    // Question 1: What is the main topic of the note "Bio Note"? (Biology)
    answerQuizQuestion('Biology');
    // Question 2: Which of the following tags is associated with "Bio Note"? (enzymes)
    answerQuizQuestion('enzymes');
    // Question 3: Does the content of "Bio Note" contain details about the subject matter? (No, since content is empty)
    answerQuizQuestion('No');

    // Verify perfect score
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('test_delete_note_during_quiz: Open a quiz for a note, delete the note or simulate deleting it from local storage, and verify it exit/fails gracefully', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Delete Me Note',
      content: 'Study content details.',
      tags: [],
      category: 'History',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Start Quiz
    const startQuizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(startQuizBtn);

    // Verify Quiz view active
    expect(screen.getByText('Quiz: Delete Me Note')).toBeInTheDocument();

    // Delete note from storage (simulating deletion during quiz)
    deleteNote('n1');

    // Click Exit Quiz
    const exitBtn = screen.getByRole('button', { name: /exit quiz/i });
    fireEvent.click(exitBtn);

    // Verify we navigated back to Notes List gracefully, and note is no longer listed
    expect(screen.getByText('My Study Notes')).toBeInTheDocument();
    expect(screen.queryByText('Delete Me Note')).not.toBeInTheDocument();
  });

  it('test_quiz_score_updates_mastery_prompt: Verify that completing a quiz with high score (100%) allows or prompts easily updating the mastery rating, which updates dashboard metrics', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Mastery Prompt Note',
      content: 'Study content details.',
      tags: ['test-tag'],
      category: 'Science',
      masteryRating: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Start Quiz
    const startQuizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(startQuizBtn);

    // Take the quiz correctly
    answerQuizQuestion('Science');
    answerQuizQuestion('test-tag');
    answerQuizQuestion('Yes');

    // Verify 100% score page is shown
    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByText(/perfect score/i)).toBeInTheDocument();

    // Click Mastery Button 5 on the finished screen
    const masteryBtn = screen.getByTestId('mastery-btn-5');
    fireEvent.click(masteryBtn);

    // Go to Dashboard
    const dashboardBtn = screen.getByRole('button', { name: /go to dashboard/i });
    fireEvent.click(dashboardBtn);

    // Verify Dashboard average mastery is 5.0
    const masteryPanel = screen.getByText('Average Mastery Rating').parentElement;
    expect(masteryPanel).toHaveTextContent('5.0');
  });

  it('test_create_note_with_tag_filters_immediately: Create note with a new tag, verify tag filter dropdown updates immediately, select it, verify only the new note appears', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Existing Note',
      content: 'Existing content.',
      tags: ['existing-tag'],
      category: 'History',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Click Create New Note
    const createBtn = screen.getByRole('button', { name: /create new note/i });
    fireEvent.click(createBtn);

    // Fill Form with new tag
    const titleInput = screen.getByPlaceholderText('Enter note title...');
    const tagsInput = screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...');
    fireEvent.change(titleInput, { target: { value: 'New Astro Note' } });
    fireEvent.change(tagsInput, { target: { value: 'astro' } });

    // Save
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Verify tag filter select has the new tag
    const selects = screen.getAllByRole('combobox');
    const tagSelect = selects[1];
    
    const options = Array.from(tagSelect.getElementsByTagName('option')).map(o => o.value);
    expect(options).toContain('astro');

    // Filter by new tag 'astro'
    fireEvent.change(tagSelect, { target: { value: 'astro' } });

    // Verify only new note appears
    expect(screen.getByText('New Astro Note')).toBeInTheDocument();
    expect(screen.queryByText('Existing Note')).not.toBeInTheDocument();
  });

  it('test_mastery_update_recalculates_dashboard: Change mastery ratings on multiple notes, check dashboard charts and stats recalculate correctly', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Note 1',
        content: 'Content 1',
        tags: [],
        category: 'Physics',
        masteryRating: 5,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Note 2',
        content: 'Content 2',
        tags: [],
        category: 'Math',
        masteryRating: 3,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n3',
        title: 'Note 3',
        content: 'Content 3',
        tags: [],
        category: 'History',
        masteryRating: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    // Verify initial average mastery is (5+3+1)/3 = 3.0
    let masteryPanel = screen.getByText('Average Mastery Rating').parentElement;
    expect(masteryPanel).toHaveTextContent('3.0');

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Edit Note 3 and change mastery to 4
    const editBtns = screen.getAllByRole('button', { name: /edit/i });
    // Click edit on the third note card
    fireEvent.click(editBtns[2]);

    // Click mastery button 4 in editor
    const ratingBtns = screen.getAllByRole('button').filter(btn => btn.textContent && /^[0-5]$/.test(btn.textContent));
    // Rating buttons are 0, 1, 2, 3, 4, 5. So button 4 is index 4.
    const ratingBtn4 = ratingBtns.find(btn => btn.textContent === '4');
    if (ratingBtn4) {
      fireEvent.click(ratingBtn4);
    }

    // Save note
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Go to Dashboard
    const dashboardTab = screen.getByRole('button', { name: /^dashboard$/i });
    fireEvent.click(dashboardTab);

    // Verify updated average mastery is (5+3+4)/3 = 4.0
    masteryPanel = screen.getByText('Average Mastery Rating').parentElement;
    expect(masteryPanel).toHaveTextContent('4.0');
  });
});
