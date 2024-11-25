import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { RefreshCw, Loader2 } from 'lucide-react';
import { API_CONFIG } from '../config/api';

interface SyncStatusProps {
  accountId: string;
  onSyncComplete?: () => void;
}

export function SyncStatus({ accountId, onSyncComplete }: SyncStatusProps) {
  const [lastSync, setLastSync] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSyncStatus = async () => {
    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/sync/status`);
      if (!response.ok) {
        throw new Error('Failed to fetch sync status');
      }
      const data = await response.json();
      setLastSync(data.lastSync);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sync status');
    }
  };

  const triggerSync = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/sync/trigger`, {
        method: 'POST',
        headers: API_CONFIG.headers,
        body: JSON.stringify({ accountId }),
      });

      if (!response.ok) throw new Error('Failed to trigger sync');
      
      await fetchSyncStatus();
      onSyncComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger sync');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSyncStatus();
  }, []);

  return (
    <div className="mt-4 space-y-2">
      {lastSync && (
        <p className="text-sm text-gray-500">
          Last synced: {format(new Date(lastSync), 'MMM d, yyyy HH:mm')}
        </p>
      )}
      
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      <button
        onClick={triggerSync}
        disabled={isLoading}
        className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Syncing...
          </>
        ) : (
          <>
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync Now
          </>
        )}
      </button>
    </div>
  );
}