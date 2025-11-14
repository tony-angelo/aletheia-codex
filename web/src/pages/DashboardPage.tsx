import React, { useState, useEffect } from 'react';
import { collection, query, where, getDocs, orderBy, limit } from 'firebase/firestore';
import { db, auth } from '../firebase/config';

interface Stats {
  totalNotes: number;
  totalEntities: number;
  totalRelationships: number;
  recentNotes: Array<{
    id: string;
    content: string;
    status: string;
    createdAt: any;
  }>;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<Stats>({
    totalNotes: 0,
    totalEntities: 0,
    totalRelationships: 0,
    recentNotes: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const user = auth.currentUser;
      if (!user) return;

      // Get total notes
      const notesQuery = query(
        collection(db, 'notes'),
        where('user_id', '==', user.uid)
      );
      const notesSnapshot = await getDocs(notesQuery);

      // Get recent notes
      const recentQuery = query(
        collection(db, 'notes'),
        where('user_id', '==', user.uid),
        orderBy('createdAt', 'desc'),
        limit(5)
      );
      const recentSnapshot = await getDocs(recentQuery);

      // Get review queue items
      const reviewQuery = query(
        collection(db, 'review_queue'),
        where('user_id', '==', user.uid)
      );
      const reviewSnapshot = await getDocs(reviewQuery);

      // Count entities and relationships
      let entityCount = 0;
      let relationshipCount = 0;
      reviewSnapshot.forEach((doc) => {
        const data = doc.data();
        if (data.type === 'entity') entityCount++;
        if (data.type === 'relationship') relationshipCount++;
      });

      setStats({
        totalNotes: notesSnapshot.size,
        totalEntities: entityCount,
        totalRelationships: relationshipCount,
        recentNotes: recentSnapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        })) as any,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Overview of your knowledge graph activity
        </p>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-indigo-100 rounded-lg p-3">
              <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Notes</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalNotes}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Entities</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalEntities}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
              <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Relationships</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalRelationships}</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Recent Notes */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Notes</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {stats.recentNotes.map((note) => (
            <div key={note.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-gray-900 line-clamp-2">{note.content}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    {note.createdAt?.toDate?.()?.toLocaleDateString() || 'Unknown date'}
                  </p>
                </div>
                <span className={`ml-4 px-2 py-1 text-xs font-medium rounded-full ${
                  note.status === 'completed' ? 'bg-green-100 text-green-800' :
                  note.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {note.status}
                </span>
              </div>
            </div>
          ))}
          {stats.recentNotes.length === 0 && (
            <div className="px-6 py-8 text-center text-gray-500">
              No notes yet. Create your first note to get started!
            </div>
          )}
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <a
          href="/notes"
          className="block bg-indigo-600 text-white rounded-lg p-6 hover:bg-indigo-700 transition-colors"
        >
          <h3 className="font-semibold mb-2">Create Note</h3>
          <p className="text-sm text-indigo-100">Add a new note to your knowledge graph</p>
        </a>
        <a
          href="/review"
          className="block bg-green-600 text-white rounded-lg p-6 hover:bg-green-700 transition-colors"
        >
          <h3 className="font-semibold mb-2">Review Queue</h3>
          <p className="text-sm text-green-100">Approve or reject extracted entities</p>
        </a>
        <a
          href="/graph"
          className="block bg-purple-600 text-white rounded-lg p-6 hover:bg-purple-700 transition-colors"
        >
          <h3 className="font-semibold mb-2">Browse Graph</h3>
          <p className="text-sm text-purple-100">Explore your knowledge graph</p>
        </a>
      </div>
    </div>
  );
};

export default DashboardPage;