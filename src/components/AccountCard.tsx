import React from 'react';
import { format } from 'date-fns';
import { Building2, Calendar, CreditCard } from 'lucide-react';
import type { BankAccount } from '../types/gocardless';

interface AccountCardProps {
  account: BankAccount;
}

export function AccountCard({ account }: AccountCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <Building2 className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">{account.bank_name}</h3>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          account.status === 'enabled' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
        }`}>
          {account.status}
        </span>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center space-x-2 text-gray-600">
          <CreditCard className="h-5 w-5" />
          <span>••••{account.account_number_ending}</span>
        </div>
        
        <div className="flex items-center space-x-2 text-gray-600">
          <Calendar className="h-5 w-5" />
          <span>Added {format(new Date(account.created_at), 'MMM d, yyyy')}</span>
        </div>
        
        <div className="pt-2">
          <p className="text-sm font-medium text-gray-500">Account Holder</p>
          <p className="text-gray-900">{account.account_holder_name}</p>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-100">
        <button className="w-full bg-blue-50 text-blue-600 hover:bg-blue-100 py-2 px-4 rounded-md transition-colors">
          View Details
        </button>
      </div>
    </div>
  );
}