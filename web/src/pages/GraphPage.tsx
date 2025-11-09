import React from 'react';

const GraphPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Graph</h1>
        <p className="mt-2 text-gray-600">
          Visualize your approved entities and relationships
        </p>
      </div>

      <div className="bg-white shadow rounded-lg p-8 text-center">
        <div className="text-gray-500">
          <div className="mb-4">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h2 className="text-lg font-medium text-gray-900 mb-2">Coming Soon</h2>
          <p className="text-sm text-gray-500">
            The Knowledge Graph visualization will be implemented in a future sprint.
            This will allow you to explore your approved entities and relationships 
            in an interactive graph format.
          </p>
        </div>
      </div>
    </div>
  );
};

export default GraphPage;