import React from 'react';
import { BookOpen, ExternalLink, ShieldCheck, Calendar, FileText } from 'lucide-react';
import { Citation } from '../../types';

interface CitationCardProps {
  citation: Citation;
  compact?: boolean;
}

export const CitationCard: React.FC<CitationCardProps> = ({ citation, compact = false }) => {
  return (
    <div className="rounded-xl border border-govgreen-200 bg-govgreen-50/40 p-4 transition hover:border-govgreen-300 hover:shadow-subtle">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-govgreen-100 text-govgreen-800 flex items-center justify-center flex-shrink-0 mt-0.5">
            <BookOpen className="w-4 h-4 text-govgreen-700" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-govgreen-900 tracking-tight">
                {citation.title}
              </span>
              <span className="inline-flex items-center gap-1 rounded bg-govgreen-100 text-govgreen-800 px-1.5 py-0.5 text-[10px] font-semibold border border-govgreen-200">
                <ShieldCheck className="w-3 h-3 text-govgreen-700" />
                {citation.verificationBadge}
              </span>
            </div>
            <p className="text-xs text-charcoal-700 mt-0.5 font-medium">
              {citation.documentName}
            </p>
          </div>
        </div>

        <a
          href={citation.officialSourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-500 hover:text-govgreen-800 p-1 rounded-md hover:bg-white transition flex-shrink-0"
          title="Open official government publication"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      <div className="mt-3 bg-white rounded-lg p-3 border border-govgreen-100/80 text-xs text-slate-700 leading-relaxed font-sans shadow-inner">
        <span className="font-semibold text-govgreen-800 block mb-1">
          {citation.clauseNumber}:
        </span>
        <blockquote className="italic border-l-2 border-govgreen-500 pl-2.5 text-slate-700">
          {citation.excerpt}
        </blockquote>
      </div>

      {!compact && (
        <div className="mt-2.5 pt-2 border-t border-govgreen-100 flex items-center justify-between text-[11px] text-slate-500 flex-wrap gap-2">
          <span className="inline-flex items-center gap-1">
            <FileText className="w-3 h-3 text-slate-400" />
            Circular: <code className="bg-slate-100 px-1 py-0.2 rounded font-mono text-[10px] text-slate-700">{citation.circularNumber}</code>
          </span>
          <span className="inline-flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" />
            Dated: {citation.notificationDate}
          </span>
        </div>
      )}
    </div>
  );
};
