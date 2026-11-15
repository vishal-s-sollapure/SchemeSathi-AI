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
