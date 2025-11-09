import { useState, useEffect } from 'react';
import { auth } from '../services/firebase';
import { onAuthStateChanged, User } from 'firebase/auth';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(
      auth,
      (user) => {
        setUser(user);
        setLoading(false);
        setError(null);
      },
      (error) => {
        console.error('Auth state change error:', error);
        setError(error.message);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, []);

  // For development/testing purposes, allow setting a mock user
  const signInMock = (userId: string = 'test-user') => {
    setUser({
      uid: userId,
      email: `${userId}@example.com`,
      displayName: `Test User ${userId}`,
      photoURL: null,
      emailVerified: true,
      isAnonymous: false,
      metadata: {},
      providerData: [],
      refreshToken: '',
      tenantId: null,
      phoneNumber: null,
      providerId: 'mock',
      delete: async () => {},
      getIdToken: async () => 'mock-token',
      getIdTokenResult: async () => ({
        token: 'mock-token',
        claims: {},
        authTime: new Date().toISOString(),
        expirationTime: new Date(Date.now() + 3600000).toISOString(),
        issuedAtTime: new Date().toISOString(),
        signInProvider: 'mock',
        signInSecondFactor: null,
      }),
      reload: async () => {},
      toJSON: () => ({}),
    } as User);
    setLoading(false);
    setError(null);
  };

  const signOut = async () => {
    try {
      await auth.signOut();
    } catch (error) {
      console.error('Sign out error:', error);
      setError('Failed to sign out');
    }
  };

  return {
    user,
    loading,
    error,
    signIn: signInMock, // Replace with real sign-in implementation
    signOut,
  };
};