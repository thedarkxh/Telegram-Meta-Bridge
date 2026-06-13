/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from 'react';
import type { Note, QuizQuestion, QuizSession } from '../types';
import { getNotes, saveQuizSession, saveNote } from '../utils/storage';
import type { View } from '../App';

interface QuizViewProps {
  noteId: string;
  navigateTo: (view: View, noteId?: string | null) => void;
}

export default function QuizView({ noteId, navigateTo }: QuizViewProps) {
  const [note, setNote] = useState<Note | null>(null);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [showFeedback, setShowFeedback] = useState(false);
  const [quizFinished, setQuizFinished] = useState(false);
  const [finalScore, setFinalScore] = useState(0);
  const [masteryRating, setMasteryRating] = useState<number>(0);

  const handleUpdateMastery = (rating: number) => {
    if (!note) return;
    const updatedNote = {
      ...note,
      masteryRating: rating,
      updatedAt: new Date().toISOString()
    };
    saveNote(updatedNote);
    setMasteryRating(rating);
  };

  // Flashcards state
  const [mode, setMode] = useState<'quiz' | 'flashcard'>('quiz');
  const [currentFlashcardIdx, setCurrentFlashcardIdx] = useState(0);
  const [flipped, setFlipped] = useState(false);

  const parseQuestionsFromContent = (content: string): QuizQuestion[] => {
    const parsed: QuizQuestion[] = [];
    if (!content) return parsed;

    const lines = content.split('\n');
    let currentQuestion = '';
    let currentAnswer = '';
    let count = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      const qMatch = line.match(/^(?:###?\s+)?(?:q|question):\s*(.*)$/i);
      const aMatch = line.match(/^(?:###?\s+)?(?:a|answer):\s*(.*)$/i);

      if (qMatch) {
        if (currentQuestion) {
          const ans = currentAnswer || 'True';
          parsed.push({
            id: `q-parsed-${count++}`,
            question: currentQuestion,
            answer: ans,
            options: [ans, 'Alternative A', 'Alternative B', 'Alternative C'].sort(() => Math.random() - 0.5)
          });
          currentAnswer = '';
        }
        currentQuestion = qMatch[1].trim();
      } else if (aMatch) {
        currentAnswer = aMatch[1].trim();
      }
    }

    if (currentQuestion) {
      const ans = currentAnswer || 'True';
      parsed.push({
        id: `q-parsed-${count}`,
        question: currentQuestion,
        answer: ans,
        options: [ans, 'Alternative A', 'Alternative B', 'Alternative C'].sort(() => Math.random() - 0.5)
      });
    }

    return parsed;
  };

  useEffect(() => {
    const notes = getNotes();
    const activeNote = notes.find(n => n.id === noteId);
    if (activeNote) {
      setNote(activeNote);
      setMasteryRating(activeNote.masteryRating || 0);
      
      let generatedQuestions = parseQuestionsFromContent(activeNote.content);
      if (generatedQuestions.length === 0) {
        generatedQuestions = [
          {
            id: 'q1',
            question: `What is the main topic of the note "${activeNote.title}"?`,
            answer: activeNote.category || 'General Study',
            options: [
              activeNote.category || 'General Study',
              'Unrelated Subject A',
              'Unrelated Subject B',
              'Unrelated Subject C'
            ].sort(() => Math.random() - 0.5)
          },
          {
            id: 'q2',
            question: `Which of the following tags is associated with "${activeNote.title}"?`,
            answer: activeNote.tags && activeNote.tags.length > 0 ? activeNote.tags[0] : 'None',
            options: [
              activeNote.tags && activeNote.tags.length > 0 ? activeNote.tags[0] : 'None',
              'random-tag-1',
              'random-tag-2',
              'random-tag-3'
            ].sort(() => Math.random() - 0.5)
          },
          {
            id: 'q3',
            question: `Does the content of "${activeNote.title}" contain details about the subject matter?`,
            answer: activeNote.content.length > 0 ? 'Yes' : 'No',
            options: ['Yes', 'No', 'Partially', 'Cannot be determined'].sort(() => Math.random() - 0.5)
          }
        ];
      }
      setQuestions(generatedQuestions);
    }
  }, [noteId]);

  if (!note) {
    return (
      <div className="glass-panel p-8 text-center rounded-xl">
        <p className="text-slate-400">Note not found.</p>
        <button onClick={() => navigateTo('notes-list')} className="mt-4 glass-button-primary cursor-pointer">
          Back to Notes
        </button>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIdx];

  const flashcards = questions.map(q => ({
    front: q.question,
    back: q.answer
  }));

  const handleSelectOption = (option: string) => {
    if (showFeedback) return;
    setSelectedAnswers({
      ...selectedAnswers,
      [currentQuestion.id]: option
    });
  };

  const handleNext = () => {
    if (!selectedAnswers[currentQuestion.id]) {
      alert('Please select an option');
      return;
    }

    if (currentQuestionIdx < questions.length - 1) {
      setCurrentQuestionIdx(currentQuestionIdx + 1);
      setShowFeedback(false);
    } else {
      // Calculate score
      let score = 0;
      questions.forEach(q => {
        if (selectedAnswers[q.id] === q.answer) {
          score += 1;
        }
      });

      const session: QuizSession = {
        id: crypto.randomUUID(),
        noteId: note.id,
        score,
        totalQuestions: questions.length,
        timestamp: new Date().toISOString()
      };

      saveQuizSession(session);
      setFinalScore(score);
      setQuizFinished(true);
    }
  };

  const handleNextFlashcard = () => {
    if (currentFlashcardIdx < flashcards.length - 1) {
      setCurrentFlashcardIdx(currentFlashcardIdx + 1);
      setFlipped(false);
    }
  };

  const handlePrevFlashcard = () => {
    if (currentFlashcardIdx > 0) {
      setCurrentFlashcardIdx(currentFlashcardIdx - 1);
      setFlipped(false);
    }
  };

  if (quizFinished) {
    const scorePercentage = ((finalScore / questions.length) * 100).toFixed(0);
    return (
      <div className="max-w-2xl mx-auto glass-panel p-8 rounded-xl text-center space-y-6 animate-fade-in" data-testid="quiz-view">
        <h2 className="text-3xl font-extrabold text-white">Quiz Finished!</h2>
        <p className="text-slate-400">You completed the quiz for "{note.title}"</p>
        
        <div className="py-6">
          <div className="inline-block relative">
            <span className="text-6xl font-extrabold text-indigo-400">{scorePercentage}%</span>
            <div className="text-sm text-slate-500 mt-2">{finalScore} / {questions.length} Correct Answers</div>
          </div>
        </div>

        {/* Mastery rating updater prompt */}
        <div className="py-4 bg-[#151726]/40 rounded-xl p-4 border border-white/5 space-y-3">
          <p className="text-sm font-semibold text-slate-300">
            {finalScore === questions.length 
              ? 'Perfect score! Would you like to update the mastery rating?' 
              : 'Update the mastery rating for this note:'}
          </p>
          <div className="flex justify-center space-x-2">
            {[0, 1, 2, 3, 4, 5].map((num) => (
              <button
                key={num}
                onClick={() => handleUpdateMastery(num)}
                className={`w-9 h-9 rounded-lg font-bold transition-all border cursor-pointer ${
                  masteryRating === num
                    ? `mastery-bg-${num} scale-105 shadow-md`
                    : 'bg-[#090d16]/60 text-slate-400 border-white/5 hover:border-white/20'
                }`}
                data-testid={`mastery-btn-${num}`}
              >
                {num}
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-center gap-4 pt-4 border-t border-white/5">
          <button
            onClick={() => navigateTo('dashboard')}
            className="glass-button-primary cursor-pointer"
          >
            Go to Dashboard
          </button>
          <button
            onClick={() => navigateTo('notes-list')}
            className="glass-button-secondary cursor-pointer"
          >
            My Notes
          </button>
        </div>
      </div>
    );
  }

  const currentSelection = selectedAnswers[currentQuestion?.id] || null;

  return (
    <div className="max-w-2xl mx-auto glass-panel p-6 rounded-xl space-y-6 animate-fade-in" data-testid="quiz-or-flashcard-view">
      {/* Mode Switcher */}
      <div className="flex border-b border-white/5 pb-1 gap-4">
        <button
          onClick={() => setMode('quiz')}
          className={`pb-2 px-4 font-semibold text-sm cursor-pointer transition-all border-b-2 ${
            mode === 'quiz' ? 'border-indigo-500 text-white' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
          data-testid="mode-quiz-button"
        >
          Quiz Mode
        </button>
        <button
          onClick={() => setMode('flashcard')}
          className={`pb-2 px-4 font-semibold text-sm cursor-pointer transition-all border-b-2 ${
            mode === 'flashcard' ? 'border-indigo-500 text-white' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
          data-testid="mode-flashcards-button"
        >
          Flashcards
        </button>
      </div>

      {mode === 'quiz' ? (
        <div className="space-y-6" data-testid="quiz-view">
          {/* Header */}
          <div className="flex justify-between items-center pb-4 border-b border-white/5">
            <div>
              <h3 className="font-bold text-white text-lg">Quiz: {note.title}</h3>
              <p className="text-xs text-slate-400">Question {currentQuestionIdx + 1} of {questions.length}</p>
            </div>
            <button
              onClick={() => navigateTo('notes-list')}
              className="text-xs text-slate-400 hover:text-white underline cursor-pointer"
            >
              Exit Quiz
            </button>
          </div>

          {/* Question */}
          {currentQuestion && (
            <div className="space-y-6">
              <h4 className="text-lg font-semibold text-slate-100">{currentQuestion.question}</h4>
              
              <div className="flex flex-col gap-3">
                {currentQuestion.options.map((option, idx) => {
                  let buttonStyle = 'bg-[#151726]/40 text-slate-300 border-white/5 hover:border-indigo-500/30';
                  if (currentSelection === option) {
                    buttonStyle = 'bg-indigo-600/20 text-indigo-300 border-indigo-500/50 shadow-md';
                  }
                  
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelectOption(option)}
                      className={`w-full text-left p-4 rounded-xl font-medium transition-all border cursor-pointer ${buttonStyle}`}
                    >
                      {option}
                    </button>
                  );
                })}
              </div>

              {currentSelection && (
                <div data-testid="quiz-feedback" className={`p-4 rounded-xl text-sm font-semibold border ${
                  currentSelection === currentQuestion.answer
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                }`}>
                  {currentSelection === currentQuestion.answer
                    ? 'Correct!'
                    : `Incorrect. The correct answer is: ${currentQuestion.answer}`}
                </div>
              )}
            </div>
          )}

          {/* Nav Actions */}
          <div className="flex justify-end pt-6 border-t border-white/5">
            <button
              onClick={handleNext}
              disabled={!currentSelection}
              className={`glass-button-primary cursor-pointer ${!currentSelection ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {currentQuestionIdx < questions.length - 1 ? 'Next Question' : 'Finish Quiz'}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6" data-testid="flashcard-view">
          {/* Header */}
          <div className="flex justify-between items-center pb-4 border-b border-white/5">
            <div>
              <h3 className="font-bold text-white text-lg">Flashcards: {note.title}</h3>
              <p className="text-xs text-slate-400">Card {currentFlashcardIdx + 1} of {flashcards.length}</p>
            </div>
            <button
              onClick={() => navigateTo('notes-list')}
              className="text-xs text-slate-400 hover:text-white underline cursor-pointer"
            >
              Exit Flashcards
            </button>
          </div>

          {/* Card Element */}
          <div
            data-testid="flashcard-element"
            onClick={() => setFlipped(!flipped)}
            className="glass-panel p-12 text-center rounded-xl cursor-pointer hover:border-indigo-500/50 transition-all select-none min-h-[200px] flex flex-col justify-center items-center"
          >
            {!flipped ? (
              <div>
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Question / Front</span>
                <p className="text-xl font-semibold text-slate-100 mt-4">{flashcards[currentFlashcardIdx]?.front}</p>
                <p className="text-xs text-slate-500 mt-6">Click card to reveal answer</p>
              </div>
            ) : (
              <div>
                <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Answer / Back</span>
                <p className="text-xl font-semibold text-slate-100 mt-4" data-testid="flashcard-answer">{flashcards[currentFlashcardIdx]?.back}</p>
                <p className="text-xs text-slate-500 mt-6">Click card to hide answer</p>
              </div>
            )}
          </div>

          {/* Nav Actions */}
          <div className="flex justify-between pt-6 border-t border-white/5">
            <button
              onClick={handlePrevFlashcard}
              disabled={currentFlashcardIdx === 0}
              className={`glass-button-secondary cursor-pointer ${currentFlashcardIdx === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
              data-testid="prev-flashcard-button"
            >
              Previous Card
            </button>
            <button
              onClick={handleNextFlashcard}
              disabled={currentFlashcardIdx === flashcards.length - 1}
              className={`glass-button-primary cursor-pointer ${currentFlashcardIdx === flashcards.length - 1 ? 'opacity-50 cursor-not-allowed' : ''}`}
              data-testid="next-flashcard-button"
            >
              Next Card
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
