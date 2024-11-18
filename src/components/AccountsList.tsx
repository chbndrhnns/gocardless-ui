import { CreditCard, Calendar, Building2 } from 'lucide-react';
import { format } from 'date-fns';
import type { BankAccount } from '../types/gocardless';

interface AccountsListProps {
  accounts: BankAccount[];
}

export function AccountsList({ accounts }: AccountsListProps) {
  if (accounts.length === 0) {
    return (
      <div className="text-center py-6">
        <p className="text-gray-500">No accounts found for this connection.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {accounts.map((account) => (
        <div
          key={account.id}
          className="bg-gray-50 rounded-lg p-4 space-y-3"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Building2 className="h-5 w-5 text-blue-600" />
              <h4 className="font-medium text-gray-900">{account.owner_name}</h4>
            </div>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              account.status === 'enabled' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {account.status}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2 text-gray-600">
              <CreditCard className="h-4 w-4" />
              <span className="text-sm">{account.iban}</span>
            </div>

            <div className="flex items-center space-x-2 text-gray-600">
              <Calendar className="h-4 w-4" />
              <span className="text-sm">
                Last accessed {format(new Date(account.last_accessed), 'MMM d, yyyy')}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <div>
              <p className="text-sm font-medium text-gray-500">Balance</p>
              <p className="text-lg font-semibold text-gray-900">
                {new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: account.balance.currency,
                }).format(parseFloat(account.balance.amount))}
              </p>
            </div>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              View Transactions
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}