import React, { useState } from 'react';
import { AlertCircle, X, ExternalLink } from 'lucide-react';
import { DEMO_DATA_DISCLAIMER } from '../../data/mockData';

export const DemoBanner: React.FC = () => {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) {
    return (
      <div className="bg-purple-900 text-purple-100 text-[11px] py-1 px-4 flex items-center justify-between">
        <span className="font-medium">
          ⚠️ Demonstration Preview Mode Active (Sample civic records for evaluation)
        </span>
        <button 
          onClick={() => setDismissed(false)}
          className="text-purple-300 hover:text-white underline text-[10px]"
        >
          View Full Notice
        </button>
      </div>
    );
  }

  return (
    <aside 
      aria-label="Demonstration Notice"
      className="bg-purple-950 text-purple-100 border-b border-purple-800/80 px-4 py-2 sm:py-2.5 transition"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <div className="w-5 h-5 rounded-full bg-purple-800 text-purple-200 flex items-center justify-center flex-shrink-0">
            <AlertCircle className="w-3.5 h-3.5" />
          </div>
          <div className="leading-snug">
            <span className="font-bold text-purple-200 uppercase tracking-wide text-[10px] bg-purple-900 px-1.5 py-0.5 rounded mr-2 border border-purple-700">
              Demo Environment
            </span>
            <span className="text-purple-100/90 hidden sm:inline">
              {DEMO_DATA_DISCLAIMER}
            </span>
            <span className="text-purple-100/90 sm:hidden">
              Illustrative demo data for UI preview. Not verified government records.
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <a
            href="https://www.myscheme.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:inline-flex items-center gap-1 text-[11px] text-purple-300 hover:text-white transition"
          >
            Official myScheme Portal <ExternalLink className="w-3 h-3" />
          </a>
          <button
            onClick={() => setDismissed(true)}
            className="text-purple-400 hover:text-white p-1 rounded transition"
            title="Minimize disclaimer banner"
            aria-label="Minimize disclaimer banner"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
};
