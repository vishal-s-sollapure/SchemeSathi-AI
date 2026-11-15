import React from 'react';
import { SearchX, ArrowRight, LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: LucideIcon;
  actionText?: string;
  onAction?: () => void;
  secondaryActionText?: string;
  onSecondaryAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No Matching Schemes Found",
  description = "Try adjusting your search terms, removing specific filters, or resetting the annual income threshold.",
  icon: Icon = SearchX,
  actionText = "Reset All Filters",
  onAction,
  secondaryActionText,
  onSecondaryAction
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-2xl bg-white border border-slate-200/90 shadow-subtle max-w-md mx-auto my-6">
      <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-500 flex items-center justify-center mb-4">
        <Icon className="w-7 h-7 text-slate-400" />
      </div>

      <h4 className="text-base font-bold text-charcoal-900">
        {title}
      </h4>

      <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
        {description}
      </p>

      <div className="mt-5 flex flex-wrap gap-2 justify-center">
        {onAction && (
          <button
            onClick={onAction}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-govgreen-700 hover:bg-govgreen-800 rounded-lg shadow-subtle transition"
          >
            <span>{actionText}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        )}

        {secondaryActionText && onSecondaryAction && (
          <button
            onClick={onSecondaryAction}
            className="px-4 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
          >
            {secondaryActionText}
          </button>
        )}
      </div>
    </div>
  );
};
