import React, { useState, useEffect } from 'react';
import { graphService, NodeDetails as NodeDetailsType } from '../../../services/graphService';

interface NodeDetailsProps {
  nodeId: string;
  onClose: () => void;
}

export const NodeDetails: React.FC<NodeDetailsProps> = ({ nodeId, onClose }) => {
  const [node, setNode] = useState<NodeDetailsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadNodeDetails();
  }, [nodeId]);

  const loadNodeDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const details = await graphService.getNodeDetails(nodeId);
      setNode(details);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load node details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }

  if (error || !node) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md">
          <p className="text-red-800 mb-4">{error || 'Node not found'}</p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{node.name}</h2>
            <div className="mt-1 flex flex-wrap gap-2">
              {node.types.map((type) => (
                <span
                  key={type}
                  className="inline-block px-3 py-1 text-sm font-medium bg-indigo-100 text-indigo-800 rounded-full"
                >
                  {type}
                </span>
              ))}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Content */}
        <div className="px-6 py-4 space-y-6">
          {/* Properties */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Properties</h3>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              {Object.entries(node.properties || {}).map(([key, value]) => (
                <div key={key} className="flex">
                  <span className="font-medium text-gray-700 w-1/3">{key}:</span>
                  <span className="text-gray-900 w-2/3">{String(value)}</span>
                </div>
              ))}
              {Object.keys(node.properties || {}).length === 0 && (
                <p className="text-gray-500 italic">No properties</p>
              )}
            </div>
          </div>
          
          {/* Relationships */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Relationships ({node.relationships?.length || 0})
            </h3>
            <div className="space-y-3">
              {node.relationships?.map((rel, index) => (
                <div
                  key={index}
                  className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      rel.direction === 'outgoing' ? 'bg-green-100' : 'bg-blue-100'
                    }`}>
                      <svg
                        className={`h-4 w-4 ${
                          rel.direction === 'outgoing' ? 'text-green-600' : 'text-blue-600'
                        }`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d={rel.direction === 'outgoing' ? 'M13 7l5 5m0 0l-5 5m5-5H6' : 'M11 17l-5-5m0 0l5-5m-5 5h12'}
                        />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{rel.relationship}</p>
                      <p className="text-sm text-gray-600">{rel.node.name}</p>
                      <div className="mt-1 flex gap-1">
                        {rel.nodeTypes.map((type) => (
                          <span
                            key={type}
                            className="inline-block px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded"
                          >
                            {type}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {(!node.relationships || node.relationships.length === 0) && (
                <p className="text-gray-500 italic">No relationships</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};