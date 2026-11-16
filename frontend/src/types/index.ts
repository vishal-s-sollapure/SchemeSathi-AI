export type LanguageCode = 'en' | 'kn' | 'hi' | 'te' | 'ta' | 'mr';

export interface LanguageOption {
  code: LanguageCode;
  label: string;
  nativeLabel: string;
  flag?: string;
}

export type SchemeCategory = 
  | 'All'
  | 'Agriculture & Farming'
  | 'Education & Scholarships'
  | 'Social Security & Pensions'
  | 'Healthcare & Ayushman'
  | 'Women & Child Development'
  | 'MSME & Entrepreneurship'
  | 'Housing & Rural Development';

export type EligibilityStatus = 
  | 'eligible'
  | 'conditionally_eligible'
  | 'missing_documents'
  | 'ineligible'
  | 'pending_evaluation';

export interface Scheme {
  id: string;
  title: string;
  ministry: string;
  level: 'Central' | 'State (Karnataka)' | 'State (Maharashtra)' | 'State (Uttar Pradesh)' | 'State (All)';
  category: SchemeCategory;
  annualBenefit: string;
  benefitType: 'Direct Benefit Transfer (DBT)' | 'Subsidy' | 'Fee Reimbursement' | 'Health Insurance Cover' | 'Credit Support';
  description: string;
  targetBeneficiaries: string;
  eligibilityCriteria: string[];
  requiredDocuments: string[];
  officialPortal: string;
  applicationDeadline: string;
  isExpiringSoon?: boolean;
  isDemo: true;
  demoNote: string;
}

export interface Scholarship {
  id: string;
  title: string;
  provider: string;
  level: 'National / Central' | 'State Gov' | 'Institutional / Merit';
  targetAudience: string;
  courseLevel: 'Pre-Matric' | 'Post-Matric / Higher Secondary' | 'Undergraduate' | 'Postgraduate & PhD' | 'Technical / Professional';
  maxAnnualIncome: number; // in INR
  minPercentage: number;
  eligibleCategories: string[]; // ['SC', 'ST', 'OBC', 'General', 'EWS', 'Minority']
  amountPerYear: string;
  applicationDeadline: string;
  matchScore?: number; // 0 - 100%
  requiredDocuments: {
    name: string;
    description: string;
    status: 'ready' | 'missing' | 'expiring';
  }[];
  isDemo: true;
  demoNote: string;
}

export interface StudentProfile {
  fullName: string;
  domicileState: string;
  category: string;
  annualFamilyIncome: number;
  currentCourse: string;
  yearOfStudy: string;
  marksPercentage: number;
  gender: string;
  disabilityStatus: boolean;
  hostellerStatus: 'Day Scholar' | 'Hosteller';
}

export interface Citation {
  id: string;
  title: string;
  documentName: string;
  issuingAuthority: string;
  circularNumber: string;
  notificationDate: string;
  clauseNumber: string;
  excerpt: string;
  officialSourceUrl: string;
  verificationBadge: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  language: LanguageCode;
  citations?: Citation[];
  suggestedFollowUps?: string[];
  isDemo?: boolean;
}

export interface DocumentAnalysisResult {
  fileName: string;
  fileSize: string;
  pages: number;
  extractedDate: string;
  documentType: string;
  issuingDepartment: string;
  executiveSummary: string;
  keyEligibilityRules: {
    criterion: string;
    officialClause: string;
    requirementType: 'Mandatory' | 'Relaxation Available' | 'Conditional';
  }[];
  mandatoryDocumentList: {
    document: string;
    issuingOffice: string;
    criticalNotes: string;
  }[];
  criticalDeadlines: {
    milestone: string;
    deadlineDate: string;
    consequence: string;
  }[];
  flaggedAmbiguities: string[];
  isDemo: true;
}

// ============================================================================
// Phase 6: Deterministic Scheme Discovery & Evaluation Types
// ============================================================================

export type DeterministicEligibilityStatus =
  | 'MEETS_REQUIREMENT'
  | 'DOES_NOT_MEET_REQUIREMENT'
  | 'MISSING_INFORMATION'
  | 'NEEDS_REVIEW';

