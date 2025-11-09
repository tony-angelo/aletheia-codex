import React, { useState, useRef, useEffect } from 'react';

interface NoteInputProps {
  onSubmit: (content: string) => Promise<void>;
  disabled?: boolean;
}

const NoteInput: React.FC<NoteInputProps> = ({ onSubmit, disabled = false }) => {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const MAX_CHARS = 10000;

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 400)}px`;
    }
  }, [content]);

  // Update character count
  useEffect(() => {
    setCharCount(content.length);
  }, [content]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim() || content.length > MAX_CHARS || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(content.trim());
      setContent('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch (error) {
      console.error('Failed to submit note:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClear = () => {
    setContent('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isSubmitDisabled = !content.trim() || content.length > MAX_CHARS || isSubmitting || disabled;
  const isClearDisabled = !content.trim() || isSubmitting;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your note here... (Press Ctrl+Enter or Cmd+Enter to submit)"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
          style={{ minHeight: '120px', maxHeight: '400px' }}
          disabled={isSubmitting || disabled}
          rows={4}
        />
        
        {/* Character count */}
        <div className="absolute bottom-2 right-2 text-xs text-gray-500">
          <span className={charCount > MAX_CHARS * 0.9 ? 'text-orange-500' : ''}>
            {charCount}/{MAX_CHARS}
          </span>
        </div>
      </div>

      {/* Character warning */}
      {charCount > MAX_CHARS * 0.9 && (
        <div className="text-sm text-orange-600">
          {charCount > MAX_CHARS 
            ? `Note exceeds maximum length by ${charCount - MAX_CHARS} characters`
            : `Note approaching maximum length (${Math.round(charCount / MAX_CHARS * 100)}%)`
          }
        </div>
      )}

      {/* Action buttons */}
      <div className="flex justify-between items-center">
        <button
          type="button"
          onClick={handleClear}
          disabled={isClearDisabled}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Clear
        </button>

        <div className="flex items-center space-x-3">
          <span className="text-xs text-gray-500">
            Tip: Press Ctrl+Enter or Cmd+Enter to submit
          </span>
          <button
            type="submit"
            disabled={isSubmitDisabled}
            className="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Submitting...
              </span>
            ) : (
              'Submit Note'
            )}
          </button>
        </div>
      </div>
    </form>
  );
};

export default NoteInput;