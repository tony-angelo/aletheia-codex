

export interface ProcessingProgress {
  step: 'extraction' | 'review' | 'graph_update';
  progress: number; // 0-100
  message: string;
  startTime: number;
}

export interface ProcessingResult {
  success: boolean;
  noteId: string;
  extractionSummary?: {
    entityCount: number;
    relationshipCount: number;
  };
  error?: string;
}

export interface OrchestrationResponse {
  success: boolean;
  noteId: string;
  message: string;
  extractionSummary?: {
    entityCount: number;
    relationshipCount: number;
  };
  error?: string;
}

class OrchestrationService {
  private baseUrl: string;

  constructor() {
    // Use environment variable or default to local development
    this.baseUrl = process.env.REACT_APP_ORCHESTRATION_URL || 
                   'https://us-central1-aletheia-codex.cloudfunctions.net/orchestration';
  }

  /**
   * Process a note through the AI extraction pipeline
   */
  async processNote(
    noteId: string,
    content: string,
    userId: string,
    onProgress?: (progress: ProcessingProgress) => void
  ): Promise<ProcessingResult> {
    try {
      // Simulate progress updates for now
      // In production, this would use Server-Sent Events or WebSockets
      if (onProgress) {
        onProgress({
          step: 'extraction',
          progress: 10,
          message: 'Starting AI extraction...',
          startTime: Date.now()
        });
      }

      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          noteId,
          content,
          userId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: OrchestrationResponse = await response.json();

      if (onProgress) {
        onProgress({
          step: 'review',
          progress: 60,
          message: 'Adding items to review queue...',
          startTime: Date.now()
        });
      }

      // Simulate final progress update
      if (onProgress) {
        onProgress({
          step: 'graph_update',
          progress: 100,
          message: 'Processing complete!',
          startTime: Date.now()
        });
      }

      return {
        success: data.success,
        noteId: data.noteId,
        extractionSummary: data.extractionSummary,
        error: data.error,
      };
    } catch (error) {
      console.error('Error processing note:', error);
      
      return {
        success: false,
        noteId,
        error: error instanceof Error ? error.message : 'Failed to process note',
      };
    }
  }

  /**
   * Get the status of a processing job
   * (For future implementation with job tracking)
   */
  async getProcessingStatus(noteId: string): Promise<ProcessingProgress | null> {
    try {
      const response = await fetch(`${this.baseUrl}/status/${noteId}`);
      
      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting processing status:', error);
      return null;
    }
  }

  /**
   * Cancel a processing job
   * (For future implementation)
   */
  async cancelProcessing(noteId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/cancel/${noteId}`, {
        method: 'POST',
      });

      return response.ok;
    } catch (error) {
      console.error('Error canceling processing:', error);
      return false;
    }
  }
}

// Export singleton instance
export const orchestrationService = new OrchestrationService();
export default orchestrationService;