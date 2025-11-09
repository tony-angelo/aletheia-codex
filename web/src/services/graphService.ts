import { auth } from '../firebase/config';

const GRAPH_API_URL = process.env.REACT_APP_GRAPH_API_URL || 
  'https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function';

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
   * Get list of nodes for current user
   */
  async getNodes(options: {
    limit?: number;
    offset?: number;
    type?: string;
  } = {}): Promise<NodesResponse> {
    const user = auth.currentUser;
    if (!user) throw new Error('Not authenticated');
    
    const token = await user.getIdToken();
    
    const params = new URLSearchParams({
      userId: user.uid,
      limit: String(options.limit || 50),
      offset: String(options.offset || 0),
    });
    
    if (options.type) {
      params.append('type', options.type);
    }
    
    const response = await fetch(`${GRAPH_API_URL}?${params}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
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
    
    const token = await user.getIdToken();
    const params = new URLSearchParams({ userId: user.uid, nodeId });
    
    const response = await fetch(`${GRAPH_API_URL}?${params}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
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
    
    const token = await user.getIdToken();
    const params = new URLSearchParams({
      userId: user.uid,
      query,
      search: 'true',
    });
    
    const response = await fetch(`${GRAPH_API_URL}?${params}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error(`Failed to search nodes: ${response.statusText}`);
    }
    
    return response.json();
  },
};