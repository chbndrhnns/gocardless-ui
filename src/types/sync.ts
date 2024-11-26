export interface SyncStatus {
  gocardlessId: string;
  gocardlessName: string;
  lunchmoneyName: string;
  lastSync: string | null;
  nextSync: string;
  lastSyncStatus: 'success' | 'error' | 'pending' | null;
  lastSyncTransactions: number;
  isSyncing: boolean;
}