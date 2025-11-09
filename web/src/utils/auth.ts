/**
 * Authentication utilities for making authenticated API requests.
 * 
 * Provides helper functions to get Firebase authentication tokens
 * and create properly authenticated request headers.
 */

import { auth } from '../firebase/config';

/**
 * Get authentication headers with Firebase token.
 * 
 * @returns Headers with Authorization bearer token
 * @throws Error if user is not authenticated
 */
export async function getAuthHeaders(): Promise<HeadersInit> {
  const user = auth.currentUser;
  
  if (!user) {
    throw new Error('Not authenticated. Please sign in.');
  }
  
  try {
    // Get fresh ID token from Firebase
    const token = await user.getIdToken();
    
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  } catch (error) {
    console.error('Failed to get auth token:', error);
    throw new Error('Failed to get authentication token. Please sign in again.');
  }
}

/**
 * Get authentication headers with token refresh.
 * Forces a token refresh to ensure it's not expired.
 * 
 * @returns Headers with fresh Authorization bearer token
 * @throws Error if user is not authenticated
 */
export async function getAuthHeadersWithRefresh(): Promise<HeadersInit> {
  const user = auth.currentUser;
  
  if (!user) {
    throw new Error('Not authenticated. Please sign in.');
  }
  
  try {
    // Force token refresh
    const token = await user.getIdToken(true);
    
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  } catch (error) {
    console.error('Failed to refresh auth token:', error);
    throw new Error('Failed to refresh authentication token. Please sign in again.');
  }
}

/**
 * Check if user is authenticated.
 * 
 * @returns true if user is signed in
 */
export function isAuthenticated(): boolean {
  return auth.currentUser !== null;
}

/**
 * Get current user ID.
 * 
 * @returns User ID if authenticated, null otherwise
 */
export function getCurrentUserId(): string | null {
  return auth.currentUser?.uid || null;
}

/**
 * Handle authentication errors from API responses.
 * 
 * @param error - Error from API request
 * @returns User-friendly error message
 */
export function handleAuthError(error: any): string {
  if (error.message?.includes('Not authenticated')) {
    return 'Please sign in to continue.';
  }
  
  if (error.message?.includes('authentication token')) {
    return 'Your session has expired. Please sign in again.';
  }
  
  if (error.message?.includes('401')) {
    return 'Authentication failed. Please sign in again.';
  }
  
  if (error.message?.includes('403')) {
    return 'You do not have permission to perform this action.';
  }
  
  return error.message || 'An error occurred. Please try again.';
}