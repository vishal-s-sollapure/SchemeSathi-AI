import React, { useState } from 'react';
import { 
  Building2, 
  ExternalLink, 
  Calendar, 
  CheckCircle2, 
  AlertCircle,
  HelpCircle,
  FileText, 
  ArrowRight,
  ShieldCheck,
  X,
  BookOpen
} from 'lucide-react';
import { Scheme, SchemeEvaluationResult } from '../../types';

interface SchemeCardProps {
  scheme?: Scheme;
  evaluation?: SchemeEvaluationResult;
  onEvaluate?: (schemeId: string) => void;
}

export const SchemeCard: React.FC<SchemeCardProps> = ({ scheme, evaluation, onEvaluate }) => {
  const [showModal, setShowModal] = useState(false);

  // Extract attributes from either evaluation or raw scheme
  const title = evaluation?.official_name || scheme?.title || 'Government Welfare Scheme';
  const department = evaluation?.government_department || scheme?.ministry || 'Government Department';
  const category = evaluation?.category || scheme?.category || 'General';
  const level = evaluation?.level || scheme?.level || 'Central';
  const annualBenefit = evaluation?.annual_benefit || scheme?.annualBenefit || 'Financial Assistance';
  const benefitType = evaluation?.benefit_type || scheme?.benefitType || 'Direct Benefit Transfer (DBT)';
  const description = scheme?.description || 'Official government welfare initiative providing direct financial and social support to verified beneficiaries.';
  const officialSourceUrl = evaluation?.official_source_url || scheme?.officialPortal || '#';
  const applicationUrl = evaluation?.application_url || scheme?.officialPortal || '#';
  const deadline = evaluation?.application_deadline || scheme?.applicationDeadline || 'Continuous Enrollment';
  const verificationDate = evaluation?.verification_date || '2024-11-01';
  const targetBeneficiaries = evaluation?.target_beneficiaries || scheme?.targetBeneficiaries || 'Citizens meeting eligibility criteria';

  // Eligibility Status mapping
  const status = evaluation?.overall_status;
  const matchScore = evaluation?.match_score;

  const renderStatusBadge = () => {
    if (!status) {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-600 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded-full">
          <span>Unassessed</span>
        </span>
      );
    }

    switch (status) {
      case 'MEETS_REQUIREMENT':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-300 px-2.5 py-0.5 rounded-full shadow-xs">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Eligible ({matchScore}% Match)</span>
          </span>
        );
      case 'MISSING_INFORMATION':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 bg-amber-50 border border-amber-300 px-2.5 py-0.5 rounded-full shadow-xs">
            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
            <span>Missing Information</span>
          </span>
        );
      case 'DOES_NOT_MEET_REQUIREMENT':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-rose-800 bg-rose-50 border border-rose-300 px-2.5 py-0.5 rounded-full shadow-xs">
            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>Not Eligible</span>
          </span>
        );
      case 'NEEDS_REVIEW':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-purple-800 bg-purple-50 border border-purple-300 px-2.5 py-0.5 rounded-full shadow-xs">
            <AlertCircle className="w-3.5 h-3.5 text-purple-600" />
            <span>Needs Administrative Review</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <>
      <div className="bg-white rounded-xl border border-slate-200/90 hover:border-govgreen-300 shadow-subtle hover:shadow-elevated transition-all duration-200 flex flex-col justify-between p-5 relative overflow-hidden group">
        {/* Top Accent Strip */}
        <div className={`absolute top-0 left-0 right-0 h-1.5 ${
          status === 'MEETS_REQUIREMENT' 
            ? 'bg-gradient-to-r from-emerald-600 to-teal-500'
            : status === 'MISSING_INFORMATION'
            ? 'bg-gradient-to-r from-amber-500 to-yellow-400'
            : status === 'DOES_NOT_MEET_REQUIREMENT'
            ? 'bg-gradient-to-r from-rose-500 to-red-400'
            : 'bg-gradient-to-r from-govgreen-700 via-govgreen-500 to-emerald-400'
        }`} />

        <div>
          {/* Header Row: Category & Badges */}
          <div className="flex items-center justify-between gap-2 flex-wrap mb-3 pt-1">
            <span className="text-[11px] font-semibold text-govgreen-800 bg-govgreen-50 border border-govgreen-200/70 px-2.5 py-0.5 rounded-md">
              {category}
            </span>

            <div className="flex items-center gap-1.5 flex-wrap">
              {renderStatusBadge()}
              <span className="text-[10px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                {level}
              </span>
            </div>
          </div>

          {/* Scheme Title & Ministry */}
          <h3 className="text-base sm:text-lg font-bold text-charcoal-900 group-hover:text-govgreen-800 transition-colors line-clamp-2">
            {title}
          </h3>

          <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
            <Building2 className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span className="truncate">{department}</span>
          </div>

          {/* Benefit Highlight Box */}
          <div className="mt-4 p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-100/90">
            <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 mb-0.5">
              Assistance &amp; Financial Benefit
            </div>
            <div className="text-sm sm:text-base font-extrabold text-govgreen-900">
              {annualBenefit}
            </div>
            <div className="text-[11px] text-emerald-700 mt-0.5">
              Delivery Channel: <span className="font-semibold">{benefitType}</span>
            </div>
          </div>

          {/* Description */}
          <p className="mt-3 text-xs text-slate-600 line-clamp-2 leading-relaxed">
            {description}
          </p>

          {/* Important Conditions / Key Requirements */}
          <div className="mt-3 pt-3 border-t border-slate-100 space-y-1.5">
            <div className="text-[11px] font-semibold text-slate-700 flex items-center justify-between">
              <span>Verified Eligibility Criteria:</span>
              {evaluation && (
                <span className="text-[10px] text-slate-500">
                  {evaluation.requirements_satisfied.length} satisfied / {evaluation.requirements_satisfied.length + evaluation.requirements_not_satisfied.length + evaluation.missing_information.length + evaluation.conditions_under_review.length} rules
                </span>
              )}
            </div>

            {/* Display rule items if evaluated, or static criteria */}
            {evaluation ? (
              <div className="space-y-1">
                {evaluation.requirements_satisfied.slice(0, 2).map((item, idx) => (
                  <div key={`sat-${idx}`} className="flex items-start gap-1.5 text-xs text-emerald-800">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span className="line-clamp-1">{item.requirement_description}</span>
                  </div>
                ))}
                {evaluation.missing_information.slice(0, 1).map((item, idx) => (
                  <div key={`mis-${idx}`} className="flex items-start gap-1.5 text-xs text-amber-800">
                    <HelpCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <span className="line-clamp-1">{item.requirement_description}</span>
                  </div>
                ))}
                {evaluation.requirements_not_satisfied.slice(0, 1).map((item, idx) => (
                  <div key={`not-${idx}`} className="flex items-start gap-1.5 text-xs text-rose-800">
                    <AlertCircle className="w-3.5 h-3.5 text-rose-600 flex-shrink-0 mt-0.5" />
                    <span className="line-clamp-1">{item.requirement_description}</span>
                  </div>
                ))}
              </div>
            ) : (
              (scheme?.eligibilityCriteria || []).slice(0, 2).map((item, idx) => (
                <div key={idx} className="flex items-start gap-1.5 text-xs text-slate-600">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <span className="line-clamp-1">{item}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between gap-2 flex-wrap">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" />
            <span>Verified: {verificationDate}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowModal(true)}
              className="text-xs font-semibold text-slate-700 hover:text-govgreen-800 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 transition"
            >
              Evidence &amp; Details
            </button>
            <a
              href={applicationUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 bg-govgreen-700 hover:bg-govgreen-800 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-sm transition"
            >
              <span>Official Portal</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>

      {/* Details & Official Source Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-200 shadow-premium p-6">
            <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                  <span className="text-xs font-bold text-govgreen-800 bg-govgreen-50 px-2.5 py-0.5 rounded-full border border-govgreen-200">
                    {category}
                  </span>
                  <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md">
                    {level}
                  </span>
                  {renderStatusBadge()}
                </div>
                <h2 className="text-xl font-bold text-charcoal-900">
                  {title}
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Issued by: {department} • Verified {verificationDate}
                </p>
              </div>

              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-700 p-1.5 rounded-lg hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4 space-y-5">
              {/* Official Source Reference Card */}
              <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-3.5 text-xs text-emerald-950 flex items-start gap-2.5">
                <ShieldCheck className="w-4 h-4 text-emerald-700 flex-shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="font-bold text-govgreen-900">
                    Official Government Citation &amp; Gazette Reference
                  </div>
                  <div className="text-[11px] text-slate-700">
                    {evaluation?.official_source_title || 'Central / State Operational Guidelines'} 
                    {evaluation?.circular_number && ` • Circular: ${evaluation.circular_number}`}
                  </div>
                  <a
                    href={officialSourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 font-semibold text-govgreen-800 hover:underline text-[11px] mt-0.5"
                  >
                    <span>View Authoritative Notification</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>

              {/* Benefit Box */}
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <div className="text-xs font-bold text-emerald-800 uppercase tracking-wide">
                  Benefit Amount &amp; Delivery Channel
                </div>
                <div className="text-xl font-extrabold text-govgreen-900 mt-1">
                  {annualBenefit}
                </div>
                <div className="text-xs text-emerald-700 mt-1">
                  Disbursement Mode: <strong>{benefitType}</strong> • Cycle: <strong>{evaluation?.policy_cycle || 'Continuous'}</strong>
                </div>
              </div>

              {/* Target Beneficiaries */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Target Beneficiary Group
                </h4>
                <p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200">
                  {targetBeneficiaries}
                </p>
              </div>

              {/* Evaluated Rule Breakdown */}
              {evaluation && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5 flex items-center justify-between">
                    <span>Deterministic Eligibility Criteria Evaluation</span>
                    <span className="text-[11px] text-govgreen-800 font-semibold">
                      {evaluation.match_score}% Score
                    </span>
                  </h4>

                  <div className="space-y-2">
                    {/* Satisfied Criteria */}
                    {evaluation.requirements_satisfied.map((item, idx) => (
                      <div key={`s-${idx}`} className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200 space-y-1">
                        <div className="flex items-center justify-between text-xs font-bold text-emerald-900">
                          <span className="flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            {item.requirement_description}
                          </span>
                          <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                            SATISFIED
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-700">{item.explanation}</p>
                        <div className="text-[10px] text-slate-500 font-mono">
                          Clause: {item.clause_or_section} {item.page_number && `(Page ${item.page_number})`}
                        </div>
                      </div>
                    ))}

                    {/* Missing Information Criteria */}
                    {evaluation.missing_information.map((item, idx) => (
                      <div key={`m-${idx}`} className="p-3 rounded-lg bg-amber-50/60 border border-amber-200 space-y-1">
                        <div className="flex items-center justify-between text-xs font-bold text-amber-900">
                          <span className="flex items-center gap-1.5">
                            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
                            {item.requirement_description}
                          </span>
                          <span className="text-[10px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded">
                            INFO NEEDED
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-700">{item.explanation}</p>
                        <div className="text-[10px] text-slate-500 font-mono">
                          Clause: {item.clause_or_section}
                        </div>
                      </div>
                    ))}

                    {/* Unmet Criteria */}
                    {evaluation.requirements_not_satisfied.map((item, idx) => (
                      <div key={`f-${idx}`} className="p-3 rounded-lg bg-rose-50/60 border border-rose-200 space-y-1">
                        <div className="flex items-center justify-between text-xs font-bold text-rose-900">
                          <span className="flex items-center gap-1.5">
                            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                            {item.requirement_description}
                          </span>
                          <span className="text-[10px] bg-rose-100 text-rose-800 px-2 py-0.5 rounded">
                            DOES NOT MEET
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-700">{item.explanation}</p>
                        <div className="text-[10px] text-slate-500 font-mono">
                          Clause: {item.clause_or_section}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actionable Instructions */}
              {evaluation?.suggested_next_actions && evaluation.suggested_next_actions.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Actionable Citizen Next Steps
                  </h4>
                  <ul className="space-y-1.5 bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs text-slate-700">
                    {evaluation.suggested_next_actions.map((action, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="w-4 h-4 rounded-full bg-govgreen-100 text-govgreen-800 flex items-center justify-center font-bold text-[10px] flex-shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span>{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Required Documents */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Mandatory Verification Documents
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {(evaluation?.required_documents || (scheme?.requiredDocuments?.map(d => ({ title: d, issuing_authority: 'Competent Authority', is_mandatory: true })) || [])).map((doc: any, idx: number) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-800 flex items-start gap-2">
                      <FileText className="w-4 h-4 text-govgreen-700 flex-shrink-0 mt-0.5" />
                      <div>
                        <div className="font-semibold">{doc.title}</div>
                        {doc.issuing_authority && (
                          <div className="text-[10px] text-slate-500">Issuer: {doc.issuing_authority}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="border-t border-slate-100 pt-4 flex items-center justify-between gap-3 flex-wrap">
              <a
                href={officialSourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-govgreen-800 transition"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Official Circular</span>
                <ExternalLink className="w-3 h-3" />
              </a>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-lg transition"
                >
                  Close
                </button>
                <a
                  href={applicationUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 text-xs font-semibold text-white bg-govgreen-700 hover:bg-govgreen-800 rounded-lg shadow-sm transition inline-flex items-center gap-1"
                >
                  <span>Apply on Official Portal</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

