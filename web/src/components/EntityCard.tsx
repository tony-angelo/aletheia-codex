import React, { useState } from 'react';
import { EntityCardProps, ReviewItemType } from '../types/review';
import ConfidenceBadge from './ConfidenceBadge';

const EntityCard: React.FC<EntityCardProps> = ({ 
  entity, 
  onApprove, 
  onReject, 
  isSelected = false,
  onSelect 
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showRejectionForm, setShowRejectionForm] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  if (entity.type !== ReviewItemType.ENTITY) {
    return null;
  }

  const handleApprove = async () => {
    if (isProcessing) return;
    
    setIsProcessing(true);
    try {
      await onApprove(entity.id);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async (reason?: string) => {
    if (isProcessing) return;
    
    setIsProcessing(true);
    try {
      await onReject(entity.id, reason);
    } finally {
      setIsProcessing(false);
      setShowRejectionForm(false);
      setRejectionReason('');
    }
  };

  const handleRejectSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleReject(rejectionReason);
  };

  const entityData = entity.data as any;

  return (
    <div className={`card ${isSelected ? 'border-2 border-blue-500' : ''}`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {entityData.name || 'Unnamed Entity'}
          </h3>
          <p className="text-sm text-gray-600 mb-2">
            Type: <span className="font-medium">{entityData.type || 'Unknown'}</span>
          </p>
          {entityData.description && (
            <p className="text-sm text-gray-700 mb-2">
              {entityData.description}
            </p>
          )}
        </div>
        <div className="ml-4">
          <ConfidenceBadge confidence={entityData.confidence || 0} size="sm" />
        </div>
      </div>

      {entityData.source_reference && (
        <div className="text-sm text-gray-500 mb-4">
          <strong>Source:</strong> {entityData.source_reference}
        </div>
      )}

      <div className="text-xs text-gray-400 mb-4">
        ID: {entity.id} • Document: {entity.source_document_id}
      </div>

      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <button
            onClick={() => onSelect?.(entity.id)}
            className={`btn btn-outline text-sm ${
              isSelected ? 'bg-blue-50 border-blue-500 text-blue-700' : ''
            }`}
            disabled={isProcessing}
          >
            {isSelected ? '✓ Selected' : 'Select'}
          </button>
        </div>

        <div className="flex gap-2">
          {!showRejectionForm ? (
            <>
              <button
                onClick={handleApprove}
                className="btn btn-primary text-sm"
                disabled={isProcessing}
              >
                {isProcessing ? 'Processing...' : '✓ Approve'}
              </button>
              <button
                onClick={() => setShowRejectionForm(true)}
                className="btn btn-secondary text-sm"
                disabled={isProcessing}
              >
                ✗ Reject
              </button>
            </>
          ) : (
            <form onSubmit={handleRejectSubmit} className="flex gap-2">
              <input
                type="text"
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Rejection reason (optional)"
                className="border rounded px-2 py-1 text-sm flex-1"
                disabled={isProcessing}
              />
              <button
                type="submit"
                className="btn btn-danger text-sm"
                disabled={isProcessing}
              >
                {isProcessing ? 'Processing...' : 'Confirm'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowRejectionForm(false);
                  setRejectionReason('');
                }}
                className="btn btn-outline text-sm"
                disabled={isProcessing}
              >
                Cancel
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default EntityCard;