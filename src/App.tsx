import { useState } from 'react';
import { Settings, RefreshCw } from 'lucide-react';
import { SyncDashboard } from './components/SyncDashboard';
import { SettingsView } from './components/SettingsView';

function App() {
  const [activeTab, setActiveTab] = useState<'sync' | 'settings'>('sync');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Add refresh logic here
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">GoCardless Sync</h1>
            <p className="mt-1 text-sm text-gray-500">
              Sync your bank transactions with Lunch Money
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        <div className="mb-8">
          <nav className="flex space-x-4" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('sync')}
              className={`px-3 py-2 font-medium text-sm rounded-md ${
                activeTab === 'sync'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Sync Status
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`inline-flex items-center px-3 py-2 font-medium text-sm rounded-md ${
                activeTab === 'settings'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </button>
          </nav>
        </div>

        {activeTab === 'sync' ? <SyncDashboard /> : <SettingsView />}
      </div>
    </div>
  );
}

export default App;