import React, { useState } from 'react';
import { useApproval } from '../hooks/useApproval';

interface BatchActionsProps {
  selectedItems: Set<string>;
  onActionComplete: () => void;
}

const BatchActions: React.FC<BatchActionsProps> = ({ 
  selectedItems, 
  onActionComplete 
}) => {
  const { batchApprove, batchReject, processing, error, clearError } = useApproval({
    onSuccess: () => {
      onActionComplete();
    },
    onError: (errorMessage) => {
      console.error('Batch action failed:', errorMessage);
    }
  });

  const [showRejectForm, setShowRejectForm] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  const handleBatchApprove = async () => {
    if (selectedItems.size === 0) return;
    
    const itemIds = Array.from(selectedItems);
    const result = await batchApprove(itemIds);
    
    if (result) {
      console.log(`Batch approve completed: ${result.successful_items}/${result.total_items} successful`);
    }
  };

  const handleBatchReject = async (reason?: string) => {
    if (selectedItems.size === 0) return;
    
    const itemIds = Array.from(selectedItems);
    const result = await batchReject(itemIds, reason);
    
    if (result) {
      console.log(`Batch reject completed: ${result.successful_items}/${result.total_items} successful`);
      setShowRejectForm(false);
      setRejectReason('');
    }
  };

  const handleRejectSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleBatchReject(rejectReason);
  };

  if (selectedItems.size === 0) {
    return null;
  }

  return (
    <div className="card bg-yellow-50 border-yellow-200 sticky bottom-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-yellow-900">
            Batch Actions
          </h3>
          <p className="text-sm text-yellow-700">
            {selectedItems.size} item{selectedItems.size !== 1 ? 's' : ''} selected
          </p>
        </div>

        {!showRejectForm ? (
          <div className="flex gap-2">
            <button
              onClick={handleBatchApprove}
              className="btn btn-primary"
              disabled={processing}
            >
              {processing ? 'Processing...' : `✓ Approve All (${selectedItems.size})`}
            </button>
            <button
              onClick={() => setShowRejectForm(true)}
              className="btn btn-secondary"
              disabled={processing}
            >
              {processing ? 'Processing...' : `✗ Reject All (${selectedItems.size})`}
            </button>
          </div>
        ) : (
          <form onSubmit={handleRejectSubmit} className="flex gap-2 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rejection Reason (optional)
              </label>
              <input
                type="text"
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Enter reason for batch rejection"
                className="w-full border rounded px-3 py-2"
                disabled={processing}
              />
            </div>
            <button
              type="submit"
              className="btn btn-danger"
              disabled={processing}
            >
              {processing ? 'Processing...' : 'Confirm Reject'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowRejectForm(false);
                setRejectReason('');
              }}
              className="btn btn-outline"
              disabled={processing}
            >
              Cancel
            </button>
          </form>
        )}
      </div>

      {error && (
        <div className="error mt-4">
          <strong>Error:</strong> {error}
          <button
            onClick={clearError}
            className="ml-2 btn btn-outline text-sm"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};

export default BatchActions;