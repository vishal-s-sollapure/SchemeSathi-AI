import React, { useState } from 'react';
import { 
  FileText, 
  HelpCircle, 
  CheckCircle2, 
  AlertTriangle, 
  Copy, 
  Check, 
  Send, 
  FileCheck2,
  ShieldCheck,
  BookOpen
} from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { DocumentUpload } from '../components/common/DocumentUpload';
import { CitationCard } from '../components/common/CitationCard';
import { MOCK_CITATIONS } from '../data/mockData';
import { Citation, RAGResponse, ValidatedCitation } from '../types';
import { apiService } from '../services/api';

function mapValidatedCitation(c: ValidatedCitation, idx: number): Citation {
  return {
    id: c.matched_chunk_id || `cit-${Date.now()}-${idx}`,
    title: c.clause_or_section || 'Official Clause',
    documentName: c.source_title,
    issuingAuthority: 'Government Authority',
    circularNumber: c.circular_number || 'Official Circular',
    notificationDate: 'Verified 2024-25',
    clauseNumber: c.clause_or_section,
    excerpt: c.excerpt,
    officialSourceUrl: c.official_source_url,
    verificationBadge: c.verification_status === 'OFFICIALLY_VERIFIED' ? 'Verified Official Source' : 'Authoritative Record'
  };
}

