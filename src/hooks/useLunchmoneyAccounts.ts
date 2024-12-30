import {useEffect, useState} from 'react';
import {fetchLunchmoneyAssets, linkLunchmoneyAccount, unlinkLunchmoneyAccount} from '../services/lunchmoney';
import {useStore} from '../store/store';

export function useLunchmoneyAccounts() {
    const {lunchmoneyAssets, setLunchmoneyAssets} = useStore();
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Only load data if we don't have any assets yet
    useEffect(() => {
        if (lunchmoneyAssets.length === 0) {
            refresh();
        } else {
            setIsLoading(false);
        }
    }, [lunchmoneyAssets.length]);

    const refresh = async () => {
        setIsLoading(true);
        try {
            const data = await fetchLunchmoneyAssets();
            setLunchmoneyAssets(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load Lunchmoney accounts');
        } finally {
            setIsLoading(false);
        }
    };

    const handleLinkAccounts = async (gocardlessId: string, lunchmoneyId: number) => {
        try {
            await linkLunchmoneyAccount(lunchmoneyId, gocardlessId);
            await refresh();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to link accounts');
        }
    };

    const handleUnlinkAccount = async (lunchmoneyId: number, gocardlessId: string) => {
        try {
            await unlinkLunchmoneyAccount(lunchmoneyId, gocardlessId);
            await refresh();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to unlink account');
        }
    };

    return {
        accounts: lunchmoneyAssets,
        isLoading,
        error,
        refresh,
        handleLinkAccounts,
        handleUnlinkAccount,
    };
}