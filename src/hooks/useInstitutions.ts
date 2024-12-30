import {useCallback, useState} from 'react';
import {fetchInstitutions} from '../services/api';
import {useStore} from '../store/store';

export function useInstitutions(country: string) {
    const {institutions, setInstitutions} = useStore();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadInstitutions = useCallback(async (forceRefresh = false) => {
        // Return cached data if available
        if (!forceRefresh && institutions[country]) {
            return;
        }

        setIsLoading(true);
        setError(null);
        try {
            const data = await fetchInstitutions(country);
            setInstitutions(country, data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load institutions');
        } finally {
            setIsLoading(false);
        }
    }, [country, institutions, setInstitutions]);

    return {
        institutions: institutions[country] || [],
        isLoading,
        error,
        loadInstitutions,
    };
}