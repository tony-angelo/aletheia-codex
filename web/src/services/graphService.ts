import { getAuthHeaders, handleAuthError } from '../utils/auth';

const GRAPH_API_URL = process.env.REACT_APP_GRAPH_API_URL || '/api/graph';

export interface GraphNode {
  id: string;
  name: string;
  types: string[];
  properties?: Record<string, any>;
  createdAt?: string;
}

export interface NodeDetails extends GraphNode {
  relationships: Array<{
    relationship: string;
    direction: 'incoming' | 'outgoing';
    node: GraphNode;
    nodeTypes: string[];
    nodeId: string;
  }>;
}

export interface NodesResponse {
  nodes: GraphNode[];
  total: number;
}

export const graphService = {
  /**
   * Get list of nodes for current user (authenticated)
   */
  async getNodes(options: {
    limit?: number;
    offset?: number;
    type?: string;
  } = {}): Promise<NodesResponse> {
    try {
      // Get authentication headers (includes Firebase token)
      const headers = await getAuthHeaders();
      
      // Build query parameters (no userId needed - comes from auth token)
      const params = new URLSearchParams({
        limit: String(options.limit || 50),
        offset: String(options.offset || 0),
      });
      
      if (options.type) {
        params.append('type', options.type);
      }
      
      const response = await fetch(`${GRAPH_API_URL}?${params}`, {
        headers,
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        }
        throw new Error(`Failed to fetch nodes: ${response.statusText}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('Error fetching nodes:', error);
      throw new Error(handleAuthError(error));
    }
  },
  
  /**
   * Get detailed information about a specific node (authenticated)
   */
  async getNodeDetails(nodeId: string): Promise<NodeDetails> {
    try {
      // Get authentication headers
      const headers = await getAuthHeaders();
      
      // Build query parameters (no userId needed)
      const params = new URLSearchParams({ nodeId });
      
      const response = await fetch(`${GRAPH_API_URL}?${params}`, {
        headers,
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        }
        if (response.status === 404) {
          throw new Error('Node not found');
        }
        throw new Error(`Failed to fetch node details: ${response.statusText}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('Error fetching node details:', error);
      throw new Error(handleAuthError(error));
    }
  },
  
  /**
   * Search nodes by name or properties (authenticated)
   */
  async searchNodes(query: string): Promise<NodesResponse> {
    try {
      // Get authentication headers
      const headers = await getAuthHeaders();
      
      // Build query parameters (no userId needed)
      const params = new URLSearchParams({
        query,
        search: 'true',
      });
      
      const response = await fetch(`${GRAPH_API_URL}?${params}`, {
        headers,
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        }
        throw new Error(`Failed to search nodes: ${response.statusText}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('Error searching nodes:', error);
      throw new Error(handleAuthError(error));
    }
  },
};