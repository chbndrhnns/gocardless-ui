import {useState} from 'react';
import {PlusCircle} from 'lucide-react';
import {RequisitionCard} from './RequisitionCard';
import {AddBankDialog} from './AddBankDialog';
import {LunchmoneyAccountsList} from './LunchmoneyAccountsList';
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
        isLoading: isLoadingRequisitions,
        error: requisitionsError,
        handleLinkClick,
        handleDeleteRequisition,
        isDeletingRequisition,
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
        error: lunchmoneyError,
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

    const completedRequisitions = requisitions.filter(req => req.status === 'CR' || req.status === 'LN');
    const problematicRequisitions = requisitions.filter(req => req.status !== 'CR' && req.status !== 'LN');

    return (
        <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">Bank Connections</h2>
                        <p className="mt-1 text-sm text-gray-500">
                            Manage your connected bank accounts
                        </p>
                    </div>
                    <button
                        onClick={handleOpenDialog}
                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        <PlusCircle className="h-4 w-4 mr-2"/>
                        New Connection
                    </button>
                </div>

                {isLoadingRequisitions ? (
                    <div className="space-y-4">
                        {[...Array(2)].map((_, i) => (
                            <div key={i} className="animate-pulse bg-gray-100 h-32 rounded-lg"></div>
                        ))}
                    </div>
                ) : requisitionsError ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                        {requisitionsError}
                    </div>
                ) : (
                    <div className="space-y-6">
                        {completedRequisitions.length > 0 && (
                            <section>
                                <h3 className="text-lg font-medium text-gray-900 mb-4">Active Connections</h3>
                                <div className="space-y-4">
                                    {completedRequisitions.map((requisition) => (
                                        <RequisitionCard
                                            key={requisition.id}
                                            requisition={requisition}
                                            details={requisitionDetails[requisition.id]}
                                            onLinkClick={handleLinkClick}
                                            onDelete={handleDeleteRequisition}
                                            isDeleting={isDeletingRequisition === requisition.id}
                                        />
                                    ))}
                                </div>
                            </section>
                        )}

                        {problematicRequisitions.length > 0 && (
                            <section>
                                <h3 className="text-lg font-medium text-gray-900 mb-4">Pending or Problematic</h3>
                                <div className="space-y-4">
                                    {problematicRequisitions.map((requisition) => (
                                        <RequisitionCard
                                            key={requisition.id}
                                            requisition={requisition}
                                            details={requisitionDetails[requisition.id]}
                                            onLinkClick={handleLinkClick}
                                            onDelete={handleDeleteRequisition}
                                            isDeleting={isDeletingRequisition === requisition.id}
                                        />
                                    ))}
                                </div>
                            </section>
                        )}

                        {requisitions.length === 0 && (
                            <div className="text-center py-8">
                                <p className="text-gray-500">No bank connections found. Add your first connection to get
                                    started.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">Lunch Money Accounts</h2>
                    <p className="mt-1 text-sm text-gray-500">
                        Link your Lunch Money accounts with bank connections
                    </p>
                </div>

                <LunchmoneyAccountsList
                    accounts={lunchmoneyAccounts}
                    gocardlessAccounts={Object.values(requisitionDetails)}
                    onLinkAccounts={handleLinkAccounts}
                    onUnlinkAccount={handleUnlinkAccount}
                    isLoading={isLoadingLunchmoney}
                    error={lunchmoneyError}
                />
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