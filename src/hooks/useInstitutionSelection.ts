import {useState} from 'react';
import {createRequisition} from '../services/api';
import type {Institution} from '../types/gocardless';

export function useInstitutionSelection() {
    const [isCreatingRequisition, setIsCreatingRequisition] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleInstitutionSelect = async (institution: Institution) => {
        setIsCreatingRequisition(true);
        setError(null);

        try {
            const params = {
                institutionId: institution.id,
                redirectUrl: `${window.location.origin}/settings`,
                reference: `connect_${Date.now()}`,
                userLanguage: navigator.language.split('-')[0] || 'en',
            };

            const requisition = await createRequisition(params);
            if (requisition.link) {
                window.location.href = requisition.link;
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create bank connection');
        } finally {
            setIsCreatingRequisition(false);
        }
    };

    return {
        handleInstitutionSelect,
        isCreatingRequisition,
        error,
    };
}