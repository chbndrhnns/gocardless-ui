import React, { useState, useEffect } from 'react';
import { PlusCircle, RefreshCw } from 'lucide-react';
import { RequisitionCard } from './components/RequisitionCard';
import { fetchRequisitions } from './services/api';
import type { Requisition } from './types/gocardless';

function App() {
  const [requisitions, setRequisitions] = useState<Requisition[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRequisitions = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await fetchRequisitions();
      setRequisitions(data.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLinkClick = (link: string) => {
    window.open(link, '_blank');
  };

  const handleNewConnection = () => {
    // This would typically initiate a new requisition
    // We'll implement this in the next step
    console.log('Starting new connection...');
  };

  useEffect(() => {
    loadRequisitions();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Bank Connections</h1>
              <p className="mt-1 text-sm text-gray-500">
                Manage your bank account connections and view their status
              </p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={loadRequisitions}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </button>
              <button
                onClick={handleNewConnection}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusCircle className="h-4 w-4 mr-2" />
                New Connection
              </button>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        ) : requisitions.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900">No bank connections found</h3>
            <p className="mt-2 text-gray-500">Start by connecting your first bank account.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {requisitions.map((requisition) => (
              <RequisitionCard
                key={requisition.id}
                requisition={requisition}
                onLinkClick={handleLinkClick}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;