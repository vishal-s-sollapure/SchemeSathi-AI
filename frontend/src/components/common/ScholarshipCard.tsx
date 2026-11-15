import React, { useState } from 'react';
import { 
  GraduationCap, 
  Calendar, 
  FileCheck2, 
  ArrowRight, 
  Sparkles,
  CheckCircle2,
  XCircle,
  FileWarning,
  X
} from 'lucide-react';
import { Scholarship } from '../../types';
import { StatusBadge } from './StatusBadge';

interface ScholarshipCardProps {
  scholarship: Scholarship;
  onCheckReadiness?: (scholarship: Scholarship) => void;
}

export const ScholarshipCard: React.FC<ScholarshipCardProps> = ({ scholarship, onCheckReadiness }) => {
  const [showModal, setShowModal] = useState(false);

  const readyDocs = scholarship.requiredDocuments.filter(d => d.status === 'ready').length;
  const totalDocs = scholarship.requiredDocuments.length;
  const readinessPercent = Math.round((readyDocs / totalDocs) * 100);

  return (
    <>
      <div className="bg-white rounded-xl border border-slate-200 hover:border-emerald-300 shadow-subtle hover:shadow-elevated transition-all duration-200 flex flex-col justify-between p-5 relative overflow-hidden group">
        {/* Accent Strip */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-ashoka-700 via-govgreen-600 to-emerald-400" />

        <div>
          {/* Top Row: Provider & Match Score */}
          <div className="flex items-center justify-between gap-2 flex-wrap mb-3 pt-1">
            <span className="text-[11px] font-semibold text-ashoka-800 bg-ashoka-50 border border-ashoka-200/80 px-2 py-0.5 rounded-md">
              {scholarship.level}
            </span>

            <div className="flex items-center gap-1.5">
              {scholarship.matchScore && (
                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-govgreen-800 bg-govgreen-100 border border-govgreen-300/80 px-2 py-0.5 rounded-full">
                  <CheckCircle2 className="w-3 h-3 text-govgreen-700" />
                  {scholarship.matchScore}% Match
                </span>
              )}
              <StatusBadge status="demo" label="Demo Data" />
            </div>
          </div>

          {/* Title & Target */}
          <h3 className="text-base sm:text-lg font-bold text-charcoal-900 group-hover:text-ashoka-800 transition-colors line-clamp-2">
            {scholarship.title}
          </h3>

          <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
            <GraduationCap className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span className="truncate">{scholarship.provider}</span>
          </div>

          {/* Amount Box */}
          <div className="mt-4 p-3 rounded-lg bg-ashoka-50/70 border border-ashoka-100">
            <div className="text-[10px] font-bold uppercase tracking-wider text-ashoka-800 mb-0.5">
              Scholarship Support / Year
            </div>
            <div className="text-sm sm:text-base font-extrabold text-ashoka-900">
              {scholarship.amountPerYear}
            </div>
            <div className="text-[11px] text-slate-600 mt-0.5">
              Course Level: <span className="font-medium text-slate-800">{scholarship.courseLevel}</span>
            </div>
          </div>

          {/* Eligibility Criteria Quick Summary */}
          <div className="mt-3.5 space-y-2 text-xs text-slate-600">
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Max Family Income:</span>
              <span className="font-semibold text-slate-800">
                ₹{(scholarship.maxAnnualIncome / 100000).toFixed(2)} Lakh/year
              </span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Min Academic Marks:</span>
              <span className="font-semibold text-slate-800">{scholarship.minPercentage}%</span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Eligible Categories:</span>
              <span className="font-medium text-slate-800">
                {scholarship.eligibleCategories.join(', ')}
              </span>
            </div>
          </div>

          {/* Document Readiness Meter */}
          <div className="mt-4 p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="font-semibold text-slate-700 flex items-center gap-1">
                <FileCheck2 className="w-3.5 h-3.5 text-govgreen-700" />
                Document Readiness
              </span>
              <span className="text-[11px] font-bold text-govgreen-800">
                {readyDocs}/{totalDocs} Prepared ({readinessPercent}%)
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-300 ${
                  readinessPercent >= 80 ? 'bg-govgreen-600' : readinessPercent >= 50 ? 'bg-amber-500' : 'bg-orange-500'
                }`}
                style={{ width: `${readinessPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between gap-2 flex-wrap">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" />
            <span>Deadline: {scholarship.applicationDeadline}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowModal(true)}
              className="text-xs font-semibold text-slate-700 hover:text-ashoka-800 px-2.5 py-1.5 rounded-md hover:bg-slate-100 transition"
            >
              Checklist
            </button>
            <button
              onClick={() => onCheckReadiness ? onCheckReadiness(scholarship) : setShowModal(true)}
              className="inline-flex items-center gap-1 bg-ashoka-700 hover:bg-ashoka-800 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-sm transition"
            >
              <span>Readiness Plan</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Details & Checklist Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-200 shadow-premium p-6">
            <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-xs font-bold text-ashoka-800 bg-ashoka-50 px-2.5 py-0.5 rounded-full border border-ashoka-200">
                    {scholarship.level}
                  </span>
                  <StatusBadge status="demo" label="Sample Student Scheme" />
                </div>
                <h2 className="text-xl font-bold text-charcoal-900">
                  {scholarship.title}
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Provided by: {scholarship.provider}
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
              {/* Notice */}
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-xs text-purple-900 flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold">{scholarship.demoNote}:</span> Demonstration record to evaluate the ScholarReady dynamic document evaluation module.
                </div>
              </div>

              {/* Amount and Grant details */}
              <div className="p-4 rounded-xl bg-ashoka-50 border border-ashoka-200">
                <div className="text-xs font-bold text-ashoka-800 uppercase tracking-wide">
                  Annual Financial Grant
                </div>
                <div className="text-xl font-extrabold text-ashoka-900 mt-1">
                  {scholarship.amountPerYear}
                </div>
                <div className="text-xs text-ashoka-700 mt-1">
                  Target Course Level: <strong>{scholarship.courseLevel}</strong>
                </div>
              </div>

              {/* Document Readiness Checklist */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Required Document Readiness Checklist
                  </h4>
                  <span className="text-xs font-bold text-govgreen-800">
                    {readyDocs} of {totalDocs} Documents Ready
                  </span>
                </div>

                <div className="space-y-2">
                  {scholarship.requiredDocuments.map((doc, idx) => (
                    <div 
                      key={idx} 
                      className={`p-3 rounded-lg border flex items-start justify-between gap-3 ${
                        doc.status === 'ready' 
                          ? 'bg-emerald-50/50 border-emerald-200 text-slate-800' 
                          : doc.status === 'expiring'
                          ? 'bg-amber-50/50 border-amber-200 text-slate-800'
                          : 'bg-rose-50/40 border-rose-200 text-slate-800'
                      }`}
                    >
                      <div className="flex items-start gap-2.5">
                        {doc.status === 'ready' ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                        ) : doc.status === 'expiring' ? (
                          <FileWarning className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                        ) : (
                          <XCircle className="w-4 h-4 text-rose-500 mt-0.5 flex-shrink-0" />
                        )}
                        <div>
                          <div className="text-xs font-bold text-charcoal-900">
                            {doc.name}
                          </div>
                          <div className="text-[11px] text-slate-500 mt-0.5">
                            {doc.description}
                          </div>
                        </div>
                      </div>

                      <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full flex-shrink-0 ${
                        doc.status === 'ready' 
                          ? 'bg-emerald-100 text-emerald-800' 
                          : doc.status === 'expiring'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}>
                        {doc.status === 'ready' ? 'Ready' : doc.status === 'expiring' ? 'Expiring' : 'Missing'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="border-t border-slate-100 pt-4 flex items-center justify-between gap-3">
              <span className="text-xs text-slate-500">
                Deadline: <strong className="text-slate-700">{scholarship.applicationDeadline}</strong>
              </span>

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
                    if (onCheckReadiness) onCheckReadiness(scholarship);
                  }}
                  className="px-4 py-2 text-xs font-semibold text-white bg-ashoka-700 hover:bg-ashoka-800 rounded-lg shadow-sm transition"
                >
                  Start ScholarReady Check
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
