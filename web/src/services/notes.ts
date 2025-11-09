import { collection, doc, addDoc, updateDoc, deleteDoc, getDocs, getDoc, query, where, orderBy, limit, onSnapshot, Timestamp } from 'firebase/firestore';
import { db } from '../firebase/config';

export interface Note {
  id: string;
  userId: string;
  content: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  status: 'processing' | 'completed' | 'failed';
  processingStartedAt?: Timestamp;
  processingCompletedAt?: Timestamp;
  error?: string;
  extractionSummary?: {
    entityCount: number;
    relationshipCount: number;
  };
  metadata: {
    source: 'web' | 'api';
    ipAddress?: string;
    userAgent?: string;
  };
}

export interface CreateNoteRequest {
  userId: string;
  content: string;
  source?: 'web' | 'api';
  metadata?: {
    ipAddress?: string;
    userAgent?: string;
  };
}

export interface UpdateNoteRequest {
  status?: 'processing' | 'completed' | 'failed';
  processingStartedAt?: Timestamp;
  processingCompletedAt?: Timestamp;
  error?: string;
  extractionSummary?: {
    entityCount: number;
    relationshipCount: number;
  };
}

const COLLECTION_NAME = 'notes';

class NotesService {
  /**
   * Create a new note
   */
  async createNote(request: CreateNoteRequest): Promise<Note> {
    const now = Timestamp.now();
    const noteData = {
      userId: request.userId,
      content: request.content,
      createdAt: now,
      updatedAt: now,
      status: 'processing' as const,
      metadata: {
        source: request.source || 'web',
        ...request.metadata,
      },
    };

    const docRef = await addDoc(collection(db, COLLECTION_NAME), noteData);
    
    return {
      id: docRef.id,
      ...noteData,
    } as Note;
  }

  /**
   * Get all notes for a user
   */
  async getUserNotes(
    userId: string, 
    options?: {
      limit?: number;
      status?: 'processing' | 'completed' | 'failed';
      orderBy?: 'createdAt' | 'updatedAt';
      orderDirection?: 'asc' | 'desc';
    }
  ): Promise<Note[]> {
    const constraints: any[] = [where('userId', '==', userId)];
    
    if (options?.status) {
      constraints.push(where('status', '==', options.status));
    }
    
    constraints.push(orderBy(options?.orderBy || 'createdAt', options?.orderDirection || 'desc'));
    
    if (options?.limit) {
      constraints.push(limit(options.limit));
    }

    const q = query(collection(db, COLLECTION_NAME), ...constraints);
    const querySnapshot = await getDocs(q);
    
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
    })) as Note[];
  }

  /**
   * Get a single note by ID
   */
  async getNote(noteId: string): Promise<Note | null> {
    const docRef = doc(db, COLLECTION_NAME, noteId);
    const docSnap = await getDoc(docRef);
    
    if (docSnap.exists()) {
      return {
        id: docSnap.id,
        ...docSnap.data(),
      } as Note;
    }
    
    return null;
  }

  /**
   * Update a note
   */
  async updateNote(noteId: string, request: UpdateNoteRequest): Promise<void> {
    const docRef = doc(db, COLLECTION_NAME, noteId);
    const updateData = {
      ...request,
      updatedAt: Timestamp.now(),
    };
    
    await updateDoc(docRef, updateData);
  }

  /**
   * Delete a note
   */
  async deleteNote(noteId: string): Promise<void> {
    const docRef = doc(db, COLLECTION_NAME, noteId);
    await deleteDoc(docRef);
  }

  /**
   * Subscribe to real-time updates for a user's notes
   */
  subscribeToUserNotes(
    userId: string,
    callback: (notes: Note[]) => void,
    options?: {
      limit?: number;
      status?: 'processing' | 'completed' | 'failed';
      orderBy?: 'createdAt' | 'updatedAt';
      orderDirection?: 'asc' | 'desc';
    }
  ): () => void {
    const constraints: any[] = [where('userId', '==', userId)];
    
    if (options?.status) {
      constraints.push(where('status', '==', options.status));
    }
    
    constraints.push(orderBy(options?.orderBy || 'createdAt', options?.orderDirection || 'desc'));
    
    if (options?.limit) {
      constraints.push(limit(options.limit));
    }

    const q = query(collection(db, COLLECTION_NAME), ...constraints);
    
    return onSnapshot(q, (querySnapshot) => {
      const notes = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
      })) as Note[];
      callback(notes);
    });
  }

  /**
   * Subscribe to real-time updates for a single note
   */
  subscribeToNote(
    noteId: string,
    callback: (note: Note | null) => void
  ): () => void {
    const docRef = doc(db, COLLECTION_NAME, noteId);
    
    return onSnapshot(docRef, (docSnap) => {
      if (docSnap.exists()) {
        callback({
          id: docSnap.id,
          ...docSnap.data(),
        } as Note);
      } else {
        callback(null);
      }
    });
  }

  /**
   * Get statistics for a user's notes
   */
  async getUserNoteStats(userId: string): Promise<{
    total: number;
    processing: number;
    completed: number;
    failed: number;
    totalEntities: number;
    totalRelationships: number;
  }> {
    const notes = await this.getUserNotes(userId);
    
    return notes.reduce(
      (stats, note) => ({
        total: stats.total + 1,
        processing: stats.processing + (note.status === 'processing' ? 1 : 0),
        completed: stats.completed + (note.status === 'completed' ? 1 : 0),
        failed: stats.failed + (note.status === 'failed' ? 1 : 0),
        totalEntities: stats.totalEntities + (note.extractionSummary?.entityCount || 0),
        totalRelationships: stats.totalRelationships + (note.extractionSummary?.relationshipCount || 0),
      }),
      {
        total: 0,
        processing: 0,
        completed: 0,
        failed: 0,
        totalEntities: 0,
        totalRelationships: 0,
      }
    );
  }
}

// Export singleton instance
export const notesService = new NotesService();
export default notesService;

// Export individual functions for easier import
export const createNote = notesService.createNote.bind(notesService);
export const getNote = notesService.getNote.bind(notesService);
export const getUserNotes = notesService.getUserNotes.bind(notesService);
export const updateNoteStatus = notesService.updateNote.bind(notesService);
export const deleteNote = notesService.deleteNote.bind(notesService);
export const subscribeToUserNotes = notesService.subscribeToUserNotes.bind(notesService);
export const subscribeToNote = notesService.subscribeToNote.bind(notesService);
export const getUserNoteStats = notesService.getUserNoteStats.bind(notesService);