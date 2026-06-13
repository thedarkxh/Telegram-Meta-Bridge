/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from 'react';
import type { Note } from '../types';
import { getNotes, saveNote } from '../utils/storage';
import type { View } from '../App';

interface NoteEditorProps {
  noteId: string | null;
  navigateTo: (view: View, noteId?: string | null) => void;
}

export default function NoteEditor({ noteId, navigateTo }: NoteEditorProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [masteryRating, setMasteryRating] = useState<number>(0);
  const [createdAt, setCreatedAt] = useState('');
  const [currentNoteId, setCurrentNoteId] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [autosaveStatus, setAutosaveStatus] = useState('');

  // Load note if editing
  useEffect(() => {
    if (noteId) {
      const notes = getNotes();
      const existing = notes.find(n => n.id === noteId);
      if (existing) {
        setTitle(existing.title);
        setContent(existing.content);
        setCategory(existing.category || '');
        setTagsInput(existing.tags ? existing.tags.join(', ') : '');
        setMasteryRating(existing.masteryRating || 0);
        setCreatedAt(existing.createdAt || '');
        setCurrentNoteId(existing.id);
      }
    } else {
      // Reset for creation
      setTitle('');
      setContent('');
      setCategory('');
      setTagsInput('');
      setMasteryRating(0);
      setCreatedAt('');
      setCurrentNoteId(null);
    }
    setIsDirty(false);
    setAutosaveStatus('');
  }, [noteId]);

  // Debounced autosave
  useEffect(() => {
    if (!isDirty) return;

    const delayDebounceFn = setTimeout(() => {
      const tags = tagsInput
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);
      const uniqueTags = Array.from(new Set(tags));

      const now = new Date().toISOString();
      const generatedId = currentNoteId || crypto.randomUUID();
      if (!currentNoteId) {
        setCurrentNoteId(generatedId);
      }

      const noteToSave: Note = {
        id: generatedId,
        title: title.trim() || 'Untitled Note',
        content: content.trim(),
        category: category.trim(),
        tags: uniqueTags,
        masteryRating: Math.max(0, Math.min(5, masteryRating)),
        createdAt: createdAt || now,
        updatedAt: now
      };

      saveNote(noteToSave);
      setAutosaveStatus('Draft autosaved');
    }, 1000); // 1-second debounce

    return () => clearTimeout(delayDebounceFn);
  }, [title, content, category, tagsInput, masteryRating, isDirty, currentNoteId, createdAt]);

  const handleTitleChange = (val: string) => {
    setTitle(val);
    setIsDirty(true);
    setAutosaveStatus('Saving...');
  };

  const handleContentChange = (val: string) => {
    setContent(val);
    setIsDirty(true);
    setAutosaveStatus('Saving...');
  };

  const handleCategoryChange = (val: string) => {
    setCategory(val);
    setIsDirty(true);
    setAutosaveStatus('Saving...');
  };

  const handleTagsChange = (val: string) => {
    setTagsInput(val);
    setIsDirty(true);
    setAutosaveStatus('Saving...');
  };

  const handleMasteryChange = (val: number) => {
    setMasteryRating(val);
    setIsDirty(true);
    setAutosaveStatus('Saving...');
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();

    const tags = tagsInput
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0);
    const uniqueTags = Array.from(new Set(tags));

    const now = new Date().toISOString();
    const generatedId = currentNoteId || crypto.randomUUID();

    const noteToSave: Note = {
      id: generatedId,
      title: title.trim() || 'Untitled Note',
      content: content.trim(),
      category: category.trim(),
      tags: uniqueTags,
      masteryRating: Math.max(0, Math.min(5, masteryRating)),
      createdAt: createdAt || now,
      updatedAt: now
    };

    saveNote(noteToSave);
    navigateTo('notes-list');
  };

  return (
    <div className="space-y-8" data-testid="note-editor-view">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            {noteId ? 'Edit Study Note' : 'Create Study Note'}
          </h2>
          <p className="text-slate-400 mt-1">
            {noteId ? 'Modify your note and save changes.' : 'Write down your study materials to prepare for self-assessments.'}
          </p>
        </div>
        {autosaveStatus && (
          <span 
            data-testid="autosave-status" 
            className="text-xs font-semibold px-2 py-1 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
          >
            {autosaveStatus}
          </span>
        )}
      </div>

      {/* Editor Form */}
      <form onSubmit={handleSave} className="glass-panel p-6 rounded-xl space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Title */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Note Title *</label>
            <input
              type="text"
              placeholder="Enter note title..."
              value={title}
              onChange={(e) => handleTitleChange(e.target.value)}
              className="glass-input"
            />
          </div>

          {/* Category */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Category</label>
            <input
              type="text"
              placeholder="e.g. Science, Languages, History..."
              value={category}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="glass-input"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tags */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tags (comma-separated)</label>
            <input
              type="text"
              placeholder="e.g. chemistry, verbs, ww2..."
              value={tagsInput}
              onChange={(e) => handleTagsChange(e.target.value)}
              className="glass-input"
            />
          </div>

          {/* Mastery Rating */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Mastery Rating</label>
            <div className="flex items-center space-x-2 h-[42px]">
              {[0, 1, 2, 3, 4, 5].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => handleMasteryChange(num)}
                  className={`w-9 h-9 rounded-lg font-bold transition-all border cursor-pointer ${
                    masteryRating === num
                      ? `mastery-bg-${num} scale-105 shadow-md`
                      : 'bg-[#151726]/40 text-slate-400 border-white/5 hover:border-white/20'
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Content (Markdown supported)</label>
          <textarea
            placeholder="Type your study notes here..."
            value={content}
            onChange={(e) => handleContentChange(e.target.value)}
            className="glass-input h-64 font-mono text-sm resize-y"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-6 border-t border-white/5">
          <button
            type="button"
            onClick={() => navigateTo('notes-list')}
            className="glass-button-secondary cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="glass-button-primary cursor-pointer"
          >
            Save Note
          </button>
        </div>
      </form>
    </div>
  );
}
