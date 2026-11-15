import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  FileWarning, 
  XCircle, 
  Clock, 
  Sparkles,
  Info
} from 'lucide-react';
import { EligibilityStatus } from '../../types';

interface StatusBadgeProps {
  status: EligibilityStatus | 'demo' | 'expiring' | 'high_match' | 'active';
  label?: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, size = 'sm' }) => {
  const sizeClasses = size === 'sm' 
    ? 'px-2 py-0.5 text-xs font-semibold' 
    : 'px-3 py-1 text-xs sm:text-sm font-semibold';

  switch (status) {
    case 'eligible':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 ${sizeClasses}`}>
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
          <span>{label || 'Fully Eligible'}</span>
        </span>
      );
    case 'conditionally_eligible':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 ${sizeClasses}`}>
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
          <span>{label || 'Conditionally Eligible'}</span>
        </span>
      );
    case 'missing_documents':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-orange-50 text-orange-800 border border-orange-200 ${sizeClasses}`}>
          <FileWarning className="w-3.5 h-3.5 text-orange-600 flex-shrink-0" />
          <span>{label || 'Missing Documents'}</span>
        </span>
      );
    case 'ineligible':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-rose-50 text-rose-800 border border-rose-200 ${sizeClasses}`}>
          <XCircle className="w-3.5 h-3.5 text-rose-600 flex-shrink-0" />
          <span>{label || 'Not Eligible'}</span>
        </span>
      );
    case 'pending_evaluation':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-slate-100 text-slate-700 border border-slate-300 ${sizeClasses}`}>
          <Clock className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
          <span>{label || 'Needs Profile Evaluation'}</span>
        </span>
      );
    case 'demo':
      return (
        <span className={`inline-flex items-center gap-1 rounded-full bg-purple-50 text-purple-800 border border-purple-200/80 ${sizeClasses} uppercase tracking-wider text-[10px]`}>
          <Sparkles className="w-3 h-3 text-purple-600 flex-shrink-0" />
          <span>{label || 'Demo Preview Data'}</span>
        </span>
      );
    case 'expiring':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 ${sizeClasses}`}>
          <Clock className="w-3.5 h-3.5 text-rose-500 animate-pulse flex-shrink-0" />
          <span>{label || 'Expiring Soon'}</span>
        </span>
      );
    case 'high_match':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-govgreen-50 text-govgreen-800 border border-govgreen-200 ${sizeClasses}`}>
          <CheckCircle2 className="w-3.5 h-3.5 text-govgreen-600 flex-shrink-0" />
          <span>{label || 'High Match (90%+)'}</span>
        </span>
      );
    case 'active':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 ${sizeClasses}`}>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
          <span>{label || 'Active Cycle'}</span>
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center gap-1 rounded-full bg-slate-100 text-slate-700 ${sizeClasses}`}>
          <Info className="w-3 h-3" />
          <span>{label || 'Status'}</span>
        </span>
      );
  }
};
