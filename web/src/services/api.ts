// API service for communicating with review backend (with Firebase Authentication)

import { getAuthHeaders, handleAuthError } from '../utils/auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/review';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

// Generic API request helper with authentication
const apiRequest = async <T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    // Get authentication headers (includes Firebase token)
    const authHeaders = await getAuthHeaders();
    
    const headers = {
      ...authHeaders,
      ...(options.headers || {}),
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle authentication errors
      if (response.status === 401) {
        throw new Error('Authentication failed. Please sign in again.');
      }
      if (response.status === 403) {
        throw new Error('You do not have permission to perform this action.');
      }
      throw new Error(data.error?.message || `HTTP error! status: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw new Error(handleAuthError(error));
  }
};

// Review queue API
export const reviewApi = {
  // Get pending review items (authenticated)
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

  // Approve a single item (authenticated)
  approveItem: async (itemId: string) => {
    return apiRequest('/review/approve', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId }),
    });
  },

  // Reject a single item (authenticated)
  rejectItem: async (itemId: string, reason?: string) => {
    return apiRequest('/review/reject', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId, reason }),
    });
  },

  // Batch approve items (authenticated)
  batchApproveItems: async (itemIds: string[]) => {
    return apiRequest('/review/batch-approve', {
      method: 'POST',
      body: JSON.stringify({ item_ids: itemIds }),
    });
  },

  // Batch reject items (authenticated)
  batchRejectItems: async (itemIds: string[], reason?: string) => {
    return apiRequest('/review/batch-reject', {
      method: 'POST',
      body: JSON.stringify({ item_ids: itemIds, reason }),
    });
  },

  // Get user statistics (authenticated)
  getUserStats: async () => {
    return apiRequest('/review/stats');
  },
};

export default reviewApi;