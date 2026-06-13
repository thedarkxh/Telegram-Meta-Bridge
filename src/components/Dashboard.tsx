import { useState } from 'react';
import { getNotes, getQuizSessions } from '../utils/storage';
import type { View } from '../App';

interface DashboardProps {
  navigateTo: (view: View, noteId?: string | null) => void;
}

export default function Dashboard({ navigateTo }: DashboardProps) {
  const [resetToggle, setResetToggle] = useState(false);
  
  const notes = getNotes();
  const sessions = getQuizSessions();

  // Compute metrics
  const totalNotes = notes.length;
  const totalQuizzes = sessions.length;
  
  const ratedNotes = notes.filter(n => n.masteryRating > 0);
  const avgMastery = ratedNotes.length > 0 
    ? (ratedNotes.reduce((acc, curr) => acc + curr.masteryRating, 0) / ratedNotes.length).toFixed(1)
    : '0.0';

  const averageScore = sessions.length > 0
    ? (sessions.reduce((acc, curr) => acc + (curr.score / curr.totalQuestions) * 100, 0) / sessions.length).toFixed(0)
    : null;

  // Find note title for each session
  const getNoteTitle = (noteId: string) => {
    const note = notes.find(n => n.id === noteId);
    return note ? note.title : 'Deleted Note';
  };

  // Get badge based on quiz score
  const getScoreBadge = (score: number, total: number) => {
    const pct = (score / total) * 100;
    if (pct === 100) return { label: 'Master', className: 'bg-amber-500/20 text-amber-300 border-amber-500/30' };
    if (pct >= 75) return { label: 'Expert', className: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' };
    if (pct >= 50) return { label: 'Passing', className: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' };
    return { label: 'Needs Review', className: 'bg-rose-500/20 text-rose-300 border-rose-500/30' };
  };

  const handleReset = () => {
    if (confirm('Are you sure you want to reset all data? This cannot be undone.')) {
      localStorage.removeItem('sa-portal:notes');
      localStorage.removeItem('sa-portal:quizzes');
      setResetToggle(prev => !prev);
      navigateTo('dashboard');
    }
  };

  return (
    <div className="space-y-8" data-testid="dashboard-view">
      {/* Title */}
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Dashboard Overview</h2>
        <p className="text-slate-400 mt-1">Real-time learning stats and mastery distribution.</p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-xl flex flex-col justify-between">
          <span className="text-slate-400 font-medium text-sm">Total Study Notes</span>
          <div className="flex items-baseline mt-4 space-x-2">
            <span className="text-4xl font-extrabold text-indigo-400">{totalNotes}</span>
            <span className="text-slate-500 text-sm">notes</span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl flex flex-col justify-between">
          <span className="text-slate-400 font-medium text-sm">Average Mastery Rating</span>
          <div className="flex items-baseline mt-4 space-x-2">
            <span className="text-4xl font-extrabold text-emerald-400">{avgMastery}</span>
            <span className="text-slate-500 text-sm">/ 5.0</span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl flex flex-col justify-between">
          <span className="text-slate-400 font-medium text-sm">Completed Assessments</span>
          <div className="flex items-baseline mt-4 space-x-2">
            <span className="text-4xl font-extrabold text-purple-400">{totalQuizzes}</span>
            <span className="text-slate-500 text-sm">{averageScore !== null ? `(${averageScore}% avg)` : 'quizzes'}</span>
          </div>
        </div>
      </div>

      {/* Revision History and Mastered Notes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Revision History */}
        <div className="glass-panel p-6 rounded-xl space-y-4">
          <h3 className="text-xl font-bold text-white">Revision History</h3>
          {sessions.length === 0 ? (
            <p className="text-slate-400 text-sm">No revision history found.</p>
          ) : (
            <div className="space-y-3 max-h-60 overflow-y-auto" data-testid="revision-history">
              {sessions.slice().reverse().map((session) => {
                const badge = getScoreBadge(session.score, session.totalQuestions);
                const scorePct = ((session.score / session.totalQuestions) * 100).toFixed(0);
                return (
                  <div key={session.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="space-y-1">
                      <p className="text-sm font-semibold text-white truncate max-w-[180px]">
                        {getNoteTitle(session.noteId)}
                      </p>
                      <p className="text-xs text-slate-500">
                        {session.timestamp.slice(0, 10)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded font-medium border ${badge.className}`} data-testid="history-badge">
                        {badge.label}
                      </span>
                      <span className="text-sm font-bold text-slate-300" data-testid="history-score">
                        {scorePct}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Mastered Notes */}
        <div className="glass-panel p-6 rounded-xl space-y-4">
          <h3 className="text-xl font-bold text-white">Mastered Notes (5/5)</h3>
          {notes.filter(n => n.masteryRating === 5).length === 0 ? (
            <p className="text-slate-400 text-sm">No mastered notes yet.</p>
          ) : (
            <div className="space-y-2" data-testid="mastered-notes-list">
              {notes.filter(n => n.masteryRating === 5).map(note => (
                <div key={note.id} className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm rounded-lg flex justify-between items-center">
                  <span className="font-medium truncate max-w-[200px]" data-testid="mastered-note-title">{note.title}</span>
                  <span className="text-xs bg-emerald-500 text-white px-2 py-0.5 rounded-full font-bold">Mastered</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Start Note-Taking Action */}
      <div className="glass-panel p-8 rounded-xl space-y-4">
        <h3 className="text-xl font-bold text-white">Start Note-Taking</h3>
        <p className="text-slate-400 max-w-2xl text-sm leading-relaxed">
          Create structured markdown notes, assign categories, and generate randomized self-assessment quizzes to test your knowledge retention.
        </p>
        <div className="flex space-x-4 pt-2">
          <button
            onClick={() => navigateTo('note-editor')}
            className="glass-button-primary cursor-pointer"
          >
            Create New Note
          </button>
          <button
            onClick={() => navigateTo('notes-list')}
            className="glass-button-secondary cursor-pointer"
          >
            Browse My Notes
          </button>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="glass-panel p-6 rounded-xl border border-rose-500/20 flex items-center justify-between bg-rose-500/5">
        <div>
          <h4 className="text-base font-bold text-rose-400">Danger Zone</h4>
          <p className="text-slate-400 text-xs mt-0.5">Delete all study notes, quiz sessions, and mastery progress.</p>
        </div>
        <button
          onClick={handleReset}
          className="px-4 py-2 bg-rose-600/20 text-rose-400 border border-rose-500/30 text-xs font-semibold rounded-lg hover:bg-rose-600/30 cursor-pointer transition-all"
          data-testid="reset-data-btn"
        >
          Reset Data
        </button>
      </div>
    </div>
  );
}
