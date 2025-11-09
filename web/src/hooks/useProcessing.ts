import { useState, useCallback } from 'react';
import { Timestamp } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { orchestrationService, ProcessingProgress, ProcessingResult } from '../services/orchestration';
import { updateNoteStatus } from '../services/notes';

interface UseProcessingReturn {
  isProcessing: boolean;
  progress: ProcessingProgress | null;
  error: string | null;
  processNote: (noteId: string, content: string, userId: string) => Promise<ProcessingResult>;
  cancelProcessing: () => Promise<void>;
  clearError: () => void;
}

export const useProcessing = (): UseProcessingReturn => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState<ProcessingProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentNoteId, setCurrentNoteId] = useState<string | null>(null);

  const processNote = useCallback(async (
    noteId: string,
    content: string,
    userId: string
  ): Promise<ProcessingResult> => {
    try {
      setIsProcessing(true);
      setError(null);
      setCurrentNoteId(noteId);
      setProgress({
        step: 'extraction',
        progress: 0,
        message: 'Initializing...',
        startTime: Date.now()
      });

      // Get Firebase Auth token
      const auth = getAuth();
      const user = auth.currentUser;
      if (!user) {
        throw new Error('User not authenticated');
      }
      const authToken = await user.getIdToken();

      // Update note status to processing
      await updateNoteStatus(noteId, {
        status: 'processing',
        processingStartedAt: Timestamp.now(),
      });

      // Process the note with progress updates
      const result = await orchestrationService.processNote(
        noteId,
        content,
        userId,
        authToken,
        (progressUpdate) => {
          setProgress(progressUpdate);
        }
      );

      if (result.success) {
        // Update note status to completed
        await updateNoteStatus(noteId, {
          status: 'completed',
          processingCompletedAt: Timestamp.now(),
          extractionSummary: result.extractionSummary,
        });

        setProgress({
          step: 'graph_update',
          progress: 100,
          message: 'Processing complete!',
          startTime: Date.now()
        });
      } else {
        // Update note status to failed
        await updateNoteStatus(noteId, {
          status: 'failed',
          processingCompletedAt: Timestamp.now(),
          error: result.error,
        });

        setError(result.error || 'Processing failed');
      }

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process note';
      setError(errorMessage);
      
      // Update note status to failed
      if (noteId) {
        await updateNoteStatus(noteId, {
          status: 'failed',
          processingCompletedAt: Timestamp.now(),
          error: errorMessage,
        });
      }

      return {
        success: false,
        noteId,
        error: errorMessage,
      };
    } finally {
      setIsProcessing(false);
      setCurrentNoteId(null);
    }
  }, []);

  const cancelProcessing = useCallback(async () => {
    if (currentNoteId) {
      await orchestrationService.cancelProcessing(currentNoteId);
      setIsProcessing(false);
      setProgress(null);
      setCurrentNoteId(null);
    }
  }, [currentNoteId]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isProcessing,
    progress,
    error,
    processNote,
    cancelProcessing,
    clearError,
  };
};

export default useProcessing;