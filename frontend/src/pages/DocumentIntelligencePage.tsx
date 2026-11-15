import React, { useState } from 'react';
import { 
  FileSearch, 
  CheckCircle2, 
  Clock, 
  Sparkles, 
  Download, 
  Calendar, 
  AlertTriangle, 
  RefreshCw, 
  Layers, 
  FileCheck2 
} from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { DocumentUpload } from '../components/common/DocumentUpload';
import { MOCK_DOCUMENT_ANALYSIS } from '../data/mockData';
import { DocumentAnalysisResult } from '../types';

export const DocumentIntelligencePage: React.FC = () => {
  const [analysisData, setAnalysisData] = useState<DocumentAnalysisResult>(MOCK_DOCUMENT_ANALYSIS);
  const [processingStage, setProcessingStage] = useState<number>(4); // 4 = completed
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [downloadSuccess, setDownloadSuccess] = useState<boolean>(false);

  const pipelineStages = [
    { id: 1, name: 'PyMuPDF Text & Layout Extraction', desc: 'Bilingual OCR & tabular layout preservation' },
    { id: 2, name: 'Legal Clause Segmentation', desc: 'Isolating eligibility conditions & sub-clauses' },
    { id: 3, name: 'Rule Engine Mapping', desc: 'Deterministic matching against citizen criteria' },
    { id: 4, name: 'Gazette Citation Grounding', desc: 'Attaching verifiable circular metadata' }
  ];

  const handleFileUploaded = (file: { name: string; size: string }) => {
    setIsProcessing(true);
    setProcessingStage(1);

    // Simulate multi-step pipeline progression
    setTimeout(() => setProcessingStage(2), 600);
    setTimeout(() => setProcessingStage(3), 1200);
    setTimeout(() => {
      setProcessingStage(4);
      setIsProcessing(false);
      setAnalysisData({
        ...MOCK_DOCUMENT_ANALYSIS,
        fileName: file.name,
        fileSize: file.size
      });
    }, 1800);
  };

  const handleDownload = () => {
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 2500);
  };

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-govgreen-950 via-charcoal-900 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-elevated relative overflow-hidden">
        <div className="relative max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold bg-govgreen-800 text-emerald-200 px-3 py-1 rounded-full border border-govgreen-600">
            <FileSearch className="w-4 h-4 text-emerald-300" />
            <span>Document Intelligence Pipeline</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Automated Circular &amp; PDF Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Fast, client-side extraction of eligibility parameters, mandatory checklists, and critical filing deadlines from official Indian government circulars using specialized NLP &amp; deterministic parsing.
          </p>
        </div>
      </div>

      {/* 1. PDF UPLOAD INTERFACE */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-govgreen-600" />
            <h2 className="text-base font-bold text-charcoal-900">
              Upload Official Circular or Gazette Notice
            </h2>
          </div>
          <StatusBadge status="demo" label="Document Intelligence Engine" />
        </div>

        <DocumentUpload
          title="Drop Government Circular PDF here"
          subtitle="Supports bilingual documents in English, Kannada, Hindi (PyMuPDF parser ready)"
          onFileSelected={handleFileUploaded}
        />
      </section>

      {/* 2. DOCUMENT PROCESSING PIPELINE STAGES */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-charcoal-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-govgreen-700" />
              <span>Document Processing Pipeline</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Active file: <strong className="text-slate-800 font-mono text-[11px]">{analysisData.fileName}</strong> ({analysisData.fileSize})
            </p>
          </div>

          <div className="flex items-center gap-2">
            {isProcessing ? (
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-800 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-600" />
                Processing Pipeline...
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-800 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                Pipeline Complete (100% Extracted)
              </span>
            )}
          </div>
        </div>

        {/* 4 Pipeline Stage Badges */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {pipelineStages.map((stage) => {
            const isDone = processingStage >= stage.id;
            const isCurrent = processingStage === stage.id && isProcessing;

            return (
              <div
                key={stage.id}
                className={`p-3.5 rounded-xl border text-xs transition ${
                  isDone 
                    ? 'bg-govgreen-50/60 border-govgreen-200 text-govgreen-950' 
                    : isCurrent 
                    ? 'bg-amber-50 border-amber-300 text-amber-950 animate-pulse' 
                    : 'bg-slate-50 border-slate-200 text-slate-400'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                    Stage 0{stage.id}
                  </span>
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-govgreen-700" />
                  ) : isCurrent ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-600" />
                  ) : (
                    <Clock className="w-3.5 h-3.5 text-slate-300" />
                  )}
                </div>
                <div className="font-bold">{stage.name}</div>
                <div className="text-[11px] text-slate-500 mt-0.5 leading-snug">{stage.desc}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 3. SUMMARY DISPLAY AREA */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold text-govgreen-800 bg-govgreen-50 px-2.5 py-0.5 rounded border border-govgreen-200">
                Extracted Intelligence Summary
              </span>
              <StatusBadge status="demo" label="Demo Verification" />
            </div>
            <h2 className="text-xl font-bold text-charcoal-900">
              {analysisData.documentType}
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Issued by: <strong>{analysisData.issuingDepartment}</strong> &bull; Extracted {analysisData.pages} Pages
            </p>
          </div>

          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-govgreen-700 hover:bg-govgreen-800 text-white text-xs font-bold shadow-subtle transition self-start sm:self-center"
          >
            <Download className="w-4 h-4" />
            <span>{downloadSuccess ? 'Summary Exported!' : 'Export Summary (JSON/PDF)'}</span>
          </button>
        </div>

        {/* Executive Summary Box */}
        <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200 space-y-2">
          <div className="text-xs font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
            <span>Executive Policy Summary</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
            {analysisData.executiveSummary}
          </p>
        </div>

        {/* Key Eligibility Rules Table */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Deterministic Eligibility Rules Extracted
          </h3>
          <div className="space-y-2">
            {analysisData.keyEligibilityRules.map((rule, idx) => (
              <div 
                key={idx}
                className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
              >
                <div className="space-y-0.5">
                  <div className="font-bold text-charcoal-900 text-xs sm:text-sm">
                    {rule.criterion}
                  </div>
                  <div className="text-slate-500 text-[11px] font-mono">
                    Clause: {rule.officialClause}
                  </div>
                </div>
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full self-start sm:self-center ${
                  rule.requirementType === 'Mandatory' 
                    ? 'bg-rose-100 text-rose-900 border border-rose-200' 
                    : rule.requirementType === 'Relaxation Available'
                    ? 'bg-emerald-100 text-emerald-900 border border-emerald-200'
                    : 'bg-amber-100 text-amber-900 border border-amber-200'
                }`}>
                  {rule.requirementType}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Mandatory Document Checklist */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Mandatory Documents Checklist for Applicant
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {analysisData.mandatoryDocumentList.map((doc, idx) => (
              <div key={idx} className="p-3.5 rounded-xl border border-slate-200 bg-white space-y-1.5 text-xs">
                <div className="font-bold text-charcoal-900 flex items-center gap-1.5">
                  <FileCheck2 className="w-4 h-4 text-govgreen-700 flex-shrink-0" />
                  <span>{doc.document}</span>
                </div>
                <div className="text-[11px] text-slate-500">
                  Office: <span className="font-medium text-slate-700">{doc.issuingOffice}</span>
                </div>
                <div className="text-[11px] text-govgreen-900 bg-govgreen-50 p-2 rounded-lg border border-govgreen-100">
                  Note: {doc.criticalNotes}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Critical Filing Deadlines */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Critical Official Filing Milestones
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {analysisData.criticalDeadlines.map((dl, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
                <div className="flex items-center justify-between text-slate-500 text-[11px]">
                  <span className="font-semibold">{dl.milestone}</span>
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                </div>
                <div className="text-sm font-extrabold text-charcoal-900">
                  {dl.deadlineDate}
                </div>
                <div className="text-[11px] text-rose-700 pt-1 border-t border-slate-200/80">
                  {dl.consequence}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Flagged Ambiguities */}
        <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 space-y-2">
          <div className="flex items-center gap-2 font-bold text-amber-950">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <span>Flagged Ambiguities &amp; Potential Blockers</span>
          </div>
          <ul className="list-disc pl-5 space-y-1 text-slate-700">
            {analysisData.flaggedAmbiguities.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
};
