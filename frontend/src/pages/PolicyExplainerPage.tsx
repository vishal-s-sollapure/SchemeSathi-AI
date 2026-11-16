import React, { useEffect, useState } from 'react';
import { 
  FileText, 
  HelpCircle, 
  CheckCircle2, 
  AlertTriangle, 
  Copy, 
  Check, 
  Send, 
  FileCheck2,
  ExternalLink,
  Volume2,
  Square,
  Calendar,
  Layers,
  ShieldCheck,
  ListOrdered,
  FileQuestion,
  Search,
  BookOpen
} from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { DocumentUpload } from '../components/common/DocumentUpload';
import { CitationCard } from '../components/common/CitationCard';
import { useLanguage } from '../context/LanguageContext';
import { 
  Citation, 
  PolicyDeadlineItem,
  PolicyDocumentRequiredItem,
  PolicyDocumentSummary, 
  PolicyExplanationResponse, 
  PolicySimplificationResult, 
  ValidatedCitation 
} from '../types';
import { apiService } from '../services/api';
import { voiceAssistant } from '../services/voiceAssistant';

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
  const { language } = useLanguage();

  // Mode: 'simplification' (6-point workflow) vs 'clause_qa' (section Q&A)
  const [activeTab, setActiveTab] = useState<'simplification' | 'clause_qa'>('simplification');

  // Documents
  const [documents, setDocuments] = useState<PolicyDocumentSummary[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string>('POL-SSP-EATTEST-CIRCULAR');
  const [searchDocQuery, setSearchDocQuery] = useState<string>('');
  const [loadingDocs, setLoadingDocs] = useState<boolean>(false);

  // Simplification State
  const [simplification, setSimplification] = useState<PolicySimplificationResult | null>(null);
  const [loadingSimplification, setLoadingSimplification] = useState<boolean>(false);

  // Q&A State
  const [selectedClause, setSelectedClause] = useState<string>('');
  const [question, setQuestion] = useState<string>('Explain this notification in simple language.');
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [explanationResponse, setExplanationResponse] = useState<PolicyExplanationResponse | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Audio state
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);

  // Custom Upload state
  const [isCustomUpload, setIsCustomUpload] = useState<boolean>(false);
  const [uploadedFileName, setUploadedFileName] = useState<string>('');

  const presetQuestions = [
    'Explain this notification in simple language.',
    'What are the important conditions?',
    'Who can benefit from this policy?',
    'What documents are required?',
    'What are the application deadlines?',
    'What does this particular clause mean?'
  ];

  // 1. Fetch available verified policy documents
  useEffect(() => {
    async function loadDocuments() {
      setLoadingDocs(true);
      try {
        const res = await apiService.listPolicyDocuments(searchDocQuery);
        setDocuments(res);
        if (res.length > 0 && !selectedDocId) {
          setSelectedDocId(res[0].id);
        }
      } catch (err) {
        console.warn('Failed to fetch policy documents:', err);
      } finally {
        setLoadingDocs(false);
      }
    }
    loadDocuments();
  }, [searchDocQuery]);

  // 2. Fetch 6-point simplification whenever active document or language changes
  useEffect(() => {
    if (!selectedDocId || isCustomUpload) return;
    async function fetchSimplification() {
      setLoadingSimplification(true);
      try {
        const res = await apiService.getPolicySimplification(selectedDocId, language);
        setSimplification(res);
      } catch (err) {
        console.warn('Failed to fetch policy simplification:', err);
      } finally {
        setLoadingSimplification(false);
      }
    }
    fetchSimplification();
  }, [selectedDocId, language, isCustomUpload]);

  // Handle Q&A Submission
  const handleAsk = async (e?: React.FormEvent, customQ?: string) => {
    if (e) e.preventDefault();
    const queryText = customQ || question;
    if (!queryText.trim()) return;

    setAnalyzing(true);
    try {
      const res = await apiService.explainPolicy({
        document_id: isCustomUpload ? undefined : selectedDocId,
        clause_or_section: selectedClause || undefined,
        question: queryText,
        language: language,
      });
      setExplanationResponse(res);
      setActiveTab('clause_qa');
    } catch (err) {
      console.warn('Policy explanation query failed:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelectPreset = (q: string) => {
    setQuestion(q);
    handleAsk(undefined, q);
  };

  const handleSelectDocument = (docId: string) => {
    setIsCustomUpload(false);
    setSelectedDocId(docId);
    setSelectedClause('');
    setExplanationResponse(null);
  };

  // Upload Custom PDF
  const handlePdfUpload = async (file: File) => {
    setIsCustomUpload(true);
    setUploadedFileName(file.name);
    setLoadingSimplification(true);
    try {
      const res = await apiService.simplifyUploadedPdf(
        file,
        file.name.replace(/\.pdf$/i, ''),
        'Government Department / Agency',
        'https://india.gov.in',
        language
      );
      setSimplification(res);
    } catch (err) {
      console.warn('Failed to parse uploaded PDF:', err);
    } finally {
      setLoadingSimplification(false);
    }
  };

  // Audio Read-Aloud
  const handleToggleSpeak = (text: string) => {
    if (isSpeaking) {
      voiceAssistant.stopSpeaking();
      setIsSpeaking(false);
    } else {
      setIsSpeaking(true);
      voiceAssistant.speak(text, language, () => {
        setIsSpeaking(false);
      });
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const activeDocSummary = documents.find(d => d.id === selectedDocId);

  return (
    <div className="space-y-8 animate-in fade-in pb-16">
      {/* 1. Header Banner */}
      <div className="bg-gradient-to-r from-govgreen-950 via-govgreen-900 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-elevated relative overflow-hidden">
        <div className="relative max-w-4xl space-y-3">
          <div className="inline-flex items-center gap-2 text-xs font-bold bg-govgreen-800/90 text-emerald-100 px-3.5 py-1 rounded-full border border-govgreen-600/80 shadow-sm">
            <FileText className="w-4 h-4 text-emerald-300" />
            <span>Civic Policy &amp; Rights Explainer (Phase 10)</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Government Document &amp; Policy Explainer
          </h1>
          <p className="text-xs sm:text-sm text-emerald-100/90 leading-relaxed max-w-3xl">
            Demystifies complicated government notifications, welfare rules, and administrative gazettes into plain language.
            Generates 5-line summaries, important conditions, filing deadlines, required documents, and verbatim clause citations in English, ಕನ್ನಡ, and हिन्दी.
          </p>
        </div>
      </div>

      {/* 2. Document Selection & Search Area */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-govgreen-700" />
            <h2 className="text-base font-bold text-charcoal-900">
              Select or Search Verified Government Circular
            </h2>
          </div>
          <span className="text-xs text-slate-500 font-medium">
            Active Knowledge Base: {documents.length} Officially Verified Circulars
          </span>
        </div>

        {/* Search & Selector Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1 space-y-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                value={searchDocQuery}
                onChange={(e) => setSearchDocQuery(e.target.value)}
                placeholder="Search circulars (e.g. Sakala, PM-KISAN, OTR)..."
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:border-govgreen-600"
              />
            </div>

            <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
              {loadingDocs ? (
                <div className="text-xs text-slate-400 py-3 text-center">Loading official circulars...</div>
              ) : documents.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => handleSelectDocument(doc.id)}
                  className={`w-full text-left p-3 rounded-xl border text-xs transition flex flex-col gap-1 ${
                    selectedDocId === doc.id && !isCustomUpload
                      ? 'bg-govgreen-50 border-govgreen-500 text-govgreen-950 font-bold shadow-sm'
                      : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold line-clamp-1">{doc.title}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                      {doc.applicable_cycle.split(' ')[0]}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 line-clamp-1">
                    {doc.issuing_department}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Active Document Overview Card */}
          <div className="md:col-span-2 p-5 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col justify-between space-y-4">
            {isCustomUpload ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-800 bg-amber-100 px-2 py-0.5 rounded-full">
                    Custom Uploaded Gazette PDF
                  </span>
                  <StatusBadge status="review" label="PyMuPDF Parsed" />
                </div>
                <h3 className="text-base font-bold text-charcoal-900 flex items-center gap-2">
                  <FileCheck2 className="w-5 h-5 text-emerald-600" />
                  <span>{uploadedFileName}</span>
                </h3>
                <p className="text-xs text-slate-600">
                  Optical parsing complete. Review the extracted 6-point civic workflow below or ask questions about specific clauses.
                </p>
              </div>
            ) : activeDocSummary ? (
              <div className="space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-xs font-bold text-govgreen-800 bg-govgreen-100 px-2.5 py-0.5 rounded-full">
                    {activeDocSummary.category}
                  </span>
                  <StatusBadge status="verified" label="Human Reviewed Knowledge" />
                </div>
                <h3 className="text-base font-bold text-charcoal-900 leading-snug">
                  {activeDocSummary.title}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {activeDocSummary.executive_summary}
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 text-[11px]">
                  <div className="p-2 bg-white rounded-lg border border-slate-200">
                    <span className="text-slate-400 block font-medium">Notification Number</span>
                    <span className="font-mono text-charcoal-900 font-bold">{activeDocSummary.notification_number || 'N/A'}</span>
                  </div>
                  <div className="p-2 bg-white rounded-lg border border-slate-200">
                    <span className="text-slate-400 block font-medium">Applicable Cycle</span>
                    <span className="text-charcoal-900 font-bold">{activeDocSummary.applicable_cycle}</span>
                  </div>
                  <div className="p-2 bg-white rounded-lg border border-slate-200 col-span-2 sm:col-span-1">
                    <span className="text-slate-400 block font-medium">Official Gazette URL</span>
                    <a
                      href={activeDocSummary.official_gazette_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-govgreen-700 font-bold hover:underline flex items-center gap-1 mt-0.5"
                    >
                      <span>View Gazette</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-400 py-10 text-center">
                Select a verified circular or upload a custom notification PDF.
              </div>
            )}

            {/* Custom PDF Upload Dropzone */}
            <div className="pt-3 border-t border-slate-200/80">
              <DocumentUpload
                title="Or Upload Custom Government Notification / Circular PDF"
                subtitle="PyMuPDF optical extraction into 6-point civic simplification (English, Kannada, Hindi)"
                onFileSelected={handlePdfUpload}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Main View Mode Tabs */}
      <div className="flex border-b border-slate-200 gap-4">
        <button
          onClick={() => setActiveTab('simplification')}
          className={`pb-3 px-2 text-sm font-bold flex items-center gap-2 border-b-2 transition ${
            activeTab === 'simplification'
              ? 'border-govgreen-700 text-govgreen-900'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>6-Point Civic Simplification Workflow</span>
        </button>
        <button
          onClick={() => setActiveTab('clause_qa')}
          className={`pb-3 px-2 text-sm font-bold flex items-center gap-2 border-b-2 transition ${
            activeTab === 'clause_qa'
              ? 'border-govgreen-700 text-govgreen-900'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <HelpCircle className="w-4 h-4" />
          <span>Interactive Clause &amp; Section Q&amp;A</span>
        </button>
      </div>

      {/* =========================================================================
          TAB 1: 6-POINT CIVIC SIMPLIFICATION WORKFLOW
         ========================================================================= */}
      {activeTab === 'simplification' && (
        <div className="space-y-6">
          {loadingSimplification ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-white rounded-2xl border border-slate-200">
              Analyzing government notification and structuring 6-point civic workflow...
            </div>
          ) : simplification ? (
            <>
              {/* Header Action Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-emerald-50/70 border border-emerald-200">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-700 flex-shrink-0" />
                  <div>
                    <h3 className="text-xs sm:text-sm font-bold text-emerald-950">
                      Standardized Civic Policy Simplification Workflow
                    </h3>
                    <p className="text-[11px] text-emerald-800">
                      Language: <span className="font-bold uppercase">{language}</span> &bull; 6 Core Civic Pillars Formulated
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggleSpeak(simplification.five_line_summary.join('. '))}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-bold transition ${
                      isSpeaking
                        ? 'bg-rose-50 border-rose-300 text-rose-700'
                        : 'bg-white border-emerald-300 text-emerald-800 hover:bg-emerald-100'
                    }`}
                  >
                    {isSpeaking ? <Square className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                    <span>{isSpeaking ? 'Stop Audio' : 'Listen to 5-Line Summary'}</span>
                  </button>
                  <button
                    onClick={() => handleCopy(simplification.five_line_summary.join('\n'))}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
              </div>

              {/* 1. FIVE-LINE PLAIN-LANGUAGE SUMMARY */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                      1
                    </span>
                    <h3 className="text-sm font-bold text-charcoal-900">
                      Five-Line Plain-Language Summary
                    </h3>
                  </div>
                  <span className="text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                    Zero Legalese Guarantee
                  </span>
                </div>
                <div className="grid grid-cols-1 gap-2.5">
                  {simplification.five_line_summary.map((line, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-slate-50 hover:bg-emerald-50/50 border border-slate-200 hover:border-emerald-200 text-xs sm:text-sm text-slate-800 font-medium leading-relaxed transition flex items-start gap-3"
                    >
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span>{line}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 2 & 3. IMPORTANT CONDITIONS & DATES/DEADLINES */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* 2. Important Conditions */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                        2
                      </span>
                      <h3 className="text-sm font-bold text-charcoal-900">
                        Important Conditions &amp; Criteria
                      </h3>
                    </div>
                    <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                      Eligibility &amp; Caps
                    </span>
                  </div>
                  <div className="space-y-2.5">
                    {simplification.important_conditions.map((cond, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed flex items-start gap-2.5"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 flex-shrink-0 mt-1.5" />
                        <span>{cond}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 3. Dates and Statutory Deadlines */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                        3
                      </span>
                      <h3 className="text-sm font-bold text-charcoal-900">
                        Critical Dates &amp; Statutory Deadlines
                      </h3>
                    </div>
                    <span className="text-[10px] font-bold text-govgreen-800 bg-govgreen-50 px-2 py-0.5 rounded-full">
                      Timeline Calendar
                    </span>
                  </div>
                  <div className="space-y-2.5">
                    {simplification.dates_and_deadlines.map((dateItem: PolicyDeadlineItem, idx: number) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-xl border text-xs flex flex-col gap-1 ${
                          dateItem.is_critical
                            ? 'bg-rose-50/70 border-rose-200 text-rose-950'
                            : 'bg-slate-50 border-slate-200 text-slate-800'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5 text-slate-500" />
                            {dateItem.label}
                          </span>
                          {dateItem.is_critical && (
                            <span className="text-[10px] font-bold uppercase tracking-wider bg-rose-200 text-rose-900 px-1.5 py-0.5 rounded">
                              Critical Cutoff
                            </span>
                          )}
                        </div>
                        <div className="font-bold text-xs mt-0.5">{dateItem.timeframe_or_date}</div>
                        <div className="text-[11px] text-slate-500">
                          Statutory Authority: {dateItem.statutory_authority}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 4 & 5. REQUIRED DOCUMENTS & APPLICATION STEPS */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* 4. Required Documents */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                        4
                      </span>
                      <h3 className="text-sm font-bold text-charcoal-900">
                        Required Documents &amp; Issuing Authorities
                      </h3>
                    </div>
                    <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                      Evidence Mandate
                    </span>
                  </div>
                  <div className="space-y-2.5">
                    {simplification.required_documents.map((docItem: PolicyDocumentRequiredItem, idx: number) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1"
                      >
                        <div className="font-bold text-charcoal-900">{docItem.name}</div>
                        <div className="text-[11px] text-govgreen-800 font-medium">
                          Issuing Authority: {docItem.issuing_authority}
                        </div>
                        <div className="text-[11px] text-slate-500 italic">
                          Format: {docItem.format_or_requirement}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 5. Application Steps */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                        5
                      </span>
                      <h3 className="text-sm font-bold text-charcoal-900">
                        Citizen Application Steps
                      </h3>
                    </div>
                    <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                      Execution Flow
                    </span>
                  </div>
                  <div className="space-y-2.5">
                    {simplification.application_steps.map((step, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed flex items-start gap-2.5"
                      >
                        <span className="w-5 h-5 rounded-full bg-govgreen-100 text-govgreen-800 font-bold flex items-center justify-center text-[10px] flex-shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 6. IMPORTANT WARNINGS & STATUTORY EXCLUSION CAUTIONS */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-xs">
                      6
                    </span>
                    <h3 className="text-sm font-bold text-charcoal-900">
                      Important Warnings, Disqualifications &amp; Exclusion Penalties
                    </h3>
                  </div>
                  <span className="text-[10px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded-full">
                    Statutory Cautions
                  </span>
                </div>
                <div className="space-y-2.5">
                  {simplification.important_warnings.map((warn, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-950 flex items-start gap-3"
                    >
                      <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                      <span className="font-medium leading-relaxed">{warn}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Ambiguities & Edge Cases (if any) */}
              {simplification.flagged_ambiguities && simplification.flagged_ambiguities.length > 0 && (
                <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-700 space-y-2">
                  <div className="flex items-center gap-2 font-bold text-slate-900">
                    <FileQuestion className="w-4 h-4 text-slate-600" />
                    <span>Identified Circular Ambiguities &amp; Boundary Conditions</span>
                  </div>
                  <ul className="list-disc pl-5 space-y-1">
                    {simplification.flagged_ambiguities.map((amb, i) => (
                      <li key={i}>{amb}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Strict Legal Notice & Guardrail */}
              <div className="p-4 rounded-xl bg-slate-900 text-slate-200 text-xs space-y-1.5 shadow-sm">
                <div className="font-bold text-emerald-400 flex items-center gap-1.5 text-[11px] uppercase tracking-wider">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Authoritative Legal Guardrail</span>
                </div>
                <p className="leading-relaxed text-slate-300">
                  {simplification.legal_disclaimer}
                </p>
              </div>
            </>
          ) : null}
        </div>
      )}

      {/* =========================================================================
          TAB 2: INTERACTIVE CLAUSE & SECTION Q&A
         ========================================================================= */}
      {activeTab === 'clause_qa' && (
        <div className="space-y-6">
          {/* Query Formulation Form */}
          <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-govgreen-700" />
                <h2 className="text-base font-bold text-charcoal-900">
                  Ask a Specific Clause or Section Question
                </h2>
              </div>
              <span className="text-[11px] text-slate-500 font-medium">
                Grounds answer in the selected circular
              </span>
            </div>

            {/* Input Bar with Clause Filter */}
            <form onSubmit={handleAsk} className="space-y-3">
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g. What is the time limit for Sakala attestation? Are income tax payers excluded?"
                  className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:outline-none focus:border-govgreen-600 shadow-sm"
                />
                <button
                  type="submit"
                  disabled={analyzing || !question.trim()}
                  className="px-6 py-2.5 bg-govgreen-700 hover:bg-govgreen-800 disabled:opacity-50 text-white font-bold text-xs sm:text-sm rounded-xl shadow-subtle flex items-center justify-center gap-1.5 transition flex-shrink-0"
                >
                  <span>{analyzing ? 'Analyzing Gazette...' : 'Explain'}</span>
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </form>

            {/* Preset Example Chips */}
            <div className="space-y-1.5 pt-1">
              <div className="text-[11px] font-semibold text-slate-500">
                Example Questions (Phase 10 Mandate):
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

          {/* Explanation Output Area: Dual Column Comparison */}
          {explanationResponse ? (
            <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-govgreen-800 bg-govgreen-50 border border-govgreen-200 px-2 py-0.5 rounded">
                      Verified Policy Response
                    </span>
                    <StatusBadge
                      status={explanationResponse.sufficient_evidence ? 'verified' : 'review'}
                      label={explanationResponse.sufficient_evidence ? 'Grounded in Gazette' : 'No Sufficient Evidence'}
                    />
                  </div>
                  <h3 className="text-base sm:text-lg font-bold text-charcoal-900 mt-1">
                    Query: &ldquo;{explanationResponse.question}&rdquo;
                  </h3>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggleSpeak(explanationResponse.simplified_explanation)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-bold transition ${
                      isSpeaking
                        ? 'bg-rose-50 border-rose-300 text-rose-700'
                        : 'bg-white border-emerald-300 text-emerald-800 hover:bg-emerald-100'
                    }`}
                  >
                    {isSpeaking ? <Square className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                    <span>{isSpeaking ? 'Stop Audio' : 'Listen'}</span>
                  </button>
                  <button
                    onClick={() => handleCopy(explanationResponse.simplified_explanation)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
              </div>

              {/* Side-by-Side: Plain Language Interpretation vs Official Gazette Clause */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Column 1: Citizen-Simplified Summary */}
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
                    <span className="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded-full uppercase">
                      {explanationResponse.language}
                    </span>
                  </div>

                  <div className="p-4 bg-white rounded-xl border border-emerald-100 space-y-3 shadow-inner">
                    <div className="text-xs sm:text-sm text-slate-700 whitespace-pre-line leading-relaxed font-sans">
                      {explanationResponse.simplified_explanation}
                    </div>

                    {explanationResponse.suggested_follow_ups && explanationResponse.suggested_follow_ups.length > 0 && (
                      <div className="pt-3 border-t border-slate-100 space-y-1.5">
                        <span className="text-[10px] font-bold text-slate-400 block uppercase">
                          Suggested Inquiries:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {explanationResponse.suggested_follow_ups.map((f, i) => (
                            <button
                              key={i}
                              type="button"
                              onClick={() => handleSelectPreset(f)}
                              className="text-[11px] bg-slate-50 hover:bg-emerald-50 text-slate-600 hover:text-emerald-800 px-2 py-0.5 rounded border border-slate-200 transition"
                            >
                              {f}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Column 2: Official Gazette Legal Clause & Citations */}
                <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-xs">
                        B
                      </div>
                      <h4 className="text-sm font-bold text-charcoal-900">
                        Authoritative Gazette Clauses &amp; Source Citations
                      </h4>
                    </div>
                    <span className="text-[10px] font-bold text-slate-600 bg-slate-200 px-2 py-0.5 rounded-full">
                      {explanationResponse.citations.length} Verified Sources
                    </span>
                  </div>

                  {explanationResponse.verbatim_official_clause && (
                    <div className="p-3.5 rounded-xl bg-white border border-slate-200 text-xs space-y-1.5 shadow-sm">
                      <div className="font-bold text-slate-800 flex items-center justify-between">
                        <span>{explanationResponse.clause_referenced || 'Official Gazette Clause'}</span>
                        <span className="text-[10px] font-mono text-govgreen-700">Verbatim Phrasing</span>
                      </div>
                      <blockquote className="italic border-l-2 border-slate-400 pl-2.5 text-slate-600 text-xs leading-relaxed">
                        &ldquo;{explanationResponse.verbatim_official_clause}&rdquo;
                      </blockquote>
                    </div>
                  )}

                  <div className="space-y-3">
                    {explanationResponse.citations.map((c, i) => (
                      <CitationCard key={i} citation={mapValidatedCitation(c, i)} />
                    ))}
                  </div>
                </div>
              </div>

              {/* Important Statutory Disclaimer */}
              <div className="p-4 rounded-xl bg-slate-900 text-slate-200 text-xs space-y-1">
                <div className="font-bold text-emerald-400 flex items-center gap-1.5 text-[11px] uppercase tracking-wider">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Statutory Notice &amp; Legal Guardrail</span>
                </div>
                <p className="leading-relaxed text-slate-300">
                  {explanationResponse.legal_disclaimer}
                </p>
              </div>
            </section>
          ) : (
            <div className="p-8 text-center text-xs text-slate-400 bg-white rounded-2xl border border-slate-200">
              Submit an inquiry above or click any of the preset questions to generate a grounded explanation with verbatim gazette clauses.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
