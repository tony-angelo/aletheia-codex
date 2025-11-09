# Sprint 6 Implementation Guide: Functional UI Foundation

**Sprint Duration**: 2-3 weeks  
**Primary Objective**: Build functional UI foundation with all pages, organized component library, and documented function library  
**Status**: Ready for Implementation

---

## Table of Contents
1. [Overview](#overview)
2. [Success Criteria](#success-criteria)
3. [Current State Analysis](#current-state-analysis)
4. [Implementation Plan](#implementation-plan)
5. [Technical Specifications](#technical-specifications)
6. [Testing Strategy](#testing-strategy)
7. [Deployment](#deployment)

---

## Overview

### Sprint Goal

**Build a functional UI foundation** that includes all necessary pages with basic elements, an organized component library, and documented function library. This prepares the codebase for AI-assisted redesign in Sprint 7.

### Why This Sprint Matters

Sprint 5 proved the **core workflow works** (note processing, AI extraction, review queue). Now we need to:
1. **Complete the UI** - All pages functional with basic elements
2. **Organize Components** - Clear component library structure
3. **Document Functions** - Function library for reuse
4. **Prepare for AI Analysis** - Structure code so design AI can understand and improve it

### Key Principle

**Functional Over Beautiful** - Focus on making everything work, not making it pretty. The redesign happens in Sprint 7.

---

## Success Criteria

Sprint 6 is ONLY complete when ALL 8 criteria are met:

### 1. ✅ All Pages Functional
- Dashboard/Home page with overview statistics
- Knowledge Graph page with node browser and details view
- User Profile/Settings page with user information
- Enhanced NotesPage with filters and sorting
- Enhanced ReviewPage with bulk actions

### 2. ✅ Component Library Organized
- Components categorized into logical folders (common/, layout/, features/)
- Component documentation created (README.md in components/)
- Naming conventions established and documented
- Reusable patterns identified and documented

### 3. ✅ Function Library Documented
- All utility functions documented with JSDoc comments
- Function library reference created (README.md in utils/)
- Common patterns established and documented
- Code is AI-analyzable (clear structure, good naming)

### 4. ✅ Navigation Working
- All pages accessible via navigation menu
- Active page highlighting
- Breadcrumbs where appropriate
- Mobile-responsive navigation

### 5. ✅ Basic Testing
- Critical components have unit tests
- Testing patterns established
- Test documentation created
- All tests passing

### 6. ✅ UI Consistency
- Consistent styling across all pages (same color scheme, typography)
- Loading states for all async operations
- Error messages for all failure scenarios
- Toast notifications for user feedback

### 7. ✅ Deployed to Production
- All changes deployed to Firebase Hosting
- All pages tested in production environment
- No critical errors in production
- Performance acceptable (page load < 3s)

### 8. ✅ Documentation Complete
- Component library README with examples
- Function library README with API docs
- Architecture documentation updated
- Completion report created with screenshots

---

## Current State Analysis

### Existing Pages (3 pages)

1. **NotesPage** ✅ Functional
   - Note input component
   - Note history
   - Processing status
   - **Missing**: Filters, sorting, pagination

2. **ReviewPage** ✅ Functional
   - Review queue display
   - Approval workflow
   - Entity and relationship cards
   - **Missing**: Bulk actions, filters, advanced sorting

3. **GraphPage** ⚠️ Placeholder Only
   - Shows "Coming Soon" message
   - **Missing**: Everything (node browser, details, search)

### Existing Components (13 components)

**Current Structure** (flat):
```
web/src/components/
├── BatchActions.tsx
├── ConfidenceBadge.tsx
├── EntityCard.tsx
├── ExtractionResults.tsx
├── Navigation.tsx
├── NoteCard.tsx
├── NoteHistory.tsx
├── NoteInput.tsx
├── ProcessingStatus.tsx
├── RelationshipCard.tsx
├── ReviewQueue.tsx
├── SignIn.tsx
└── SignUp.tsx
```

**Issues**:
- No organization (all components in one folder)
- No documentation
- No clear naming conventions
- Hard for AI to analyze

### Missing Functionality

1. ❌ Knowledge Graph browsing
2. ❌ Node details view
3. ❌ Relationship browser
4. ❌ Search functionality
5. ❌ Dashboard/home page
6. ❌ User profile/settings page
7. ❌ Filters and sorting on existing pages
8. ❌ Bulk actions on review page

---

## Implementation Plan

### Phase 1: Knowledge Graph Page (Days 1-3)

**Goal**: Build functional Knowledge Graph page with node browsing

#### Step 1.1: Create Graph API Endpoint (Day 1)

**Location**: `functions/graph/main.py`

**Functionality**:
```python
# GET /graph/nodes?userId={userId}&limit={limit}&offset={offset}
# Returns list of nodes from Neo4j

# GET /graph/nodes/{nodeId}?userId={userId}
# Returns node details with relationships

# GET /graph/search?userId={userId}&query={query}
# Searches nodes by name or properties
```

**Implementation**:
```python
import functions_framework
from flask import jsonify, request
from shared.db.neo4j_client import get_neo4j_client
import logging

logger = logging.getLogger(__name__)

@functions_framework.http
def graph_function(request):
    """HTTP Cloud Function for graph operations."""
    
    # CORS headers
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Get user ID from request
        user_id = request.args.get('userId')
        if not user_id:
            return (jsonify({'error': 'userId required'}), 400, headers)
        
        # Route based on path
        path = request.path
        
        if path == '/nodes':
            return get_nodes(user_id, request, headers)
        elif path.startswith('/nodes/'):
            node_id = path.split('/')[-1]
            return get_node_details(user_id, node_id, headers)
        elif path == '/search':
            return search_nodes(user_id, request, headers)
        else:
            return (jsonify({'error': 'Invalid path'}), 404, headers)
            
    except Exception as e:
        logger.error(f"Graph function error: {str(e)}", exc_info=True)
        return (jsonify({'error': str(e)}), 500, headers)

def get_nodes(user_id: str, request, headers):
    """Get list of nodes for user."""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    node_type = request.args.get('type')  # Optional filter by type
    
    client = get_neo4j_client()
    
    # Build query
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    """
    
    if node_type:
        query += f"WHERE '{node_type}' IN labels(n) "
    
    query += """
    RETURN n, labels(n) as types
    ORDER BY n.createdAt DESC
    SKIP $offset
    LIMIT $limit
    """
    
    result = client.execute_query(query, {
        'userId': user_id,
        'offset': offset,
        'limit': limit
    })
    
    nodes = []
    for record in result.get('data', []):
        node_data = record['n']
        node_data['types'] = record['types']
        nodes.append(node_data)
    
    return (jsonify({'nodes': nodes, 'total': len(nodes)}), 200, headers)

def get_node_details(user_id: str, node_id: str, headers):
    """Get detailed information about a node."""
    client = get_neo4j_client()
    
    # Get node with relationships
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    WHERE elementId(n) = $nodeId
    OPTIONAL MATCH (n)-[r]-(related)
    RETURN n, labels(n) as types, 
           collect({
               relationship: type(r),
               direction: CASE 
                   WHEN startNode(r) = n THEN 'outgoing'
                   ELSE 'incoming'
               END,
               node: related,
               nodeTypes: labels(related)
           }) as relationships
    """
    
    result = client.execute_query(query, {
        'userId': user_id,
        'nodeId': node_id
    })
    
    if not result.get('data'):
        return (jsonify({'error': 'Node not found'}), 404, headers)
    
    record = result['data'][0]
    node_data = record['n']
    node_data['types'] = record['types']
    node_data['relationships'] = record['relationships']
    
    return (jsonify(node_data), 200, headers)

def search_nodes(user_id: str, request, headers):
    """Search nodes by name or properties."""
    query_text = request.args.get('query', '')
    if not query_text:
        return (jsonify({'error': 'query parameter required'}), 400, headers)
    
    client = get_neo4j_client()
    
    # Search by name (case-insensitive)
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    WHERE toLower(n.name) CONTAINS toLower($query)
    RETURN n, labels(n) as types
    ORDER BY n.name
    LIMIT 50
    """
    
    result = client.execute_query(query, {
        'userId': user_id,
        'query': query_text
    })
    
    nodes = []
    for record in result.get('data', []):
        node_data = record['n']
        node_data['types'] = record['types']
        nodes.append(node_data)
    
    return (jsonify({'nodes': nodes, 'total': len(nodes)}), 200, headers)
```

**Deployment**:
```bash
gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=functions/graph \
  --entry-point=graph_function \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=256MB \
  --timeout=60s
```

#### Step 1.2: Create Graph Service (Day 1)

**Location**: `web/src/services/graphService.ts`

```typescript
import { auth } from '../firebase/config';

const GRAPH_API_URL = process.env.REACT_APP_GRAPH_API_URL || 
  'https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function';

export interface GraphNode {
  id: string;
  name: string;
  types: string[];
  properties: Record<string, any>;
  createdAt: string;
}

export interface NodeDetails extends GraphNode {
  relationships: Array<{
    relationship: string;
    direction: 'incoming' | 'outgoing';
    node: GraphNode;
    nodeTypes: string[];
  }>;
}

export interface NodesResponse {
  nodes: GraphNode[];
  total: number;
}

export const graphService = {
  /**
   * Get list of nodes for current user
   */
  async getNodes(options: {
    limit?: number;
    offset?: number;
    type?: string;
  } = {}): Promise<NodesResponse> {
    const user = auth.currentUser;
    if (!user) throw new Error('Not authenticated');
    
    const params = new URLSearchParams({
      userId: user.uid,
      limit: String(options.limit || 50),
      offset: String(options.offset || 0),
    });
    
    if (options.type) {
      params.append('type', options.type);
    }
    
    const response = await fetch(`${GRAPH_API_URL}/nodes?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch nodes: ${response.statusText}`);
    }
    
    return response.json();
  },
  
  /**
   * Get detailed information about a specific node
   */
  async getNodeDetails(nodeId: string): Promise<NodeDetails> {
    const user = auth.currentUser;
    if (!user) throw new Error('Not authenticated');
    
    const params = new URLSearchParams({ userId: user.uid });
    const response = await fetch(`${GRAPH_API_URL}/nodes/${nodeId}?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch node details: ${response.statusText}`);
    }
    
    return response.json();
  },
  
  /**
   * Search nodes by name or properties
   */
  async searchNodes(query: string): Promise<NodesResponse> {
    const user = auth.currentUser;
    if (!user) throw new Error('Not authenticated');
    
    const params = new URLSearchParams({
      userId: user.uid,
      query,
    });
    
    const response = await fetch(`${GRAPH_API_URL}/search?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to search nodes: ${response.statusText}`);
    }
    
    return response.json();
  },
};
```

#### Step 1.3: Create Graph Components (Days 2-3)

**A. NodeBrowser Component**

**Location**: `web/src/components/features/graph/NodeBrowser.tsx`

```typescript
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
```

**B. NodeDetails Component**

**Location**: `web/src/components/features/graph/NodeDetails.tsx`

```typescript
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
```

**C. Update GraphPage**

**Location**: `web/src/pages/GraphPage.tsx`

```typescript
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
```

### Phase 2: Dashboard & Settings Pages (Days 4-7)

#### Step 2.1: Create Dashboard Page (Days 4-5)

**Location**: `web/src/pages/DashboardPage.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { collection, query, where, getDocs, orderBy, limit } from 'firebase/firestore';
import { db, auth } from '../firebase/config';

interface Stats {
  totalNotes: number;
  totalEntities: number;
  totalRelationships: number;
  recentNotes: Array<{
    id: string;
    content: string;
    status: string;
    createdAt: any;
  }>;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<Stats>({
    totalNotes: 0,
    totalEntities: 0,
    totalRelationships: 0,
    recentNotes: [],
  });
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadStats();
  }, []);
  
  const loadStats = async () => {
    try {
      const user = auth.currentUser;
      if (!user) return;
      
      // Get total notes
      const notesQuery = query(
        collection(db, 'notes'),
        where('userId', '==', user.uid)
      );
      const notesSnapshot = await getDocs(notesQuery);
      
      // Get recent notes
      const recentQuery = query(
        collection(db, 'notes'),
        where('userId', '==', user.uid),
        orderBy('createdAt', 'desc'),
        limit(5)
      );
      const recentSnapshot = await getDocs(recentQuery);
      
      // Get review queue items
      const reviewQuery = query(
        collection(db, 'reviewQueue'),
        where('userId', '==', user.uid)
      );
      const reviewSnapshot = await getDocs(reviewQuery);
      
      // Count entities and relationships
      let entityCount = 0;
      let relationshipCount = 0;
      reviewSnapshot.forEach((doc) => {
        const data = doc.data();
        if (data.type === 'entity') entityCount++;
        if (data.type === 'relationship') relationshipCount++;
      });
      
      setStats({
        totalNotes: notesSnapshot.size,
        totalEntities: entityCount,
        totalRelationships: relationshipCount,
        recentNotes: recentSnapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        })) as any,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
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
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Overview of your knowledge graph activity
        </p>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-indigo-100 rounded-lg p-3">
              <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Notes</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalNotes}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Entities</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalEntities}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
              <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Relationships</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalRelationships}</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Recent Notes */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Notes</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {stats.recentNotes.map((note) => (
            <div key={note.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-gray-900 line-clamp-2">{note.content}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    {note.createdAt?.toDate?.()?.toLocaleDateString() || 'Unknown date'}
                  </p>
                </div>
                <span className={`ml-4 px-2 py-1 text-xs font-medium rounded-full ${
                  note.status === 'completed' ? 'bg-green-100 text-green-800' :
                  note.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {note.status}
                </span>
              </div>
            </div>
          ))}
          {stats.recentNotes.length === 0 && (
            <div className="px-6 py-8 text-center text-gray-500">
              No notes yet. Create your first note to get started!
            </div>
          )}
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <a
          href="/notes"
          className="block bg-indigo-600 text-white rounded-lg p-6 hover:bg-indigo-700 transition-colors"
        >
          <h3 className="font-semibold mb-2">Create Note</h3>
          <p className="text-sm text-indigo-100">Add a new note to your knowledge graph</p>
        </a>
        <a
          href="/review"
          className="block bg-green-600 text-white rounded-lg p-6 hover:bg-green-700 transition-colors"
        >
          <h3 className="font-semibold mb-2">Review Queue</h3>
          <p className="text-sm text-green-100">Approve or reject extracted entities</p>
        </a>
        <a
          href="/graph"
          className="block bg-purple-600 text-white rounded-lg p-6 hover:bg-purple-700 transition-colors"
        >
          <h3 className="font-semibold mb-2">Browse Graph</h3>
          <p className="text-sm text-purple-100">Explore your knowledge graph</p>
        </a>
      </div>
    </div>
  );
};

export default DashboardPage;
```

#### Step 2.2: Create Settings Page (Days 6-7)

**Location**: `web/src/pages/SettingsPage.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { auth } from '../firebase/config';
import { updateProfile } from 'firebase/auth';

const SettingsPage: React.FC = () => {
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  useEffect(() => {
    const user = auth.currentUser;
    if (user) {
      setDisplayName(user.displayName || '');
      setEmail(user.email || '');
    }
  }, []);
  
  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    try {
      const user = auth.currentUser;
      if (!user) throw new Error('Not authenticated');
      
      await updateProfile(user, { displayName });
      setMessage({ type: 'success', text: 'Profile updated successfully' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to update profile',
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Manage your account settings and preferences
        </p>
      </div>
      
      {/* Profile Settings */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Profile</h2>
        </div>
        <form onSubmit={handleUpdateProfile} className="px-6 py-4 space-y-4">
          <div>
            <label htmlFor="displayName" className="block text-sm font-medium text-gray-700 mb-1">
              Display Name
            </label>
            <input
              type="text"
              id="displayName"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              disabled
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
            />
            <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
          </div>
          
          {message && (
            <div className={`p-4 rounded-lg ${
              message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
            }`}>
              {message.text}
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
      
      {/* Account Information */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Account Information</h2>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <p className="text-sm font-medium text-gray-700">User ID</p>
            <p className="mt-1 text-sm text-gray-900 font-mono">{auth.currentUser?.uid}</p>
          </div>
          
          <div>
            <p className="text-sm font-medium text-gray-700">Account Created</p>
            <p className="mt-1 text-sm text-gray-900">
              {auth.currentUser?.metadata.creationTime || 'Unknown'}
            </p>
          </div>
          
          <div>
            <p className="text-sm font-medium text-gray-700">Last Sign In</p>
            <p className="mt-1 text-sm text-gray-900">
              {auth.currentUser?.metadata.lastSignInTime || 'Unknown'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
```

#### Step 2.3: Update Navigation (Day 7)

**Location**: `web/src/components/layout/Navigation.tsx`

Add Dashboard and Settings links to navigation menu.

### Phase 3: Component Library Organization (Days 8-10)

#### Step 3.1: Reorganize Components (Day 8)

**New Structure**:
```
web/src/components/
├── common/                    # Shared UI components
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Input.tsx
│   ├── Badge.tsx
│   ├── LoadingSpinner.tsx
│   └── ErrorMessage.tsx
├── layout/                    # Layout components
│   ├── Navigation.tsx
│   ├── Header.tsx
│   └── Footer.tsx
├── features/                  # Feature-specific components
│   ├── notes/
│   │   ├── NoteInput.tsx
│   │   ├── NoteCard.tsx
│   │   ├── NoteHistory.tsx
│   │   └── ProcessingStatus.tsx
│   ├── review/
│   │   ├── ReviewQueue.tsx
│   │   ├── EntityCard.tsx
│   │   ├── RelationshipCard.tsx
│   │   ├── ConfidenceBadge.tsx
│   │   ├── BatchActions.tsx
│   │   └── ExtractionResults.tsx
│   ├── graph/
│   │   ├── NodeBrowser.tsx
│   │   ├── NodeDetails.tsx
│   │   └── RelationshipBrowser.tsx
│   └── auth/
│       ├── SignIn.tsx
│       └── SignUp.tsx
└── README.md                  # Component library documentation
```

#### Step 3.2: Create Component Documentation (Days 9-10)

**Location**: `web/src/components/README.md`

```markdown
# Component Library Documentation

## Overview

This directory contains all React components for the Aletheia Codex application, organized by category.

## Directory Structure

### common/
Reusable UI components that can be used across the application.

**Components**:
- `Button.tsx` - Styled button component with variants
- `Card.tsx` - Container component for content
- `Input.tsx` - Form input component
- `Badge.tsx` - Label/tag component
- `LoadingSpinner.tsx` - Loading indicator
- `ErrorMessage.tsx` - Error display component

### layout/
Components that define the application layout and structure.

**Components**:
- `Navigation.tsx` - Main navigation menu
- `Header.tsx` - Page header component
- `Footer.tsx` - Page footer component

### features/
Feature-specific components organized by domain.

#### features/notes/
Components related to note creation and management.

**Components**:
- `NoteInput.tsx` - Text input for creating notes
- `NoteCard.tsx` - Display component for individual notes
- `NoteHistory.tsx` - List of user's notes
- `ProcessingStatus.tsx` - Shows note processing status

#### features/review/
Components for the review queue and approval workflow.

**Components**:
- `ReviewQueue.tsx` - Main review queue interface
- `EntityCard.tsx` - Display component for entities
- `RelationshipCard.tsx` - Display component for relationships
- `ConfidenceBadge.tsx` - Shows confidence score
- `BatchActions.tsx` - Bulk action controls
- `ExtractionResults.tsx` - Shows extraction results

#### features/graph/
Components for knowledge graph browsing and visualization.

**Components**:
- `NodeBrowser.tsx` - Browse and search nodes
- `NodeDetails.tsx` - Detailed view of a node
- `RelationshipBrowser.tsx` - Browse relationships

#### features/auth/
Authentication-related components.

**Components**:
- `SignIn.tsx` - Sign in form
- `SignUp.tsx` - Sign up form

## Component Patterns

### Props Interface
All components should define a TypeScript interface for their props:

\`\`\`typescript
interface MyComponentProps {
  title: string;
  onAction: () => void;
  optional?: boolean;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, onAction, optional }) => {
  // Component implementation
};
\`\`\`

### State Management
Use React hooks for local state:

\`\`\`typescript
const [value, setValue] = useState<string>('');
const [loading, setLoading] = useState(false);
\`\`\`

### Error Handling
Always handle errors gracefully:

\`\`\`typescript
try {
  await someAsyncOperation();
} catch (error) {
  console.error('Operation failed:', error);
  setError(error instanceof Error ? error.message : 'Unknown error');
}
\`\`\`

### Loading States
Show loading indicators for async operations:

\`\`\`typescript
if (loading) {
  return <LoadingSpinner />;
}
\`\`\`

## Naming Conventions

- **Components**: PascalCase (e.g., `NoteInput.tsx`)
- **Props Interfaces**: PascalCase with "Props" suffix (e.g., `NoteInputProps`)
- **Functions**: camelCase (e.g., `handleSubmit`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_LENGTH`)

## Styling

All components use Tailwind CSS for styling. Follow these guidelines:

- Use utility classes for styling
- Keep responsive design in mind (use `sm:`, `md:`, `lg:` prefixes)
- Use consistent color scheme (indigo for primary, gray for neutral)
- Maintain consistent spacing (use `p-4`, `m-4`, `gap-4`, etc.)

## Testing

Components should be testable. Write tests for:
- User interactions (clicks, form submissions)
- State changes
- Error handling
- Edge cases

## Adding New Components

1. Create component file in appropriate directory
2. Define TypeScript interface for props
3. Implement component with proper error handling
4. Add to this documentation
5. Write tests if applicable

## Common Patterns

### Async Data Loading

\`\`\`typescript
const [data, setData] = useState<DataType[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  loadData();
}, []);

const loadData = async () => {
  try {
    setLoading(true);
    setError(null);
    const result = await fetchData();
    setData(result);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to load data');
  } finally {
    setLoading(false);
  }
};
\`\`\`

### Form Handling

\`\`\`typescript
const [formData, setFormData] = useState({ field1: '', field2: '' });

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  // Handle form submission
};

const handleChange = (field: string, value: string) => {
  setFormData(prev => ({ ...prev, [field]: value }));
};
\`\`\`

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
```

### Phase 4: Function Library Documentation (Days 11-12)

#### Step 4.1: Document Utility Functions (Day 11)

**Location**: `web/src/utils/README.md`

```markdown
# Function Library Documentation

## Overview

This directory contains utility functions and services used throughout the application.

## Directory Structure

### api/
API client functions for backend communication.

**Files**:
- `notesApi.ts` - Notes CRUD operations
- `reviewApi.ts` - Review queue operations
- `graphApi.ts` - Knowledge graph operations

### formatting/
Data formatting and transformation utilities.

**Files**:
- `dateFormatting.ts` - Date/time formatting functions
- `textFormatting.ts` - Text manipulation functions
- `numberFormatting.ts` - Number formatting functions

### validation/
Input validation functions.

**Files**:
- `formValidation.ts` - Form input validation
- `dataValidation.ts` - Data structure validation

## API Functions

### notesApi.ts

\`\`\`typescript
/**
 * Create a new note
 * @param content - Note content
 * @returns Promise<string> - Note ID
 */
export async function createNote(content: string): Promise<string>

/**
 * Get user's notes
 * @param options - Query options (limit, offset, status)
 * @returns Promise<Note[]> - Array of notes
 */
export async function getNotes(options?: QueryOptions): Promise<Note[]>

/**
 * Get note by ID
 * @param noteId - Note ID
 * @returns Promise<Note> - Note object
 */
export async function getNote(noteId: string): Promise<Note>

/**
 * Delete note
 * @param noteId - Note ID
 * @returns Promise<void>
 */
export async function deleteNote(noteId: string): Promise<void>
\`\`\`

### reviewApi.ts

\`\`\`typescript
/**
 * Get review queue items
 * @param options - Query options
 * @returns Promise<ReviewItem[]> - Array of review items
 */
export async function getReviewItems(options?: QueryOptions): Promise<ReviewItem[]>

/**
 * Approve review item
 * @param itemId - Review item ID
 * @returns Promise<void>
 */
export async function approveItem(itemId: string): Promise<void>

/**
 * Reject review item
 * @param itemId - Review item ID
 * @returns Promise<void>
 */
export async function rejectItem(itemId: string): Promise<void>

/**
 * Batch approve items
 * @param itemIds - Array of item IDs
 * @returns Promise<void>
 */
export async function batchApprove(itemIds: string[]): Promise<void>
\`\`\`

### graphApi.ts

\`\`\`typescript
/**
 * Get nodes from knowledge graph
 * @param options - Query options (limit, offset, type)
 * @returns Promise<GraphNode[]> - Array of nodes
 */
export async function getNodes(options?: NodeQueryOptions): Promise<GraphNode[]>

/**
 * Get node details
 * @param nodeId - Node ID
 * @returns Promise<NodeDetails> - Node with relationships
 */
export async function getNodeDetails(nodeId: string): Promise<NodeDetails>

/**
 * Search nodes
 * @param query - Search query
 * @returns Promise<GraphNode[]> - Matching nodes
 */
export async function searchNodes(query: string): Promise<GraphNode[]>
\`\`\`

## Formatting Functions

### dateFormatting.ts

\`\`\`typescript
/**
 * Format date to relative time (e.g., "2 hours ago")
 * @param date - Date to format
 * @returns string - Formatted date
 */
export function formatRelativeTime(date: Date): string

/**
 * Format date to short format (e.g., "Jan 15, 2025")
 * @param date - Date to format
 * @returns string - Formatted date
 */
export function formatShortDate(date: Date): string

/**
 * Format date to long format (e.g., "January 15, 2025 at 3:45 PM")
 * @param date - Date to format
 * @returns string - Formatted date
 */
export function formatLongDate(date: Date): string
\`\`\`

### textFormatting.ts

\`\`\`typescript
/**
 * Truncate text to specified length
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns string - Truncated text
 */
export function truncateText(text: string, maxLength: number): string

/**
 * Capitalize first letter of each word
 * @param text - Text to capitalize
 * @returns string - Capitalized text
 */
export function capitalizeWords(text: string): string

/**
 * Convert text to slug (URL-friendly)
 * @param text - Text to convert
 * @returns string - Slug
 */
export function textToSlug(text: string): string
\`\`\`

## Validation Functions

### formValidation.ts

\`\`\`typescript
/**
 * Validate email address
 * @param email - Email to validate
 * @returns boolean - True if valid
 */
export function isValidEmail(email: string): boolean

/**
 * Validate password strength
 * @param password - Password to validate
 * @returns { valid: boolean; message: string } - Validation result
 */
export function validatePassword(password: string): ValidationResult

/**
 * Validate required field
 * @param value - Value to validate
 * @returns boolean - True if not empty
 */
export function isRequired(value: string): boolean
\`\`\`

## Common Patterns

### Error Handling

All API functions should handle errors consistently:

\`\`\`typescript
try {
  const result = await apiFunction();
  return result;
} catch (error) {
  console.error('API call failed:', error);
  throw new Error(error instanceof Error ? error.message : 'Unknown error');
}
\`\`\`

### Type Safety

Always use TypeScript types for function parameters and return values:

\`\`\`typescript
interface QueryOptions {
  limit?: number;
  offset?: number;
  status?: string;
}

export async function getData(options?: QueryOptions): Promise<DataType[]> {
  // Implementation
}
\`\`\`

### Async/Await

Use async/await for asynchronous operations:

\`\`\`typescript
export async function fetchData(): Promise<DataType> {
  const response = await fetch(url);
  const data = await response.json();
  return data;
}
\`\`\`

## Adding New Functions

1. Create function in appropriate directory
2. Add JSDoc comments with parameter and return type documentation
3. Export function from index file
4. Add to this documentation
5. Write tests if applicable

## Resources

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [MDN Web Docs](https://developer.mozilla.org/)
```

### Phase 5: Testing & Deployment (Days 13-14)

#### Step 5.1: Add Basic Tests (Day 13)

**Example Test**: `web/src/components/features/notes/__tests__/NoteInput.test.tsx`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { NoteInput } from '../NoteInput';

describe('NoteInput', () => {
  it('renders input field', () => {
    render(<NoteInput onSubmit={jest.fn()} />);
    expect(screen.getByPlaceholderText(/enter your note/i)).toBeInTheDocument();
  });
  
  it('calls onSubmit when form is submitted', async () => {
    const onSubmit = jest.fn();
    render(<NoteInput onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText(/enter your note/i);
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    fireEvent.change(input, { target: { value: 'Test note' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith('Test note');
    });
  });
  
  it('shows error message on submission failure', async () => {
    const onSubmit = jest.fn().mockRejectedValue(new Error('Submission failed'));
    render(<NoteInput onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText(/enter your note/i);
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    fireEvent.change(input, { target: { value: 'Test note' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/submission failed/i)).toBeInTheDocument();
    });
  });
});
```

#### Step 5.2: Deploy to Production (Day 14)

```bash
# Build and deploy frontend
cd web
npm run build
firebase deploy --only hosting

# Verify deployment
# Test all pages in production
# Check for errors in browser console
# Verify performance (page load < 3s)
```

---

## Technical Specifications

### Technology Stack

**Frontend**:
- React 18
- TypeScript
- Tailwind CSS
- Firebase SDK (Auth, Firestore)

**Backend**:
- Cloud Functions (Python 3.11)
- Firestore
- Neo4j Aura
- Gemini AI

**Deployment**:
- Firebase Hosting (frontend)
- Cloud Functions (backend)

### API Endpoints

**Graph API** (NEW):
- `GET /nodes?userId={userId}&limit={limit}&offset={offset}&type={type}`
- `GET /nodes/{nodeId}?userId={userId}`
- `GET /search?userId={userId}&query={query}`

**Existing APIs**:
- Orchestration Function (Firestore trigger)
- Review Queue Function (HTTP)

### Database Schema

**Firestore Collections**:
- `notes` - User notes
- `reviewQueue` - Pending review items
- `users` - User profiles

**Neo4j Graph**:
- Nodes: User, Person, Place, Organization, Concept, Thing
- Relationships: OWNS, KNOWS, WORKS_AT, LOCATED_IN, etc.

### Component Structure

```
web/src/
├── components/
│   ├── common/           # Reusable UI components
│   ├── layout/           # Layout components
│   ├── features/         # Feature-specific components
│   │   ├── notes/
│   │   ├── review/
│   │   ├── graph/
│   │   └── auth/
│   └── README.md
├── pages/
│   ├── DashboardPage.tsx
│   ├── NotesPage.tsx
│   ├── ReviewPage.tsx
│   ├── GraphPage.tsx
│   └── SettingsPage.tsx
├── services/
│   ├── graphService.ts
│   ├── notesService.ts
│   └── reviewService.ts
├── utils/
│   ├── api/
│   ├── formatting/
│   ├── validation/
│   └── README.md
└── firebase/
    └── config.ts
```

---

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Test utility functions
- Test service functions
- Use Jest and React Testing Library

### Integration Tests
- Test component interactions
- Test API integrations
- Test authentication flow

### Manual Testing
- Test all pages in browser
- Test responsive design
- Test error scenarios
- Test loading states

### Production Testing
- Deploy to production
- Test all pages live
- Check browser console for errors
- Verify performance metrics

---

## Deployment

### Prerequisites
- Firebase CLI installed
- GCP authentication configured
- All environment variables set

### Frontend Deployment

```bash
cd web
npm run build
firebase deploy --only hosting
```

### Backend Deployment

```bash
# Deploy graph function
cd functions/graph
gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=256MB \
  --timeout=60s
```

### Verification

1. **Frontend**:
   - Visit production URL
   - Test all pages
   - Check browser console
   - Verify responsive design

2. **Backend**:
   - Test API endpoints
   - Check function logs
   - Verify authentication
   - Test error handling

3. **Performance**:
   - Page load < 3s
   - API response < 500ms
   - No memory leaks
   - No console errors

---

## Common Issues and Solutions

### Issue: Component Not Found
**Solution**: Check import paths after reorganization

### Issue: API Call Fails
**Solution**: Verify CORS headers and authentication

### Issue: Build Fails
**Solution**: Check TypeScript errors and dependencies

### Issue: Deployment Fails
**Solution**: Verify Firebase configuration and permissions

---

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)

---

**End of Sprint 6 Implementation Guide**