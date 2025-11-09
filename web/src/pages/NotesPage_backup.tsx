import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNotes } from '../hooks/useNotes';
import { useProcessing } from '../hooks/useProcessing';
import NoteInput from '../components/NoteInput';
import ProcessingStatus, { ProcessingStatusData } from '../components/ProcessingStatus';
import ExtractionResults from '../components/ExtractionResults';
import NoteHistory from '../components/NoteHistory';

const NotesPage: React.FC = () => {
  const { user } = useAuth();
  const { createNewNote } = useNotes();
  const { isProcessing, progress, error: processingError, processNote } = useProcessing();
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatusData | null>(null);
  const [extractionResults, setExtractionResults] = useState<{
    noteId: string;
    entities: any[];
    relationships: any[];
  } | null>(null);

  const handleNoteSubmit = async (content: string) => {
    if (!user) {
      console.error('User not authenticated');
      return;
    }

    try {
      // Create the note in Firestore
      const note = await createNewNote(content);

      // Initialize processing status
      setProcessingStatus({
        id: note.id,
        noteId: note.id,
        status: 'extracting',
        currentStep: 'Initializing AI extraction...',
        progress: 0,
        startedAt: new Date(),
        steps: {
          extraction: { status: 'processing' },
          review: { status: 'pending' },
          graphUpdate: { status: 'pending' },
        },
      });

      // Process the note through orchestration
      const result = await processNote(note.id, content, user.uid);

      if (result.success) {
        // Update final status
        setProcessingStatus(prev => prev ? {
          ...prev,
          status: 'completed',
          currentStep: 'Processing completed successfully',
          progress: 100,
          completedAt: new Date(),
          steps: {
            extraction: { status: 'completed', completedAt: new Date() },
            review: { status: 'completed', completedAt: new Date() },
            graphUpdate: { status: 'completed', completedAt: new Date() },
          },
        } : null);

        // Set extraction results if available
        if (result.extractionSummary) {
          setExtractionResults({
            noteId: note.id,
            entities: [], // Will be populated from review queue
            relationships: [],
          });
        }
      } else {
        // Update error status
        setProcessingStatus(prev => prev ? {
          ...prev,
          status: 'failed',
          currentStep: result.error || 'Processing failed',
          progress: 0,
          completedAt: new Date(),
          error: result.error,
          steps: {
            extraction: { status: 'failed', error: result.error },
            review: { status: 'pending' },
            graphUpdate: { status: 'pending' },
          },
        } : null);
      }
    } catch (error) {
      console.error('Error submitting note:', error);
      setProcessingStatus(prev => prev ? {
        ...prev,
        status: 'failed',
        currentStep: 'Failed to submit note',
        progress: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      } : null);
    }
  };

  // Update processing status based on progress
  React.useEffect(() => {
    if (progress && processingStatus) {
      setProcessingStatus(prev => {
        if (!prev) return null;

        const newStatus = { ...prev };
        newStatus.progress = progress.progress;
        newStatus.currentStep = progress.message;

        // Update step statuses based on current step
        if (progress.step === 'extraction') {
          newStatus.status = 'extracting';
          newStatus.steps.extraction.status = 'processing';
        } else if (progress.step === 'review') {
          newStatus.status = 'reviewing';
          newStatus.steps.extraction.status = 'completed';
          newStatus.steps.extraction.completedAt = new Date();
          newStatus.steps.review.status = 'processing';
        } else if (progress.step === 'graph_update') {
          newStatus.status = 'completed';
          newStatus.steps.review.status = 'completed';
          newStatus.steps.review.completedAt = new Date();
          newStatus.steps.graphUpdate.status = 'processing';
        }

        return newStatus;
      });
    }
  }, [progress, processingStatus]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Notes</h1>
          <p className="mt-2 text-gray-600">
            Capture your thoughts and let AI extract knowledge automatically
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Note Input */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">New Note</h2>
              <NoteInput
                onSubmit={handleNoteSubmit}
                disabled={isProcessing}
              />
            </div>

            {/* Processing Status */}
            {processingStatus && (
              <ProcessingStatus status={processingStatus} />
            )}

            {/* Extraction Results */}
            {extractionResults && (
              <ExtractionResults
                noteId={extractionResults.noteId}
                entities={extractionResults.entities}
                relationships={extractionResults.relationships}
              />
            )}

            {/* Error Display */}
            {processingError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Processing Error</h3>
                    <p className="mt-1 text-sm text-red-700">{processingError}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Recent Notes */}
            {user && <NoteHistory userId={user.uid} />}

            {/* Tips */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-2">💡 Tips</h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• Write naturally - AI understands context</li>
                <li>• Include names, dates, and relationships</li>
                <li>• Review extracted items before adding to graph</li>
                <li>• Notes are processed automatically</li>
              </ul>
            </div>

            {/* Stats */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Processing</span>
                  <span className="text-sm font-medium text-yellow-600">
                    {isProcessing ? '1' : '0'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Completed Today</span>
                  <span className="text-sm font-medium text-green-600">0</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotesPage;