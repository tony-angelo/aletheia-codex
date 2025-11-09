import React, { useState } from 'react';
import { useAuth } from './hooks/useAuth';
import ReviewQueue from './components/ReviewQueue';
import BatchActions from './components/BatchActions';
import './App.css';

function App() {
  const { user, loading, signIn, signOut } = useAuth();
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());

  // Handle mock authentication for development
  const handleSignIn = () => {
    signIn('demo-user');
  };

  const handleSignOut = () => {
    signOut();
    setSelectedItems(new Set());
  };

  const handleActionComplete = () => {
    setSelectedItems(new Set());
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p className="ml-2 text-gray-600">Loading application...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              AletheiaCodex Review System
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Review AI-extracted entities and relationships
            </p>
          </div>
          <div className="mt-8 space-y-6">
            <div className="rounded-md shadow-sm">
              <button
                onClick={handleSignIn}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Sign In (Demo Mode)
              </button>
            </div>
            <div className="text-center text-xs text-gray-500">
              <p>This is a demo environment. Click "Sign In" to continue.</p>
              <p className="mt-1">In production, Firebase Authentication will be used.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                AletheiaCodex
              </h1>
              <p className="text-sm text-gray-600">
                AI Entity & Relationship Review System
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {user.displayName || user.email}
                </div>
                <div className="text-xs text-gray-500">
                  {user.email}
                </div>
              </div>
              <button
                onClick={handleSignOut}
                className="btn btn-outline text-sm"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        <ReviewQueue />
        <BatchActions 
          selectedItems={selectedItems}
          onActionComplete={handleActionComplete}
        />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-8 mt-16">
        <div className="container">
          <div className="text-center text-sm text-gray-500">
            <p>&copy; 2024 AletheiaCodex. Sprint 3 Review Queue & User Interface.</p>
            <p className="mt-1">
              Built with React, TypeScript, and Firebase.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;