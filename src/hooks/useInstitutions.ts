import {useState} from 'react';
import {fetchInstitutions} from '../services/api';
import type {Institution} from '../types/gocardless';

export function useInstitutions() {
    const [institutions, setInstitutions] = useState<Institution[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadInstitutions = async (country: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await fetchInstitutions(country);
            setInstitutions(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load institutions');
        } finally {
            setIsLoading(false);
        }
    };

    return {
        institutions,
        isLoading,
        error,
        loadInstitutions,
    };
}