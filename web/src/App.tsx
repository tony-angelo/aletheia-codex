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
              <p>&copy; 2025 AletheiaCodex. Sprint 4.5 - Firebase Authentication.</p>
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