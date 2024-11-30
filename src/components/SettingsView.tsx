import { useState } from 'react';
import { PlusCircle, AlertCircle } from 'lucide-react';
import { AddBankDialog } from './AddBankDialog';
import { LinkedAccountsTable } from './LinkedAccountsTable';
import { BankAccountsList } from './BankAccountsList';
import { useRequisitions } from '../hooks/useRequisitions';
import { useLunchmoneyAccounts } from '../hooks/useLunchmoneyAccounts';
import { useInstitutions } from '../hooks/useInstitutions';
import { useInstitutionSelection } from '../hooks/useInstitutionSelection';

export function SettingsView() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState('de');

  const {
    requisitions,
    requisitionDetails,
    isLoading: isLoadingRequisitions,
    error: requisitionsError,
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

  // Collect all bank accounts from requisitions
  const allBankAccounts = requisitions
    .filter(req => req.status === 'LN')
    .flatMap(req => {
      const details = requisitionDetails[req.id];
      return details ? details.accounts : [];
    });

  return (
    <div className="space-y-8">
      {/* Linked Accounts Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Linked Accounts</h2>
          <p className="mt-1 text-sm text-gray-500">
            Currently linked Lunch Money and bank accounts
          </p>
        </div>

        <LinkedAccountsTable
          accounts={lunchmoneyAccounts}
          gocardlessAccounts={Object.values(requisitionDetails)}
          onUnlinkAccount={handleUnlinkAccount}
        />
      </div>

      {/* Bank Accounts Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Bank Accounts</h2>
            <p className="mt-1 text-sm text-gray-500">
              Manage your connected bank accounts
            </p>
          </div>
          <button
            onClick={handleOpenDialog}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusCircle className="h-4 w-4 mr-2" />
            Connect New Bank
          </button>
        </div>

        {isLoadingRequisitions ? (
          <div className="animate-pulse space-y-4">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-100 rounded-lg" />
            ))}
          </div>
        ) : requisitionsError ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center text-red-700">
            <AlertCircle className="h-5 w-5 mr-2" />
            {requisitionsError}
          </div>
        ) : (
          <BankAccountsList
            accounts={allBankAccounts}
            onLinkClick={(accountId) => {
              // Handle linking logic
            }}
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