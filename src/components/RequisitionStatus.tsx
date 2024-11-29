import { Clock, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import type { Requisition } from '../types/gocardless';

type StatusConfig = {
  label: string;
  icon: typeof Clock | typeof CheckCircle2 | typeof XCircle | typeof AlertCircle;
  className: string;
};

const DEFAULT_STATUS: StatusConfig = {
  label: 'Unknown',
  icon: AlertCircle,
  className: 'bg-gray-100 text-gray-800'
};

const STATUS_CONFIG: Record<string, StatusConfig> = {
  CR: {
    label: 'Created',
    icon: Clock,
    className: 'bg-blue-100 text-blue-800'
  },
  LN: {
    label: 'Linked',
    icon: CheckCircle2,
    className: 'bg-green-100 text-green-800'
  },
  RJ: {
    label: 'Rejected',
    icon: XCircle,
    className: 'bg-red-100 text-red-800'
  },
  ER: {
    label: 'Error',
    icon: AlertCircle,
    className: 'bg-red-100 text-red-800'
  },
  EX: {
    label: 'Expired',
    icon: Clock,
    className: 'bg-gray-100 text-gray-800'
  },
  GA: {
    label: 'Granting Access',
    icon: Clock,
    className: 'bg-yellow-100 text-yellow-800'
  }
};

interface RequisitionStatusProps {
  status: Requisition['status'];
}

export function RequisitionStatus({ status }: RequisitionStatusProps) {
  const config = STATUS_CONFIG[status] || DEFAULT_STATUS;
  const StatusIcon = config.icon;

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.className}`}>
      <StatusIcon className="w-4 h-4 mr-1.5" />
      {config.label}
    </span>
  );
}