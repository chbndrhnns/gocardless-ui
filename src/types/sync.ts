export interface SyncStatus {
  createdAt: string;
  gocardlessId: string;
  gocardlessName: string;
  lastSync: string | null;
  nextSync: string;
  lastSyncStatus: 'success' | 'error' | 'pending' | null;
  lastSyncTransactions: number;
  isSyncing: boolean;
}