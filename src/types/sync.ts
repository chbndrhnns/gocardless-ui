export interface RateLimit {
    limit: number;
    remaining: number;
    reset: string;
}

export interface SyncStatus {
    gocardlessId: string;
    gocardlessName: string;
    institutionName: string;
    lunchmoneyName: string;
    lastSync: string | null;
    nextSync: string;
    lastSyncStatus: 'success' | 'error' | 'pending' | null;
    lastSyncTransactions: number;
    isSyncing: boolean;
    rateLimit: RateLimit;
}