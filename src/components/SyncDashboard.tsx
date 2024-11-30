import { useState, useEffect } from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';
import type { SyncStatus } from '../types/sync';
import { API_CONFIG } from '../config/api';
import { SyncTable } from './SyncTable';

export function SyncDashboard() {
  const [syncStatus, setSyncStatus] = useState<SyncStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSyncStatus();
    const interval = setInterval(fetchSyncStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchSyncStatus = async () => {
    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/sync/status`);
      if (!response.ok) throw new Error('Failed to fetch sync status');
      const data = await response.json();
      setSyncStatus(data.accounts);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const triggerSync = async (accountId: string) => {
    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accountId }),
      });
      if (!response.ok) throw new Error('Failed to trigger sync');
      await fetchSyncStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger sync');
    }
  };

  const triggerSyncAll = async () => {
    try {
      await Promise.all(syncStatus.map(account => triggerSync(account.gocardlessId)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to sync all accounts');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center text-red-700">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {syncStatus.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Connected Accounts
          </h3>
          <p className="text-gray-500">
            Go to Settings to connect your bank accounts and start syncing.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <SyncTable
            syncStatus={syncStatus}
            onSync={triggerSync}
            onSyncAll={triggerSyncAll}
          />
        </div>
      )}
    </div>
  );
}