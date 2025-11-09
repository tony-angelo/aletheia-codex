import { useState, useCallback } from 'react';
import { reviewApi } from '../services/api';

interface UseApprovalOptions {
  onSuccess?: (action: 'approve' | 'reject', itemIds: string[]) => void;
  onError?: (error: string) => void;
}

export const useApproval = (options: UseApprovalOptions = {}) => {
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { onSuccess, onError } = options;

  // Approve a single item
  const approveItem = useCallback(async (itemId: string) => {
    setProcessing(true);
    setError(null);

    try {
      const response = await reviewApi.approveItem(itemId);
      
      if (response.success) {
        onSuccess?.('approve', [itemId]);
        return true;
      } else {
        const errorMessage = response.error?.message || 'Failed to approve item';
        setError(errorMessage);
        onError?.(errorMessage);
        return false;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      onError?.(errorMessage);
      return false;
    } finally {
      setProcessing(false);
    }
  }, [onSuccess, onError]);

  // Reject a single item
  const rejectItem = useCallback(async (itemId: string, reason?: string) => {
    setProcessing(true);
    setError(null);

    try {
      const response = await reviewApi.rejectItem(itemId, reason);
      
      if (response.success) {
        onSuccess?.('reject', [itemId]);
        return true;
      } else {
        const errorMessage = response.error?.message || 'Failed to reject item';
        setError(errorMessage);
        onError?.(errorMessage);
        return false;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      onError?.(errorMessage);
      return false;
    } finally {
      setProcessing(false);
    }
  }, [onSuccess, onError]);

  // Batch approve items
  const batchApprove = useCallback(async (itemIds: string[]) => {
    if (itemIds.length === 0) return null;

    setProcessing(true);
    setError(null);

    try {
      const response = await reviewApi.batchApproveItems(itemIds);
      
      if (response.success) {
        onSuccess?.('approve', itemIds);
        return response.data;
      } else {
        const errorMessage = response.error?.message || 'Failed to batch approve items';
        setError(errorMessage);
        onError?.(errorMessage);
        return null;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      onError?.(errorMessage);
      return null;
    } finally {
      setProcessing(false);
    }
  }, [onSuccess, onError]);

  // Batch reject items
  const batchReject = useCallback(async (itemIds: string[], reason?: string) => {
    if (itemIds.length === 0) return null;

    setProcessing(true);
    setError(null);

    try {
      const response = await reviewApi.batchRejectItems(itemIds, reason);
      
      if (response.success) {
        onSuccess?.('reject', itemIds);
        return response.data;
      } else {
        const errorMessage = response.error?.message || 'Failed to batch reject items';
        setError(errorMessage);
        onError?.(errorMessage);
        return null;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      onError?.(errorMessage);
      return null;
    } finally {
      setProcessing(false);
    }
  }, [onSuccess, onError]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    approveItem,
    rejectItem,
    batchApprove,
    batchReject,
    processing,
    error,
    clearError,
  };
};