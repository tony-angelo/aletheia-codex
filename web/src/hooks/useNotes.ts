import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';
import { 
  Note, 
  createNote, 
  getUserNotes, 
  updateNoteStatus, 
  deleteNote,
  subscribeToUserNotes,
  getUserNoteStats
} from '../services/notes';

interface UseNotesOptions {
  limit?: number;
  autoRefresh?: boolean;
  filterByStatus?: 'processing' | 'completed' | 'failed';
}

interface UseNotesReturn {
  notes: Note[];
  loading: boolean;
  error: string | null;
  stats: {
    total: number;
    processing: number;
    completed: number;
    failed: number;
  } | null;
  createNewNote: (content: string) => Promise<Note>;
  updateNote: (noteId: string, data: Partial<Note>) => Promise<void>;
  deleteNoteById: (noteId: string) => Promise<void>;
  refreshNotes: () => Promise<void>;
  clearError: () => void;
}

export const useNotes = (options: UseNotesOptions = {}): UseNotesReturn => {
  const { user } = useAuth();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<UseNotesReturn['stats']>(null);

  const {
    limit = 50,
    autoRefresh = true,
    filterByStatus
  } = options;

  // Load user's notes
  const loadNotes = useCallback(async () => {
    if (!user) {
      setNotes([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const userNotes = await getUserNotes(user.uid, {
        limit,
        status: filterByStatus,
        orderBy: 'createdAt',
        orderDirection: 'desc'
      });

      setNotes(userNotes);

      // Load stats
      const userStats = await getUserNoteStats(user.uid);
      setStats(userStats);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load notes';
      setError(errorMessage);
      console.error('Error loading notes:', err);
    } finally {
      setLoading(false);
    }
  }, [user, limit, filterByStatus]);

  // Set up real-time subscription
  useEffect(() => {
    if (!user || !autoRefresh) {
      return;
    }

    const unsubscribe = subscribeToUserNotes(
      user.uid,
      (updatedNotes) => {
        setNotes(updatedNotes);
      },
      {
        limit,
        status: filterByStatus,
        orderBy: 'createdAt',
        orderDirection: 'desc'
      }
    );

    // Load stats
    const loadStats = async () => {
      try {
        const userStats = await getUserNoteStats(user.uid);
        setStats(userStats);
      } catch (err) {
        console.error('Failed to load stats:', err);
      }
    };

    loadStats();

    return () => unsubscribe();
  }, [user, limit, filterByStatus, autoRefresh]);

  // Create a new note
  const createNewNote = useCallback(async (content: string): Promise<Note> => {
    if (!user) {
      throw new Error('User not authenticated');
    }

    try {
      setError(null);

      const noteData = {
        userId: user.uid,
        content,
        metadata: {
          source: 'web' as const,
          userAgent: navigator.userAgent,
          // IP address would need to be collected server-side
        }
      };

      const newNote = await createNote(noteData);
      
      // Add to local state immediately for optimistic updates
      setNotes(prev => [newNote, ...prev]);
      
      return newNote;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create note';
      setError(errorMessage);
      console.error('Error creating note:', err);
      throw err;
    }
  }, [user]);

  // Update a note
  const updateNote = useCallback(async (noteId: string, data: Partial<Note>) => {
    try {
      setError(null);

      const updateData: any = {};
      
      if (data.status) {
        updateData.status = data.status;
      }
      if (data.processingStartedAt) {
        updateData.processingStartedAt = data.processingStartedAt;
      }
      if (data.processingCompletedAt) {
        updateData.processingCompletedAt = data.processingCompletedAt;
      }
      if (data.error !== undefined) {
        updateData.error = data.error;
      }
      if (data.extractionSummary) {
        updateData.extractionSummary = data.extractionSummary;
      }

      await updateNoteStatus(noteId, updateData);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update note';
      setError(errorMessage);
      console.error('Error updating note:', err);
      throw err;
    }
  }, []);

  // Delete a note
  const deleteNoteById = useCallback(async (noteId: string) => {
    try {
      setError(null);

      await deleteNote(noteId);
      
      // Remove from local state for optimistic updates
      setNotes(prev => prev.filter(note => note.id !== noteId));

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete note';
      setError(errorMessage);
      console.error('Error deleting note:', err);
      throw err;
    }
  }, []);

  // Refresh notes manually
  const refreshNotes = useCallback(async () => {
    await loadNotes();
  }, [loadNotes]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    notes,
    loading,
    error,
    stats,
    createNewNote,
    updateNote,
    deleteNoteById,
    refreshNotes,
    clearError
  };
};

export default useNotes;