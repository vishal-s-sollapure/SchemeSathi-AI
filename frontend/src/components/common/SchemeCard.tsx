import React, { useState } from 'react';
import { 
  Building2, 
  ExternalLink, 
  Calendar, 
  CheckCircle2, 
  FileText, 
  ArrowRight,
  Sparkles,
  Info,
  ShieldCheck,
  ChevronRight,
  X
} from 'lucide-react';
import { Scheme } from '../../types';
import { StatusBadge } from './StatusBadge';

interface SchemeCardProps {
  scheme: Scheme;
  onEvaluate?: (scheme: Scheme) => void;
}

export const SchemeCard: React.FC<SchemeCardProps> = ({ scheme, onEvaluate }) => {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className="bg-white rounded-xl border border-slate-200/90 hover:border-govgreen-300 shadow-subtle hover:shadow-elevated transition-all duration-200 flex flex-col justify-between p-5 relative overflow-hidden group">
        {/* Top Accent Strip */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-govgreen-700 via-govgreen-500 to-emerald-400" />

        <div>
          {/* Header Row: Category & Badges */}
          <div className="flex items-center justify-between gap-2 flex-wrap mb-3 pt-1">
            <span className="text-[11px] font-semibold text-govgreen-800 bg-govgreen-50 border border-govgreen-200/70 px-2 py-0.5 rounded-md">
              {scheme.category}
            </span>

            <div className="flex items-center gap-1.5 flex-wrap">
              {scheme.isExpiringSoon && (
                <StatusBadge status="expiring" label="Deadline Soon" />
              )}
              <StatusBadge status="demo" label="Demo Data" />
            </div>
          </div>

          {/* Scheme Title & Ministry */}
          <h3 className="text-base sm:text-lg font-bold text-charcoal-900 group-hover:text-govgreen-800 transition-colors line-clamp-2">
            {scheme.title}
          </h3>

          <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
            <Building2 className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span className="truncate">{scheme.ministry}</span>
          </div>

          {/* Benefit Highlight Box */}
          <div className="mt-4 p-3 rounded-lg bg-emerald-50/60 border border-emerald-100/80">
            <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 mb-0.5">
              Financial / Welfare Benefit
            </div>
            <div className="text-sm sm:text-base font-extrabold text-govgreen-900">
              {scheme.annualBenefit}
            </div>
            <div className="text-[11px] text-emerald-700 mt-0.5">
              Mode: <span className="font-medium">{scheme.benefitType}</span>
            </div>
          </div>

          {/* Description */}
          <p className="mt-3 text-xs text-slate-600 line-clamp-2 leading-relaxed">
            {scheme.description}
          </p>

          {/* Key Eligibility Chips */}
          <div className="mt-3 pt-3 border-t border-slate-100 space-y-1.5">
            <div className="text-[11px] font-semibold text-slate-700">Key Criteria:</div>
            {scheme.eligibilityCriteria.slice(0, 2).map((item, idx) => (
              <div key={idx} className="flex items-start gap-1.5 text-xs text-slate-600">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span className="line-clamp-1">{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between gap-2 flex-wrap">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" />
            <span>{scheme.applicationDeadline}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowModal(true)}
              className="text-xs font-semibold text-slate-700 hover:text-govgreen-800 px-2.5 py-1.5 rounded-md hover:bg-slate-100 transition"
            >
              Details
            </button>
            <button
              onClick={() => onEvaluate ? onEvaluate(scheme) : setShowModal(true)}
              className="inline-flex items-center gap-1 bg-govgreen-700 hover:bg-govgreen-800 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-sm transition"
            >
              <span>Check Eligibility</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Details Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-200 shadow-premium p-6">
            <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-xs font-bold text-govgreen-800 bg-govgreen-50 px-2.5 py-0.5 rounded-full border border-govgreen-200">
                    {scheme.category}
                  </span>
                  <StatusBadge status="demo" label="Illustrative Demo Scheme" />
                </div>
                <h2 className="text-xl font-bold text-charcoal-900">
                  {scheme.title}
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Issued by: {scheme.ministry} ({scheme.level})
                </p>
              </div>

              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4 space-y-5">
              {/* Demo Notice */}
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-xs text-purple-900 flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold">{scheme.demoNote}:</span> This preview record illustrates how SchemeSathi AI organizes government benefit criteria and required documents for citizens.
                </div>
              </div>

              {/* Benefit Box */}
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <div className="text-xs font-bold text-emerald-800 uppercase tracking-wide">
                  Benefit Amount & Delivery Channel
                </div>
                <div className="text-xl font-extrabold text-govgreen-900 mt-1">
                  {scheme.annualBenefit}
                </div>
                <div className="text-xs text-emerald-700 mt-1">
                  Payment Mechanism: <strong>{scheme.benefitType}</strong>
                </div>
              </div>

              {/* Description */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Scheme Overview & Purpose
                </h4>
                <p className="text-sm text-slate-700 leading-relaxed">
                  {scheme.description}
                </p>
              </div>

              {/* Target Beneficiaries */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Target Beneficiary Group
                </h4>
                <p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200">
                  {scheme.targetBeneficiaries}
                </p>
              </div>

              {/* Eligibility Criteria */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Deterministic Eligibility Rules
                </h4>
                <div className="space-y-2">
                  {scheme.eligibilityCriteria.map((criterion, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-sm text-slate-700">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span>{criterion}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Required Documents */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Mandatory Verification Documents
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {scheme.requiredDocuments.map((doc, idx) => (
                    <div key={idx} className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-800">
                      <FileText className="w-3.5 h-3.5 text-govgreen-700 flex-shrink-0" />
                      <span>{doc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="border-t border-slate-100 pt-4 flex items-center justify-between gap-3">
              <a
                href={scheme.officialPortal}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-govgreen-800 transition"
              >
                <span>Official Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-lg transition"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    setShowModal(false);
                    if (onEvaluate) onEvaluate(scheme);
                  }}
                  className="px-4 py-2 text-xs font-semibold text-white bg-govgreen-700 hover:bg-govgreen-800 rounded-lg shadow-sm transition"
                >
                  Evaluate for My Profile
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
