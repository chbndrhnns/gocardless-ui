import { useState, useEffect } from 'react';
import { PlusCircle, RefreshCw } from 'lucide-react';
import { RequisitionCard } from './components/RequisitionCard';
import { AddBankDialog } from './components/AddBankDialog';
import { LunchmoneyAccountsList } from './components/LunchmoneyAccountsList';
import { fetchRequisitions, fetchInstitutions, createRequisition, deleteRequisition, fetchRequisitionDetails } from './services/api';
import { fetchLunchmoneyAssets } from './services/lunchmoney';
import { linkLunchmoneyAccount, unlinkLunchmoneyAccount } from './services/lunchmoney';
import type { Requisition, Institution, RequisitionDetails } from './types/gocardless';
import type { LunchmoneyAsset } from './types/lunchmoney';

function App() {
  const [requisitions, setRequisitions] = useState<Requisition[]>([]);
  const [requisitionDetails, setRequisitionDetails] = useState<Record<string, RequisitionDetails>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [selectedCountry, setSelectedCountry] = useState('de');
  const [isLoadingInstitutions, setIsLoadingInstitutions] = useState(false);
  const [institutionsError, setInstitutionsError] = useState<string | null>(null);
  const [isCreatingRequisition, setIsCreatingRequisition] = useState(false);
  const [isDeletingRequisition, setIsDeletingRequisition] = useState<string | null>(null);

  // Lunchmoney state
  const [lunchmoneyAccounts, setLunchmoneyAccounts] = useState<LunchmoneyAsset[]>([]);
  const [isLoadingLunchmoney, setIsLoadingLunchmoney] = useState(true);
  const [lunchmoneyError, setLunchmoneyError] = useState<string | null>(null);

  const loadRequisitions = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchRequisitions();
      const sortedRequisitions = data.results.sort((a, b) =>
          new Date(a.created).getTime() - new Date(b.created).getTime()
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

  const loadLunchmoneyAccounts = async () => {
    setIsLoadingLunchmoney(true);
    setLunchmoneyError(null);

    try {
      const accounts = await fetchLunchmoneyAssets();
      setLunchmoneyAccounts(accounts);
    } catch (err) {
      setLunchmoneyError(err instanceof Error ? err.message : 'Failed to load Lunchmoney accounts');
    } finally {
      setIsLoadingLunchmoney(false);
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

  const loadInstitutions = async (country: string) => {
    setIsLoadingInstitutions(true);
    setInstitutionsError(null);

    try {
      const data = await fetchInstitutions(country);
      setInstitutions(data);
    } catch (err) {
      setInstitutionsError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoadingInstitutions(false);
    }
  };

  const handleLinkClick = (link: string) => {
    window.open(link, '_blank');
  };

  const handleInstitutionSelect = async (institution: Institution) => {
    setIsCreatingRequisition(true);
    try {
      const redirectUrl = `${window.location.origin}/callback`;
      const reference = `REQ-${Date.now()}`;
      const requisition = await createRequisition({
        institutionId: institution.id,
        redirectUrl,
        reference,
        userLanguage: selectedCountry.toUpperCase(),
      });

      setRequisitions(prev => [requisition, ...prev].sort((a, b) =>
          new Date(a.created).getTime() - new Date(b.created).getTime()
      ));
      setIsDialogOpen(false);

      if (requisition.link) {
        window.location.href = requisition.link;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create bank connection');
    } finally {
      setIsCreatingRequisition(false);
    }
  };

  const handleDeleteRequisition = async (id: string) => {
    setIsDeletingRequisition(id);
    try {
      await deleteRequisition(id);
      setRequisitions(prev => prev.filter(req => req.id !== id));
      setRequisitionDetails(prev => {
        const updated = { ...prev };
        delete updated[id];
        return updated;
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete bank connection');
    } finally {
      setIsDeletingRequisition(null);
    }
  };

  const handleCountryChange = (country: string) => {
    setSelectedCountry(country);
    loadInstitutions(country);
  };

  const handleLinkAccounts = async (lunchmoneyId: number, gocardlessId: string) => {
    try {
      await linkLunchmoneyAccount(lunchmoneyId, gocardlessId);
      // Refresh both account lists
      await Promise.all([loadRequisitions(), loadLunchmoneyAccounts()]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to link accounts');
    }
  };

  const handleUnlinkAccount = async (lunchmoneyId: number) => {
    try {
      await unlinkLunchmoneyAccount(lunchmoneyId);
      // Refresh both account lists
      await Promise.all([loadRequisitions(), loadLunchmoneyAccounts()]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unlink account');
    }
  };

  useEffect(() => {
    loadRequisitions();
    loadLunchmoneyAccounts();
  }, []);

  useEffect(() => {
    if (isDialogOpen) {
      loadInstitutions(selectedCountry);
    }
  }, [isDialogOpen, selectedCountry]);

  const completedRequisitions = requisitions.filter(req => req.status === 'CR' || req.status === 'LN');
  const problematicRequisitions = requisitions.filter(req => req.status !== 'CR' && req.status !== 'LN');

  return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Bank Connections</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Manage your bank account connections and view their status
                </p>
              </div>
              <div className="flex space-x-4">
                <button
                    onClick={loadRequisitions}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </button>
                <button
                    onClick={() => setIsDialogOpen(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <PlusCircle className="h-4 w-4 mr-2" />
                  New Connection
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">GoCardless Accounts</h2>
              {isLoading ? (
                  <div className="grid grid-cols-1 gap-6">
                    {[...Array(3)].map((_, i) => (
                        <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                          <div className="space-y-3">
                            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                          </div>
                        </div>
                    ))}
                  </div>
              ) : error ? (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                    {error}
                  </div>
              ) : requisitions.length === 0 ? (
                  <div className="text-center py-12">
                    <h3 className="text-lg font-medium text-gray-900">No bank connections found</h3>
                    <p className="mt-2 text-gray-500">Start by connecting your first bank account.</p>
                  </div>
              ) : (
                  <div className="space-y-8">
                    {completedRequisitions.length > 0 && (
                        <section>
                          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Connections</h3>
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
                          <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending or Problematic Connections</h3>
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
                  </div>
              )}
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Lunchmoney Accounts</h2>
              {isLoadingLunchmoney ? (
                  <div className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                        <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                          <div className="space-y-3">
                            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                          </div>
                        </div>
                    ))}
                  </div>
              ) : lunchmoneyError ? (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                    {lunchmoneyError}
                  </div>
              ) : (
                  <LunchmoneyAccountsList
                      accounts={lunchmoneyAccounts}
                      gocardlessAccounts={Object.values(requisitionDetails)}
                      onLinkAccounts={handleLinkAccounts}
                      onUnlinkAccount={handleUnlinkAccount}
                  />
              )}
            </div>
          </div>

          <AddBankDialog
              isOpen={isDialogOpen}
              onClose={() => setIsDialogOpen(false)}
              institutions={institutions}
              isLoading={isLoadingInstitutions}
              error={institutionsError}
              onInstitutionSelect={handleInstitutionSelect}
              selectedCountry={selectedCountry}
              onCountryChange={handleCountryChange}
              isCreatingRequisition={isCreatingRequisition}
          />
        </div>
      </div>
  );
}

export default App;