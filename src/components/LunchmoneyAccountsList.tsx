import { useState } from 'react';
import { Building2, Calendar, DollarSign, Link as LinkIcon, Unlink } from 'lucide-react';
import { format } from 'date-fns';
import type { LunchmoneyAsset } from '../types/lunchmoney';
import type { RequisitionDetails } from '../types/gocardless';

interface LunchmoneyAccountsListProps {
  accounts: LunchmoneyAsset[];
  gocardlessAccounts?: RequisitionDetails[];
  onLinkAccounts?: (lunchmoneyId: number, gocardlessId: string) => void;
  onUnlinkAccount?: (lunchmoneyId: number) => void;
}

export function LunchmoneyAccountsList({
                                         accounts,
                                         gocardlessAccounts,
                                         onLinkAccounts,
                                         onUnlinkAccount
                                       }: LunchmoneyAccountsListProps) {
  const [selectedAccount, setSelectedAccount] = useState<number | null>(null);

  if (accounts.length === 0) {
    return (
        <div className="text-center py-6">
          <p className="text-gray-500">No Lunchmoney accounts found.</p>
        </div>
    );
  }

  const getLinkedAccountDetails = (gocardlessId: string) => {
    for (const requisition of gocardlessAccounts || []) {
      const account = requisition.accounts.find(acc => acc.id === gocardlessId);
      if (account) return account;
    }
    return null;
  };

  return (
      <div className="space-y-4">
        {accounts.map((account) => {
          const linkedAccount = account.linked_account
              ? getLinkedAccountDetails(account.linked_account)
              : null;

          return (
              <div
                  key={account.id}
                  className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Building2 className="h-6 w-6 text-emerald-600" />
                    <h3 className="text-lg font-semibold text-gray-900">
                      {account.display_name || account.name}
                    </h3>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      account.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                  }`}>
                {account.status}
              </span>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <DollarSign className="h-5 w-5" />
                    <span>
                  {parseFloat(account.balance).toLocaleString(undefined, {
                    style: 'currency',
                    currency: account.currency
                  })}
                </span>
                  </div>

                  <div className="flex items-center space-x-2 text-gray-600">
                    <Calendar className="h-5 w-5" />
                    <span>
                  Balance as of {format(new Date(account.balance_as_of), 'MMM d, yyyy')}
                </span>
                  </div>

                  {account.institution_name && (
                      <div className="pt-2">
                        <p className="text-sm font-medium text-gray-500">Institution</p>
                        <p className="text-gray-900">{account.institution_name}</p>
                      </div>
                  )}

                  {linkedAccount && (
                      <div className="mt-2 p-3 bg-gray-50 rounded-md">
                        <p className="text-sm font-medium text-gray-500 mb-1">Linked to GoCardless Account</p>
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{linkedAccount.owner_name}</p>
                            <p className="text-sm text-gray-500">{linkedAccount.iban}</p>
                          </div>
                          {onUnlinkAccount && (
                              <button
                                  onClick={() => onUnlinkAccount(account.id)}
                                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-gray-100 rounded-full transition-colors"
                              >
                                <Unlink className="h-5 w-5" />
                              </button>
                          )}
                        </div>
                      </div>
                  )}
                </div>

                {!linkedAccount && gocardlessAccounts && onLinkAccounts && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <button
                          onClick={() => setSelectedAccount(selectedAccount === account.id ? null : account.id)}
                          className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500"
                      >
                        <LinkIcon className="h-4 w-4 mr-2" />
                        {selectedAccount === account.id ? 'Cancel Linking' : 'Link to GoCardless'}
                      </button>

                      {selectedAccount === account.id && (
                          <div className="mt-4 space-y-2">
                            {gocardlessAccounts.map(gc =>
                                    gc.accounts.map(gcAccount => (
                                        <button
                                            key={gcAccount.id}
                                            onClick={() => {
                                              onLinkAccounts(account.id, gcAccount.id);
                                              setSelectedAccount(null);
                                            }}
                                            className="w-full text-left px-4 py-2 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500"
                                        >
                                          <div className="flex items-center justify-between">
                                            <div>
                                              <p className="font-medium text-gray-900">{gcAccount.owner_name}</p>
                                              <p className="text-sm text-gray-500">{gcAccount.iban}</p>
                                            </div>
                            {/*                <span className="text-sm text-gray-500">*/}
                            {/*  {parseFloat(gcAccount.balance.amount).toLocaleString(undefined, {*/}
                            {/*    style: 'currency',*/}
                            {/*    currency: gcAccount.balance.currency*/}
                            {/*  })}*/}
                            {/*</span>*/}
                                          </div>
                                        </button>
                                    ))
                            )}
                          </div>
                      )}
                    </div>
                )}
              </div>
          );
        })}
      </div>
  );
}