import React, { useState } from 'react';
import { useReviewQueue } from '../../../hooks/useReviewQueue';
import { ReviewItemType } from '../../../types/review';
import EntityCard from './EntityCard';
import RelationshipCard from './RelationshipCard';

const ReviewQueue: React.FC = () => {
  const {
    items,
    stats,
    loading,
    error,
    filters,
    fetchItems,
    approveItem,
    rejectItem,
    updateFilters,
    clearError,
  } = useReviewQueue();

  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());

  const handleSelectItem = (itemId: string) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId);
    } else {
      newSelected.add(itemId);
    }
    setSelectedItems(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedItems.size === items.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(items.map(item => item.id)));
    }
  };

  const handleApproveItem = async (itemId: string) => {
    await approveItem(itemId);
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      newSet.delete(itemId);
      return newSet;
    });
  };

  const handleRejectItem = async (itemId: string, reason?: string) => {
    await rejectItem(itemId, reason);
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      newSet.delete(itemId);
      return newSet;
    });
  };

  const handleFilterChange = (key: string, value: any) => {
    updateFilters({ [key]: value });
  };

  const handleRefresh = () => {
    fetchItems();
  };

  if (loading && items.length === 0) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p className="ml-2 text-gray-600">Loading review queue...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Review Queue</h1>
            <p className="text-gray-600 mt-1">
              Review AI-extracted entities and relationships
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="btn btn-outline"
            disabled={loading}
          >
            {loading ? 'Refreshing...' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
          <button
            onClick={clearError}
            className="ml-2 btn btn-outline text-sm"
          >
            Dismiss
          </button>
        </div>
      )}

      {stats && (
        <div className="card bg-blue-50 border-blue-200">
          <h2 className="text-lg font-semibold text-blue-900 mb-2">Your Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-blue-700 font-medium">Total:</span> {stats.total_items}
            </div>
            <div>
              <span className="text-yellow-700 font-medium">Pending:</span> {stats.pending_items}
            </div>
            <div>
              <span className="text-green-700 font-medium">Approved:</span> {stats.approved_items}
            </div>
            <div>
              <span className="text-red-700 font-medium">Rejected:</span> {stats.rejected_items}
            </div>
          </div>
        </div>
      )}

      <div className="card mb-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Limit
            </label>
            <select
              value={filters.limit || 50}
              onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
              className="w-full border rounded px-3 py-2"
            >
              <option value={10}>10 items</option>
              <option value={25}>25 items</option>
              <option value={50}>50 items</option>
              <option value={100}>100 items</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Min Confidence
            </label>
            <select
              value={filters.min_confidence || 0}
              onChange={(e) => handleFilterChange('min_confidence', parseFloat(e.target.value))}
              className="w-full border rounded px-3 py-2"
            >
              <option value={0}>Any (0%)</option>
              <option value={0.4}>Low (40%)</option>
              <option value={0.6}>Medium (60%)</option>
              <option value={0.8}>High (80%)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={filters.type || ''}
              onChange={(e) => handleFilterChange('type', e.target.value || undefined)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">All Types</option>
              <option value="entity">Entities</option>
              <option value="relationship">Relationships</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Order By
            </label>
            <select
              value={filters.order_by || 'confidence'}
              onChange={(e) => handleFilterChange('order_by', e.target.value)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="confidence">Confidence</option>
              <option value="extracted_at">Extracted Date</option>
              <option value="name">Name</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Order
            </label>
            <select
              value={filters.descending ? 'desc' : 'asc'}
              onChange={(e) => handleFilterChange('descending', e.target.value === 'desc')}
              className="w-full border rounded px-3 py-2"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
        </div>
      </div>

      <div className="card mb-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Review Items ({items.length})
            </h2>
            {items.length > 0 && (
              <button
                onClick={handleSelectAll}
                className="btn btn-outline text-sm"
              >
                {selectedItems.size === items.length ? 'Deselect All' : 'Select All'}
              </button>
            )}
          </div>
          <div className="text-sm text-gray-500">
            {selectedItems.size > 0 && (
              <span>{selectedItems.size} selected</span>
            )}
          </div>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="card text-center py-8">
          <p className="text-gray-500">
            No items to review. Try adjusting filters or refresh to get new items.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div key={item.id}>
              {item.type === ReviewItemType.ENTITY ? (
                <EntityCard
                  entity={item}
                  onApprove={handleApproveItem}
                  onReject={handleRejectItem}
                  isSelected={selectedItems.has(item.id)}
                  onSelect={handleSelectItem}
                />
              ) : (
                <RelationshipCard
                  relationship={item}
                  onApprove={handleApproveItem}
                  onReject={handleRejectItem}
                  isSelected={selectedItems.has(item.id)}
                  onSelect={handleSelectItem}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReviewQueue;