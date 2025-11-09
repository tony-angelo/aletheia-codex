// API service for communicating with review backend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

// Auth token management
let authToken: string | null = null;

export const setAuthToken = (token: string) => {
  authToken = token;
};

export const getAuthToken = () => authToken;

// Generic API request helper
const apiRequest = async <T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error?.message || `HTTP error! status: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Review queue API
export const reviewApi = {
  // Get pending review items
  getPendingItems: async (params: {
    limit?: number;
    min_confidence?: number;
    type?: 'entity' | 'relationship';
    order_by?: string;
    descending?: boolean;
  } = {}) => {
    const queryParams = new URLSearchParams();
    
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.min_confidence) queryParams.append('min_confidence', params.min_confidence.toString());
    if (params.type) queryParams.append('type', params.type);
    if (params.order_by) queryParams.append('order_by', params.order_by);
    if (params.descending !== undefined) queryParams.append('descending', params.descending.toString());

    const endpoint = `/review/pending${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return apiRequest(endpoint);
  },

  // Approve a single item
  approveItem: async (itemId: string) => {
    return apiRequest('/review/approve', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId }),
    });
  },

  // Reject a single item
  rejectItem: async (itemId: string, reason?: string) => {
    return apiRequest('/review/reject', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId, reason }),
    });
  },

  // Batch approve items
  batchApproveItems: async (itemIds: string[]) => {
    return apiRequest('/review/batch-approve', {
      method: 'POST',
      body: JSON.stringify({ item_ids: itemIds }),
    });
  },

  // Batch reject items
  batchRejectItems: async (itemIds: string[], reason?: string) => {
    return apiRequest('/review/batch-reject', {
      method: 'POST',
      body: JSON.stringify({ item_ids: itemIds, reason }),
    });
  },

  // Get user statistics
  getUserStats: async () => {
    return apiRequest('/review/stats');
  },

  // Health check
  healthCheck: async () => {
    return apiRequest('/health');
  },
};

export default reviewApi;