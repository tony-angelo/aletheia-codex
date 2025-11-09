import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Navigation from './components/Navigation';
import NotesPage from './pages/NotesPage';
import ReviewPage from './pages/ReviewPage';
import GraphPage from './pages/GraphPage';
import './App.css';

function App() {
  const { user, loading, signIn } = useAuth();

  // Handle mock authentication for development
  const handleSignIn = () => {
    signIn('demo-user');
  };


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
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              AletheiaCodex
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              AI-powered Knowledge Extraction & Review
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
              <p>&copy; 2024 AletheiaCodex. Sprint 4 Note Input & AI Processing.</p>
              <p className="mt-1">
                Built with React, TypeScript, and Firebase.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;