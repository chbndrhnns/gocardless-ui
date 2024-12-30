import {useState} from 'react';
import {PlusCircle, RefreshCw} from 'lucide-react';
import {AddBankDialog} from './AddBankDialog';
import {AccountsTable} from './AccountsTable';
import {useRequisitions} from '../hooks/useRequisitions';
import {useLunchmoneyAccounts} from '../hooks/useLunchmoneyAccounts';
import {useInstitutions} from '../hooks/useInstitutions';
import {useInstitutionSelection} from '../hooks/useInstitutionSelection';

export function SettingsView() {
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [selectedCountry, setSelectedCountry] = useState('de');

    const {
        requisitions,
        requisitionDetails,
        refresh: refreshRequisitions,
        handleDeleteRequisition,
        isLoading: isLoadingRequisitions,
        error: requisitionsError,
    } = useRequisitions();

    const {
        institutions,
        isLoading: isLoadingInstitutions,
        error: institutionsError,
        loadInstitutions,
    } = useInstitutions();

    const {
        accounts: lunchmoneyAccounts,
        isLoading: isLoadingLunchmoney,
        refresh: refreshLunchmoneyAccounts,
        handleLinkAccounts,
        handleUnlinkAccount,
    } = useLunchmoneyAccounts();

    const {
        handleInstitutionSelect,
        isCreatingRequisition,
        error: institutionSelectionError,
    } = useInstitutionSelection();

    const handleCountryChange = (country: string) => {
        setSelectedCountry(country);
        loadInstitutions(country);
    };

    const handleOpenDialog = () => {
        setIsDialogOpen(true);
        loadInstitutions(selectedCountry);
    };

    const handleRefresh = async () => {
        await Promise.all([
            refreshRequisitions(),
            refreshLunchmoneyAccounts()
        ]);
    };

    requisitions.filter(req => req.status === 'CR' || req.status === 'LN');
    requisitions.filter(req => req.status !== 'CR' && req.status !== 'LN');

    return (
        <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">Bank Connections</h2>
                        <p className="mt-1 text-sm text-gray-500">
                            Manage your connected bank accounts
                        </p>
                    </div>
                    <div className="flex space-x-4">
                        <button
                            onClick={handleRefresh}
                            disabled={isLoadingRequisitions || isLoadingLunchmoney}
                            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            <RefreshCw
                                className={`h-4 w-4 mr-2 ${(isLoadingRequisitions || isLoadingLunchmoney) ? 'animate-spin' : ''}`}/>
                            Refresh
                        </button>
                        <button
                            onClick={handleOpenDialog}
                            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                            <PlusCircle className="h-4 w-4 mr-2"/>
                            New Connection
                        </button>
                    </div>
                </div>

                {requisitionsError ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                        {requisitionsError}
                    </div>
                ) : (
                    <AccountsTable
                        accounts={Object.values(requisitionDetails)}
                        lunchmoneyAccounts={lunchmoneyAccounts}
                        onLinkAccount={handleLinkAccounts}
                        onDeleteAccount={handleDeleteRequisition}
                        onUnlinkAccount={handleUnlinkAccount}
                        isLoading={isLoadingRequisitions || isLoadingLunchmoney}
                    />
                )}
            </div>

            <AddBankDialog
                isOpen={isDialogOpen}
                onClose={() => setIsDialogOpen(false)}
                selectedCountry={selectedCountry}
                onCountryChange={handleCountryChange}
                onInstitutionSelect={handleInstitutionSelect}
                isCreatingRequisition={isCreatingRequisition}
                institutions={institutions}
                isLoading={isLoadingInstitutions}
                error={institutionsError || institutionSelectionError}
            />
        </div>
    );
}