export interface RuleAssessmentItem {
  rule_id: string;
  requirement_description: string;
  rule_type: string;
  official_condition: Record<string, any>;
  user_provided_value?: any;
  status: DeterministicEligibilityStatus;
  is_mandatory: boolean;
  explanation: string;
  official_source_title: string;
  circular_number: string;
  clause_or_section: string;
  page_number?: string;
  official_source_url: string;
}

export interface SchemeEvaluationResult {
  scheme_id: string;
  official_name: string;
  category: string;
  government_department: string;
  level: string;
  benefit_type: string;
  annual_benefit: string;
  target_beneficiaries: string;
  application_deadline?: string;
  official_source_url: string;
  application_url?: string;
  verification_date: string;
  policy_cycle?: string;
  information_status: string;
  overall_status: DeterministicEligibilityStatus;
  match_score: number;
  requirements_satisfied: RuleAssessmentItem[];
  requirements_not_satisfied: RuleAssessmentItem[];
  missing_information: RuleAssessmentItem[];
  conditions_under_review: RuleAssessmentItem[];
  suggested_next_actions: string[];
  important_conditions: string[];
  required_documents: {
    id: string;
    document_type: string;
    title: string;
    description?: string;
    issuing_authority?: string;
    is_mandatory: boolean;
  }[];
  official_source_title?: string;
  circular_number?: string;
}

export interface SchemeDiscoverySummary {
  citizen_name?: string;
  total_schemes_evaluated: number;
  eligible_count: number;
  missing_info_count: number;
  ineligible_count: number;
  under_review_count: number;
  schemes: SchemeEvaluationResult[];
  evaluated_at: string;
}

export interface CitizenProfileInput {
  full_name?: string;
  domicile_state?: string;
  district?: string;
  age?: number;
  occupation?: string;
  annual_family_income?: number;
  area_type?: string;
  gender?: string;
  social_category?: string;
  landholding_hectares?: number;
  is_income_tax_payer?: boolean;
  bpl_card_holder?: boolean;
  is_differently_abled?: boolean;
  extra_attributes?: Record<string, any>;
}

export interface SensitiveFieldExplanation {
  field_name: string;
  display_name: string;
  required_by_scheme_id: string;
  scheme_name: string;
  official_clause: string;
  explanation: string;
}

// ============================================================================
// Phase 8: Document Intelligence & Dynamic Checklist Types
// ============================================================================

export type DynamicChecklistItemStatus =
  | 'NOT_STARTED'
  | 'REQUIRED'
  | 'UPLOADED'
  | 'CONFIRMED'
  | 'NEEDS_REVIEW'
  | 'NOT_APPLICABLE';

export interface DynamicChecklistItem {
  requirement_id?: string;
  name: string;
  document_type: string;
  description?: string;
  status: DynamicChecklistItemStatus;
  is_mandatory: boolean;
  issuing_office?: string;
  document_id?: string;
  critical_notes?: string;
  confirmed_evidence?: Record<string, any>;
  official_clause?: string;
  verification_advice?: string;
}

export interface DynamicApplicationChecklist {
  id: string;
  student_profile_id?: string;
  citizen_profile_id?: string;
  scholarship_id?: string;
  scheme_id?: string;
  readiness_score: number;
  overall_status: string;
  checklist_items: DynamicChecklistItem[];
  unresolved_mandatory_count: number;
  is_ready_for_submission: boolean;
  disclaimer: string;
  evaluated_at: string;
}

export interface ExtractedEvidenceItem {
  id: string;
  document_id: string;
  evidence_type: string;
  field_key?: string;
  extracted_value: string;
  confirmed_value?: string;
  is_confirmed: boolean;
  confidence_score: number;
  page_number?: number;
  raw_text_snippet?: string;
  verification_disclaimer?: string;
}

export interface DocumentIntelligenceResponse {
  document: {
    id: string;
    original_filename: string;
    file_size_bytes: number;
    mime_type: string;
    page_count: number;
    ocr_applied: boolean;
    document_type: string;
    storage_path?: string;
    processing_status: string;
  };
  extracted_candidates: ExtractedEvidenceItem[];
  page_count: number;
  ocr_applied: boolean;
  detected_document_type: string;
  disclaimer: string;
}


export interface EvidenceConfirmationItem {
  evidence_id: string;
  confirmed_value: string;
  is_confirmed?: boolean;
}

