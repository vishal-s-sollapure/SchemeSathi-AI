import axios from 'axios';
import { 
  CitizenProfileInput, 
  DocumentIntelligenceResponse,
  DynamicApplicationChecklist,
  EvidenceConfirmationItem,
  ExtractedEvidenceItem,
  PolicyDocumentSummary,
  PolicyExplanationRequest,
  PolicyExplanationResponse,
  PolicySimplificationResult,
  RAGQueryRequest,
  RAGResponse,
  ScholarReadyEvaluationSummary,
  ScholarshipEvaluationResult,
  SchemeDiscoverySummary, 
  SchemeEvaluationResult, 
  SensitiveFieldExplanation,
  StudentEvaluationInput
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface HealthResponse {
  status: string;
  application: string;
  version?: string;
  environment?: string;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const apiService = {
  /**
   * Fetches health status from backend
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/health');
    return response.data;
  },

  /**
   * Fetches versioned health status
   */
  async checkV1Health(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/v1/health');
    return response.data;
  },

  /**
   * Evaluates citizen profile across all verified government schemes (SchemeSathi Discovery)
   */
  async discoverSchemes(
    profile: CitizenProfileInput,
    filters?: {
      search?: string;
      category?: string;
      level?: string;
      benefit_type?: string;
    }
  ): Promise<SchemeDiscoverySummary> {
    const params: Record<string, string> = {};
    if (filters?.search) params.search = filters.search;
    if (filters?.category && filters.category !== 'All') params.category = filters.category;
    if (filters?.level && filters.level !== 'All') params.level = filters.level;
    if (filters?.benefit_type && filters.benefit_type !== 'All') params.benefit_type = filters.benefit_type;

    const response = await apiClient.post<SchemeDiscoverySummary>(
      '/api/v1/eligibility/discover-schemes',
      profile,
      { params }
    );
    return response.data;
  },

  /**
   * Evaluates a single scheme against a citizen profile
   */
  async evaluateSingleScheme(
    schemeId: string,
    profile: CitizenProfileInput
  ): Promise<SchemeEvaluationResult> {
    const response = await apiClient.post<SchemeEvaluationResult>(
      `/api/v1/eligibility/evaluate-scheme/${schemeId}`,
      profile
    );
    return response.data;
  },

  /**
   * Retrieves explanations for why sensitive questions are legally asked
   */
  async getSensitiveFieldsExplanation(): Promise<SensitiveFieldExplanation[]> {
    const response = await apiClient.get<SensitiveFieldExplanation[]>(
      '/api/v1/eligibility/sensitive-fields'
    );
    return response.data;
  },

  /**
   * Lists verified schemes from database registry
   */
  async listVerifiedSchemes(filters?: {
    search?: string;
    category?: string;
    level?: string;
    benefit_type?: string;
  }): Promise<any[]> {
    const params: Record<string, string> = {};
    if (filters?.search) params.search = filters.search;
    if (filters?.category && filters.category !== 'All') params.category = filters.category;
    if (filters?.level && filters.level !== 'All') params.level = filters.level;
    if (filters?.benefit_type && filters.benefit_type !== 'All') params.benefit_type = filters.benefit_type;

    const response = await apiClient.get<any[]>('/api/v1/schemes', { params });
    return response.data;
  },

  /**
   * Phase 7: RAG & Grounded Question Answering with Official-Source Citations
   */
  async queryRAG(request: RAGQueryRequest): Promise<RAGResponse> {
    const response = await apiClient.post<RAGResponse>(
      '/api/v1/chat/query',
      request
    );
    return response.data;
  },

  /**
   * Uploads and parses official PDF circular page-by-page into verified RAG knowledge base
   */
  async ingestPdf(file: File, documentTitle?: string, schemeId?: string): Promise<{ status: string; message: string; chunks_indexed: number }> {
    const formData = new FormData();
    formData.append('file', file);
    if (documentTitle) formData.append('document_title', documentTitle);
    if (schemeId) formData.append('scheme_id', schemeId);

    const response = await apiClient.post<{ status: string; message: string; chunks_indexed: number }>(
      '/api/v1/chat/ingest-pdf',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // ============================================================================
  // ScholarReady: Deterministic Scholarship Evaluation
  // ============================================================================

  /**
   * Evaluates a student profile across all active verified scholarships
   */
  async evaluateScholarships(profile: StudentEvaluationInput): Promise<ScholarReadyEvaluationSummary> {
    const response = await apiClient.post<ScholarReadyEvaluationSummary>(
      '/api/v1/eligibility/evaluate-scholarships',
      profile
    );
    return response.data;
  },

  /**
   * Evaluates a student profile against a single verified scholarship
   */
  async evaluateSingleScholarship(scholarshipId: string, profile: StudentEvaluationInput): Promise<ScholarshipEvaluationResult> {
    const response = await apiClient.post<ScholarshipEvaluationResult>(
      `/api/v1/eligibility/evaluate-scholarship/${scholarshipId}`,
      profile
    );
    return response.data;
  },

  /**
   * Lists verified scholarships from database catalog
   */
  async listScholarships(filters?: {
    search?: string;
    level?: string;
    category?: string;
    course_level?: string;
    max_income?: number;
  }): Promise<any[]> {
    const params: Record<string, any> = {};
    if (filters?.search) params.search = filters.search;
    if (filters?.level && filters.level !== 'All') params.level = filters.level;
    if (filters?.category && filters.category !== 'All') params.category = filters.category;
    if (filters?.course_level && filters.course_level !== 'All') params.course_level = filters.course_level;
    if (filters?.max_income) params.max_income = filters.max_income;

    const response = await apiClient.get<any[]>('/api/v1/scholarships', { params });
    return response.data;
  },

  // ============================================================================
  // Phase 8: Document Intelligence & Dynamic Checklist Engine
  // ============================================================================

  /**
   * Uploads and parses candidate PDF document via PyMuPDF extractor.
   * Extracts candidate entities (Name, Income, Marks, Course, Institution, Dates)
   * with confidence scores, source page numbers, and non-authenticity disclaimer.
   */
  async uploadDocument(
    file: File,
    options?: {
      documentTypeHint?: string;
      studentProfileId?: string;
      citizenProfileId?: string;
    }
  ): Promise<DocumentIntelligenceResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.documentTypeHint) formData.append('document_type_hint', options.documentTypeHint);
    if (options?.studentProfileId) formData.append('student_profile_id', options.studentProfileId);
    if (options?.citizenProfileId) formData.append('citizen_profile_id', options.citizenProfileId);

    const response = await apiClient.post<DocumentIntelligenceResponse>(
      '/api/v1/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Confirms or corrects extracted values for an uploaded document.
   * Stores confirmed values distinctly from unconfirmed extraction.
   * If checklistId is provided, dynamically syncs profile attributes and recalculates eligibility.
   */
  async confirmEvidence(
    docId: string,
    items: EvidenceConfirmationItem[],
    checklistId?: string
  ): Promise<ExtractedEvidenceItem[]> {
    const params: Record<string, string> = {};
    if (checklistId) params.checklist_id = checklistId;

    const response = await apiClient.post<ExtractedEvidenceItem[]>(
      `/api/v1/documents/${docId}/confirm-evidence`,
      { items },
      { params }
    );
    return response.data;
  },

  /**
   * Deletes an uploaded document, cleans physical disk storage, and rolls back linked checklist items.
   */
  async deleteDocument(docId: string): Promise<{ status: string; message: string }> {
    const response = await apiClient.delete<{ status: string; message: string }>(
      `/api/v1/documents/${docId}`
    );
    return response.data;
  },

  /**
   * Generates a personalized dynamic application checklist based on verified statutory requirements.
   */
  async generateChecklist(params: {
    studentProfileId?: string;
    citizenProfileId?: string;
    scholarshipId?: string;
    schemeId?: string;
  }): Promise<DynamicApplicationChecklist> {
    const queryParams: Record<string, string> = {};
    if (params.studentProfileId) queryParams.student_profile_id = params.studentProfileId;
    if (params.citizenProfileId) queryParams.citizen_profile_id = params.citizenProfileId;
    if (params.scholarshipId) queryParams.scholarship_id = params.scholarshipId;
    if (params.schemeId) queryParams.scheme_id = params.schemeId;

    const response = await apiClient.post<DynamicApplicationChecklist>(
      '/api/v1/checklists/generate',
      null,
      { params: queryParams }
    );
    return response.data;
  },

  /**
   * Retrieves an application checklist by ID
   */
  async getChecklist(checklistId: string): Promise<DynamicApplicationChecklist> {
    const response = await apiClient.get<DynamicApplicationChecklist>(
      `/api/v1/checklists/${checklistId}`
    );
    return response.data;
  },

  // ============================================================================
  // Phase 10: Policy and Rights Explainer Engine
  // ============================================================================

  /**
   * Discovers and retrieves verified government policies, gazettes, and guidelines
   */
  async listPolicyDocuments(search?: string): Promise<PolicyDocumentSummary[]> {
    const params: Record<string, string> = {};
    if (search) params.search = search;
    const response = await apiClient.get<PolicyDocumentSummary[]>('/api/v1/policy/documents', { params });
    return response.data;
  },

  /**
   * Retrieves detailed clauses and structured metadata for a policy circular
   */
  async getPolicyDocumentDetail(documentId: string): Promise<any> {
    const response = await apiClient.get(`/api/v1/policy/documents/${documentId}`);
    return response.data;
  },

  /**
   * Generates the 6-part civic policy simplification workflow
   */
  async getPolicySimplification(
    documentId: string,
    language: string = 'en'
  ): Promise<PolicySimplificationResult> {
    const response = await apiClient.get<PolicySimplificationResult>(
      `/api/v1/policy/simplify/${documentId}`,
      { params: { language } }
    );
    return response.data;
  },

  /**
   * Asks specific clause-level or standard questions grounded in verified government documents
   */
  async explainPolicy(request: PolicyExplanationRequest): Promise<PolicyExplanationResponse> {
    const response = await apiClient.post<PolicyExplanationResponse>(
      '/api/v1/policy/explain',
      request
    );
    return response.data;
  },

  /**
   * Uploads and simplifies a custom government PDF circular via PyMuPDF
   */
  async simplifyUploadedPdf(
    file: File,
    documentTitle: string,
    issuingDepartment: string = 'Government Department',
    officialGazetteUrl: string = 'https://india.gov.in',
    language: string = 'en'
  ): Promise<PolicySimplificationResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_title', documentTitle);
    formData.append('issuing_department', issuingDepartment);
    formData.append('official_gazette_url', officialGazetteUrl);
    formData.append('language', language);

    const response = await apiClient.post<PolicySimplificationResult>(
      '/api/v1/policy/simplify-pdf',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};


