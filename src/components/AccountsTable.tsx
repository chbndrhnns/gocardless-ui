import {useState} from 'react';
import {Building2, Link as LinkIcon, Loader2, Unlink} from 'lucide-react';
import {format} from 'date-fns';
import type {RequisitionDetails} from '../types/gocardless';
import type {LunchmoneyAsset} from '../types/lunchmoney';
import {ConfirmDialog} from './ConfirmDialog';

interface AccountsTableProps {
    accounts: RequisitionDetails[];
    lunchmoneyAccounts: LunchmoneyAsset[];
    onLinkAccount: (gocardlessId: string, lunchmoneyId: number) => void;
    onUnlinkAccount: (lunchmoneyId: number, gocardlessId: string) => void;
    isLoading?: boolean;
}

export function AccountsTable({
                                  accounts,
                                  lunchmoneyAccounts,
                                  onLinkAccount,
                                  onUnlinkAccount,
                                  isLoading = false
                              }: AccountsTableProps) {
    const [unlinkConfirm, setUnlinkConfirm] = useState<{
        lunchmoneyId: number;
        accountName: string;
        gocardlessId: string;
    } | null>(null);

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-12">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin"/>
            </div>
        );
    }

    const getLinkedLunchmoneyAccount = (gocardlessId: string) => {
        return lunchmoneyAccounts.find(acc => acc.linked_account === gocardlessId);
    };

    const getUnlinkedLunchmoneyAccounts = () => {
        return lunchmoneyAccounts.filter(acc => !acc.linked_account);
    };

    return (
        <>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                    <tr>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Bank Account
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Details
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Lunch Money Account
                        </th>
                        <th scope="col"
                            className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                        </th>
                    </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                    {accounts.map(requisition => (
                        requisition.accounts.map(account => {
                            const linkedAccount = getLinkedLunchmoneyAccount(account.id);
                            const unlinkedAccounts = getUnlinkedLunchmoneyAccounts();

                            return (
                                <tr key={account.id}>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <Building2 className="h-5 w-5 text-gray-400 mr-3"/>
                                            <div>
                                                <div className="text-sm font-medium text-gray-900">
                                                    {account.owner_name}
                                                </div>
                                                <div className="text-sm text-gray-500">
                                                    {account.iban}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">
                                            Balance: {parseFloat(account.balance || '0').toLocaleString(undefined, {
                                            style: 'currency',
                                            currency: (account.currency || 'EUR').toUpperCase()
                                        })}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                            Last accessed: {format(new Date(account.last_accessed), 'MMM d, yyyy')}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        {linkedAccount ? (
                                            <div className="text-sm">
                                                <p className="font-medium text-gray-900">{linkedAccount.name}</p>
                                                <p className="text-gray-500">
                                                    {parseFloat(linkedAccount.balance || '0').toLocaleString(undefined, {
                                                        style: 'currency',
                                                        currency: (linkedAccount.currency || 'EUR').toUpperCase()
                                                    })}
                                                </p>
                                            </div>
                                        ) : (
                                            <select
                                                onChange={(e) => {
                                                    const lunchmoneyId = parseInt(e.target.value);
                                                    if (lunchmoneyId) onLinkAccount(account.id, lunchmoneyId);
                                                }}
                                                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                                                defaultValue=""
                                            >
                                                <option value="">Link to Lunch Money account...</option>
                                                {unlinkedAccounts.map(lunchmoneyAcc => (
                                                    <option key={lunchmoneyAcc.id} value={lunchmoneyAcc.id}>
                                                        {lunchmoneyAcc.name} ({(lunchmoneyAcc.currency || 'EUR').toUpperCase()})
                                                    </option>
                                                ))}
                                            </select>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        {linkedAccount ? (
                                            <button
                                                onClick={() => setUnlinkConfirm({
                                                    lunchmoneyId: linkedAccount.id,
                                                    accountName: linkedAccount.name,
                                                    gocardlessId: account.id
                                                })}
                                                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                            >
                                                <Unlink className="h-3 w-3 mr-1"/>
                                                Unlink
                                            </button>
                                        ) : (
                                            <span
                                                className="inline-flex items-center px-3 py-1.5 text-xs text-gray-500">
                          <LinkIcon className="h-3 w-3 mr-1"/>
                          Not Linked
                        </span>
                                        )}
                                    </td>
                                </tr>
                            );
                        })
                    ))}
                    </tbody>
                </table>
            </div>

            <ConfirmDialog
                isOpen={!!unlinkConfirm}
                title="Unlink Account"
                message={`Are you sure you want to unlink "${unlinkConfirm?.accountName}"? This will stop syncing transactions for this account.`}
                confirmLabel="Unlink"
                onConfirm={() => {
                    if (unlinkConfirm) {
                        onUnlinkAccount(unlinkConfirm.lunchmoneyId, unlinkConfirm.gocardlessId);
                        setUnlinkConfirm(null);
                    }
                }}
                onCancel={() => setUnlinkConfirm(null)}
            />
        </>
    );
}