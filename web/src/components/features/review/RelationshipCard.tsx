import React, { useState } from 'react';
import { RelationshipCardProps, ReviewItemType } from '../../../types/review';
import ConfidenceBadge from '../../common/ConfidenceBadge';

const RelationshipCard: React.FC<RelationshipCardProps> = ({ 
  relationship, 
  onApprove, 
  onReject, 
  isSelected = false,
  onSelect 
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showRejectionForm, setShowRejectionForm] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  if (relationship.type !== ReviewItemType.RELATIONSHIP) {
    return null;
  }

  const handleApprove = async () => {
    if (isProcessing) return;
    
    setIsProcessing(true);
    try {
      await onApprove(relationship.id);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async (reason?: string) => {
    if (isProcessing) return;
    
    setIsProcessing(true);
    try {
      await onReject(relationship.id, reason);
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

  const relationshipData = relationship.data as any;

  return (
    <div className={`card ${isSelected ? 'border-2 border-blue-500' : ''}`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {relationshipData.relationship_type || 'Unknown Relationship'}
          </h3>
          <div className="text-sm text-gray-600 mb-2">
            <div className="mb-1">
              <strong>Source:</strong> {relationshipData.source_entity_id || 'Unknown'}
            </div>
            <div>
              <strong>Target:</strong> {relationshipData.target_entity_id || 'Unknown'}
            </div>
          </div>
          {relationshipData.metadata && Object.keys(relationshipData.metadata).length > 0 && (
            <div className="text-sm text-gray-700 mb-2">
              <strong>Metadata:</strong>
              <pre className="text-xs bg-gray-50 p-2 rounded mt-1 overflow-auto">
                {JSON.stringify(relationshipData.metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
        <div className="ml-4">
          <ConfidenceBadge confidence={relationshipData.confidence || 0} size="sm" />
        </div>
      </div>

      {relationshipData.source_reference && (
        <div className="text-sm text-gray-500 mb-4">
          <strong>Source:</strong> {relationshipData.source_reference}
        </div>
      )}

      <div className="text-xs text-gray-400 mb-4">
        ID: {relationship.id} • Document: {relationship.source_document_id}
      </div>

      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <button
            onClick={() => onSelect?.(relationship.id)}
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

export default RelationshipCard;