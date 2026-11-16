import React, { useState } from 'react';
import { 
  FileSearch, 
  CheckCircle2, 
  Clock, 
  Sparkles, 
  Calendar, 
  AlertTriangle, 
  RefreshCw, 
  Layers, 
  FileCheck2,
  Trash2,
  Check,
  Edit2,
  Info,
  ShieldAlert,
  Percent,
  Award,
  IndianRupee,
  BookOpen,
  User,
  Building
} from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { DocumentUpload } from '../components/common/DocumentUpload';
import { apiService } from '../services/api';
import { 
  DocumentIntelligenceResponse, 
  EvidenceConfirmationItem, 
  ExtractedEvidenceItem 
} from '../types';

export const DocumentIntelligencePage: React.FC = () => {
  const [docResponse, setDocResponse] = useState<DocumentIntelligenceResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processingError, setProcessingError] = useState<string | null>(null);
  const [selectedDocHint, setSelectedDocHint] = useState<string>('Auto Detect');
  
  // Field editing state
  const [editableValues, setEditableValues] = useState<Record<string, string>>({});
  const [confirmedEvidences, setConfirmedEvidences] = useState<Record<string, boolean>>({});
  const [isConfirming, setIsConfirming] = useState<boolean>(false);
  const [confirmationSuccessMsg, setConfirmationSuccessMsg] = useState<string | null>(null);

  // Fallback demo state if user selects sample preset
  const handleFileUploaded = async (fileInfo: { name: string; size: string; isPreset?: boolean; rawFile?: File }) => {
    setIsProcessing(true);
    setProcessingError(null);
    setConfirmationSuccessMsg(null);

    if (fileInfo.rawFile) {
      try {
        const hint = selectedDocHint !== 'Auto Detect' ? selectedDocHint : undefined;
        const resp = await apiService.uploadDocument(fileInfo.rawFile, { documentTypeHint: hint });
        setDocResponse(resp);
        
        // Initialize editable values
        const initialValues: Record<string, string> = {};
        const initialConfirmed: Record<string, boolean> = {};
        resp.extracted_candidates.forEach(c => {
          initialValues[c.id] = c.confirmed_value || c.extracted_value;
          initialConfirmed[c.id] = c.is_confirmed;
        });
        setEditableValues(initialValues);
        setConfirmedEvidences(initialConfirmed);
      } catch (err: any) {
        console.error('Failed to parse document:', err);
        setProcessingError(err?.response?.data?.detail || 'Document upload & processing failed. Please verify the PDF format.');
      } finally {
        setIsProcessing(false);
      }
    } else {
      // Preset / Simulated PDF parsing fallback
      setTimeout(() => {
        const mockResp: DocumentIntelligenceResponse = {
          document: {
            id: 'doc-demo-uuid-401',
            original_filename: fileInfo.name,
            file_size_bytes: 1420000,
            mime_type: 'application/pdf',
            page_count: 2,
            ocr_applied: false,
            document_type: selectedDocHint !== 'Auto Detect' ? selectedDocHint : 'Income and Caste Certificate',
            processing_status: 'COMPLETED'
          },
          detected_document_type: 'Income & Domicile Certificate (Tahsildar Form-F)',
          page_count: 2,
          ocr_applied: false,
          disclaimer: 'Extracted text is for applicant convenience only. The system does NOT certify government authenticity or validity.',
          extracted_candidates: [
            {
              id: 'ev-1',
              document_id: 'doc-demo-uuid-401',
              evidence_type: 'STUDENT_NAME',
              field_key: 'student_name',
              extracted_value: 'Ananya Sharma',
              confirmed_value: undefined,
              is_confirmed: false,
              confidence_score: 0.94,
              page_number: 1,
              raw_text_snippet: 'This is to certify that Kum. Ananya Sharma daughter of Sri Ramesh Sharma...',
              verification_disclaimer: 'Applicant must verify against Government UIDAI record.'
            },
            {
              id: 'ev-2',
              document_id: 'doc-demo-uuid-401',
              evidence_type: 'ANNUAL_INCOME',
              field_key: 'annual_income',
              extracted_value: '180000',
              confirmed_value: undefined,
              is_confirmed: false,
              confidence_score: 0.96,
              page_number: 1,
              raw_text_snippet: 'Total Annual Family Income from all sources is Rs. 1,80,000/- (One Lakh Eighty Thousand Only)',
              verification_disclaimer: 'Extracted income does not replace statutory revenue department verification.'
            },
            {
              id: 'ev-3',
              document_id: 'doc-demo-uuid-401',
              evidence_type: 'COURSE_NAME',
              field_key: 'course',
              extracted_value: 'B.E. Computer Science and Engineering',
              confirmed_value: undefined,
              is_confirmed: false,
              confidence_score: 0.91,
              page_number: 1,
              raw_text_snippet: 'Currently admitted to B.E. Computer Science and Engineering for academic cycle 2024-25',
              verification_disclaimer: 'Subject to AICTE / VTU enrollment roll record.'
            },
            {
              id: 'ev-4',
              document_id: 'doc-demo-uuid-401',
              evidence_type: 'MARKS_PERCENTAGE',
              field_key: 'marks_percentage',
              extracted_value: '84.5',
              confirmed_value: undefined,
              is_confirmed: false,
              confidence_score: 0.89,
              page_number: 2,
              raw_text_snippet: 'Qualifying Examination Aggregate Score: 84.50% (Distinction)',
              verification_disclaimer: 'Self-reported extraction requires original marks card presentation.'
            },
            {
              id: 'ev-5',
              document_id: 'doc-demo-uuid-401',
              evidence_type: 'ISSUE_DATE',
              field_key: 'issue_date',
              extracted_value: '2024-06-15',
              confirmed_value: undefined,
              is_confirmed: false,
              confidence_score: 0.92,
              page_number: 1,
              raw_text_snippet: 'Date of Issue: 15/06/2024 under digital signature of Tahsildar, Bengaluru South',
              verification_disclaimer: 'Validity expires after 3 financial years.'
            }
          ]
        };

        setDocResponse(mockResp);
        const initialValues: Record<string, string> = {};
        const initialConfirmed: Record<string, boolean> = {};
        mockResp.extracted_candidates.forEach(c => {
          initialValues[c.id] = c.extracted_value;
          initialConfirmed[c.id] = false;
        });
        setEditableValues(initialValues);
        setConfirmedEvidences(initialConfirmed);
        setIsProcessing(false);
      }, 900);
    }
  };

  const handleConfirmEvidence = async () => {
    if (!docResponse) return;
    setIsConfirming(true);
    setConfirmationSuccessMsg(null);

    const items: EvidenceConfirmationItem[] = docResponse.extracted_candidates.map(c => ({
      evidence_id: c.id,
      confirmed_value: editableValues[c.id] || c.extracted_value,
      is_confirmed: true
    }));

    try {
      if (docResponse.document.id.startsWith('doc-demo')) {
        // Local simulation
        const updatedConfirmed: Record<string, boolean> = {};
        docResponse.extracted_candidates.forEach(c => {
          updatedConfirmed[c.id] = true;
        });
        setConfirmedEvidences(updatedConfirmed);
        setConfirmationSuccessMsg('Evidence confirmed! Confirmed values have been saved separately from unconfirmed raw extractions.');
      } else {
        const updatedItems = await apiService.confirmEvidence(docResponse.document.id, items);
        const updatedConfirmed: Record<string, boolean> = {};
        updatedItems.forEach(item => {
          updatedConfirmed[item.id] = item.is_confirmed;
        });
        setConfirmedEvidences(updatedConfirmed);
        setConfirmationSuccessMsg('Evidence successfully confirmed and recorded into verified profile repository.');
      }
    } catch (err: any) {
      console.error('Confirmation failed:', err);
      setProcessingError(err?.response?.data?.detail || 'Failed to record confirmed evidence.');
    } finally {
      setIsConfirming(false);
    }
  };

  const handleDeleteDocument = async () => {
    if (!docResponse) return;
    if (!window.confirm('Are you sure you want to delete this document? This will remove physical files and rollback linked checklist states.')) {
      return;
    }

    try {
      if (!docResponse.document.id.startsWith('doc-demo')) {
        await apiService.deleteDocument(docResponse.document.id);
      }
      setDocResponse(null);
      setEditableValues({});
      setConfirmedEvidences({});
      setConfirmationSuccessMsg('Document securely deleted and all evidence unlinked.');
    } catch (err: any) {
      console.error('Delete document failed:', err);
      setProcessingError(err?.response?.data?.detail || 'Failed to delete document.');
    }
  };

  const getFieldIcon = (evidenceType: string) => {
    switch (evidenceType) {
      case 'STUDENT_NAME':
      case 'CITIZEN_NAME':
        return <User className="w-4 h-4 text-sky-600" />;
      case 'ANNUAL_INCOME':
        return <IndianRupee className="w-4 h-4 text-emerald-600" />;
      case 'MARKS_PERCENTAGE':
        return <Percent className="w-4 h-4 text-amber-600" />;
      case 'COURSE_NAME':
        return <BookOpen className="w-4 h-4 text-indigo-600" />;
      case 'INSTITUTION_NAME':
        return <Building className="w-4 h-4 text-purple-600" />;
      case 'ISSUE_DATE':
        return <Calendar className="w-4 h-4 text-rose-600" />;
      default:
        return <FileSearch className="w-4 h-4 text-slate-600" />;
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-govgreen-950 via-charcoal-900 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-elevated relative overflow-hidden">
        <div className="relative max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold bg-govgreen-800 text-emerald-200 px-3 py-1 rounded-full border border-govgreen-600">
            <FileSearch className="w-4 h-4 text-emerald-300" />
            <span>Document Intelligence &amp; Evidence Engine</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            PDF Document Intelligence &amp; Verification
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            High-precision PyMuPDF text &amp; layout extraction for Indian income certificates, marksheets, bonafide slips, and state gazettes.
            Extract candidate parameters, review with side-by-side evidence, and confirm profile attributes with strict non-authenticity guardrails.
          </p>
        </div>
      </div>

      {/* Mandatory Legal & Non-Authenticity Disclaimer Banner */}
      <div className="bg-amber-50/80 border-2 border-amber-300/80 rounded-2xl p-4 sm:p-5 flex items-start gap-3.5 text-amber-950 shadow-subtle">
        <ShieldAlert className="w-6 h-6 text-amber-700 flex-shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <div className="font-bold text-sm text-amber-900">
            Statutory Document Verification Disclaimer
          </div>
          <p className="text-slate-700 leading-relaxed">
            Document extraction is an automated convenience tool to accelerate application checklists. 
            <strong> The system does NOT certify government authenticity, validity, or tampering resistance of any uploaded certificate.</strong> 
            Uploading a document does <strong>not</strong> guarantee scheme or scholarship eligibility. Always verify certificates via official government portals (e-Pramaan, Nadakacheri, Digilocker).
          </p>
        </div>
      </div>

      {/* 1. PDF UPLOAD INTERFACE */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-govgreen-600" />
            <h2 className="text-base font-bold text-charcoal-900">
              Upload Official Document (PyMuPDF Engine)
            </h2>
          </div>
          
          {/* Document Type Hint Selector */}
          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold text-slate-600">Document Type:</label>
            <select
              value={selectedDocHint}
              onChange={(e) => setSelectedDocHint(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1.5 font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-govgreen-500"
            >
              <option value="Auto Detect">Auto Detect</option>
              <option value="Income Certificate">Income Certificate</option>
              <option value="Marksheet / Academic Transcript">Marksheet / Grade Card</option>
              <option value="Caste / Category Certificate">Caste / Category Certificate</option>
              <option value="Bonafide Certificate">College Bonafide Certificate</option>
              <option value="Bank Passbook / DBT Proof">Bank Passbook (DBT Active)</option>
              <option value="Official Scheme Circular">Government Scheme Circular</option>
            </select>
          </div>
        </div>

        <DocumentUpload
          title="Drop PDF Certificate or Marksheet here (Max 15MB)"
          subtitle="PyMuPDF extractor reads text streams, extracts candidate fields, and locates source pages"
          acceptedFormats=".pdf"
          onFileSelected={handleFileUploaded}
        />

        {isProcessing && (
          <div className="flex items-center justify-center gap-3 p-4 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-900 text-xs font-semibold">
            <RefreshCw className="w-4 h-4 animate-spin text-emerald-700" />
            <span>Extracting candidate text, layout structure, and metadata using PyMuPDF...</span>
          </div>
        )}

        {processingError && (
          <div className="flex items-center gap-2 p-3.5 bg-rose-50 rounded-xl border border-rose-200 text-rose-900 text-xs font-medium">
            <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            <span>{processingError}</span>
          </div>
        )}

        {confirmationSuccessMsg && (
          <div className="flex items-center gap-2 p-3.5 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-900 text-xs font-semibold">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{confirmationSuccessMsg}</span>
          </div>
        )}
      </section>

      {/* 2. EXTRACTED CANDIDATE EVIDENCE REVIEW */}
      {docResponse && (
        <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold text-govgreen-800 bg-govgreen-50 px-2.5 py-0.5 rounded border border-govgreen-200">
                  {docResponse.detected_document_type || 'Parsed Certificate'}
                </span>
                <span className="text-xs font-medium text-slate-500">
                  Pages: <strong>{docResponse.page_count}</strong> {docResponse.ocr_applied ? '(OCR Fallback Active)' : '(Digital Text Stream)'}
                </span>
              </div>
              <h2 className="text-lg font-bold text-charcoal-900">
                Extracted Candidate Evidence &amp; User Confirmation
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                File: <strong className="font-mono text-slate-700">{docResponse.document.original_filename}</strong> &bull; Size: {(docResponse.document.file_size_bytes / 1024).toFixed(1)} KB
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleConfirmEvidence}
                disabled={isConfirming}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-govgreen-700 hover:bg-govgreen-800 text-white text-xs font-bold shadow-subtle transition disabled:opacity-50"
              >
                {isConfirming ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Check className="w-3.5 h-3.5" />
                )}
                <span>Confirm &amp; Record Values</span>
              </button>

              <button
                onClick={handleDeleteDocument}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-semibold transition"
                title="Delete document and rollback linked states"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Delete File</span>
              </button>
            </div>
          </div>

          {/* Candidate Extractions List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Candidate Fields for Review ({docResponse.extracted_candidates.length} Detected)
              </h3>
              <span className="text-[11px] text-slate-500">
                Edit values directly if OCR or extraction contains discrepancies
              </span>
            </div>

            {docResponse.extracted_candidates.length === 0 ? (
              <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-300 text-xs text-slate-500">
                No specific candidate fields matched the extraction rules. The document is stored as supporting proof.
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3.5">
                {docResponse.extracted_candidates.map((cand) => {
                  const isConfirmed = confirmedEvidences[cand.id];
                  const currentVal = editableValues[cand.id] ?? cand.extracted_value;

                  return (
                    <div 
                      key={cand.id}
                      className={`p-4 rounded-xl border transition ${
                        isConfirmed 
                          ? 'bg-emerald-50/40 border-emerald-300' 
                          : 'bg-white border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                        {/* Field Header */}
                        <div className="space-y-1.5 flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="p-1.5 rounded-lg bg-slate-100 border border-slate-200">
                              {getFieldIcon(cand.evidence_type)}
                            </span>
                            <span className="font-bold text-sm text-charcoal-900">
                              {cand.evidence_type.replace(/_/g, ' ')}
                            </span>
                            
                            {/* Page Badge */}
                            {cand.page_number && (
                              <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
                                Page {cand.page_number}
                              </span>
                            )}

                            {/* Confidence Score */}
                            <span className="text-[10px] font-bold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-200">
                              {Math.round(cand.confidence_score * 100)}% Confidence
                            </span>

                            {/* Confirmation Status */}
                            {isConfirmed ? (
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-300">
                                <CheckCircle2 className="w-3 h-3 text-emerald-700" />
                                Confirmed &amp; Stored
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-[10px] font-medium text-amber-800 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                                <Clock className="w-3 h-3 text-amber-600" />
                                Awaiting Confirmation
                              </span>
                            )}
                          </div>

                          {/* Raw Snippet Context */}
                          {cand.raw_text_snippet && (
                            <div className="text-[11px] text-slate-600 font-mono bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                              <span className="text-slate-400 select-none">Source snippet: </span>
                              &ldquo;{cand.raw_text_snippet}&rdquo;
                            </div>
                          )}

                          {/* Field-level verification disclaimer */}
                          {cand.verification_disclaimer && (
                            <div className="text-[10px] text-slate-500 italic flex items-center gap-1">
                              <Info className="w-3 h-3 text-slate-400 flex-shrink-0" />
                              <span>{cand.verification_disclaimer}</span>
                            </div>
                          )}
                        </div>

                        {/* Editable Confirmed Value Box */}
                        <div className="sm:w-72 space-y-1.5 flex-shrink-0">
                          <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                            <Edit2 className="w-3 h-3 text-slate-400" />
                            <span>Candidate / Confirmed Value:</span>
                          </label>
                          <div className="flex items-center gap-1.5">
                            <input
                              type="text"
                              value={currentVal}
                              onChange={(e) => setEditableValues(prev => ({ ...prev, [cand.id]: e.target.value }))}
                              className={`w-full text-xs font-bold px-3 py-2 rounded-lg border focus:outline-none focus:ring-2 ${
                                isConfirmed 
                                  ? 'bg-emerald-50/70 border-emerald-300 text-emerald-950 focus:ring-emerald-500' 
                                  : 'bg-white border-slate-300 text-charcoal-900 focus:ring-govgreen-500'
                              }`}
                            />
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-slate-400">
                            <span>Raw: {cand.extracted_value}</span>
                            {currentVal !== cand.extracted_value && (
                              <span className="text-amber-600 font-semibold">(Edited by user)</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Action Bar */}
          <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="text-xs text-slate-500">
              Raw extraction is preserved for administrative audits; confirmed values are saved to your student profile.
            </div>

            <button
              onClick={handleConfirmEvidence}
              disabled={isConfirming}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-govgreen-700 hover:bg-govgreen-800 text-white text-xs font-bold shadow-subtle transition disabled:opacity-50 self-start sm:self-center"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Confirm All &amp; Update Checklist</span>
            </button>
          </div>
        </section>
      )}

      {/* 3. DOCUMENT PROCESSING PIPELINE REFERENCE */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
        <h3 className="text-sm font-bold text-charcoal-900 flex items-center gap-2">
          <Layers className="w-4 h-4 text-govgreen-700" />
          <span>PyMuPDF Document Intelligence Architecture</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { step: '01', title: 'File & Header Validation', desc: 'Validates %PDF- magic bytes, structure integrity, and enforces 15MB size ceiling.' },
            { step: '02', title: 'Stream & Layout Parsing', desc: 'Extracts unicode text streams per page and flags scanned pages for OCR fallback.' },
            { step: '03', title: 'Entity Regex & Extraction', desc: 'Extracts income, marks, student name, dates with confidence scoring and source page.' },
            { step: '04', title: 'Confirmed State Sync', desc: 'Separates raw from user-confirmed evidence and syncs with dynamic checklist items.' }
          ].map(stage => (
            <div key={stage.step} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
              <span className="text-[10px] font-bold text-govgreen-700">STAGE {stage.step}</span>
              <div className="font-bold text-charcoal-900">{stage.title}</div>
              <p className="text-[11px] text-slate-500 leading-snug">{stage.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
