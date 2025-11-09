import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Note } from '../services/notes';

interface NoteCardProps {
  note: Note;
  onDelete?: (noteId: string) => Promise<void>;
  isSelected?: boolean;
  onSelect?: (noteId: string) => void;
  showSelection?: boolean;
}

const NoteCard: React.FC<NoteCardProps> = ({ 
  note, 
  onDelete, 
  isSelected = false, 
  onSelect,
  showSelection = false 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing':
        return 'text-blue-600 bg-blue-50';
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return (
          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      case 'completed':
        return (
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    
    if (!onDelete || isDeleting) return;
    
    const confirmed = window.confirm('Are you sure you want to delete this note?');
    if (!confirmed) return;
    
    setIsDeleting(true);
    try {
      await onDelete(note.id);
    } catch (error) {
      console.error('Failed to delete note:', error);
      setIsDeleting(false);
    }
  };

  const handleSelect = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (onSelect) {
      onSelect(note.id);
    }
  };

  const handleToggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    setIsExpanded(!isExpanded);
  };

  const formatDate = (timestamp: any) => {
    if (!timestamp) return '';
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const truncateContent = (content: string, maxLength: number = 150) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  return (
    <div className={`bg-white border rounded-lg p-4 hover:shadow-md transition-shadow ${isSelected ? 'ring-2 ring-blue-500' : 'border-gray-200'}`}>
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            {/* Selection checkbox */}
            {showSelection && onSelect && (
              <button
                onClick={handleSelect}
                className="flex-shrink-0 w-5 h-5 border-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{
                  backgroundColor: isSelected ? '#3B82F6' : 'transparent',
                  borderColor: isSelected ? '#3B82F6' : '#D1D5DB'
                }}
              >
                {isSelected && (
                  <svg className="w-full h-full text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            )}

            {/* Status */}
            <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(note.status)}`}>
              {getStatusIcon(note.status)}
              <span>{note.status.charAt(0).toUpperCase() + note.status.slice(1)}</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2">
            {onDelete && (
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="text-gray-400 hover:text-red-500 focus:outline-none disabled:opacity-50"
                title="Delete note"
              >
                {isDeleting ? (
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="space-y-2">
          <p className="text-gray-900 text-sm leading-relaxed">
            {isExpanded ? note.content : truncateContent(note.content)}
          </p>

          {note.content.length > 150 && (
            <button
              onClick={handleToggleExpand}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium focus:outline-none"
            >
              {isExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>

        {/* Metadata */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{formatDate(note.createdAt)}</span>
            <span>Source: {note.metadata.source}</span>
          </div>

          {/* Extraction summary */}
          {note.extractionSummary && (
            <div className="flex items-center space-x-4 text-xs">
              <span className="text-gray-600">
                🏷️ {note.extractionSummary.entityCount} entities
              </span>
              <span className="text-gray-600">
                🔗 {note.extractionSummary.relationshipCount} relationships
              </span>
            </div>
          )}

          {/* Error message */}
          {note.error && (
            <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
              <strong>Error:</strong> {note.error}
            </div>
          )}
        </div>

        {/* Link to review queue (if completed) */}
        {note.status === 'completed' && note.extractionSummary && (
          <div className="pt-2 border-t border-gray-100">
            <Link
              to={`/review?noteId=${note.id}`}
              className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              <svg className="mr-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
              View extracted items
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default NoteCard;