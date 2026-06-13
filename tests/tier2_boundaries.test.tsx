import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import App from '../src/App';
import { getNotes, saveNote, getQuizSessions, saveQuizSession } from '../src/utils/storage';

describe('Tier 2 Boundary & Corner Cases Test Suite', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.spyOn(window, 'confirm').mockImplementation(() => true);
    vi.spyOn(window, 'alert').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ==========================================
  // 1. Note CRUD Edge Cases (6 tests)
  // ==========================================

  it('test_create_note_empty_title: Handle note save/creation with empty title (defaults to Untitled Note)', () => {
    render(<App />);

    // Navigate to Create Note
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Create New Note/i }));

    // Fill content but leave title empty
    const contentInput = screen.getByPlaceholderText('Type your study notes here...');
    fireEvent.change(contentInput, { target: { value: 'This note has no title but has content.' } });

    // Save note
    fireEvent.click(screen.getByRole('button', { name: /Save Note/i }));

    // Verify it saved and redirected
    expect(screen.getByText('My Study Notes')).toBeInTheDocument();

    // Verify it defaulted to 'Untitled Note'
    expect(screen.getByText('Untitled Note')).toBeInTheDocument();
    
    // Double check in storage
    const notes = getNotes();
    expect(notes).toHaveLength(1);
    expect(notes[0].title).toBe('Untitled Note');
  });

  it('test_create_note_empty_content: Handle save/creation with empty content', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Create New Note/i }));

    const titleInput = screen.getByPlaceholderText('Enter note title...');
    fireEvent.change(titleInput, { target: { value: 'Empty Content Note' } });

    // Save note without typing content
    fireEvent.click(screen.getByRole('button', { name: /Save Note/i }));

    // Verify it appears in Notes List
    expect(screen.getByText('Empty Content Note')).toBeInTheDocument();
    
    const notes = getNotes();
    expect(notes).toHaveLength(1);
    expect(notes[0].content).toBe('');
  });

  it('test_create_note_extreme_long_title: Title of 1000 characters handles layout/rendering gracefully', () => {
    const extremeTitle = 'A'.repeat(1000);
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Create New Note/i }));

    const titleInput = screen.getByPlaceholderText('Enter note title...');
    fireEvent.change(titleInput, { target: { value: extremeTitle } });

    fireEvent.click(screen.getByRole('button', { name: /Save Note/i }));

    // The component should render the title (usually with class line-clamp or truncated)
    const renderedTitle = screen.getByRole('heading', { level: 3 });
    expect(renderedTitle.textContent).toBe(extremeTitle);

    const notes = getNotes();
    expect(notes).toHaveLength(1);
    expect(notes[0].title).toHaveLength(1000);
  });

  it('test_create_note_extreme_large_content: Very large note content (50KB markdown) parses and saves', () => {
    // 50KB content
    const largeContent = '# Heading\n' + 'Body text with markdown.\n'.repeat(2000); // 2000 * 25 bytes = ~50KB
    
    // Save programmatically to check parsing and storage first
    const mockNote = {
      id: 'large-note-id',
      title: 'Large Content Note',
      content: largeContent,
      tags: [],
      category: 'Performance',
      masteryRating: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    // Verify layout renders without crashing
    expect(screen.getByText('Large Content Note')).toBeInTheDocument();
    
    // Check that we can open it in the editor
    fireEvent.click(screen.getByRole('button', { name: /Edit/i }));
    expect(screen.getByDisplayValue('Large Content Note')).toBeInTheDocument();
    const contentTextarea = screen.getByPlaceholderText('Type your study notes here...');
    expect(contentTextarea.textContent).toBe(largeContent);
  });

  it('test_autosave_on_title_debounce: Check auto-save functions correctly or triggers when fields change', () => {
    vi.useFakeTimers();
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Create New Note/i }));

    const titleInput = screen.getByPlaceholderText('Enter note title...');
    fireEvent.change(titleInput, { target: { value: 'Autosave Title Note' } });

    // Verify no autosave before 1000ms debounce
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(getNotes()).toHaveLength(0);

    // Verify autosave after 1000ms debounce
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(getNotes()).toHaveLength(1);
    expect(getNotes()[0].title).toBe('Autosave Title Note');
    expect(screen.getByTestId('autosave-status')).toHaveTextContent('Draft autosaved');

    vi.useRealTimers();
  });

  it('test_autosave_on_content_debounce: Verify auto-save triggers for content', () => {
    vi.useFakeTimers();
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Create New Note/i }));

    const contentInput = screen.getByPlaceholderText('Type your study notes here...');
    fireEvent.change(contentInput, { target: { value: 'Autosaved content text' } });

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    const notes = getNotes();
    expect(notes).toHaveLength(1);
    expect(notes[0].content).toBe('Autosaved content text');
    expect(screen.getByTestId('autosave-status')).toHaveTextContent('Draft autosaved');

    vi.useRealTimers();
  });

  // ==========================================
  // 2. Tag & Category Edge Cases (5 tests)
  // ==========================================

  it('test_add_duplicate_tag: Verify duplicate tags are de-duplicated or ignored', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Create New Note/i }));

    const titleInput = screen.getByPlaceholderText('Enter note title...');
    fireEvent.change(titleInput, { target: { value: 'Tag Deduplication Note' } });

    const tagsInput = screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...');
    // Type duplicates
    fireEvent.change(tagsInput, { target: { value: 'science, physics, science, physics' } });

    fireEvent.click(screen.getByRole('button', { name: /Save Note/i }));

    // Verify storage has unique tags
    const notes = getNotes();
    expect(notes[0].tags).toEqual(['science', 'physics']);
  });

  it('test_add_extremely_long_tag: Extremely long tag badge (100 characters) behaves correctly', () => {
    const longTag = 'T'.repeat(100);
    const mockNote = {
      id: 'long-tag-note',
      title: 'Long Tag Note',
      content: 'Hello world',
      tags: [longTag],
      category: 'General',
      masteryRating: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    // Verify tag is rendered on the screen
    expect(screen.getByText(`#${longTag}`)).toBeInTheDocument();
  });

  it('test_add_tag_special_chars: Special characters/emojis in tags are rendered', () => {
    const specialTags = ['💻coding', '🚀launch', '#testing!', 'hello_world'];
    const mockNote = {
      id: 'special-tags-note',
      title: 'Special Tags Note',
      content: 'Testing tags with emojis',
      tags: specialTags,
      category: 'General',
      masteryRating: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    specialTags.forEach(tag => {
      expect(screen.getByText(`#${tag}`)).toBeInTheDocument();
    });
  });

  it('test_delete_all_tags: Remove all tags from a note and verify display', () => {
    const mockNote = {
      id: 'tags-delete-note',
      title: 'Tags Delete Note',
      content: 'Has some tags initially',
      tags: ['tag1', 'tag2'],
      category: 'General',
      masteryRating: 2,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    // Click Edit
    fireEvent.click(screen.getByRole('button', { name: /Edit/i }));

    // Clear tags input
    const tagsInput = screen.getByPlaceholderText('e.g. chemistry, verbs, ww2...');
    fireEvent.change(tagsInput, { target: { value: '' } });

    // Save
    fireEvent.click(screen.getByRole('button', { name: /Save Note/i }));

    // Verify note in storage has no tags
    const notes = getNotes();
    expect(notes[0].tags).toEqual([]);

    // Verify tags are not rendered on the card anymore
    expect(screen.queryByText('#tag1')).not.toBeInTheDocument();
    expect(screen.queryByText('#tag2')).not.toBeInTheDocument();
  });

  it('test_empty_category_handling: Notes with no category are treated/grouped under Uncategorized or empty category', () => {
    const mockNote1 = {
      id: 'note-no-cat',
      title: 'Uncategorized Note',
      content: 'Content',
      tags: [],
      category: '',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    const mockNote2 = {
      id: 'note-with-cat',
      title: 'Science Note',
      content: 'Content',
      tags: [],
      category: 'Science',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote1);
    saveNote(mockNote2);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    // Note List should render Uncategorized badge for note 1
    expect(screen.getByTestId('uncategorized-badge')).toBeInTheDocument();

    // Select category dropdown filter
    const categorySelect = screen.getAllByRole('combobox')[0];
    fireEvent.change(categorySelect, { target: { value: 'Uncategorized' } });

    // Verify Uncategorized Note is visible and Science Note is filtered out
    expect(screen.getByText('Uncategorized Note')).toBeInTheDocument();
    expect(screen.queryByText('Science Note')).not.toBeInTheDocument();
  });

  // ==========================================
  // 3. Search & Filter Edge Cases (5 tests)
  // ==========================================

  it('test_search_special_characters: Search query with regex special chars does not crash search', () => {
    const mockNote = {
      id: 'regex-note',
      title: 'Special .* [a-z] Title',
      content: 'Regex characters content',
      tags: [],
      category: 'Regex',
      masteryRating: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    const searchInput = screen.getByPlaceholderText('Search title or content...');
    // Search with regex specials
    fireEvent.change(searchInput, { target: { value: '.* [a-z]' } });

    // Verify it doesn't crash and finds the note
    expect(screen.getByText('Special .* [a-z] Title')).toBeInTheDocument();
  });

  it('test_search_no_matches: Searching a non-matching query displays a friendly No notes found message', () => {
    const mockNote = {
      id: 'some-note',
      title: 'JavaScript Study Note',
      content: 'Content',
      tags: [],
      category: 'JS',
      masteryRating: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    const searchInput = screen.getByPlaceholderText('Search title or content...');
    fireEvent.change(searchInput, { target: { value: 'Python Flask' } });

    // Verify empty state display message
    expect(screen.getByText('No notes found matching your criteria.')).toBeInTheDocument();
  });

  it('test_search_extremely_long_query: Searching with a 500-character query doesn\'t crash the search logic', () => {
    const mockNote = {
      id: 'some-note',
      title: 'Simple Note',
      content: 'Simple content',
      tags: [],
      category: 'General',
      masteryRating: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    const searchInput = screen.getByPlaceholderText('Search title or content...');
    // 500 character query
    fireEvent.change(searchInput, { target: { value: 'z'.repeat(500) } });

    // Verify no crash, and empty state rendered
    expect(screen.getByText('No notes found matching your criteria.')).toBeInTheDocument();
  });

  it('test_filter_nonexistent_tag: Filtering by a tag not in use handles empty state', () => {
    const mockNote = {
      id: 'tag-note',
      title: 'Tag Filter Note',
      content: 'Simple content',
      tags: ['existent'],
      category: 'General',
      masteryRating: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    const tagSelect = screen.getAllByRole('combobox')[1];
    // Manually force select option values not in list to test filter robustness
    fireEvent.change(tagSelect, { target: { value: 'nonexistent-tag-val' } });

    // Verify empty state is displayed
    expect(screen.getByText('No notes found matching your criteria.')).toBeInTheDocument();
  });

  it('test_filter_nonexistent_category: Filtering by a category not in use handles empty state', () => {
    const mockNote = {
      id: 'cat-note',
      title: 'Category Filter Note',
      content: 'Simple content',
      tags: [],
      category: 'existent-category',
      masteryRating: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    const categorySelect = screen.getAllByRole('combobox')[0];
    fireEvent.change(categorySelect, { target: { value: 'nonexistent-category-val' } });

    // Verify empty state is displayed
    expect(screen.getByText('No notes found matching your criteria.')).toBeInTheDocument();
  });

  // ==========================================
  // 4. Quiz Edge Cases (8 tests)
  // ==========================================

  it('test_quiz_empty_note: Attempting to generate a quiz/flashcards for an empty note handles it gracefully', () => {
    const emptyNote = {
      id: 'empty-note-quiz',
      title: 'Empty Content Quiz Note',
      content: '',
      tags: [],
      category: '',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(emptyNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));

    // Should load QuizView and render fallback question about the content details
    expect(screen.getByText('Quiz: Empty Content Quiz Note')).toBeInTheDocument();
    expect(screen.getByText('What is the main topic of the note "Empty Content Quiz Note"?')).toBeInTheDocument();

    // Select option "General Study" (correct answer for fallback q1)
    fireEvent.click(screen.getByRole('button', { name: /^General Study$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Next Question/i }));

    // Select option "None" (correct answer for fallback q2)
    fireEvent.click(screen.getByRole('button', { name: /^None$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Next Question/i }));

    // Now it should show the 3rd question
    expect(screen.getByText('Does the content of "Empty Content Quiz Note" contain details about the subject matter?')).toBeInTheDocument();
  });

  it('test_quiz_no_questions_fallback: Quiz generation handles notes with no specific question headers by showing fallback/default questions', () => {
    const standardNote = {
      id: 'standard-note-quiz',
      title: 'Standard Quiz Note',
      content: 'This note has standard content with paragraphs but no Q/A blocks.',
      tags: ['math'],
      category: 'Studies',
      masteryRating: 4,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(standardNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));

    // Should fall back to mock questions
    expect(screen.getByText('What is the main topic of the note "Standard Quiz Note"?')).toBeInTheDocument();
  });

  it('test_quiz_exit_midway: Exiting a quiz before completion does not record a completed session in history', () => {
    const standardNote = {
      id: 'exit-midway-quiz',
      title: 'Exit Midway Note',
      content: 'Some details here.',
      tags: [],
      category: 'Test',
      masteryRating: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(standardNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));

    // Interact with first question option
    const firstOption = screen.getByRole('button', { name: /^Unrelated Subject A$/i });
    fireEvent.click(firstOption);

    // Exit midway
    fireEvent.click(screen.getByRole('button', { name: /Exit Quiz/i }));

    // Redirected back to notes list
    expect(screen.getByText('My Study Notes')).toBeInTheDocument();

    // Verify no quiz sessions are saved
    expect(getQuizSessions()).toHaveLength(0);
  });

  it('test_quiz_no_answers_selected: Verify submit button behaves correctly or alerts if no answer is chosen', () => {
    const standardNote = {
      id: 'no-answer-selected-quiz',
      title: 'No Answer Note',
      content: 'Content here.',
      tags: [],
      category: 'Testing',
      masteryRating: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(standardNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));

    // Verify next question button is disabled initially
    const nextBtn = screen.getByRole('button', { name: /Next Question|Finish Quiz/i });
    expect(nextBtn).toBeDisabled();
    expect(nextBtn).toHaveClass('opacity-50');
  });

  it('test_quiz_score_0_percent: Verify scoring handles 0% score (all wrong)', () => {
    const qaNote = {
      id: 'qa-note-0',
      title: 'Score Zero Note',
      content: 'Q: What is 2 + 2?\nA: 4',
      tags: [],
      category: 'Math',
      masteryRating: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(qaNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));

    // Question: "What is 2 + 2?"
    // Answer is "4", so select one of the "Alternative" options (wrong answer)
    const wrongOption = screen.getByRole('button', { name: /Alternative A/i });
    fireEvent.click(wrongOption);

    // Click Finish Quiz
    fireEvent.click(screen.getByRole('button', { name: /Finish Quiz/i }));

    // Verify score is 0%
    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText('0 / 1 Correct Answers')).toBeInTheDocument();
  });

  it('test_quiz_score_100_percent: Verify scoring handles 100% score (all correct)', () => {
    const qaNote = {
      id: 'qa-note-100',
      title: 'Score 100 Note',
      content: 'Q: Is coding fun?\nA: Yes',
      tags: [],
      category: 'General',
      masteryRating: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(qaNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));

    // Select correct answer "Yes"
    const correctOption = screen.getByRole('button', { name: /^Yes$/i });
    fireEvent.click(correctOption);

    // Finish Quiz
    fireEvent.click(screen.getByRole('button', { name: /Finish Quiz/i }));

    // Verify score is 100%
    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByText('1 / 1 Correct Answers')).toBeInTheDocument();
  });

  it('test_quiz_multiple_attempts: Verify multiple quiz attempts are saved as distinct session logs', () => {
    const noteId = 'multiple-attempts-note';
    const mockNote = {
      id: noteId,
      title: 'Multiple Quiz Note',
      content: 'Content',
      tags: [],
      category: 'Quiz',
      masteryRating: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    // Save two sessions programmatically
    const session1 = {
      id: 'session-1',
      noteId,
      score: 1,
      totalQuestions: 3,
      timestamp: new Date(Date.now() - 10000).toISOString()
    };
    const session2 = {
      id: 'session-2',
      noteId,
      score: 3,
      totalQuestions: 3,
      timestamp: new Date().toISOString()
    };
    saveQuizSession(session1);
    saveQuizSession(session2);

    // Verify storage logs
    const sessions = getQuizSessions();
    expect(sessions).toHaveLength(2);
    expect(sessions[0].id).toBe('session-1');
    expect(sessions[1].id).toBe('session-2');
  });

  it('test_quiz_extremely_long_questions: Quiz formatting handles extremely long questions/answers without breaking', () => {
    const longQuestion = 'Q: ' + 'What '.repeat(100) + '?';
    const longAnswer = 'A: ' + 'CorrectAnswer '.repeat(100);

    const longNote = {
      id: 'long-quiz-note',
      title: 'Extremely Long Quiz Elements Note',
      content: `${longQuestion}\n${longAnswer}`,
      tags: [],
      category: 'Performance',
      masteryRating: 2,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(longNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));

    // Verify that the long question text rendering matches without crash
    const qHeading = screen.getByRole('heading', { level: 4 });
    expect(qHeading.textContent).toBe(longQuestion.replace(/^Q:\s*/i, ''));
  });

  // ==========================================
  // 5. Mastery & Dashboard Edge Cases (6 tests)
  // ==========================================

  it('test_mastery_rating_boundary_0: Mastery rating state handles 0 (unrated)', () => {
    const mockNote = {
      id: 'mastery-0-note',
      title: 'Unrated Note',
      content: 'Content',
      tags: [],
      category: 'General',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    // Displays Mastery: Unrated
    expect(screen.getByText('Mastery: Unrated')).toBeInTheDocument();
  });

  it('test_mastery_rating_boundary_6: Mastery rating clamps or handles max limits', () => {
    const mockNote = {
      id: 'mastery-6-note',
      title: 'Clamped Max Mastery Note',
      content: 'Content',
      tags: [],
      category: 'General',
      masteryRating: 6, // Exceeds upper limit 5
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    // Displays clamped value: Mastery: 5
    expect(screen.getByText('Mastery: 5')).toBeInTheDocument();
    
    // Storage clamps it
    expect(getNotes()[0].masteryRating).toBe(5);
  });

  it('test_mastery_rating_boundary_negative: Mastery rating clamps or handles negative limits', () => {
    const mockNote = {
      id: 'mastery-neg-note',
      title: 'Clamped Negative Mastery Note',
      content: 'Content',
      tags: [],
      category: 'General',
      masteryRating: -2, // Below lower limit 0
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /^my notes$/i }));

    // Displays clamped value: Mastery: Unrated
    expect(screen.getByText('Mastery: Unrated')).toBeInTheDocument();

    // Storage clamps it to 0
    expect(getNotes()[0].masteryRating).toBe(0);
  });

  it('test_persistence_corrupted_storage: Handles invalid JSON in localStorage gracefully without crashing (resetting to defaults)', () => {
    localStorage.setItem('self_assessment_notes', 'corrupted { json state');

    // Should load successfully without throwing uncaught parser errors
    expect(() => render(<App />)).not.toThrow();
    
    // Check that we render the zero state on Dashboard
    expect(screen.getByText('Dashboard Overview')).toBeInTheDocument();
    expect(screen.getByText('Total Study Notes')).toBeInTheDocument();
    
    // Ensure getNotes() falls back to empty array
    expect(getNotes()).toEqual([]);
  });

  it('test_dashboard_zero_notes: Dashboard displays clean zero-states when no notes or history are present', () => {
    render(<App />);

    // Total Study Notes card displays 0
    const totalNotesMetric = screen.getByText('Total Study Notes').parentElement;
    expect(totalNotesMetric).toHaveTextContent('0notes');

    // Average Mastery displays 0.0
    const avgMasteryMetric = screen.getByText('Average Mastery Rating').parentElement;
    expect(avgMasteryMetric).toHaveTextContent('0.0/ 5.0');

    // Completed Assessments displays 0
    const completedMetric = screen.getByText('Completed Assessments').parentElement;
    expect(completedMetric).toHaveTextContent('0quizzes');

    // Display start call to action text
    expect(screen.getByText('Start Note-Taking')).toBeInTheDocument();
  });

  it('test_dashboard_division_by_zero: Dashboard metrics do not show NaN or crash when total quizzes or ratings are 0', () => {
    // Save a note with mastery 0 (unrated)
    const mockNote = {
      id: 'unrated-note',
      title: 'Unrated Note',
      content: 'Content',
      tags: [],
      category: 'General',
      masteryRating: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    saveNote(mockNote);

    render(<App />);

    // Should display avg mastery 0.0 without producing NaN or crashes
    const avgMasteryMetric = screen.getByText('Average Mastery Rating').parentElement;
    expect(avgMasteryMetric).toHaveTextContent('0.0/ 5.0');
    expect(avgMasteryMetric).not.toHaveTextContent('NaN');

    // Should display completed assessments 0 (no average score)
    const completedMetric = screen.getByText('Completed Assessments').parentElement;
    expect(completedMetric).toHaveTextContent('0quizzes');
    expect(completedMetric).not.toHaveTextContent('NaN');
  });
});
