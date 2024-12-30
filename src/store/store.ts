import {create} from 'zustand';
import type {Institution, Requisition, RequisitionDetails} from '../types/gocardless';
import type {LunchmoneyAsset} from '../types/lunchmoney';
import type {SyncStatus} from '../types/sync';

interface Store {
    // Sync Status
    syncStatus: SyncStatus[];
    setSyncStatus: (status: SyncStatus[]) => void;

    // Requisitions
    requisitions: Requisition[];
    requisitionDetails: Record<string, RequisitionDetails>;
    setRequisitions: (requisitions: Requisition[]) => void;
    setRequisitionDetails: (id: string, details: RequisitionDetails) => void;

    // Institutions
    institutions: Record<string, Institution[]>;
    setInstitutions: (country: string, institutions: Institution[]) => void;

    // Lunchmoney Assets
    lunchmoneyAssets: LunchmoneyAsset[];
    setLunchmoneyAssets: (assets: LunchmoneyAsset[]) => void;
}

export const useStore = create<Store>((set) => ({
    // Sync Status
    syncStatus: [],
    setSyncStatus: (status) => set({syncStatus: status}),

    // Requisitions
    requisitions: [],
    requisitionDetails: {},
    setRequisitions: (requisitions) => set({requisitions}),
    setRequisitionDetails: (id, details) =>
        set((state) => ({
            requisitionDetails: {
                ...state.requisitionDetails,
                [id]: details
            }
        })),

    // Institutions
    institutions: {},
    setInstitutions: (country, institutions) =>
        set((state) => ({
            institutions: {
                ...state.institutions,
                [country]: institutions
            }
        })),

    // Lunchmoney Assets
    lunchmoneyAssets: [],
    setLunchmoneyAssets: (assets) => set({lunchmoneyAssets: assets}),
}));