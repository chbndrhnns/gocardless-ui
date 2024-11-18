import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { Building2, Calendar, Link, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { RequisitionStatus } from './RequisitionStatus';
import { AccountsList } from './AccountsList';
import { fetchRequisitionDetails } from '../services/api';
import type { Requisition, RequisitionDetails } from '../types/gocardless';

interface RequisitionCardProps {
  requisition: Requisition;
  onLinkClick: (link: string) => void;
}

export function RequisitionCard({ requisition, onLinkClick }: RequisitionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [details, setDetails] = useState<RequisitionDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDetails = async () => {
    if (!isExpanded || details) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchRequisitionDetails(requisition.id);
      setDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load account details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDetails();
  }, [isExpanded]);

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Building2 className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              {requisition.institution_id}
            </h3>
          </div>
          <RequisitionStatus status={requisition.status} />
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center space-x-2 text-gray-600">
            <Calendar className="h-5 w-5" />
            <span>Created {format(new Date(requisition.created), 'MMM d, yyyy')}</span>
          </div>
          
          <div className="pt-2">
            <p className="text-sm font-medium text-gray-500">Reference</p>
            <p className="text-gray-900">{requisition.reference}</p>
          </div>

          <div>
            <p className="text-sm font-medium text-gray-500">Connected Accounts</p>
            <p className="text-gray-900">{requisition.accounts.length}</p>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
          {requisition.link && (
            <button
              onClick={() => onLinkClick(requisition.link)}
              className="w-full inline-flex items-center justify-center bg-blue-50 text-blue-600 hover:bg-blue-100 py-2 px-4 rounded-md transition-colors"
            >
              <Link className="h-4 w-4 mr-2" />
              Continue Connection
            </button>
          )}

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full inline-flex items-center justify-center text-gray-600 hover:text-gray-900 py-2 transition-colors"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-4 w-4 mr-2" />
                Hide Accounts
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4 mr-2" />
                Show Accounts
              </>
            )}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="px-6 pb-6">
          {isLoading ? (
            <div className="flex justify-center items-center py-8">
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          ) : details ? (
            <AccountsList accounts={details.accounts} />
          ) : null}
        </div>
      )}
    </div>
  );
}