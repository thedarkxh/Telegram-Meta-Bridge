import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import App from '../src/App';

describe('Tier 1 Feature Coverage Test Suite', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  // ==========================================
  // 1. Note CRUD (5 tests)
  // ==========================================

  it('test_create_note: Create a new note and check it appears in the sidebar list', () => {
    render(<App />);

    // Navigate to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Click Create New Note
    const createBtn = screen.getByRole('button', { name: /create new note/i });
    fireEvent.click(createBtn);

    // Fill the editor form
    const titleInput = screen.getByPlaceholderText('Enter note title...');
    const contentInput = screen.getByPlaceholderText('Type your study notes here...');
    fireEvent.change(titleInput, { target: { value: 'CRUD Note 1' } });
    fireEvent.change(contentInput, { target: { value: 'CRUD content 1 description' } });

    // Click Save Note
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Verify it appears in the Notes List view
    expect(screen.getByText('CRUD Note 1')).toBeInTheDocument();
    expect(screen.getByText('CRUD content 1 description')).toBeInTheDocument();
  });

  it('test_read_note: Click a note in the sidebar and verify its title and content are displayed in the view/editor', () => {
    // Pre-populate localStorage with a note
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'note-crud-read',
      title: 'CRUD Read Note',
      content: 'Read note content details',
      tags: [],
      category: '',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Click Edit on the note card to view/edit it
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Verify values display in Editor
    const titleInput = screen.getByPlaceholderText('Enter note title...');
    const contentInput = screen.getByPlaceholderText('Type your study notes here...');
    expect(titleInput).toHaveValue('CRUD Read Note');
    expect(contentInput).toHaveValue('Read note content details');
  });

  it("test_update_note_title: Edit a note's title and verify the updated title shows", () => {
    // Pre-populate note
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'note-update-title',
      title: 'Original Title',
      content: 'Original content description',
      tags: [],
      category: '',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Edit note
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Change title
    const titleInput = screen.getByPlaceholderText('Enter note title...');
    fireEvent.change(titleInput, { target: { value: 'Updated Title' } });

    // Save
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Verify updated title shows in Notes List, and original title is gone
    expect(screen.getByText('Updated Title')).toBeInTheDocument();
    expect(screen.queryByText('Original Title')).not.toBeInTheDocument();
  });

  it("test_update_note_content: Edit a note's content and verify the updated content is rendered", () => {
    // Pre-populate note
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'note-update-content',
      title: 'Constant Title',
      content: 'Original content description',
      tags: [],
      category: '',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Edit note
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Change content
    const contentInput = screen.getByPlaceholderText('Type your study notes here...');
    fireEvent.change(contentInput, { target: { value: 'Updated content description' } });

    // Save
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Verify updated content shows in Notes List
    expect(screen.getByText('Updated content description')).toBeInTheDocument();
  });

  it('test_delete_note: Delete a note and verify it is removed from the sidebar list', () => {
    // Pre-populate note
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'note-delete',
      title: 'Delete Me Note',
      content: 'Content that will be deleted',
      tags: [],
      category: '',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Confirm deletion alert/confirm mock
    const confirmSpy = vi.spyOn(window, 'confirm').mockImplementation(() => true);

    // Delete note
    const deleteBtn = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteBtn);

    // Verify it is removed
    expect(screen.queryByText('Delete Me Note')).not.toBeInTheDocument();
    expect(screen.getByText('No notes found matching your criteria.')).toBeInTheDocument();

    confirmSpy.mockRestore();
  });

  // ==========================================
  // 2. Tag & Category Management (7 tests)
  // ==========================================

  it("test_add_tag: Add tags (e.g. 'chemistry', 'exam') during note creation/editing", () => {
    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Create note
    const createBtn = screen.getByRole('button', { name: /create new note/i });
    fireEvent.click(createBtn);

    const titleInput = screen.getByPlaceholderText('Enter note title...');
    const tagsInput = screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...');
    fireEvent.change(titleInput, { target: { value: 'Chemistry Note' } });
    fireEvent.change(tagsInput, { target: { value: 'chemistry, exam' } });

    // Save
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Click Edit on the created note
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Verify tags display in editor input field
    const tagsInputAfter = screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...');
    expect(tagsInputAfter).toHaveValue('chemistry, exam');
  });

  it('test_remove_tag: Remove a tag from a note', () => {
    // Pre-populate note with tags
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'note-tags',
      title: 'Tags Note',
      content: 'Content',
      tags: ['chemistry', 'exam'],
      category: '',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Edit note
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Change tags to remove 'exam'
    const tagsInput = screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...');
    fireEvent.change(tagsInput, { target: { value: 'chemistry' } });

    // Save
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Verify tags inside list card and tags input
    expect(screen.getByText('#chemistry')).toBeInTheDocument();
    expect(screen.queryByText('#exam')).not.toBeInTheDocument();
  });

  it('test_list_all_tags: Verify all tags appear in the filter dropdown', () => {
    // Pre-populate multiple notes with tags
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Note A',
        content: 'Content',
        tags: ['chemistry'],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Note B',
        content: 'Content',
        tags: ['exam'],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    // Go to My Notes
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Find the tag combobox
    const selects = screen.getAllByRole('combobox');
    const tagSelect = selects[1]; // second combobox is Tag

    // Verify tag options exist
    const options = Array.from(tagSelect.getElementsByTagName('option')).map(o => o.value);
    expect(options).toContain('All');
    expect(options).toContain('chemistry');
    expect(options).toContain('exam');
  });

  it('test_note_tags_render: Verify tag badges are rendered on the note card', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Render Note',
      content: 'Content',
      tags: ['mitosis', 'biology'],
      category: '',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Verify tags are rendered with # prefix
    expect(screen.getByText('#mitosis')).toBeInTheDocument();
    expect(screen.getByText('#biology')).toBeInTheDocument();
  });

  it("test_set_category: Assign a category (e.g. 'Science') to a note", () => {
    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Create note
    const createBtn = screen.getByRole('button', { name: /create new note/i });
    fireEvent.click(createBtn);

    const titleInput = screen.getByPlaceholderText('Enter note title...');
    const categoryInput = screen.getByPlaceholderText('e.g. Science, Languages, History...');
    fireEvent.change(titleInput, { target: { value: 'Bio Note' } });
    fireEvent.change(categoryInput, { target: { value: 'Science' } });

    // Save
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Click Edit on the note card
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Verify category displays in editor input field
    const categoryInputAfter = screen.getByPlaceholderText('e.g. Science, Languages, History...');
    expect(categoryInputAfter).toHaveValue('Science');
  });

  it('test_list_all_categories: Verify categories appear in the filter dropdown', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Note A',
        content: 'Content',
        tags: [],
        category: 'Science',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Note B',
        content: 'Content',
        tags: [],
        category: 'Art',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Find the category combobox (first combobox)
    const selects = screen.getAllByRole('combobox');
    const categorySelect = selects[0];

    const options = Array.from(categorySelect.getElementsByTagName('option')).map(o => o.value);
    expect(options).toContain('All');
    expect(options).toContain('Science');
    expect(options).toContain('Art');
  });

  it('test_note_category_render: Verify category badge is rendered on the note card', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Render Note',
      content: 'Content',
      tags: [],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Verify category badge renders
    expect(screen.getAllByText('Science').length).toBeGreaterThanOrEqual(1);
  });

  // ==========================================
  // 3. Search & Filter (6 tests)
  // ==========================================

  it('test_search_by_title: Type in search input and filter by title matching', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Organic Chemistry',
        content: 'Different content info',
        tags: [],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Classical Physics',
        content: 'Different content info',
        tags: [],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Search for chemistry
    const searchInput = screen.getByPlaceholderText('Search title or content...');
    fireEvent.change(searchInput, { target: { value: 'Chemistry' } });

    expect(screen.getByText('Organic Chemistry')).toBeInTheDocument();
    expect(screen.queryByText('Classical Physics')).not.toBeInTheDocument();
  });

  it('test_search_by_content: Type in search input and filter by content matching', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Note A',
        content: 'Einstein was a brilliant theoretical physicist.',
        tags: [],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Note B',
        content: 'Newton studied gravity and classical mechanics.',
        tags: [],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Search for Einstein
    const searchInput = screen.getByPlaceholderText('Search title or content...');
    fireEvent.change(searchInput, { target: { value: 'Einstein' } });

    expect(screen.getByText('Note A')).toBeInTheDocument();
    expect(screen.queryByText('Note B')).not.toBeInTheDocument();
  });

  it('test_case_insensitive_search: Search query matches case-insensitively', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'World War Two History',
        content: 'Information',
        tags: [],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const searchInput = screen.getByPlaceholderText('Search title or content...');
    fireEvent.change(searchInput, { target: { value: 'world war two' } });

    expect(screen.getByText('World War Two History')).toBeInTheDocument();
  });

  it('test_filter_by_tag: Select a tag filter and verify only matching notes are listed', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Note A',
        content: 'Content',
        tags: ['mitosis'],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Note B',
        content: 'Content',
        tags: ['gravity'],
        category: '',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const selects = screen.getAllByRole('combobox');
    const tagSelect = selects[1];
    fireEvent.change(tagSelect, { target: { value: 'mitosis' } });

    expect(screen.getByText('Note A')).toBeInTheDocument();
    expect(screen.queryByText('Note B')).not.toBeInTheDocument();
  });

  it('test_filter_by_category: Select a category filter and verify only matching notes are listed', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Note A',
        content: 'Content',
        tags: [],
        category: 'Biology',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Note B',
        content: 'Content',
        tags: [],
        category: 'Physics',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const selects = screen.getAllByRole('combobox');
    const categorySelect = selects[0];
    fireEvent.change(categorySelect, { target: { value: 'Biology' } });

    expect(screen.getByText('Note A')).toBeInTheDocument();
    expect(screen.queryByText('Note B')).not.toBeInTheDocument();
  });

  it('test_combined_search_and_filter: Apply search query and category/tag filter together', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Cell Biology Mito',
        content: 'Mitochondria are energy powerhouses.',
        tags: ['mitosis'],
        category: 'Biology',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Cell Chemistry Atom',
        content: 'Atoms bond to form chemical compounds.',
        tags: ['mitosis'],
        category: 'Chemistry',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n3',
        title: 'Plant Biology Mito',
        content: 'Photosynthesis occurs in chloroplasts.',
        tags: ['mitosis'],
        category: 'Biology',
        masteryRating: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Apply Search
    const searchInput = screen.getByPlaceholderText('Search title or content...');
    fireEvent.change(searchInput, { target: { value: 'Cell' } });

    // Apply Category
    const selects = screen.getAllByRole('combobox');
    const categorySelect = selects[0];
    fireEvent.change(categorySelect, { target: { value: 'Biology' } });

    // Apply Tag
    const tagSelect = selects[1];
    fireEvent.change(tagSelect, { target: { value: 'mitosis' } });

    // Verify results
    expect(screen.getByText('Cell Biology Mito')).toBeInTheDocument();
    expect(screen.queryByText('Cell Chemistry Atom')).not.toBeInTheDocument();
    expect(screen.queryByText('Plant Biology Mito')).not.toBeInTheDocument();
  });

  // ==========================================
  // 4. Quiz & Flashcards (8 tests)
  // ==========================================

  it('test_generate_flashcards: Check that flashcards option or view renders for a note', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Flashcard Study Note',
      content: 'Detailed description text here',
      tags: ['chemistry'],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Start Quiz
    const quizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    // Switch to Flashcards
    const flashcardsTab = screen.getByTestId('mode-flashcards-button');
    fireEvent.click(flashcardsTab);

    // Verify Flashcard View is rendered
    expect(screen.getByTestId('flashcard-view')).toBeInTheDocument();
    expect(screen.getByText('Flashcards: Flashcard Study Note')).toBeInTheDocument();
  });

  it('test_flip_flashcard: Click a flashcard and verify it flips to show the answer (if cards are flipped or answer shown)', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Flashcard Study Note',
      content: 'Detailed description text here',
      tags: ['chemistry'],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const quizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    const flashcardsTab = screen.getByTestId('mode-flashcards-button');
    fireEvent.click(flashcardsTab);

    // Verify answer is not visible initially
    expect(screen.queryByTestId('flashcard-answer')).not.toBeInTheDocument();

    // Click the card element to flip
    const flashcardEl = screen.getByTestId('flashcard-element');
    fireEvent.click(flashcardEl);

    // Verify answer is displayed
    expect(screen.getByTestId('flashcard-answer')).toBeInTheDocument();
    expect(screen.getByTestId('flashcard-answer')).toHaveTextContent('Science');
  });

  it('test_navigate_flashcards: Navigate between cards', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Flashcard Study Note',
      content: 'Detailed description text here',
      tags: ['chemistry'],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const quizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    const flashcardsTab = screen.getByTestId('mode-flashcards-button');
    fireEvent.click(flashcardsTab);

    // Card 1 showing
    expect(screen.getByText('Card 1 of 3')).toBeInTheDocument();

    // Navigate to Card 2
    const nextBtn = screen.getByTestId('next-flashcard-button');
    fireEvent.click(nextBtn);
    expect(screen.getByText('Card 2 of 3')).toBeInTheDocument();

    // Navigate back to Card 1
    const prevBtn = screen.getByTestId('prev-flashcard-button');
    fireEvent.click(prevBtn);
    expect(screen.getByText('Card 1 of 3')).toBeInTheDocument();
  });

  it('test_generate_quiz: Open a quiz for a note and verify multiple choice options render', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Quiz Study Note',
      content: 'Detailed description text here',
      tags: ['chemistry'],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const quizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    // Verify Quiz view renders
    expect(screen.getByTestId('quiz-view')).toBeInTheDocument();
    
    // Verify randomized choice options are present as buttons (e.g. Science option)
    expect(screen.getByRole('button', { name: 'Science' })).toBeInTheDocument();
  });

  it('test_submit_quiz_correct_answer: Select a correct option and check it registers correctly', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Quiz Study Note',
      content: 'Detailed description text here',
      tags: ['chemistry'],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const quizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    // Click the correct answer option
    const correctBtn = screen.getByRole('button', { name: 'Science' });
    fireEvent.click(correctBtn);

    // Verify it displays feedback registration "Correct!"
    expect(screen.getByTestId('quiz-feedback')).toBeInTheDocument();
    expect(screen.getByText('Correct!')).toBeInTheDocument();
  });

  it('test_submit_quiz_incorrect_answer: Select an incorrect option and check feedback', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Quiz Study Note',
      content: 'Detailed description text here',
      tags: ['chemistry'],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const quizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    // Click an incorrect answer option
    const incorrectBtn = screen.getByRole('button', { name: 'Unrelated Subject A' });
    fireEvent.click(incorrectBtn);

    // Verify it displays feedback with correction
    expect(screen.getByTestId('quiz-feedback')).toBeInTheDocument();
    expect(screen.getByText('Incorrect. The correct answer is: Science')).toBeInTheDocument();
  });

  it('test_complete_quiz_score: Complete all questions in a quiz and verify score percentage renders', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Quiz Study Note',
      content: 'Detailed description text here',
      tags: ['chemistry'],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const quizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    // Question 1: Science
    fireEvent.click(screen.getByRole('button', { name: 'Science' }));
    fireEvent.click(screen.getByRole('button', { name: /next question/i }));

    // Question 2: chemistry
    fireEvent.click(screen.getByRole('button', { name: 'chemistry' }));
    fireEvent.click(screen.getByRole('button', { name: /next question/i }));

    // Question 3: Yes
    fireEvent.click(screen.getByRole('button', { name: 'Yes' }));
    fireEvent.click(screen.getByRole('button', { name: /finish quiz/i }));

    // Verify Quiz Finished and score percentage renders (100%)
    expect(screen.getByText('Quiz Finished!')).toBeInTheDocument();
    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByText('3 / 3 Correct Answers')).toBeInTheDocument();
  });

  it('test_quiz_history_recorded: Verify that completed quiz session adds to total quiz sessions in history', () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Quiz Study Note',
      content: 'Detailed description text here',
      tags: ['chemistry'],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const quizBtn = screen.getByRole('button', { name: /start quiz/i });
    fireEvent.click(quizBtn);

    // Question 1: Science
    fireEvent.click(screen.getByRole('button', { name: 'Science' }));
    fireEvent.click(screen.getByRole('button', { name: /next question/i }));

    // Question 2: chemistry
    fireEvent.click(screen.getByRole('button', { name: 'chemistry' }));
    fireEvent.click(screen.getByRole('button', { name: /next question/i }));

    // Question 3: Yes
    fireEvent.click(screen.getByRole('button', { name: 'Yes' }));
    fireEvent.click(screen.getByRole('button', { name: /finish quiz/i }));

    // Verify history in localStorage has 1 session
    const sessions = JSON.parse(localStorage.getItem('self_assessment_quiz_sessions') || '[]');
    expect(sessions.length).toBe(1);
    expect(sessions[0].score).toBe(3);
    expect(sessions[0].totalQuestions).toBe(3);
  });

  // ==========================================
  // 5. Mastery & Dashboard (4 tests)
  // ==========================================

  it('test_set_mastery_rating: Click mastery rating button (0-5) in editor', () => {
    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Create note
    const createBtn = screen.getByRole('button', { name: /create new note/i });
    fireEvent.click(createBtn);

    const titleInput = screen.getByPlaceholderText('Enter note title...');
    fireEvent.change(titleInput, { target: { value: 'Mastery Note' } });

    // Click rating 4
    const ratingBtn = screen.getByRole('button', { name: '4' });
    fireEvent.click(ratingBtn);

    // Save
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Edit note and verify rating
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    const activeRatingBtn = screen.getByRole('button', { name: '4' });
    expect(activeRatingBtn.className).toContain('mastery-bg-4');
  });

  it("test_update_mastery_rating: Edit and change note's mastery rating", () => {
    localStorage.setItem('self_assessment_notes', JSON.stringify([{
      id: 'n1',
      title: 'Update Rating Note',
      content: 'Content',
      tags: [],
      category: '',
      masteryRating: 2,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }]));

    render(<App />);

    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    // Edit note
    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Change rating to 5
    const ratingBtn5 = screen.getByRole('button', { name: '5' });
    fireEvent.click(ratingBtn5);

    // Save
    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Edit again to verify it persisted
    const editBtnAgain = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtnAgain);

    const activeRatingBtn5 = screen.getByRole('button', { name: '5' });
    expect(activeRatingBtn5.className).toContain('mastery-bg-5');

    const inactiveRatingBtn2 = screen.getByRole('button', { name: '2' });
    expect(inactiveRatingBtn2.className).not.toContain('mastery-bg-2');
  });

  it('test_dashboard_metrics_render: Navigate to dashboard and check total notes, average mastery, and total quizzes stats are shown', () => {
    // Populate notes and sessions
    localStorage.setItem('self_assessment_notes', JSON.stringify([
      {
        id: 'n1',
        title: 'Note A',
        content: 'Content',
        tags: [],
        category: '',
        masteryRating: 4,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'n2',
        title: 'Note B',
        content: 'Content',
        tags: [],
        category: '',
        masteryRating: 2,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]));

    localStorage.setItem('self_assessment_quiz_sessions', JSON.stringify([{
      id: 's1',
      noteId: 'n1',
      score: 2,
      totalQuestions: 3,
      timestamp: new Date().toISOString()
    }]));

    render(<App />);

    // Dashboard is default view. Verify metrics.
    expect(screen.getByText('Dashboard Overview')).toBeInTheDocument();
    
    // Verify metrics by checking containing panels
    const notesPanel = screen.getByText('Total Study Notes').parentElement;
    expect(notesPanel).toHaveTextContent('2');

    const masteryPanel = screen.getByText('Average Mastery Rating').parentElement;
    expect(masteryPanel).toHaveTextContent('3.0');

    const quizPanel = screen.getByText('Completed Assessments').parentElement;
    expect(quizPanel).toHaveTextContent('1');
    expect(quizPanel).toHaveTextContent('(67% avg)');
  });

  it('test_local_persistence_reload: Store a note, simulate page reload (remount <App />), and verify the note is still loaded from localStorage', () => {
    const { unmount } = render(<App />);

    // Navigate to My Notes & Create a note
    const notesTab = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTab);

    const createBtn = screen.getByRole('button', { name: /create new note/i });
    fireEvent.click(createBtn);

    const titleInput = screen.getByPlaceholderText('Enter note title...');
    fireEvent.change(titleInput, { target: { value: 'Persistent Reload Note' } });

    const saveBtn = screen.getByRole('button', { name: /save note/i });
    fireEvent.click(saveBtn);

    // Unmount (simulate page close/reload)
    unmount();

    // Remount <App />
    render(<App />);

    // Go to My Notes
    const notesTabReload = screen.getByRole('button', { name: /^my notes$/i });
    fireEvent.click(notesTabReload);

    // Check it is still loaded
    expect(screen.getByText('Persistent Reload Note')).toBeInTheDocument();
  });
});
