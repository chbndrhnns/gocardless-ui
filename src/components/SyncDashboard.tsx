import { useState, useEffect } from 'react';
import { Play, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';
import type { SyncStatus } from '../types/sync';
import {API_CONFIG} from "../config/api.ts";

const defaultSyncStatus = {
  lastSyncStatus: 'unknown', // or any meaningful default status
  lastSync: null,
  nextSync: null,
  lastSyncTransactions: 0,
  isSyncing: false,
};

export function SyncDashboard() {
  const [syncStatus, setSyncStatus] = useState<SyncStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSyncStatus();
    const interval = setInterval(fetchSyncStatus, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchSyncStatus = async () => {
    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/sync/status`);
      if (!response.ok) throw new Error('Failed to fetch sync status');
      const data = await response.json();

      const updatedAccounts = data.accounts.map((account: Partial<SyncStatus>) => ({
      ...defaultSyncStatus,
      ...account,
    }));

      setSyncStatus(updatedAccounts);
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {syncStatus.map((account) => (
          <div
            key={account.gocardlessId}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {account.gocardlessName}
              </h3>
              <div className={`flex items-center ${
                account.lastSyncStatus === 'success'
                  ? 'text-green-600'
                  : account.lastSyncStatus === 'error'
                  ? 'text-red-600'
                  : 'text-gray-400'
              }`}>
                {account.lastSyncStatus === 'success' && <CheckCircle className="h-5 w-5" />}
                {account.lastSyncStatus === 'error' && <AlertCircle className="h-5 w-5" />}
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Last Sync</p>
                <p className="text-gray-900">
                  {account.lastSync
                    ? formatDistanceToNow(new Date(account.lastSync), { addSuffix: true })
                    : 'Never'}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500">Next Scheduled Sync</p>
                <p className="text-gray-900">
                  {format(new Date(account.nextSync), 'MMM d, yyyy HH:mm')}
                </p>
              </div>

              {account.lastSyncTransactions > 0 && (
                <div>
                  <p className="text-sm text-gray-500">Last Sync Results</p>
                  <p className="text-gray-900">
                    {account.lastSyncTransactions} transactions synced
                  </p>
                </div>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100">
              <button
                onClick={() => triggerSync(account.gocardlessId)}
                disabled={account.isSyncing}
                className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {account.isSyncing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Syncing...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Sync Now
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {syncStatus.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Connected Accounts</h3>
          <p className="text-gray-500">
            Go to Settings to connect your bank accounts and start syncing.
          </p>
        </div>
      )}
    </div>
  );
}