import { useState } from 'react';
import Dashboard from './components/Dashboard';
import NotesList from './components/NotesList';
import NoteEditor from './components/NoteEditor';
import QuizView from './components/QuizView';

export type View = 'dashboard' | 'notes-list' | 'note-editor' | 'quiz';

export default function App() {
  const [view, setView] = useState<View>('dashboard');
  const [activeNoteId, setActiveNoteId] = useState<string | null>(null);

  const navigateTo = (newView: View, noteId: string | null = null) => {
    setView(newView);
    setActiveNoteId(noteId);
  };

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100 font-sans">
      {/* Premium Sidebar Navigation */}
      <aside className="w-64 glass-panel border-r border-slate-800/80 p-6 flex flex-col justify-between">
        <div className="flex flex-col gap-8">
          {/* Brand Logo */}
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigateTo('dashboard')}>
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white shadow-md shadow-indigo-500/20">
              S
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Self-Assess
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col gap-2">
            <button
              id="nav-dashboard"
              onClick={() => navigateTo('dashboard')}
              className={`w-full text-left px-4 py-2.5 rounded-lg transition-all text-sm font-medium cursor-pointer ${
                view === 'dashboard'
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
              }`}
            >
              Dashboard
            </button>
            <button
              id="nav-notes"
              onClick={() => navigateTo('notes-list')}
              className={`w-full text-left px-4 py-2.5 rounded-lg transition-all text-sm font-medium cursor-pointer ${
                view === 'notes-list' || view === 'note-editor' || view === 'quiz'
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
              }`}
            >
              My Notes
            </button>
          </nav>
        </div>

        {/* Footer */}
        <div className="text-xs text-slate-500 border-t border-white/5 pt-4">
          Status: Local Storage Sync Active
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-8 overflow-y-auto max-h-screen">
        <div className="max-w-6xl mx-auto">
          {view === 'dashboard' && (
            <Dashboard navigateTo={navigateTo} />
          )}
          {view === 'notes-list' && (
            <NotesList navigateTo={navigateTo} />
          )}
          {view === 'note-editor' && (
            <NoteEditor noteId={activeNoteId} navigateTo={navigateTo} />
          )}
          {view === 'quiz' && activeNoteId && (
            <QuizView noteId={activeNoteId} navigateTo={navigateTo} />
          )}
        </div>
      </main>
    </div>
  );
}
