import {useEffect, useState} from 'react';
import {AlertCircle, AlertTriangle, CheckCircle, Loader2, Play, RefreshCw} from 'lucide-react';
import {format, formatDistance, formatDistanceToNow} from 'date-fns';
import type {SyncStatus} from '../types/sync';
import {API_CONFIG} from "../config/api";

export function SyncDashboard() {
    const [syncStatus, setSyncStatus] = useState<SyncStatus[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isSyncingAll, setIsSyncingAll] = useState(false);

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
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({accountId}),
            });
            if (!response.ok) throw new Error('Failed to trigger sync');
            await fetchSyncStatus();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to trigger sync');
        }
    };

    const syncAllAccounts = async () => {
        setIsSyncingAll(true);
        try {
            await Promise.all(syncStatus.map(account =>
                triggerSync(account.gocardlessId)
            ));
        } finally {
            setIsSyncingAll(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin"/>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                <div className="flex items-center">
                    <AlertCircle className="h-5 w-5 mr-2"/>
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="p-4 sm:p-6 border-b border-gray-200">
                    <div className="flex justify-between items-center">
                        <h2 className="text-lg font-semibold text-gray-900">Sync Status</h2>
                        <button
                            onClick={syncAllAccounts}
                            disabled={isSyncingAll || syncStatus.some(acc => acc.isSyncing)}
                            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {isSyncingAll ? (
                                <>
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin"/>
                                    Syncing All...
                                </>
                            ) : (
                                <>
                                    <RefreshCw className="h-4 w-4 mr-2"/>
                                    Sync All
                                </>
                            )}
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                        <tr>
                            <th scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Account
                            </th>
                            <th scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Last Sync
                            </th>
                            <th scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Rate Limits
                            </th>
                            <th scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Next Sync
                            </th>
                            <th scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th scope="col"
                                className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                        {syncStatus.map((account) => (
                            <tr key={account.gocardlessId}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        <div>
                                            <div className="text-sm font-medium text-gray-900">
                                                {account.gocardlessName}
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                {account.lunchmoneyName}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {account.lastSync
                                            ? formatDistanceToNow(new Date(account.lastSync), {addSuffix: true})
                                            : 'Never'}
                                    </div>
                                    {account.lastSyncTransactions > 0 && (
                                        <div className="text-sm text-gray-500">
                                            {account.lastSyncTransactions} transactions
                                        </div>
                                    )}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        <div className="text-sm text-gray-900">
                                            {account.rateLimit.remaining} / {account.rateLimit.limit}
                                        </div>
                                        {account.rateLimit.remaining < account.rateLimit.limit * 0.2 && (
                                            <AlertTriangle className="h-4 w-4 text-yellow-500 ml-2"/>
                                        )}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                        Resets {formatDistance(new Date(account.rateLimit.reset), new Date(), {addSuffix: true})}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {format(new Date(account.nextSync), 'MMM d, HH:mm')}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                        <span
                                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                account.lastSyncStatus === 'success'
                                                    ? 'bg-green-100 text-green-800'
                                                    : account.lastSyncStatus === 'error'
                                                        ? 'bg-red-100 text-red-800'
                                                        : 'bg-gray-100 text-gray-800'
                                            }`}>
                                            {account.lastSyncStatus === 'success' &&
                                                <CheckCircle className="h-3 w-3 mr-1"/>}
                                            {account.lastSyncStatus === 'error' &&
                                                <AlertCircle className="h-3 w-3 mr-1"/>}
                                            {account.lastSyncStatus || 'Never synced'}
                                        </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button
                                        onClick={() => triggerSync(account.gocardlessId)}
                                        disabled={account.isSyncing || (account.rateLimit.remaining === 0)}
                                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                                    >
                                        {account.isSyncing ? (
                                            <>
                                                <Loader2 className="h-3 w-3 mr-1 animate-spin"/>
                                                Syncing...
                                            </>
                                        ) : account.rateLimit.remaining === 0 ? (
                                            <>
                                                <AlertTriangle className="h-3 w-3 mr-1"/>
                                                Rate Limited
                                            </>
                                        ) : (
                                            <>
                                                <Play className="h-3 w-3 mr-1"/>
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
            </div>

            {
                syncStatus.length === 0 && (
                    <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Connected Accounts</h3>
                        <p className="text-gray-500">
                            Go to Settings to connect your bank accounts and start syncing.
                        </p>
                    </div>
                )
            }
        </div>
    )
        ;
}