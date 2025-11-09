import React, { useState } from 'react';
import { NodeBrowser } from '../components/features/graph/NodeBrowser';
import { NodeDetails } from '../components/features/graph/NodeDetails';
import { GraphNode } from '../services/graphService';

const GraphPage: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Graph</h1>
        <p className="mt-2 text-gray-600">
          Browse and explore your approved entities and relationships
        </p>
      </div>
      
      <NodeBrowser onNodeSelect={setSelectedNode} />
      
      {selectedNode && (
        <NodeDetails
          nodeId={selectedNode.id}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
};

export default GraphPage;