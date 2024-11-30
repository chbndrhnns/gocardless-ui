import { Unlink, ExternalLink } from 'lucide-react';
import type { LunchmoneyAsset } from '../types/lunchmoney';
import type { RequisitionDetails } from '../types/gocardless';

interface LinkedAccountsTableProps {
  accounts: LunchmoneyAsset[];
  gocardlessAccounts?: RequisitionDetails[];
  onUnlinkAccount?: (lunchmoneyId: number) => void;
}

export function LinkedAccountsTable({
  accounts,
  gocardlessAccounts,
  onUnlinkAccount,
}: LinkedAccountsTableProps) {
  const linkedAccounts = accounts.filter((account) => account.linked_account);

  if (linkedAccounts.length === 0) {
    return (
      <div className="text-center py-6 bg-gray-50 rounded-lg">
        <p className="text-gray-500">No linked accounts found.</p>
      </div>
    );
  }

  const getLinkedAccountDetails = (gocardlessId: string) => {
    for (const requisition of gocardlessAccounts || []) {
      const account = requisition.accounts.find((acc) => acc.id === gocardlessId);
      if (account) return account;
    }
    return null;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Lunch Money Account
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              GoCardless Account
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Balance
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {linkedAccounts.map((account) => {
            const gocardlessAccount = account.linked_account
              ? getLinkedAccountDetails(account.linked_account)
              : null;

            return (
              <tr key={account.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {account.display_name || account.name}
                  </div>
                  {account.institution_name && (
                    <div className="text-sm text-gray-500">
                      {account.institution_name}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {gocardlessAccount ? (
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {gocardlessAccount.owner_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {gocardlessAccount.iban}
                      </div>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-500">Not found</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {parseFloat(account.balance).toLocaleString(undefined, {
                      style: 'currency',
                      currency: account.currency,
                    })}
                  </div>
                  <div className="text-xs text-gray-500">
                    as of{' '}
                    {new Date(account.balance_as_of).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end space-x-2">
                    {gocardlessAccount?.status === 'READY' && (
                      <a
                        href={`https://bankaccountdata.gocardless.com/accounts/${gocardlessAccount.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-gray-500"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                    {onUnlinkAccount && (
                      <button
                        onClick={() => onUnlinkAccount(account.id)}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <Unlink className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}