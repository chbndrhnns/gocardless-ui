import React from 'react';
import { format } from 'date-fns';
import { Building2, Calendar, Link } from 'lucide-react';
import { RequisitionStatus } from './RequisitionStatus';
import type { Requisition } from '../types/gocardless';

interface RequisitionCardProps {
  requisition: Requisition;
  onLinkClick: (link: string) => void;
}

export function RequisitionCard({ requisition, onLinkClick }: RequisitionCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
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
      
      {requisition.link && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <button
            onClick={() => onLinkClick(requisition.link)}
            className="w-full inline-flex items-center justify-center bg-blue-50 text-blue-600 hover:bg-blue-100 py-2 px-4 rounded-md transition-colors"
          >
            <Link className="h-4 w-4 mr-2" />
            Continue Connection
          </button>
        </div>
      )}
    </div>
  );
}