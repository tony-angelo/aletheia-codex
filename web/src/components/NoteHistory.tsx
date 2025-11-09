import React, { useState, useEffect } from 'react';
import { Note } from '../services/notes';
import { subscribeToUserNotes, getUserNoteStats } from '../services/notes';
import NoteCard from './NoteCard';

interface NoteHistoryProps {
  userId: string;
  onNoteSelect?: (noteId: string) => void;
  selectedNotes?: Set<string>;
  showSelection?: boolean;
  onNoteDelete?: (noteId: string) => Promise<void>;
}

interface UserStats {
  total: number;
  processing: number;
  completed: number;
  failed: number;
}

const NoteHistory: React.FC<NoteHistoryProps> = ({
  userId,
  onNoteSelect,
  selectedNotes = new Set(),
  showSelection = false,
  onNoteDelete
}) => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'processing' | 'completed' | 'failed'>('all');
  const [stats, setStats] = useState<UserStats | null>(null);

  useEffect(() => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    // Subscribe to real-time updates
    const unsubscribe = subscribeToUserNotes(
      userId,
      (updatedNotes) => {
        setNotes(updatedNotes);
        setLoading(false);
      },
      {
        limit: 50,
        status: filter === 'all' ? undefined : filter,
        orderBy: 'createdAt',
        orderDirection: 'desc'
      }
    );

    // Load stats
    const loadStats = async () => {
      try {
        const userStats = await getUserNoteStats(userId);
        setStats(userStats);
      } catch (err) {
        console.error('Failed to load stats:', err);
      }
    };

    loadStats();

    return () => unsubscribe();
  }, [userId, filter]);

  const handleFilterChange = (newFilter: typeof filter) => {
    setFilter(newFilter);
  };

  const handleNoteSelect = (noteId: string) => {
    if (onNoteSelect) {
      onNoteSelect(noteId);
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleNoteDelete = async (noteId: string) => {
    if (onNoteDelete) {
      await onNoteDelete(noteId);
    }
  };

  const getFilteredNotesCount = () => {
    if (filter === 'all') return notes.length;
    return notes.filter(note => note.status === filter).length;
  };

  const getFilterButtonClass = (filterType: typeof filter) => {
    const baseClass = "px-3 py-1 text-sm font-medium rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
    
    if (filter === filterType) {
      return `${baseClass} bg-blue-100 text-blue-800 focus:ring-blue-500`;
    }
    
    return `${baseClass} bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-500`;
  };

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-2 text-gray-600">Loading notes...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error loading notes</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium text-gray-900">Recent Notes</h2>
          <span className="text-sm text-gray-500">
            {getFilteredNotesCount()} notes
          </span>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">{stats.total}</div>
              <div className="text-gray-600">Total</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-blue-600">{stats.processing}</div>
              <div className="text-gray-600">Processing</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-green-600">{stats.completed}</div>
              <div className="text-gray-600">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-red-600">{stats.failed}</div>
              <div className="text-gray-600">Failed</div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleFilterChange('all')}
            className={getFilterButtonClass('all')}
          >
            All ({stats?.total || 0})
          </button>
          <button
            onClick={() => handleFilterChange('processing')}
            className={getFilterButtonClass('processing')}
          >
            Processing ({stats?.processing || 0})
          </button>
          <button
            onClick={() => handleFilterChange('completed')}
            className={getFilterButtonClass('completed')}
          >
            Completed ({stats?.completed || 0})
          </button>
          <button
            onClick={() => handleFilterChange('failed')}
            className={getFilterButtonClass('failed')}
          >
            Failed ({stats?.failed || 0})
          </button>
        </div>
      </div>

      {/* Notes List */}
      <div className="space-y-4">
        {notes.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-sm font-medium">No notes found</p>
            <p className="text-xs mt-1">
              {filter === 'all' 
                ? "Start by creating your first note above" 
                : `No notes with status "${filter}"`
              }
            </p>
          </div>
        ) : (
          <>
            {notes.map((note) => (
              <NoteCard
                key={note.id}
                note={note}
                onDelete={onNoteDelete}
                isSelected={selectedNotes.has(note.id)}
                onSelect={handleNoteSelect}
                showSelection={showSelection}
              />
            ))}
            
            {/* Load more indicator */}
            {notes.length >= 50 && (
              <div className="text-center py-4">
                <p className="text-sm text-gray-500">
                  Showing the most recent 50 notes
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default NoteHistory;