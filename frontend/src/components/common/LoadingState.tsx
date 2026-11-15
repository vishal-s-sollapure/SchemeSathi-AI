import React from 'react';
import { ShieldCheck, RefreshCw } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  submessage?: string;
  variant?: 'card' | 'fullscreen' | 'inline';
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Evaluating eligibility against official rules...",
  submessage = "Verifying criteria from gazette guidelines and document thresholds",
  variant = 'card'
}) => {
  if (variant === 'inline') {
    return (
      <div className="flex items-center gap-2 text-xs text-slate-500 py-2">
        <RefreshCw className="w-3.5 h-3.5 animate-spin text-govgreen-700" />
        <span>{message}</span>
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-2xl bg-white border border-slate-200/80 shadow-subtle ${
      variant === 'fullscreen' ? 'min-h-[60vh]' : ''
    }`}>
      <div className="relative mb-4">
        <div className="w-16 h-16 rounded-2xl bg-govgreen-50 border border-govgreen-200 flex items-center justify-center text-govgreen-800 shadow-sm">
          <ShieldCheck className="w-8 h-8 text-govgreen-700 animate-pulse" />
        </div>
        <div className="absolute -inset-1 rounded-2xl border-2 border-govgreen-500/20 animate-ping pointer-events-none" />
      </div>

      <h4 className="text-base font-bold text-charcoal-900 tracking-tight">
        {message}
      </h4>

      {submessage && (
        <p className="text-xs text-slate-500 max-w-sm mt-1.5 leading-relaxed">
          {submessage}
        </p>
      )}

      {/* Subtle Progress Bar */}
      <div className="w-48 h-1.5 bg-slate-100 rounded-full mt-5 overflow-hidden">
        <div className="h-full bg-gradient-to-r from-govgreen-600 to-emerald-400 rounded-full animate-pulse w-3/4" />
      </div>
    </div>
  );
};
