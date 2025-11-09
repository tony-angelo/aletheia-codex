import { useState, useEffect, useCallback } from 'react';
import { reviewApi } from '../services/api';
import { ReviewItem, UserStats } from '../types/review';
import { isAuthenticated } from '../utils/auth';

interface UseReviewQueueOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  initialFilters?: {
    limit?: number;
    min_confidence?: number;
    type?: 'entity' | 'relationship';
    order_by?: string;
    descending?: boolean;
  };
}

export const useReviewQueue = (options: UseReviewQueueOptions = {}) => {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState(options.initialFilters || {});

  const {
    autoRefresh = true,
    refreshInterval = 30000, // 30 seconds
  } = options;

  // Fetch pending items
  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await reviewApi.getPendingItems(filters);
      if (response.success && response.data) {
        setItems(response.data.items);
      } else {
        setError(response.error?.message || 'Failed to fetch items');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Fetch user statistics
  const fetchStats = useCallback(async () => {
    try {
      const response = await reviewApi.getUserStats();
      if (response.success && response.data) {
        setStats(response.data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  // Approve item
  const approveItem = useCallback(async (itemId: string) => {
    try {
      const response = await reviewApi.approveItem(itemId);
      if (response.success) {
        // Remove the approved item from the list
        setItems(prev => prev.filter(item => item.id !== itemId));
        // Refresh stats
        fetchStats();
        return true;
      } else {
        setError(response.error?.message || 'Failed to approve item');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve item');
      return false;
    }
  }, [fetchStats]);

  // Reject item
  const rejectItem = useCallback(async (itemId: string, reason?: string) => {
    try {
      const response = await reviewApi.rejectItem(itemId, reason);
      if (response.success) {
        // Remove the rejected item from the list
        setItems(prev => prev.filter(item => item.id !== itemId));
        // Refresh stats
        fetchStats();
        return true;
      } else {
        setError(response.error?.message || 'Failed to reject item');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject item');
      return false;
    }
  }, [fetchStats]);

  // Batch approve items
  const batchApprove = useCallback(async (itemIds: string[]) => {
    try {
      const response = await reviewApi.batchApproveItems(itemIds);
      if (response.success) {
        // Remove approved items from the list
        setItems(prev => prev.filter(item => !itemIds.includes(item.id)));
        // Refresh stats
        fetchStats();
        return response.data;
      } else {
        setError(response.error?.message || 'Failed to batch approve items');
        return null;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to batch approve items');
      return null;
    }
  }, [fetchStats]);

  // Batch reject items
  const batchReject = useCallback(async (itemIds: string[], reason?: string) => {
    try {
      const response = await reviewApi.batchRejectItems(itemIds, reason);
      if (response.success) {
        // Remove rejected items from the list
        setItems(prev => prev.filter(item => !itemIds.includes(item.id)));
        // Refresh stats
        fetchStats();
        return response.data;
      } else {
        setError(response.error?.message || 'Failed to batch reject items');
        return null;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to batch reject items');
      return null;
    }
  }, [fetchStats]);

  // Update filters
  const updateFilters = useCallback((newFilters: Partial<typeof filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Initial fetch
  useEffect(() => {
    // Only fetch if user is authenticated
    if (isAuthenticated()) {
      fetchItems();
      fetchStats();
    }
  }, [fetchItems, fetchStats]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchItems();
      fetchStats();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchItems, fetchStats]);

  return {
    items,
    stats,
    loading,
    error,
    filters,
    fetchItems,
    fetchStats,
    approveItem,
    rejectItem,
    batchApprove,
    batchReject,
    updateFilters,
    clearError,
  };
};