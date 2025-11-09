import React from 'react';

export type ProcessingStep = 'queued' | 'extracting' | 'reviewing' | 'completed' | 'failed';

export interface ProcessingStatusData {
  id: string;
  noteId: string;
  status: ProcessingStep;
  currentStep: string;
  progress: number;
  startedAt: Date;
  completedAt?: Date;
  error?: string;
  steps: {
    extraction: { status: string; completedAt?: Date };
    review: { status: string; completedAt?: Date };
    graphUpdate: { status: string; completedAt?: Date };
  };
}

interface ProcessingStatusProps {
  status: ProcessingStatusData | null;
  onCancel?: () => void;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ status, onCancel }) => {
  if (!status) {
    return null;
  }

  const getStatusColor = (step: ProcessingStep) => {
    switch (step) {
      case 'queued':
        return 'text-gray-600';
      case 'extracting':
        return 'text-blue-600';
      case 'reviewing':
        return 'text-yellow-600';
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 100) return 'bg-green-500';
    if (progress >= 66) return 'bg-blue-500';
    if (progress >= 33) return 'bg-yellow-500';
    return 'bg-gray-300';
  };

  const getStepIcon = (stepStatus: string, isCompleted: boolean) => {
    if (isCompleted) {
      return (
        <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    }
    if (stepStatus === 'processing') {
      return (
        <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      );
    }
    return (
      <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
      </svg>
    );
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const getElapsedTime = () => {
    const start = status.startedAt.getTime();
    const end = status.completedAt?.getTime() || Date.now();
    const elapsed = Math.round((end - start) / 1000);
    
    if (elapsed < 60) return `${elapsed}s`;
    if (elapsed < 3600) return `${Math.round(elapsed / 60)}m ${elapsed % 60}s`;
    return `${Math.round(elapsed / 3600)}h ${Math.round((elapsed % 3600) / 60)}m`;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Processing Status</h3>
          <p className={`text-sm ${getStatusColor(status.status)}`}>
            Status: {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Elapsed time</p>
          <p className="text-sm font-medium text-gray-900">{getElapsedTime()}</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div>
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{status.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(status.progress)}`}
            style={{ width: `${status.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Current Step */}
      <div>
        <p className="text-sm text-gray-600 mb-2">Current Step:</p>
        <p className="text-sm font-medium text-gray-900">{status.currentStep}</p>
      </div>

      {/* Processing Steps */}
      <div className="space-y-3">
        <p className="text-sm text-gray-600">Processing Steps:</p>
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            {getStepIcon(status.steps.extraction.status, !!status.steps.extraction.completedAt)}
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Entity & Relationship Extraction</p>
              <p className="text-xs text-gray-500">
                {status.steps.extraction.completedAt 
                  ? `Completed at ${formatTime(status.steps.extraction.completedAt)}`
                  : status.steps.extraction.status === 'processing' 
                    ? 'Processing with AI...'
                    : 'Pending'
                }
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {getStepIcon(status.steps.review.status, !!status.steps.review.completedAt)}
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Review Queue Preparation</p>
              <p className="text-xs text-gray-500">
                {status.steps.review.completedAt
                  ? `Completed at ${formatTime(status.steps.review.completedAt)}`
                  : status.steps.review.status === 'processing'
                    ? 'Preparing review items...'
                    : 'Pending'
                }
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {getStepIcon(status.steps.graphUpdate.status, !!status.steps.graphUpdate.completedAt)}
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Knowledge Graph Update</p>
              <p className="text-xs text-gray-500">
                {status.steps.graphUpdate.completedAt
                  ? `Completed at ${formatTime(status.steps.graphUpdate.completedAt)}`
                  : status.steps.graphUpdate.status === 'processing'
                    ? 'Updating knowledge graph...'
                    : 'Pending'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {status.error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Processing Error</h3>
              <p className="mt-1 text-sm text-red-700">{status.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between items-center pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-500">
          Started at {formatTime(status.startedAt)}
          {status.completedAt && (
            <span> • Completed at {formatTime(status.completedAt)}</span>
          )}
        </div>
        {status.status === 'extracting' && onCancel && (
          <button
            onClick={onCancel}
            className="px-3 py-1 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Cancel Processing
          </button>
        )}
      </div>
    </div>
  );
};

export default ProcessingStatus;