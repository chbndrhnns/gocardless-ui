import { useState } from 'react';
import { Building2, ChevronDown, ChevronUp } from 'lucide-react';
import { format } from 'date-fns';
import type { BankAccount } from '../types/gocardless';

interface BankAccountsListProps {
  accounts: BankAccount[];
  onLinkClick?: (accountId: string) => void;
}

export function BankAccountsList({ accounts, onLinkClick }: BankAccountsListProps) {
  const [expandedAccount, setExpandedAccount] = useState<string | null>(null);

  if (accounts.length === 0) {
    return (
      <div className="text-center py-6">
        <p className="text-gray-500">No accounts found.</p>
      </div>
    );
  }

  const formatBalance = (account: BankAccount) => {
    if (!account.balance) return 'Not available';

    try {
      // Handle both possible API response formats
      const amount = typeof account.balance === 'object'
        ? account.balance.amount
        : account.balance;
      const currency = typeof account.balance === 'object'
        ? account.balance.currency
        : account.currency;

      return new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currency || 'EUR',
      }).format(parseFloat(amount));
    } catch (error) {
      console.error('Error formatting balance:', error);
      return 'Error displaying balance';
    }
  };

  return (
    <div className="space-y-4">
      {accounts.map((account) => (
        <div
          key={account.id}
          className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Building2 className="h-5 w-5 text-blue-600" />
                <div>
                  <h4 className="text-sm font-medium text-gray-900">
                    {account.owner_name}
                  </h4>
                  <p className="text-sm text-gray-500">{account.iban}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full ${
                    account.status === 'READY'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {account.status}
                </span>
                <button
                  onClick={() => setExpandedAccount(
                    expandedAccount === account.id ? null : account.id
                  )}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {expandedAccount === account.id ? (
                    <ChevronUp className="h-5 w-5" />
                  ) : (
                    <ChevronDown className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {expandedAccount === account.id && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <dl className="grid grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Balance</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {formatBalance(account)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">
                      Last Accessed
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {format(new Date(account.last_accessed), 'MMM d, yyyy')}
                    </dd>
                  </div>
                </dl>

                {onLinkClick && (
                  <div className="mt-4">
                    <button
                      onClick={() => onLinkClick(account.id)}
                      className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Link Account
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}