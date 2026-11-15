import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, FileText } from 'lucide-react';
import { EligibilityStatus } from '../../types';
import { StatusBadge } from './StatusBadge';

export interface EligibilityCriterionResult {
  ruleName: string;
  userValue: string;
  requiredValue: string;
  status: 'passed' | 'failed' | 'warning' | 'requires_document';
  explanation: string;
  officialCitationReference?: string;
}

interface EligibilityCardProps {
  overallStatus: EligibilityStatus;
  overallScore: number;
  schemeTitle: string;
  issuingBody: string;
  criteriaResults: EligibilityCriterionResult[];
  recommendationText: string;
  onApplyOrFix?: () => void;
}

export const EligibilityCard: React.FC<EligibilityCardProps> = ({
  overallStatus,
  overallScore,
  schemeTitle,
  issuingBody,
  criteriaResults,
  recommendationText,
  onApplyOrFix
}) => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-elevated p-6 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Deterministic Evaluation Engine
            </span>
            <StatusBadge status="demo" label="Simulated Engine" />
          </div>
          <h3 className="text-xl font-bold text-charcoal-900">
            {schemeTitle}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Evaluated against gazette rules from: {issuingBody}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Match Confidence
            </div>
            <div className="text-2xl font-extrabold text-govgreen-800">
              {overallScore}%
            </div>
          </div>
          <StatusBadge status={overallStatus} size="md" />
        </div>
      </div>

      {/* Criteria Breakdown Grid */}
      <div>
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
          Rule-by-Rule Assessment
        </h4>

        <div className="space-y-3">
          {criteriaResults.map((result, idx) => {
            const isPass = result.status === 'passed';
            const isFail = result.status === 'failed';

            return (
              <div 
                key={idx}
                className={`p-3.5 rounded-xl border text-xs transition ${
                  isPass ? 'bg-emerald-50/50 border-emerald-200' :
                  isFail ? 'bg-rose-50/50 border-rose-200' :
                  'bg-amber-50/50 border-amber-200'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2.5">
                    {isPass ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                    ) : isFail ? (
                      <XCircle className="w-4 h-4 text-rose-600 mt-0.5 flex-shrink-0" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                    )}
                    <div>
                      <div className="font-bold text-charcoal-900 text-sm">
                        {result.ruleName}
                      </div>
                      <div className="text-slate-600 mt-1 leading-relaxed">
                        {result.explanation}
                      </div>
                      {result.officialCitationReference && (
                        <div className="mt-2 inline-flex items-center gap-1 text-[11px] font-medium text-govgreen-800 bg-govgreen-100/70 px-2 py-0.5 rounded border border-govgreen-200">
                          <FileText className="w-3 h-3 text-govgreen-700" />
                          <span>Citation: {result.officialCitationReference}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="text-right flex-shrink-0">
                    <div className="text-[10px] text-slate-500">Your profile:</div>
                    <div className="font-bold text-slate-800 mt-0.5">{result.userValue}</div>
                    <div className="text-[10px] text-slate-500 mt-1">Rule threshold:</div>
                    <div className="font-semibold text-slate-700">{result.requiredValue}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recommendation and Next Action */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-bold text-slate-700 uppercase tracking-wide">
            Next Actionable Step
          </div>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 leading-relaxed">
            {recommendationText}
          </p>
        </div>

        {onApplyOrFix && (
          <button
            onClick={onApplyOrFix}
            className="flex-shrink-0 px-4 py-2 text-xs sm:text-sm font-bold text-white bg-govgreen-700 hover:bg-govgreen-800 rounded-xl shadow-subtle transition"
          >
            Resolve Document Gaps
          </button>
        )}
      </div>
    </div>
  );
};
