import axios from 'axios';
import { 
  CitizenProfileInput, 
  SchemeDiscoverySummary, 
  SchemeEvaluationResult, 
  SensitiveFieldExplanation 
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
};


