/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from 'react';
import type { Note } from '../types';
import { getNotes, deleteNote } from '../utils/storage';
import type { View } from '../App';

interface NotesListProps {
  navigateTo: (view: View, noteId?: string | null) => void;
}

export default function NotesList({ navigateTo }: NotesListProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedTag, setSelectedTag] = useState('All');

  // Load notes initially
  useEffect(() => {
    setNotes(getNotes());
  }, []);

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this note?')) {
      deleteNote(id);
      setNotes(getNotes());
    }
  };

  // Get categories and tags list for filters
  const hasEmptyCategory = notes.some(n => !n.category);
  const rawCategories = Array.from(new Set(notes.map(n => n.category).filter(Boolean)));
  const categories = ['All', ...(hasEmptyCategory ? ['Uncategorized'] : []), ...rawCategories];
  const tags = ['All', ...Array.from(new Set(notes.flatMap(n => n.tags || []).filter(Boolean)))];

  // Filtered notes
  const filteredNotes = notes.filter(note => {
    const matchesSearch = note.title.toLowerCase().includes(search.toLowerCase()) || 
                          note.content.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || 
                            (selectedCategory === 'Uncategorized' && !note.category) ||
                            note.category === selectedCategory;
    const matchesTag = selectedTag === 'All' || (note.tags && note.tags.includes(selectedTag));
    return matchesSearch && matchesCategory && matchesTag;
  });

  return (
    <div className="space-y-8" data-testid="notes-list-view">
      {/* Title & Action */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">My Study Notes</h2>
          <p className="text-slate-400 mt-1">Browse, search, and manage your notes.</p>
        </div>
        <button
          onClick={() => navigateTo('note-editor')}
          className="glass-button-primary cursor-pointer self-start md:self-auto"
        >
          Create New Note
        </button>
      </div>

      {/* Filters bar */}
      <div className="glass-panel p-4 rounded-xl grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Search */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Search</label>
          <input
            type="text"
            placeholder="Search title or content..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="glass-input"
          />
        </div>

        {/* Category */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Category</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="glass-input cursor-pointer"
          >
            {categories.map(c => (
              <option key={c} value={c} className="bg-slate-900 text-slate-100">{c}</option>
            ))}
          </select>
        </div>

        {/* Tag */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tag</label>
          <select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
            className="glass-input cursor-pointer"
          >
            {tags.map(t => (
              <option key={t} value={t} className="bg-slate-900 text-slate-100">{t}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Notes Grid */}
      {filteredNotes.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-xl">
          <p className="text-slate-400 text-lg">No notes found matching your criteria.</p>
          <button
            onClick={() => navigateTo('note-editor')}
            className="mt-4 text-indigo-400 hover:text-indigo-300 font-medium underline"
          >
            Create one now
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredNotes.map(note => (
            <div key={note.id} className="glass-panel p-6 rounded-xl flex flex-col justify-between hover:border-indigo-500/30 transition-all duration-300">
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <h3 className="text-xl font-bold text-white line-clamp-1">{note.title}</h3>
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium mastery-bg-${note.masteryRating || 0}`}>
                    Mastery: {note.masteryRating || 'Unrated'}
                  </span>
                </div>
                
                {note.category ? (
                  <span className="inline-block text-xs bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded">
                    {note.category}
                  </span>
                ) : (
                  <span className="inline-block text-xs bg-slate-800/50 text-slate-400 border border-white/5 px-2 py-0.5 rounded" data-testid="uncategorized-badge">
                    Uncategorized
                  </span>
                )}
                
                <p className="text-slate-400 text-sm line-clamp-3 leading-relaxed">
                  {note.content || 'No content.'}
                </p>

                {note.tags && note.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {note.tags.map(tag => (
                      <span key={tag} className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between gap-2 pt-6 mt-6 border-t border-white/5">
                <button
                  onClick={() => navigateTo('quiz', note.id)}
                  className="px-3 py-1.5 bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold rounded-lg hover:bg-emerald-600/30 cursor-pointer transition-all"
                >
                  Start Quiz
                </button>
                <div className="flex gap-2">
                  <button
                    onClick={() => navigateTo('note-editor', note.id)}
                    className="px-3 py-1.5 bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 text-xs font-semibold rounded-lg hover:bg-indigo-600/30 cursor-pointer transition-all"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(note.id)}
                    className="px-3 py-1.5 bg-rose-600/20 text-rose-400 border border-rose-500/30 text-xs font-semibold rounded-lg hover:bg-rose-600/30 cursor-pointer transition-all"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
