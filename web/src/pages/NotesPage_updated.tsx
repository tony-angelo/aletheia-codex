import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNotes } from '../hooks/useNotes';
import NoteInput from '../components/features/notes/NoteInput';
import ProcessingStatus, { ProcessingStatusData } from '../components/features/notes/ProcessingStatus';
import ExtractionResults from '../components/features/review/ExtractionResults';
import NoteHistory from '../components/features/notes/NoteHistory';

const NotesPage: React.FC = () => {
  const { user } = useAuth();
  const { createNewNote } = useNotes();
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
      console.log('=== Note Submission Started ===');
      console.log('User:', user.uid);
      console.log('Content length:', content.length);
      
      // Create the note in Firestore
      // The Firestore trigger will automatically process it
      const note = await createNewNote(content);
      
      console.log('✓ Note created:', note.id);
      console.log('Note will be processed automatically by Firestore trigger');

      // Initialize processing status
      setProcessingStatus({
        id: note.id,
        noteId: note.id,
        status: 'extracting',
        currentStep: 'Note submitted - AI extraction in progress...',
        progress: 25,
        startedAt: new Date(),
        steps: {
          extraction: { status: 'processing' },
          review: { status: 'pending' },
          graphUpdate: { status: 'pending' },
        },
      });
      
      console.log('✓ Processing status initialized');
      console.log('Note will be processed by orchestration function automatically');
      
      // Note: The orchestration function will now process this automatically
      // via Firestore trigger. No need to call HTTP endpoint.
      
    } catch (error) {
      console.error('=== Note Submission Failed ===');
      console.error('Error:', error);
      setProcessingStatus(prev => prev ? {
        ...prev,
        status: 'failed',
        currentStep: 'Failed to submit note',
        progress: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      } : null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Capture Your Knowledge
        </h1>
        <p className="text-gray-600">
          Write notes about people, places, and ideas. Our AI will extract entities and relationships automatically.
        </p>
      </div>

      {/* Note Input */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          New Note
        </h2>
        <NoteInput 
          onSubmit={handleNoteSubmit}
          disabled={!user}
        />
        {!user && (
          <p className="mt-4 text-sm text-gray-500">
            Please sign in to submit notes
          </p>
        )}
      </div>

      {/* Processing Status */}
      {processingStatus && (
        <div className="mb-8">
          <ProcessingStatus status={processingStatus} />
        </div>
      )}

      {/* Extraction Results */}
      {extractionResults && (
        <div className="mb-8">
          <ExtractionResults
            noteId={extractionResults.noteId}
            entities={extractionResults.entities}
            relationships={extractionResults.relationships}
          />
        </div>
      )}

      {/* Note History */}
      {user && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Your Notes
          </h2>
          <NoteHistory userId={user.uid} />
        </div>
      )}
    </div>
  );
};

export default NotesPage;