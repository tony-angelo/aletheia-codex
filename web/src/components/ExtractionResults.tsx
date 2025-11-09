import React, { useState } from 'react';
import { Link } from 'react-router-dom';

interface Entity {
  id: string;
  name: string;
  type: string;
  confidence: number;
  description?: string;
  source_note_id: string;
}

interface Relationship {
  id: string;
  source_entity: string;
  target_entity: string;
  relationship_type: string;
  confidence: number;
  description?: string;
  source_note_id: string;
}

interface ExtractionResultsProps {
  noteId: string;
  entities: Entity[];
  relationships: Relationship[];
  isLoading?: boolean;
}

const ExtractionResults: React.FC<ExtractionResultsProps> = ({
  noteId,
  entities,
  relationships,
  isLoading = false
}) => {
  const [expandedSection, setExpandedSection] = useState<'entities' | 'relationships' | 'none'>('none');

  if (isLoading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-2 text-gray-600">Loading extraction results...</span>
        </div>
      </div>
    );
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const EntityCard: React.FC<{ entity: Entity }> = ({ entity }) => (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="text-lg font-medium text-gray-900">{entity.name}</h4>
          <p className="text-sm text-gray-600 mt-1">Type: {entity.type}</p>
          {entity.description && (
            <p className="text-sm text-gray-700 mt-2">{entity.description}</p>
          )}
        </div>
        <div className="ml-4">
          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(entity.confidence)}`}>
            {Math.round(entity.confidence * 100)}% {getConfidenceLabel(entity.confidence)}
          </span>
        </div>
      </div>
    </div>
  );

  const RelationshipCard: React.FC<{ relationship: Relationship }> = ({ relationship }) => (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-900">{relationship.source_entity}</span>
            <svg className="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            <span className="font-medium text-blue-600">{relationship.relationship_type}</span>
            <svg className="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            <span className="font-medium text-gray-900">{relationship.target_entity}</span>
          </div>
          {relationship.description && (
            <p className="text-sm text-gray-700 mt-2">{relationship.description}</p>
          )}
        </div>
        <div className="ml-4">
          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(relationship.confidence)}`}>
            {Math.round(relationship.confidence * 100)}% {getConfidenceLabel(relationship.confidence)}
          </span>
        </div>
      </div>
    </div>
  );

  const toggleSection = (section: 'entities' | 'relationships') => {
    setExpandedSection(expandedSection === section ? 'none' : section);
  };

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-2">Extraction Summary</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-blue-700 font-medium">Entities Found:</span> {entities.length}
          </div>
          <div>
            <span className="text-blue-700 font-medium">Relationships Found:</span> {relationships.length}
          </div>
        </div>
        <div className="mt-4">
          <Link
            to={`/review?noteId=${noteId}`}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
            Review in Queue
          </Link>
        </div>
      </div>

      {/* Entities Section */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection('entities')}
          className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
        >
          <div>
            <h3 className="text-lg font-medium text-gray-900">Entities ({entities.length})</h3>
            <p className="text-sm text-gray-600 mt-1">People, places, organizations, and concepts</p>
          </div>
          <svg
            className={`h-5 w-5 text-gray-400 transform transition-transform ${expandedSection === 'entities' ? 'rotate-90' : ''}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        </button>

        {expandedSection === 'entities' && (
          <div className="px-6 pb-6">
            {entities.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No entities were extracted from this note.
              </div>
            ) : (
              <div className="space-y-4">
                {entities.map((entity) => (
                  <EntityCard key={entity.id} entity={entity} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Relationships Section */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection('relationships')}
          className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
        >
          <div>
            <h3 className="text-lg font-medium text-gray-900">Relationships ({relationships.length})</h3>
            <p className="text-sm text-gray-600 mt-1">Connections between entities</p>
          </div>
          <svg
            className={`h-5 w-5 text-gray-400 transform transition-transform ${expandedSection === 'relationships' ? 'rotate-90' : ''}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        </button>

        {expandedSection === 'relationships' && (
          <div className="px-6 pb-6">
            {relationships.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No relationships were extracted from this note.
              </div>
            ) : (
              <div className="space-y-4">
                {relationships.map((relationship) => (
                  <RelationshipCard key={relationship.id} relationship={relationship} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExtractionResults;