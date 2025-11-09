# Sprint 4.5 Implementation Guide: Firebase Authentication

**Sprint**: Sprint 4.5 - Firebase Authentication Implementation  
**Duration**: 4-6 hours  
**Priority**: CRITICAL  
**Prerequisites**: Sprint 4 complete, Firebase Auth providers enabled

---

## 🎯 Sprint Objectives

Replace mock authentication with real Firebase Authentication, enabling:
1. Email/Password sign-in
2. Google Sign-In
3. Proper user authentication for all features
4. Notes persisting to Firestore
5. Review queue working with real users

---

## 📋 What We're Fixing

### Current Problem
- Mock authentication only (demo user)
- Notes don't persist to Firestore
- Security rules reject writes (no valid auth token)
- Can't test end-to-end workflow

### Root Cause
```typescript
// Current: Mock authentication
const signInMock = (userId: string = 'test-user') => {
  setUser({ uid: userId, ... }); // No real Firebase token
}
```

Firestore security rules require real Firebase Auth:
```javascript
allow create: if isAuthenticated() && request.resource.data.userId == request.auth.uid;
```

Mock auth has no `request.auth.uid` → Writes rejected → Notes never created

---

## 🔧 What We're Building

### 1. Email/Password Sign-In
- Sign-in form with email and password fields
- Sign-up form for new users
- Password reset functionality
- Email verification (optional)
- Error handling for invalid credentials

### 2. Google Sign-In
- "Sign in with Google" button
- OAuth popup flow
- Automatic account creation
- Profile information sync

### 3. Authentication State Management
- Real Firebase Auth state listener
- Persistent sessions
- Automatic token refresh
- Sign-out functionality

### 4. Protected Routes
- Redirect to sign-in if not authenticated
- Preserve intended destination
- Handle auth state changes

---

## 📊 Firebase Configuration

### Firebase Web App Config (Provided by User)
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyCPUO0yS3_1BiJyMP96TgDy_tJgrpEvPTY",
  authDomain: "aletheia-codex-prod.firebaseapp.com",
  projectId: "aletheia-codex-prod",
  storageBucket: "aletheia-codex-prod.firebasestorage.app",
  messagingSenderId: "679360092359",
  appId: "1:679360092359:web:9af0ba475c8d03538686e2"
};
```

### Google OAuth Client ID
```
679360092359-76o7ffrihe56t2kq0qp9omvdm48bjkvj.apps.googleusercontent.com
```

### Authorized Domains (Verified)
- ✅ aletheia-codex-prod.web.app
- ✅ aletheia-codex-prod.firebaseapp.com
- ✅ localhost

---

## 🏗️ Implementation Plan

### Phase 1: Environment Configuration (30 minutes)

#### 1.1 Create Production Environment File
**File**: `web/.env.production`

```bash
# Firebase Configuration
REACT_APP_FIREBASE_API_KEY=AIzaSyCPUO0yS3_1BiJyMP96TgDy_tJgrpEvPTY
REACT_APP_FIREBASE_AUTH_DOMAIN=aletheia-codex-prod.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=aletheia-codex-prod
REACT_APP_FIREBASE_STORAGE_BUCKET=aletheia-codex-prod.firebasestorage.app
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=679360092359
REACT_APP_FIREBASE_APP_ID=1:679360092359:web:9af0ba475c8d03538686e2

# Google OAuth
REACT_APP_GOOGLE_CLIENT_ID=679360092359-76o7ffrihe56t2kq0qp9omvdm48bjkvj.apps.googleusercontent.com

# API Endpoints
REACT_APP_ORCHESTRATION_URL=https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestration
REACT_APP_REVIEW_API_URL=https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api
REACT_APP_NOTES_API_URL=https://us-central1-aletheia-codex-prod.cloudfunctions.net/notes-api
```

#### 1.2 Create Development Environment File
**File**: `web/.env.development`

```bash
# Same as production for now
REACT_APP_FIREBASE_API_KEY=AIzaSyCPUO0yS3_1BiJyMP96TgDy_tJgrpEvPTY
REACT_APP_FIREBASE_AUTH_DOMAIN=aletheia-codex-prod.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=aletheia-codex-prod
REACT_APP_FIREBASE_STORAGE_BUCKET=aletheia-codex-prod.firebasestorage.app
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=679360092359
REACT_APP_FIREBASE_APP_ID=1:679360092359:web:9af0ba475c8d03538686e2
REACT_APP_GOOGLE_CLIENT_ID=679360092359-76o7ffrihe56t2kq0qp9omvdm48bjkvj.apps.googleusercontent.com
```

#### 1.3 Update Firebase Config
**File**: `web/src/firebase/config.ts`

```typescript
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { getFunctions } from 'firebase/functions';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
};

// Validate configuration
if (!firebaseConfig.apiKey || !firebaseConfig.authDomain) {
  throw new Error('Firebase configuration is missing. Check your .env file.');
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize services
export const db = getFirestore(app);
export const auth = getAuth(app);
export const functions = getFunctions(app);

export default app;
```

#### 1.4 Update .gitignore
**File**: `web/.gitignore`

Add:
```
# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local
```

---

### Phase 2: Authentication Hook (1 hour)

#### 2.1 Update useAuth Hook
**File**: `web/src/hooks/useAuth.ts`

```typescript
import { useState, useEffect } from 'react';
import { 
  User,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut as firebaseSignOut,
  sendPasswordResetEmail,
  updateProfile
} from 'firebase/auth';
import { auth } from '../firebase/config';

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

  // Sign in with email and password
  const signInWithEmail = async (email: string, password: string) => {
    try {
      setError(null);
      const result = await signInWithEmailAndPassword(auth, email, password);
      return result.user;
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  // Sign up with email and password
  const signUpWithEmail = async (email: string, password: string, displayName?: string) => {
    try {
      setError(null);
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update profile with display name if provided
      if (displayName && result.user) {
        await updateProfile(result.user, { displayName });
      }
      
      return result.user;
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  // Sign in with Google
  const signInWithGoogle = async () => {
    try {
      setError(null);
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      return result.user;
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  // Sign out
  const signOut = async () => {
    try {
      setError(null);
      await firebaseSignOut(auth);
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  // Reset password
  const resetPassword = async (email: string) => {
    try {
      setError(null);
      await sendPasswordResetEmail(auth, email);
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  return {
    user,
    loading,
    error,
    signInWithEmail,
    signUpWithEmail,
    signInWithGoogle,
    signOut,
    resetPassword,
  };
};
```

---

### Phase 3: Authentication UI Components (2 hours)

#### 3.1 Create Sign-In Component
**File**: `web/src/components/SignIn.tsx`

```typescript
import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

interface SignInProps {
  onSuccess?: () => void;
  onSwitchToSignUp?: () => void;
}

const SignIn: React.FC<SignInProps> = ({ onSuccess, onSwitchToSignUp }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showResetPassword, setShowResetPassword] = useState(false);

  const { signInWithEmail, signInWithGoogle, resetPassword } = useAuth();

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await signInWithEmail(email, password);
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Failed to sign in');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);

    try {
      await signInWithGoogle();
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Failed to sign in with Google');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async () => {
    if (!email) {
      setError('Please enter your email address');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await resetPassword(email);
      alert('Password reset email sent! Check your inbox.');
      setShowResetPassword(false);
    } catch (err: any) {
      setError(err.message || 'Failed to send reset email');
    } finally {
      setLoading(false);
    }
  };

  if (showResetPassword) {
    return (
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Reset Password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your email to receive a password reset link
          </p>
        </div>

        <div className="mt-8 space-y-6">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email address"
            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            disabled={loading}
          />

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={handleResetPassword}
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
            <button
              onClick={() => setShowResetPassword(false)}
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md w-full space-y-8">
      <div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Sign in to AletheiaCodex
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          AI-powered Knowledge Extraction & Review
        </p>
      </div>

      <form className="mt-8 space-y-6" onSubmit={handleEmailSignIn}>
        <div className="rounded-md shadow-sm -space-y-px">
          <div>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              required
              className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              disabled={loading}
            />
          </div>
          <div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              disabled={loading}
            />
          </div>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="flex items-center justify-between">
          <div className="text-sm">
            <button
              type="button"
              onClick={() => setShowResetPassword(true)}
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Forgot your password?
            </button>
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </div>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-50 text-gray-500">Or continue with</span>
            </div>
          </div>

          <div className="mt-6">
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span className="ml-2">Sign in with Google</span>
            </button>
          </div>
        </div>

        {onSwitchToSignUp && (
          <div className="text-center">
            <button
              type="button"
              onClick={onSwitchToSignUp}
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Don't have an account? Sign up
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default SignIn;
```

#### 3.2 Create Sign-Up Component
**File**: `web/src/components/SignUp.tsx`

```typescript
import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

interface SignUpProps {
  onSuccess?: () => void;
  onSwitchToSignIn?: () => void;
}

const SignUp: React.FC<SignUpProps> = ({ onSuccess, onSwitchToSignIn }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { signUpWithEmail, signInWithGoogle } = useAuth();

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await signUpWithEmail(email, password, displayName);
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);

    try {
      await signInWithGoogle();
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Failed to sign in with Google');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full space-y-8">
      <div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Start building your knowledge graph
        </p>
      </div>

      <form className="mt-8 space-y-6" onSubmit={handleSignUp}>
        <div className="rounded-md shadow-sm space-y-3">
          <div>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Display name (optional)"
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              disabled={loading}
            />
          </div>
          <div>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              disabled={loading}
            />
          </div>
          <div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password (min 6 characters)"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              disabled={loading}
            />
          </div>
          <div>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm password"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              disabled={loading}
            />
          </div>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div>
          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Sign up'}
          </button>
        </div>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-50 text-gray-500">Or continue with</span>
            </div>
          </div>

          <div className="mt-6">
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span className="ml-2">Sign up with Google</span>
            </button>
          </div>
        </div>

        {onSwitchToSignIn && (
          <div className="text-center">
            <button
              type="button"
              onClick={onSwitchToSignIn}
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Already have an account? Sign in
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default SignUp;
```

---

### Phase 4: Update App.tsx (30 minutes)

#### 4.1 Replace Mock Auth with Real Auth
**File**: `web/src/App.tsx`

```typescript
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Navigation from './components/Navigation';
import SignIn from './components/SignIn';
import SignUp from './components/SignUp';
import NotesPage from './pages/NotesPage';
import ReviewPage from './pages/ReviewPage';
import GraphPage from './pages/GraphPage';
import './App.css';

function App() {
  const { user, loading } = useAuth();
  const [showSignUp, setShowSignUp] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="ml-2 text-gray-600">Loading application...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        {showSignUp ? (
          <SignUp
            onSuccess={() => {}}
            onSwitchToSignIn={() => setShowSignUp(false)}
          />
        ) : (
          <SignIn
            onSuccess={() => {}}
            onSwitchToSignUp={() => setShowSignUp(true)}
          />
        )}
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <Navigation />

        {/* Main Content */}
        <main className="py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/notes" />} />
            <Route path="/notes" element={<NotesPage />} />
            <Route path="/review" element={<ReviewPage />} />
            <Route path="/graph" element={<GraphPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 py-8 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center text-sm text-gray-500">
              <p>© 2025 AletheiaCodex. Sprint 4.5 - Firebase Authentication.</p>
              <p className="mt-1">
                Signed in as: {user.email || user.displayName || 'User'}
              </p>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

---

### Phase 5: Update Navigation Component (15 minutes)

#### 5.1 Add Sign Out Button
**File**: `web/src/components/Navigation.tsx`

Update to include sign-out functionality:

```typescript
import { useAuth } from '../hooks/useAuth';

// Inside component:
const { user, signOut } = useAuth();

const handleSignOut = async () => {
  if (window.confirm('Are you sure you want to sign out?')) {
    await signOut();
  }
};

// Add to user menu:
<button
  onClick={handleSignOut}
  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
>
  Sign out
</button>
```

---

### Phase 6: Testing (1 hour)

#### 6.1 Local Testing
```bash
cd web
npm start
```

**Test Cases**:
1. ✅ Sign up with email/password
2. ✅ Sign in with email/password
3. ✅ Sign in with Google
4. ✅ Password reset
5. ✅ Sign out
6. ✅ Create note (should persist to Firestore)
7. ✅ View note history
8. ✅ Navigate between pages

#### 6.2 Firestore Verification
1. Open Firebase Console → Firestore
2. Check `notes` collection
3. Verify notes are created with correct userId
4. Verify security rules allow access

---

### Phase 7: Deployment (30 minutes)

#### 7.1 Build Production
```bash
cd web
npm run build
```

#### 7.2 Deploy to Firebase Hosting
```bash
firebase deploy --only hosting
```

#### 7.3 Production Testing
1. Open: https://aletheia-codex-prod.web.app
2. Test sign-in/sign-up
3. Test note creation
4. Verify notes persist
5. Test review queue
6. Check production logs

---

## 🎯 Success Criteria

Sprint 4.5 is complete when:

- [ ] Email/password sign-in works
- [ ] Google Sign-In works
- [ ] Sign-up creates new users
- [ ] Password reset works
- [ ] Sign-out works
- [ ] Notes persist to Firestore
- [ ] Review queue works with real users
- [ ] Security rules properly enforced
- [ ] No mock authentication code remains
- [ ] Deployed to production
- [ ] Tested in production
- [ ] All tests passing

---

## 📊 Performance Targets

- Sign-in time: <2s
- Sign-up time: <3s
- Google Sign-In: <3s
- Token refresh: Automatic
- Session persistence: Yes

---

## 🔐 Security Checklist

- [ ] Firebase config in environment variables
- [ ] No secrets in code
- [ ] HTTPS only
- [ ] Firestore rules enforced
- [ ] Auth tokens validated
- [ ] Password requirements met (min 6 chars)
- [ ] Email verification (optional)

---

## 🐛 Common Issues & Solutions

### Issue: "Firebase: Error (auth/popup-blocked)"
**Solution**: User must allow popups for Google Sign-In

### Issue: "Firebase: Error (auth/email-already-in-use)"
**Solution**: User should sign in instead of sign up

### Issue: "Firebase: Error (auth/wrong-password)"
**Solution**: User should use password reset

### Issue: Notes still don't persist
**Solution**: Check Firestore security rules, verify auth token is being sent

---

## 📝 Documentation Updates

Update these files:
- [ ] README.md - Add authentication section
- [ ] DEPLOYMENT_GUIDE.md - Add .env.production setup
- [ ] USER_GUIDE.md - Add sign-in/sign-up instructions

---

**END OF IMPLEMENTATION GUIDE**