import {useEffect, useState} from 'react';
import {createRequisition, deleteRequisition, fetchRequisitionDetails, fetchRequisitions} from '../services/api';
import type {Requisition, RequisitionDetails} from '../types/gocardless';

export function useRequisitions() {
    const [requisitions, setRequisitions] = useState<Requisition[]>([]);
    const [requisitionDetails, setRequisitionDetails] = useState<Record<string, RequisitionDetails>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDeletingRequisition, setIsDeletingRequisition] = useState<string | null>(null);
    const [isCreatingRequisition, setIsCreatingRequisition] = useState(false);

    const refresh = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await fetchRequisitions();
            const sortedRequisitions = data.results.sort((a, b) =>
                new Date(b.created).getTime() - new Date(a.created).getTime()
            );
            setRequisitions(sortedRequisitions);

            sortedRequisitions.forEach(req => {
                loadRequisitionDetails(req.id);
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    const loadRequisitionDetails = async (requisitionId: string) => {
        try {
            const details = await fetchRequisitionDetails(requisitionId);
            setRequisitionDetails(prev => ({
                ...prev,
                [requisitionId]: details
            }));
        } catch (error) {
            console.error(`Error loading details for requisition ${requisitionId}:`, error);
        }
    };

    const handleLinkClick = (link: string) => {
        window.open(link, '_blank');
    };

    const handleDeleteRequisition = async (id: string) => {
        setIsDeletingRequisition(id);
        try {
            await deleteRequisition(id);
            setRequisitions(prev => prev.filter(req => req.id !== id));
            setRequisitionDetails(prev => {
                const updated = {...prev};
                delete updated[id];
                return updated;
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete bank connection');
        } finally {
            setIsDeletingRequisition(null);
        }
    };

    const handleInstitutionSelect = async (params: {
        institutionId: string;
        redirectUrl: string;
        reference: string;
        userLanguage: string;
    }) => {
        setIsCreatingRequisition(true);
        try {
            const requisition = await createRequisition(params);
            setRequisitions(prev => [requisition, ...prev]);
            if (requisition.link) {
                window.location.href = requisition.link;
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create bank connection');
        } finally {
            setIsCreatingRequisition(false);
        }
    };

    useEffect(() => {
        refresh();
    }, []);

    return {
        requisitions,
        requisitionDetails,
        isLoading,
        error,
        refresh,
        handleLinkClick,
        handleDeleteRequisition,
        isDeletingRequisition,
        handleInstitutionSelect,
        isCreatingRequisition,
    };
}