export interface EvidenceConfirmationRequest {
  items: EvidenceConfirmationItem[];
}

export interface StudentEvaluationInput {
  full_name?: string;
  age?: number;
  domicile_state?: string;
  district?: string;
  course_level?: string;
  current_course?: string;
  institution_name?: string;
  institution_type?: string;
  year_of_study?: string;
  marks_percentage?: number;
  annual_family_income?: number;
  category?: string;
  gender?: string;
  other_scholarship_recipient?: boolean;
  eligible_daughters_count?: number;
  extra_attributes?: Record<string, any>;
}

export interface ScholarshipEvaluationResult {
  scholarship_id: string;
  official_name: string;
  government_department: string;
  benefit_amount_annual: string;
  official_source_url: string;
  application_url?: string;
  application_deadline?: string;
  overall_status: DeterministicEligibilityStatus;
  match_score: number;
  requirements_satisfied: RuleAssessmentItem[];
  requirements_not_satisfied: RuleAssessmentItem[];
  missing_information: RuleAssessmentItem[];
  conditions_under_review: RuleAssessmentItem[];
  suggested_next_actions: string[];
  required_documents: {
    id?: string;
    document_type: string;
    title: string;
    description?: string;
    issuing_authority?: string;
    is_mandatory: boolean;
  }[];
}

export interface ScholarReadyEvaluationSummary {
  student_name?: string;
  total_scholarships_evaluated: number;
  eligible_count: number;
  missing_info_count: number;
  ineligible_count: number;
  under_review_count: number;
  scholarships: ScholarshipEvaluationResult[];
  evaluated_at: string;
}

export interface ValidatedCitation {
  source_title: string;
  circular_number?: string;
  clause_or_section: string;
  page_number?: string;
  official_source_url: string;
  verification_status: string;
  matched_chunk_id: string;
  excerpt: string;
}

export interface RAGQueryRequest {
  query: string;
  session_id?: string;
  language?: string;
  scheme_filter?: string;
}

export interface RAGResponse {
  query: string;
  answer: string;
  language: string;
  citations: ValidatedCitation[];
  confidence_score: number;
  is_grounded: boolean;
  sufficient_evidence: boolean;
  suggested_follow_ups: string[];
  official_disclaimer: string;
}

export interface PolicyDeadlineItem {
  label: string;
  timeframe_or_date: string;
  statutory_authority: string;
  is_critical: boolean;
}

export interface PolicyDocumentRequiredItem {
  name: string;
  issuing_authority: string;
  format_or_requirement: string;
}

export interface PolicyDocumentSummary {
  id: string;
  title: string;
  issuing_department: string;
  notification_number?: string;
  publication_date?: string;
  official_gazette_url: string;
  applicable_cycle: string;
  category: string;
  executive_summary: string;
  clause_count: number;
  verification_status: string;
}

export interface PolicySimplificationResult {
  document_id: string;
  document_title: string;
  issuing_department: string;
  notification_number?: string;
  publication_date?: string;
  official_gazette_url: string;
  applicable_cycle: string;
  language: string;
  five_line_summary: string[];
  important_conditions: string[];
  dates_and_deadlines: PolicyDeadlineItem[];
  required_documents: PolicyDocumentRequiredItem[];
  application_steps: string[];
  important_warnings: string[];
  flagged_ambiguities?: string[];
  legal_disclaimer: string;
}

export interface PolicyExplanationRequest {
  document_id?: string;
  clause_or_section?: string;
  question: string;
  language?: string;
}

export interface PolicySupportingPassage {
  source_title: string;
  clause_or_section: string;
  page_number?: string;
  official_text: string;
  official_source_url: string;
  issuing_department: string;
}

export interface PolicyExplanationResponse {
  question: string;
  document_id?: string;
  document_title?: string;
  language: string;
  simplified_explanation: string;
  clause_referenced?: string;
  verbatim_official_clause?: string;
  supporting_passages: PolicySupportingPassage[];
  citations: ValidatedCitation[];
  sufficient_evidence: boolean;
  important_dates: string[];
  restrictions_and_responsibilities: string[];
  suggested_follow_ups?: string[];
  legal_disclaimer: string;
}


