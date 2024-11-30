import { useState } from 'react';
import { Play, Loader2, AlertTriangle } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';
import type { SyncStatus } from '../types/sync';

interface SyncTableProps {
  syncStatus: SyncStatus[];
  onSync: (accountId: string) => Promise<void>;
  onSyncAll: () => Promise<void>;
}

export function SyncTable({ syncStatus, onSync, onSyncAll }: SyncTableProps) {
  const [isSyncingAll, setIsSyncingAll] = useState(false);

  const isAnyRateLimited = syncStatus.some(
    account => account.rateLimit.remaining === 0
  );

  const handleSyncAll = async () => {
    setIsSyncingAll(true);
    try {
      await onSyncAll();
    } finally {
      setIsSyncingAll(false);
    }
  };

  return (
    <div className="overflow-x-auto">
      <div className="mb-4 flex justify-end">
        <button
          onClick={handleSyncAll}
          disabled={isSyncingAll || isAnyRateLimited}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {isSyncingAll ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Syncing All...
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-2" />
              Sync All
            </>
          )}
        </button>
      </div>

      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Account
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Last Sync
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Next Sync
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Rate Limit
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {syncStatus.map((account) => (
            <tr key={account.gocardlessId}>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">
                  {account.gocardlessName}
                </div>
                <div className="text-sm text-gray-500">
                  {account.lunchmoneyName}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {account.lastSync
                  ? formatDistanceToNow(new Date(account.lastSync), {
                      addSuffix: true,
                    })
                  : 'Never'}
                {account.lastSyncTransactions > 0 && (
                  <div className="text-xs text-gray-400">
                    {account.lastSyncTransactions} transactions
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {format(new Date(account.nextSync), 'MMM d, yyyy HH:mm')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">
                  {account.rateLimit.remaining} / {account.rateLimit.limit}
                </div>
                {account.rateLimit.remaining < account.rateLimit.limit * 0.2 && (
                  <div className="flex items-center text-xs text-yellow-600">
                    <AlertTriangle className="h-3 w-3 mr-1" />
                    Running low
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    account.lastSyncStatus === 'success'
                      ? 'bg-green-100 text-green-800'
                      : account.lastSyncStatus === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {account.lastSyncStatus || 'Never synced'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => onSync(account.gocardlessId)}
                  disabled={
                    account.isSyncing ||
                    (account.rateLimit.limit > 0 &&
                      account.rateLimit.remaining === 0)
                  }
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {account.isSyncing ? (
                    <>
                      <Loader2 className="h-3 w-3 mr-1.5 animate-spin" />
                      Syncing...
                    </>
                  ) : account.rateLimit.remaining === 0 ? (
                    <>
                      <AlertTriangle className="h-3 w-3 mr-1.5" />
                      Rate Limited
                    </>
                  ) : (
                    <>
                      <Play className="h-3 w-3 mr-1.5" />
                      Sync Now
                    </>
                  )}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}