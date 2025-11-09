import React, { useState, useEffect } from 'react';
import { graphService, GraphNode } from '../../../services/graphService';

interface NodeBrowserProps {
  onNodeSelect: (node: GraphNode) => void;
}

export const NodeBrowser: React.FC<NodeBrowserProps> = ({ onNodeSelect }) => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  useEffect(() => {
    loadNodes();
  }, [typeFilter]);

  const loadNodes = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await graphService.getNodes({
        type: typeFilter || undefined,
      });
      setNodes(response.nodes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load nodes');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadNodes();
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await graphService.searchNodes(searchQuery);
      setNodes(response.nodes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={loadNodes}
          className="mt-2 text-red-600 hover:text-red-800 font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="flex-1">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search nodes..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
        <button
          onClick={handleSearch}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Search
        </button>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">All Types</option>
          <option value="Person">Person</option>
          <option value="Place">Place</option>
          <option value="Organization">Organization</option>
          <option value="Concept">Concept</option>
          <option value="Thing">Thing</option>
        </select>
      </div>
      
      {/* Node List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {nodes.map((node) => (
          <div
            key={node.id}
            onClick={() => onNodeSelect(node)}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg cursor-pointer transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{node.name}</h3>
                <div className="mt-1 flex flex-wrap gap-1">
                  {node.types.map((type) => (
                    <span
                      key={type}
                      className="inline-block px-2 py-1 text-xs font-medium bg-indigo-100 text-indigo-800 rounded"
                    >
                      {type}
                    </span>
                  ))}
                </div>
              </div>
              <svg
                className="h-5 w-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          </div>
        ))}
      </div>
      
      {nodes.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No nodes found</p>
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                loadNodes();
              }}
              className="mt-2 text-indigo-600 hover:text-indigo-800"
            >
              Clear search
            </button>
          )}
        </div>
      )}
    </div>
  );
};