# E2E Test Cases Inventory

This document details the complete list of test cases designed for the E2E Testing Track of the Self-Assessment Portal.

---

## Tier 1: Feature Coverage (>=30 tests)

### Note CRUD (5 tests)
1. **test_create_note**: Can create a new note with title and content, and it appears in the notes list.
2. **test_read_note**: Clicking a note in the list displays its title, content, and metadata correctly.
3. **test_update_note_title**: Editing and saving a note's title updates it in the list and view.
4. **test_update_note_content**: Editing and saving a note's content updates its rendered markdown view.
5. **test_delete_note**: Deleting a note removes it from the notes list and clears the active view.

### Tag & Category Management (7 tests)
6. **test_add_tag**: Can add tags to a note during creation or editing.
7. **test_remove_tag**: Can remove a tag from a note, and the tag is no longer displayed on that note.
8. **test_list_all_tags**: All unique tags across all notes are displayed in the tag filter list.
9. **test_note_tags_render**: Note tags are rendered correctly on the note card/view.
10. **test_set_category**: Can set or change the category of a note.
11. **test_list_all_categories**: All categories are displayed in the category filter list.
12. **test_note_category_render**: Note category is rendered correctly on the note.

### Search & Filter (6 tests)
13. **test_search_by_title**: Searching for a note title filters the list to show only matching notes.
14. **test_search_by_content**: Searching for a term in note content filters the list to show only matching notes.
15. **test_case_insensitive_search**: Search is case-insensitive for both titles and content.
16. **test_filter_by_tag**: Selecting a tag filter displays only notes containing that tag.
17. **test_filter_by_category**: Selecting a category filter displays only notes in that category.
18. **test_combined_search_and_filter**: Combined search query and category/tag filter works correctly.

### Quiz & Flashcards (8 tests)
19. **test_generate_flashcards**: Can generate flashcards from note content.
20. **test_flip_flashcard**: Clicking a flashcard flips it to show the answer/back side.
21. **test_navigate_flashcards**: Can navigate forward and backward through the flashcard deck.
22. **test_generate_quiz**: Can generate multiple-choice quiz questions from a note.
23. **test_submit_quiz_correct_answer**: Selecting the correct answer provides positive feedback.
24. **test_submit_quiz_incorrect_answer**: Selecting an incorrect answer provides correction feedback.
25. **test_complete_quiz_score**: Completing all quiz questions displays the final score and percentage.
26. **test_quiz_history_recorded**: A completed quiz session is saved in the user's study history.

### Mastery & Dashboard (4 tests)
27. **test_set_mastery_rating**: Can manually set the mastery rating of a note (scale 1-5).
28. **test_update_mastery_rating**: Updating the mastery rating of a note reflects the new rating.
29. **test_dashboard_metrics_render**: Dashboard displays overall learning metrics (total notes, mastery rating average).
30. **test_local_persistence_reload**: Notes and quiz history remain intact after simulated app reload (LocalStorage).

---

## Tier 2: Boundary & Corner Cases (>=30 tests)

### Note CRUD Edge Cases (6 tests)
31. **test_create_note_empty_title**: Creating a note with an empty title handles it gracefully (defaults title or saves as "(Untitled Note)").
32. **test_create_note_empty_content**: Creating a note with empty content is allowed and handles rendering gracefully.
33. **test_create_note_extreme_long_title**: Creating a note with a title of 1000 characters does not break UI layout.
34. **test_create_note_extreme_large_content**: Note with 50KB markdown content saves and parses without crashing.
35. **test_autosave_on_title_debounce**: Auto-save triggers after editing title with debounce.
36. **test_autosave_on_content_debounce**: Auto-save triggers after editing content with debounce.

### Tag & Category Edge Cases (5 tests)
37. **test_add_duplicate_tag**: Adding a duplicate tag is ignored or de-duplicated automatically.
38. **test_add_extremely_long_tag**: Adding a tag of 100 characters does not break the UI tag pills.
39. **test_add_tag_special_chars**: Tags containing special characters or emojis are saved and rendered correctly.
40. **test_delete_all_tags**: Removing all tags from a note is handled correctly.
41. **test_empty_category_handling**: Assigning no category to a note default-groups it into "Uncategorized".

### Search & Filter Edge Cases (5 tests)
42. **test_search_special_characters**: Search query with regex special characters (e.g. `.*`, `[a-z]`) does not crash search logic.
43. **test_search_no_matches**: Search query with no matches displays a friendly "No notes found" message.
44. **test_search_extremely_long_query**: Searching with a 500-character string does not crash.
45. **test_filter_nonexistent_tag**: Filtering by a tag that was deleted or doesn't exist shows empty state.
46. **test_filter_nonexistent_category**: Filtering by a category that doesn't exist shows empty state.

### Quiz Edge Cases (8 tests)
47. **test_quiz_empty_note**: Trying to generate a quiz/flashcards for an empty note displays a warning or fallback.
48. **test_quiz_no_questions_fallback**: Note without distinct quiz headers/questions fallback-generates general vocabulary or reading comprehension questions.
49. **test_quiz_exit_midway**: Exiting a quiz before completion does not record a completed session in study history.
50. **test_quiz_no_answers_selected**: Attempting to submit a quiz question without selecting an answer displays validation feedback.
51. **test_quiz_score_0_percent**: Answering all quiz questions incorrectly displays 0% score.
52. **test_quiz_score_100_percent**: Answering all quiz questions correctly displays 100% score.
53. **test_quiz_multiple_attempts**: Taking the same quiz multiple times records multiple distinct entries in history.
54. **test_quiz_extremely_long_questions**: Quiz question/option texts that are extremely long are formatted properly in UI.

### Mastery & Dashboard Edge Cases (6 tests)
55. **test_mastery_rating_boundary_0**: Mastery rating set to 0 (corrupted storage or direct state) defaults to unrated (0).
56. **test_mastery_rating_boundary_6**: Mastery rating clamped to 5 if state tries to exceed max rating.
57. **test_mastery_rating_boundary_negative**: Mastery rating clamped to 0/1 if state tries to set negative rating.
58. **test_persistence_corrupted_storage**: Application handles corrupted JSON in LocalStorage without crashing (falls back to initial state).
59. **test_dashboard_zero_notes**: Dashboard displays clean zero-states when no notes or history are present.
60. **test_dashboard_division_by_zero**: Metric charts do not fail or show NaN when calculating average score with 0 quizzes completed.

---

## Tier 3: Cross-Feature Combinations (>=6 tests)

61. **test_search_filter_then_quiz**: Apply search text and tag filter, select a matching note, and start/complete a quiz.
62. **test_edit_note_content_updates_quiz**: Edit a note's text content, then immediately start a quiz and verify the questions/answers update to reflect the changes.
63. **test_delete_note_during_quiz**: Start a quiz on a note, delete the note from the sidebar/dashboard (or simulate deletion), and verify the quiz session handles it gracefully (fails safe or returns to dashboard).
64. **test_quiz_score_updates_mastery_prompt**: Complete a quiz and verify that a high score prompts or enables setting the mastery rating easily, updating the dashboard.
65. **test_create_note_with_tag_filters_immediately**: Create a new note with a new tag, verify that the new tag immediately appears in the filters list, and selecting it shows only the new note.
66. **test_mastery_update_recalculates_dashboard**: Bulk update mastery ratings for multiple notes and verify that the dashboard average mastery score and rating distribution chart update dynamically.

---

## Tier 4: Real-World Application Scenarios (>=5 tests)

67. **test_full_user_study_flow**: 
    - User creates 3 notes (Math, History, Science).
    - Categorizes them and adds tags like "exam" and "easy".
    - Opens Math note, takes a quiz, scores 100%.
    - Sets Math note mastery to 5.
    - Views Dashboard to verify Math is 100% mastered, average mastery is updated, and 1 quiz session is logged.
68. **test_revision_session_flow**:
    - User filters notes by tag "exam".
    - Opens first note, goes through its flashcard deck.
    - Opens second note, takes a quiz, scores 80%.
    - Checks Dashboard to see overall revision progress and updated session history.
69. **test_content_refactoring_flow**:
    - User opens a note, edits its category from "General" to "Advanced Math".
    - Adds a new tag "calculus", changes content.
    - Verifies auto-save indicator.
    - Uses search to search "calculus", finds the note.
    - Opens quiz to verify questions reflect new "calculus" content.
70. **test_reset_and_reassess_flow**:
    - User has existing notes, quiz sessions, and mastery ratings.
    - User triggers history reset (or manually removes all notes/quizzes).
    - Verifies dashboard and lists are completely cleared and reset to initial state.
    - User creates one new note, takes a quiz, and verifies the dashboard starts recording fresh progress.
71. **test_multi_note_quiz_progress_milestones**:
    - User takes quizzes on 5 different notes, scoring 0%, 25%, 50%, 75%, and 100%.
    - Verifies that the dashboard average quiz score is exactly 50%.
    - Verifies the study history list is ordered chronologically with correct score badges.