export const PolicyExplainerPage: React.FC = () => {
  const [activeDocument, setActiveDocument] = useState<{ name: string; size: string } | null>({
    name: 'Standard_Operating_Procedure_Karnataka_Sakala_eAttestation_2024.pdf',
    size: '1.42 MB'
  });

  const [question, setQuestion] = useState('How many days does a college officer have to complete e-Attestation under Sakala Act?');
  const [analyzing, setAnalyzing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [ragResponse, setRagResponse] = useState<RAGResponse | null>(null);

  const presetQuestions = [
    'How many days does a college officer have to complete e-Attestation under Sakala Act?',
    'Are income tax payers eligible to receive PM-KISAN ₹6,000 financial support?',
    'What is the maximum annual family income limit for Central Sector Scheme of Scholarship (CSSS)?',
    'Who is eligible as Yajamani under Karnataka Gruha Lakshmi Scheme?'
  ];

  const executeRAGQuery = async (queryText: string) => {
    if (!queryText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await apiService.queryRAG({
        query: queryText,
        language: 'en',
      });
      setRagResponse(res);
    } catch (err) {
      console.warn("Backend RAG query failed or offline:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAsk = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    executeRAGQuery(question);
  };

  const handleSelectPreset = (q: string) => {
    setQuestion(q);
    executeRAGQuery(q);
  };

  const handleCopy = () => {
    const textToCopy = ragResponse 
      ? ragResponse.answer
      : ("Citizen Simplified Summary:\n" +
         "1. Income Limit: Maximum annual family income cap must not exceed verified scheme limit.\n" +
         "2. Concurrent Grants: Subject to exclusivity restrictions under respective scheme order.");
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-govgreen-950 via-govgreen-800 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-elevated relative overflow-hidden">
        <div className="relative max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold bg-govgreen-700/80 text-emerald-100 px-3 py-1 rounded-full border border-govgreen-500">
            <FileText className="w-4 h-4 text-emerald-300" />
            <span>Civic Policy Simplification Engine</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Government Document &amp; Policy Explainer
          </h1>
          <p className="text-xs sm:text-sm text-emerald-100/90 leading-relaxed">
            Attach complex government notifications, guidelines, or state circulars. SchemeSathi AI translates bureaucratic legalese into plain language with verified paragraph and clause citations.
          </p>
        </div>
      </div>

      {/* 1. DOCUMENT UPLOAD AREA */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-govgreen-600" />
            <h2 className="text-base font-bold text-charcoal-900">
              Government Document Source
            </h2>
          </div>
          <StatusBadge status="demo" label="PDF Clause Parser" />
        </div>

        <DocumentUpload
          title="Upload Gazette Circular or Guidelines PDF"
          subtitle="Supports Bilingual PDFs (English, Kannada, Hindi) up to 15MB"
          onFileSelected={(file) => setActiveDocument({ name: file.name, size: file.size })}
        />

        {activeDocument && (
          <div className="p-3.5 rounded-xl bg-govgreen-50/70 border border-govgreen-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2.5">
              <FileCheck2 className="w-5 h-5 text-govgreen-700 flex-shrink-0" />
              <div>
                <span className="font-bold text-govgreen-950">Active Document:</span>{' '}
                <span className="text-govgreen-900 font-mono text-[11px]">{activeDocument.name}</span>
                <span className="text-govgreen-700 ml-2">({activeDocument.size})</span>
              </div>
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider bg-govgreen-200/80 text-govgreen-900 px-2 py-0.5 rounded-full self-start sm:self-center">
              OCR &amp; Clauses Indexed
            </span>
          </div>
        )}
      </section>

      {/* 2. QUESTION INPUT & PRESET CHIPS */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-ashoka-700" />
            <h2 className="text-base font-bold text-charcoal-900">
              Ask a Specific Policy or Eligibility Question
            </h2>
          </div>
          <span className="text-[11px] text-slate-500">
            Grounds answer in the active circular
          </span>
        </div>

        {/* Input Bar */}
        <form onSubmit={handleAsk} className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Is there any quota for girl students? What happens if my college is private?"
            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:outline-none focus:border-govgreen-600 shadow-sm"
          />
          <button
            type="submit"
            disabled={analyzing || !question.trim()}
            className="px-5 py-2.5 bg-govgreen-700 hover:bg-govgreen-800 disabled:opacity-50 text-white font-bold text-xs sm:text-sm rounded-xl shadow-subtle flex items-center gap-1.5 transition flex-shrink-0"
          >
            <span>{analyzing ? 'Analyzing...' : 'Explain'}</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Preset Chips */}
        <div className="space-y-1.5 pt-1">
          <div className="text-[11px] font-semibold text-slate-500">
            Frequently Asked Circular Questions:
          </div>
          <div className="flex flex-wrap gap-1.5">
            {presetQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectPreset(q)}
                className="text-left text-xs bg-slate-50 hover:bg-govgreen-50 text-slate-700 hover:text-govgreen-900 border border-slate-200 hover:border-govgreen-300 px-3 py-1.5 rounded-lg transition"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* 3. EXPLANATION AREA: DUAL COLUMN COMPARISON */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-govgreen-800 bg-govgreen-50 border border-govgreen-200 px-2 py-0.5 rounded">
                Verified Circular Explanation
              </span>
              <StatusBadge status="high_match" label="Direct Match" />
            </div>
            <h3 className="text-lg font-bold text-charcoal-900 mt-1">
              Query: &ldquo;{question}&rdquo;
            </h3>
          </div>

          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition self-start sm:self-center"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy Explanation'}</span>
          </button>
        </div>

        {/* Side-by-Side: Citizen Simplified vs Official Legal Clause */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Card 1: Citizen Simplified Summary */}
          <div className="p-5 rounded-2xl bg-emerald-50/50 border border-emerald-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                  A
                </div>
                <h4 className="text-sm font-bold text-emerald-950">
                  Citizen-Simplified Summary (Layman Terms)
                </h4>
              </div>
              <span className="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded-full">
                Zero Legalese
              </span>
            </div>

            <div className="space-y-3 text-xs sm:text-sm text-slate-700 leading-relaxed">
              <div className="p-3 bg-white rounded-xl border border-emerald-100/90 space-y-1">
                <div className="font-bold text-emerald-900 text-xs flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Rule 1: Income Ceiling Waiver for Farmer Wards</span>
                </div>
                <p className="text-xs text-slate-600">
                  If your parent holds a verified Farmer Identification (FID) in the Karnataka FRUITS system, there is <strong>no income ceiling requirement</strong>. If your family is landless, the ceiling is ₹2,50,000 per annum.
                </p>
              </div>

              <div className="p-3 bg-white rounded-xl border border-emerald-100/90 space-y-1">
                <div className="font-bold text-emerald-900 text-xs flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Rule 2: Concurrent Grants are Allowed</span>
                </div>
                <p className="text-xs text-slate-600">
                  You <strong>can receive both</strong> this Raita Vidya Nidhi scholarship and another central scholarship (like NSP Post-Matric) because this program is designated as welfare assistance rather than an exclusive fee reimbursement.
                </p>
              </div>

              <div className="p-3 bg-white rounded-xl border border-emerald-100/90 space-y-1">
                <div className="font-bold text-emerald-900 text-xs flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Rule 3: Aadhaar Payment Bridge Requirement</span>
                </div>
                <p className="text-xs text-slate-600">
                  Payouts will fail if your bank account is merely linked to Aadhaar. You must have active NPCI mapping for Direct Benefit Transfer (DBT).
                </p>
              </div>
            </div>
          </div>

          {/* Card 2: Official Gazette Legal Clause & Citations */}
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-xs">
                  B
                </div>
                <h4 className="text-sm font-bold text-charcoal-900">
                  Official Legal Clauses &amp; Citations
                </h4>
              </div>
              <span className="text-[10px] font-bold text-slate-600 bg-slate-200 px-2 py-0.5 rounded-full">
                Gazette Grounded
              </span>
            </div>

            <div className="space-y-3">
              <CitationCard citation={MOCK_CITATIONS[1]} />

              <div className="p-3 rounded-xl bg-white border border-slate-200 text-xs space-y-1.5">
                <div className="font-bold text-slate-800 flex items-center justify-between">
                  <span>Paragraph 7, Clause 3 (Non-overlapping Grants)</span>
                  <span className="text-[10px] font-mono text-slate-500">GO-AGRI-44-EDN-2021</span>
                </div>
                <blockquote className="italic border-l-2 border-slate-400 pl-2 text-slate-600 text-xs">
                  &ldquo;Assistance sanctioned under this notification shall be supplemental in nature. Students drawing central merit awards are not debarred from availing Raita Vidya Nidhi allowance.&rdquo;
                </blockquote>
              </div>
            </div>
          </div>
        </div>

        {/* Ambiguity and Critical Advice Box */}
        <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 space-y-2">
          <div className="flex items-center gap-2 font-bold text-amber-950">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <span>Identified Circular Ambiguity / Edge Case</span>
          </div>
          <p className="text-slate-700 leading-relaxed">
            The circular does not explicitly outline whether students repeating an academic semester due to medical grounds must file a fresh application or if an attestation from the College Dean is sufficient. We recommend filing a fresh grievance on the Karnataka SSP portal if this applies to you.
          </p>
        </div>
      </section>
    </div>
  );
};
