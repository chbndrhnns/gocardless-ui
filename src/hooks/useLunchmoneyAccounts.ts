import {useEffect, useState} from 'react';
import {fetchLunchmoneyAssets, linkLunchmoneyAccount, unlinkLunchmoneyAccount} from '../services/lunchmoney';
import type {LunchmoneyAsset} from '../types/lunchmoney';

export function useLunchmoneyAccounts() {
    const [accounts, setAccounts] = useState<LunchmoneyAsset[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const handleLinkAccounts = async (gocardlessId: string, lunchmoneyId: number) => {
        try {
            await linkLunchmoneyAccount(lunchmoneyId, gocardlessId);
            await loadAccounts();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to link accounts');
        }
    };

    const loadAccounts = async () => {
        setIsLoading(true);
        try {
            const data = await fetchLunchmoneyAssets();
            setAccounts(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load Lunchmoney accounts');
        } finally {
            setIsLoading(false);
        }
    };


    const handleUnlinkAccount = async (lunchmoneyId: number, gocardlessId: string) => {
        try {
            await unlinkLunchmoneyAccount(lunchmoneyId, gocardlessId);
            await loadAccounts();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to unlink account');
        }
    };

    useEffect(() => {
        loadAccounts();
    }, []);

    return {
        accounts,
        isLoading,
        error,
        handleLinkAccounts,
        handleUnlinkAccount,
    };
}