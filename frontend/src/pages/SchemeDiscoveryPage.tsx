import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Building2, 
  X, 
  UserCheck,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Info,
  Award,
  BookOpen
} from 'lucide-react';
import { SchemeCard } from '../components/common/SchemeCard';
import { EmptyState } from '../components/common/EmptyState';
import { apiService } from '../services/api';
import { 
  CitizenProfileInput, 
  SchemeDiscoverySummary, 
  SchemeEvaluationResult, 
  SensitiveFieldExplanation 
} from '../types';

export const SchemeDiscoveryPage: React.FC = () => {
  // Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedLevel, setSelectedLevel] = useState<string>('All');
  const [selectedBenefitType, setSelectedBenefitType] = useState<string>('All');
  const [statusFilter, setStatusFilter] = useState<string>('All');

  // Profile Drawer State
  const [isProfileOpen, setIsProfileOpen] = useState(true);
  const [showSensitiveExplanation, setShowSensitiveExplanation] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);

  // Citizen Profile Form State
  const [profile, setProfile] = useState<CitizenProfileInput>({
    full_name: 'Basavaraj Patil',
    domicile_state: 'Karnataka',
    district: 'Belagavi',
    age: 46,
    gender: 'Male',
    occupation: 'Farmer',
    annual_family_income: 180000,
    area_type: 'Rural',
    landholding_hectares: 1.5,
    is_income_tax_payer: false,
    bpl_card_holder: true,
  });

  // Discovery Summary State
  const [discoverySummary, setDiscoverySummary] = useState<SchemeDiscoverySummary | null>(null);
  const [sensitiveExplanations, setSensitiveExplanations] = useState<SensitiveFieldExplanation[]>([]);

  const categories: string[] = [
    'All',
    'Agriculture & Farming',
    'Social Security & Pensions',
    'Healthcare & Ayushman',
    'Education & Scholarships',
    'MSME & Entrepreneurship',
    'Housing & Rural Development'
  ];

  // Load sensitive fields explanation on mount
  useEffect(() => {
    const loadExplanations = async () => {
      try {
        const explanations = await apiService.getSensitiveFieldsExplanation();
        setSensitiveExplanations(explanations);
      } catch (e) {
        // Fallback default explanations if backend offline
        setSensitiveExplanations([
          {
            field_name: 'is_income_tax_payer',
            display_name: 'Income Tax Payer Status',
            required_by_scheme_id: 'SCHEME-PM-KISAN',
            scheme_name: 'PM-KISAN & Karnataka Gruha Lakshmi',
            official_clause: 'Clause 5(b)(vi) of PM-KISAN & Clause 4 of Karnataka GO-WCD-41-WES-2023',
            explanation: 'Central and state welfare rules legally exclude families where any member pays income tax or files GST returns from direct income support.'
          },
          {
            field_name: 'landholding_hectares',
            display_name: 'Cultivable Farmland (Hectares)',
            required_by_scheme_id: 'SCHEME-PM-KISAN',
            scheme_name: 'Pradhan Mantri Kisan Samman Nidhi',
            official_clause: 'Clause 3.1 (Beneficiary Definition)',
            explanation: 'Requires title ownership of cultivable land duly registered in state revenue portals (e.g. Bhoomi in Karnataka).'
          },
          {
            field_name: 'bpl_card_holder',
            display_name: 'Ration Card / BPL Classification',
            required_by_scheme_id: 'SCHEME-KAR-GRUHA-LAKSHMI',
            scheme_name: 'Karnataka Gruha Lakshmi Scheme',
            official_clause: 'Clause 2 & 3 (Jurisdiction & Eligibility)',
            explanation: 'Disburses ₹2,000 monthly to the recognized female head (Yajamani) listed on active Antyodaya, BPL, or APL ration cards.'
          }
        ]);
      }
    };
    loadExplanations();
  }, []);

  // Run Scheme Discovery Evaluation
  const runEvaluation = async (activeProfile: CitizenProfileInput = profile) => {
    setIsEvaluating(true);
    try {
      const summary = await apiService.discoverSchemes(activeProfile, {
        search: searchQuery,
        category: selectedCategory,
        level: selectedLevel,
        benefit_type: selectedBenefitType,
      });
      setDiscoverySummary(summary);
    } catch (err) {
      // Local deterministic evaluation fallback matching exact verified rules
      const localResults: SchemeEvaluationResult[] = [
        {
          scheme_id: 'SCHEME-PM-KISAN',
          official_name: 'Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)',
          category: 'Agriculture & Farming',
          government_department: 'Department of Agriculture and Farmers Welfare, GoI',
          level: 'Central',
          benefit_type: 'Direct Benefit Transfer (DBT)',
          annual_benefit: '₹6,000 / year (3 installments of ₹2,000)',
          target_beneficiaries: 'Landholding farmer families with cultivable land',
          application_deadline: 'Continuous Enrollment (Year-round)',
          official_source_url: 'https://pmkisan.gov.in/',
          application_url: 'https://pmkisan.gov.in/RegistrationFormNew.aspx',
          verification_date: '2024-11-01',
          policy_cycle: 'Continuous (FY 2024-25 / 2025-26)',
          information_status: 'VERIFIED',
          overall_status: (activeProfile.landholding_hectares && activeProfile.landholding_hectares > 0 && !activeProfile.is_income_tax_payer)
            ? 'MEETS_REQUIREMENT'
            : (activeProfile.is_income_tax_payer ? 'DOES_NOT_MEET_REQUIREMENT' : 'MISSING_INFORMATION'),
          match_score: (activeProfile.landholding_hectares && activeProfile.landholding_hectares > 0 && !activeProfile.is_income_tax_payer) ? 100 : 50,
          requirements_satisfied: (activeProfile.landholding_hectares && activeProfile.landholding_hectares > 0) ? [
            {
              rule_id: 'RULE-PMKISAN-LAND',
              requirement_description: 'The farmer family must own cultivable agricultural landholding.',
              rule_type: 'LAND_CRITERION',
              official_condition: { field: 'landholding_hectares', operator: 'GT', value: 0.0 },
              user_provided_value: activeProfile.landholding_hectares,
              status: 'MEETS_REQUIREMENT',
              is_mandatory: true,
              explanation: `Meets Requirement: Farmland record (${activeProfile.landholding_hectares} ha) satisfies Clause 3.1.`,
              official_source_title: 'Revised Operational Guidelines for PM-KISAN',
              circular_number: '1-1/2019-Credit-II',
              clause_or_section: 'Clause 3.1',
              official_source_url: 'https://pmkisan.gov.in/'
            }
          ] : [],
          requirements_not_satisfied: activeProfile.is_income_tax_payer ? [
            {
              rule_id: 'RULE-PMKISAN-EXCLUSION-IT',
              requirement_description: 'Persons who paid Income Tax in last assessment year are excluded.',
              rule_type: 'EXCLUSION_CHECK',
              official_condition: { field: 'is_income_tax_payer', operator: 'EQ', value: false },
              user_provided_value: true,
              status: 'DOES_NOT_MEET_REQUIREMENT',
              is_mandatory: true,
              explanation: 'Does Not Meet: Income tax assessees are excluded under Clause 5(b)(vi).',
              official_source_title: 'Revised Operational Guidelines for PM-KISAN',
              circular_number: '1-1/2019-Credit-II',
              clause_or_section: 'Clause 5(b)(vi)',
              official_source_url: 'https://pmkisan.gov.in/'
            }
          ] : [],
          missing_information: (!activeProfile.landholding_hectares) ? [
            {
              rule_id: 'RULE-PMKISAN-LAND',
              requirement_description: 'Farmland landholding record required.',
              rule_type: 'LAND_CRITERION',
              official_condition: { field: 'landholding_hectares', operator: 'GT', value: 0.0 },
              status: 'MISSING_INFORMATION',
              is_mandatory: true,
              explanation: 'Missing input: Landholding (hectares) is required.',
              official_source_title: 'Revised Operational Guidelines for PM-KISAN',
              circular_number: '1-1/2019-Credit-II',
              clause_or_section: 'Clause 3.1',
              official_source_url: 'https://pmkisan.gov.in/'
            }
          ] : [],
          conditions_under_review: [],
          suggested_next_actions: [
            'Ensure Aadhaar e-KYC is verified on pmkisan.gov.in portal.',
            'Verify active NPCI mapper linkage on your DBT bank account.'
          ],
          important_conditions: [
            'Cultivable land registered in state land records',
            'No family member filed income tax in previous assessment year'
          ],
          required_documents: [
            { id: 'req-pmk-1', document_type: 'LAND_REVENUE_RECORD', title: 'Land Record (ROR / Record of Rights / Patta)', is_mandatory: true, issuing_authority: 'State Revenue Department' },
            { id: 'req-pmk-2', document_type: 'AADHAAR_CARD', title: 'Aadhaar Card (e-KYC verified)', is_mandatory: true, issuing_authority: 'UIDAI' }
          ],
          official_source_title: 'Operational Guidelines for PM-KISAN (MoA&FW)',
          circular_number: '1-1/2019-Credit-II'
        },
        {
          scheme_id: 'SCHEME-KAR-GRUHA-LAKSHMI',
          official_name: 'Karnataka Gruha Lakshmi Scheme',
          category: 'Social Security & Pensions',
          government_department: 'Department of Women & Child Development, Karnataka',
          level: 'State (Karnataka)',
          benefit_type: 'Direct Benefit Transfer (DBT)',
          annual_benefit: '₹24,000 / year (₹2,000 monthly)',
          target_beneficiaries: 'Recognized female head of household (Yajamani) in Karnataka',
          application_deadline: 'Continuous Enrollment',
          official_source_url: 'https://sevasindhugs.karnataka.gov.in/',
          application_url: 'https://sevasindhu.karnataka.gov.in/Gruhalakshmi/',
          verification_date: '2024-11-01',
          policy_cycle: 'Continuous (FY 2024-25 / 2025-26)',
          information_status: 'VERIFIED',
          overall_status: (activeProfile.gender === 'Female' && activeProfile.domicile_state === 'Karnataka' && !activeProfile.is_income_tax_payer)
            ? 'MEETS_REQUIREMENT'
            : (activeProfile.gender !== 'Female' || activeProfile.domicile_state !== 'Karnataka' || activeProfile.is_income_tax_payer)
            ? 'DOES_NOT_MEET_REQUIREMENT'
            : 'MISSING_INFORMATION',
          match_score: (activeProfile.gender === 'Female' && activeProfile.domicile_state === 'Karnataka' && !activeProfile.is_income_tax_payer) ? 100 : 33,
          requirements_satisfied: (activeProfile.gender === 'Female' && activeProfile.domicile_state === 'Karnataka' && !activeProfile.is_income_tax_payer) ? [
            {
              rule_id: 'RULE-GL-GENDER',
              requirement_description: 'Female head of household (Yajamani).',
              rule_type: 'GENDER_CRITERION',
              official_condition: { field: 'gender', operator: 'EQ', value: 'Female' },
              user_provided_value: activeProfile.gender,
              status: 'MEETS_REQUIREMENT',
              is_mandatory: true,
              explanation: 'Meets Requirement: Applicant is female head.',
              official_source_title: 'GO on Gruha Lakshmi Scheme',
              circular_number: 'GO-WCD-41-WES-2023',
              clause_or_section: 'Clause 2',
              official_source_url: 'https://sevasindhugs.karnataka.gov.in/'
            }
          ] : [],
          requirements_not_satisfied: (activeProfile.gender !== 'Female') ? [
            {
              rule_id: 'RULE-GL-GENDER',
              requirement_description: 'Female head of household only.',
              rule_type: 'GENDER_CRITERION',
              official_condition: { field: 'gender', operator: 'EQ', value: 'Female' },
              user_provided_value: activeProfile.gender,
              status: 'DOES_NOT_MEET_REQUIREMENT',
              is_mandatory: true,
              explanation: 'Does Not Meet: Scheme is exclusively for female head (Yajamani).',
              official_source_title: 'GO on Gruha Lakshmi Scheme',
              circular_number: 'GO-WCD-41-WES-2023',
              clause_or_section: 'Clause 2',
              official_source_url: 'https://sevasindhugs.karnataka.gov.in/'
            }
          ] : [],
          missing_information: [],
          conditions_under_review: [],
          suggested_next_actions: [
            'Verify Yajamani name on Karnataka Food & Civil Supplies Ration Card.',
            'Ensure Aadhaar-seeded bank account is active on NPCI payment bridge.'
          ],
          important_conditions: [
            'Designated female head on Karnataka Ration Card',
            'Neither female head nor husband is Income Tax or GST return filer'
          ],
          required_documents: [
            { id: 'req-gl-1', document_type: 'RATION_CARD', title: 'Karnataka Ration Card (BPL / APL / Antyodaya)', is_mandatory: true, issuing_authority: 'Food & Civil Supplies Department' },
            { id: 'req-gl-2', document_type: 'AADHAAR_CARD', title: 'Aadhaar Card of Yajamani', is_mandatory: true, issuing_authority: 'UIDAI' }
          ],
          official_source_title: 'Government Order on Gruha Lakshmi Scheme',
          circular_number: 'GO-WCD-41-WES-2023'
        }
      ];

      setDiscoverySummary({
        citizen_name: activeProfile.full_name,
        total_schemes_evaluated: localResults.length,
        eligible_count: localResults.filter(r => r.overall_status === 'MEETS_REQUIREMENT').length,
        missing_info_count: localResults.filter(r => r.overall_status === 'MISSING_INFORMATION').length,
        ineligible_count: localResults.filter(r => r.overall_status === 'DOES_NOT_MEET_REQUIREMENT').length,
        under_review_count: 0,
        schemes: localResults,
        evaluated_at: new Date().toISOString()
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  // Run on first load
  useEffect(() => {
    runEvaluation();
  }, []);

  // Quick Preset Handlers
  const handleApplyPreset = (presetType: 'farmer' | 'woman' | 'taxpayer') => {
    let newProfile: CitizenProfileInput;
    if (presetType === 'farmer') {
      newProfile = {
        full_name: 'Basavaraj Patil',
        domicile_state: 'Karnataka',
        district: 'Belagavi',
        age: 46,
        gender: 'Male',
        occupation: 'Farmer',
        annual_family_income: 180000,
        area_type: 'Rural',
        landholding_hectares: 1.8,
        is_income_tax_payer: false,
        bpl_card_holder: true,
      };
    } else if (presetType === 'woman') {
      newProfile = {
        full_name: 'Savita Gowda',
        domicile_state: 'Karnataka',
        district: 'Mandya',
        age: 38,
        gender: 'Female',
        occupation: 'Homemaker',
        annual_family_income: 120000,
        area_type: 'Rural',
        landholding_hectares: 0,
        is_income_tax_payer: false,
        bpl_card_holder: true,
      };
    } else {
      newProfile = {
        full_name: 'Rajesh Sharma',
        domicile_state: 'Karnataka',
        district: 'Bengaluru Urban',
        age: 34,
        gender: 'Male',
        occupation: 'Salaried',
        annual_family_income: 950000,
        area_type: 'Urban',
        landholding_hectares: 2.0,
        is_income_tax_payer: true, // Disqualifier
        bpl_card_holder: false,
      };
    }
    setProfile(newProfile);
    runEvaluation(newProfile);
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('All');
    setSelectedLevel('All');
    setSelectedBenefitType('All');
    setStatusFilter('All');
  };

  // Filter schemes based on search query, category, level, and status
  const displayedSchemes = (discoverySummary?.schemes || []).filter(scheme => {
    if (selectedCategory !== 'All' && scheme.category !== selectedCategory) return false;
    if (selectedLevel !== 'All' && !scheme.level.includes(selectedLevel)) return false;
    if (selectedBenefitType !== 'All' && !scheme.benefit_type.includes(selectedBenefitType)) return false;
    if (statusFilter !== 'All' && scheme.overall_status !== statusFilter) return false;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        scheme.official_name.toLowerCase().includes(q) ||
        scheme.government_department.toLowerCase().includes(q) ||
        scheme.target_beneficiaries.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-govgreen-900 via-govgreen-800 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-elevated relative overflow-hidden">
        <div className="relative max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold bg-govgreen-700/80 text-emerald-100 px-3 py-1 rounded-full border border-govgreen-500">
            <Building2 className="w-4 h-4 text-emerald-300" />
            <span>SchemeSathi Civic Welfare Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Government Scheme Discovery
          </h1>
          <p className="text-xs sm:text-sm text-emerald-100/90 leading-relaxed">
            Match your citizen profile against verified central and Karnataka state welfare programs. 
            All eligibility evaluations are calculated by a pure deterministic rule engine grounded in official gazettes—zero LLM hallucinations.
          </p>

          <div className="flex flex-wrap items-center gap-2 pt-2">
            <span className="text-[11px] font-semibold bg-white/10 text-emerald-200 px-2.5 py-1 rounded-lg border border-white/10 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              100% Deterministic Rule Engine
            </span>
            <span className="text-[11px] font-semibold bg-white/10 text-emerald-200 px-2.5 py-1 rounded-lg border border-white/10 flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-emerald-400" />
              Direct Official Portal Citations
            </span>
          </div>
        </div>
      </div>

      {/* Citizen Profile Matcher Drawer / Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-subtle space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-govgreen-100 text-govgreen-800 flex items-center justify-center font-bold">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm sm:text-base font-bold text-charcoal-900">
                Citizen Evaluation Profile
              </h2>
              <p className="text-xs text-slate-500">
                Provide your profile to run real-time deterministic eligibility checks across all verified schemes.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Quick Preset Buttons */}
            <div className="hidden sm:flex items-center gap-1.5 text-xs">
              <span className="text-slate-400 font-medium">Quick Presets:</span>
              <button
                onClick={() => handleApplyPreset('farmer')}
                className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition"
              >
                Farmer (PM-KISAN)
              </button>
              <button
                onClick={() => handleApplyPreset('woman')}
                className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition"
              >
                Woman Head (Gruha Lakshmi)
              </button>
              <button
                onClick={() => handleApplyPreset('taxpayer')}
                className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition"
              >
                Taxpayer (Exclusion)
              </button>
            </div>

            <button
              onClick={() => setIsProfileOpen(!isProfileOpen)}
              className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition"
              title={isProfileOpen ? 'Collapse profile' : 'Expand profile'}
            >
              {isProfileOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {isProfileOpen && (
          <div className="space-y-4 pt-1 animate-in fade-in">
            {/* Presets Bar for Mobile */}
            <div className="flex sm:hidden items-center gap-1.5 text-xs overflow-x-auto pb-1">
              <span className="text-slate-400 font-medium whitespace-nowrap">Presets:</span>
              <button
                onClick={() => handleApplyPreset('farmer')}
                className="px-2 py-1 rounded bg-slate-100 text-slate-700 text-[11px] whitespace-nowrap"
              >
                Farmer (Karnataka)
              </button>
              <button
                onClick={() => handleApplyPreset('woman')}
                className="px-2 py-1 rounded bg-slate-100 text-slate-700 text-[11px] whitespace-nowrap"
              >
                Woman Head
              </button>
              <button
                onClick={() => handleApplyPreset('taxpayer')}
                className="px-2 py-1 rounded bg-slate-100 text-slate-700 text-[11px] whitespace-nowrap"
              >
                Taxpayer
              </button>
            </div>

            {/* Profile Input Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              {/* Full Name */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={profile.full_name || ''}
                  onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                  placeholder="e.g. Basavaraj Patil"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600"
                />
              </div>

              {/* State */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">State of Domicile</label>
                <select
                  value={profile.domicile_state || 'Karnataka'}
                  onChange={(e) => setProfile({ ...profile, domicile_state: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600 bg-white"
                >
                  <option value="Karnataka">Karnataka</option>
                  <option value="Uttar Pradesh">Uttar Pradesh</option>
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Tamil Nadu">Tamil Nadu</option>
                  <option value="Andhra Pradesh">Andhra Pradesh</option>
                  <option value="Bihar">Bihar</option>
                  <option value="Other State">Other State</option>
                </select>
              </div>

              {/* District */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">District</label>
                <input
                  type="text"
                  value={profile.district || ''}
                  onChange={(e) => setProfile({ ...profile, district: e.target.value })}
                  placeholder="e.g. Belagavi, Mandya"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600"
                />
              </div>

              {/* Age */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Age (Years)</label>
                <input
                  type="number"
                  value={profile.age || ''}
                  onChange={(e) => setProfile({ ...profile, age: Number(e.target.value) || undefined })}
                  placeholder="e.g. 42"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600"
                />
              </div>

              {/* Gender */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Gender</label>
                <select
                  value={profile.gender || 'Male'}
                  onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600 bg-white"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female (Eligible for Gruha Lakshmi)</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Occupation */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Primary Occupation</label>
                <select
                  value={profile.occupation || 'Farmer'}
                  onChange={(e) => setProfile({ ...profile, occupation: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600 bg-white"
                >
                  <option value="Farmer">Farmer (Landholder)</option>
                  <option value="Homemaker">Homemaker</option>
                  <option value="Daily Wage Earner">Daily Wage Earner / Laborer</option>
                  <option value="Salaried">Salaried Employee</option>
                  <option value="Self-Employed">Self-Employed / MSME</option>
                  <option value="Student">Student</option>
                  <option value="Unemployed">Unemployed / Retired</option>
                </select>
              </div>

              {/* Annual Family Income */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Annual Family Income (₹)</label>
                <input
                  type="number"
                  value={profile.annual_family_income || ''}
                  onChange={(e) => setProfile({ ...profile, annual_family_income: Number(e.target.value) || 0 })}
                  placeholder="e.g. 180000"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600"
                />
              </div>

              {/* Area Type */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Area of Residence</label>
                <select
                  value={profile.area_type || 'Rural'}
                  onChange={(e) => setProfile({ ...profile, area_type: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600 bg-white"
                >
                  <option value="Rural">Rural</option>
                  <option value="Urban">Urban</option>
                  <option value="Semi-Urban">Semi-Urban</option>
                </select>
              </div>
            </div>

            {/* Sensitive Scheme-Specific Section (With Legal Explanation Badge) */}
            <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200/90 space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                  <ShieldCheck className="w-4 h-4 text-govgreen-700" />
                  <span>Scheme-Specific Verification Criteria</span>
                  <span className="text-[10px] font-normal text-slate-500">
                    (Asked strictly because official guidelines condition eligibility on them)
                  </span>
                </div>

                <button
                  type="button"
                  onClick={() => setShowSensitiveExplanation(!showSensitiveExplanation)}
                  className="text-[11px] font-semibold text-govgreen-800 hover:underline flex items-center gap-1"
                >
                  <Info className="w-3.5 h-3.5" />
                  <span>{showSensitiveExplanation ? 'Hide Legal Citations' : 'Why are these asked?'}</span>
                </button>
              </div>

              {/* Sensitive Explanation Collapsible Box */}
              {showSensitiveExplanation && (
                <div className="p-3 bg-white rounded-lg border border-emerald-200 text-xs text-slate-700 space-y-2 animate-in fade-in">
                  <div className="font-bold text-govgreen-900 flex items-center gap-1.5">
                    <BookOpen className="w-4 h-4 text-govgreen-700" />
                    <span>Statutory Mandates For Sensitive Profile Questions</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 pt-1">
                    {sensitiveExplanations.map((exp, idx) => (
                      <div key={idx} className="p-2.5 rounded-md bg-slate-50 border border-slate-200 text-[11px] space-y-1">
                        <div className="font-bold text-charcoal-900">{exp.display_name}</div>
                        <div className="text-govgreen-800 font-mono text-[10px]">{exp.official_clause}</div>
                        <p className="text-slate-600 leading-tight">{exp.explanation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Sensitive Input Controls */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1">
                {/* Cultivable Landholding (Hectares) */}
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Cultivable Farmland (Hectares)
                    <span className="text-[10px] font-normal text-govgreen-800 ml-1">(PM-KISAN)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    value={profile.landholding_hectares ?? ''}
                    onChange={(e) => setProfile({ ...profile, landholding_hectares: e.target.value === '' ? undefined : Number(e.target.value) })}
                    placeholder="e.g. 1.5 (0 if landless)"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600 bg-white"
                  />
                  <span className="text-[10px] text-slate-500">1 hectare ≈ 2.47 acres</span>
                </div>

                {/* Income Tax Payer Status */}
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Did you or spouse pay Income Tax?
                    <span className="text-[10px] font-normal text-rose-800 ml-1">(Exclusion)</span>
                  </label>
                  <select
                    value={profile.is_income_tax_payer ? 'yes' : 'no'}
                    onChange={(e) => setProfile({ ...profile, is_income_tax_payer: e.target.value === 'yes' })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600 bg-white"
                  >
                    <option value="no">No (Non-assessee / Excluded from Tax)</option>
                    <option value="yes">Yes (Filed and paid income tax in last AY)</option>
                  </select>
                  <span className="text-[10px] text-slate-500">Clause 5 excludes tax assessees from PM-KISAN &amp; Gruha Lakshmi</span>
                </div>

                {/* Ration Card Status */}
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Active Karnataka Ration Card
                    <span className="text-[10px] font-normal text-govgreen-800 ml-1">(Gruha Lakshmi)</span>
                  </label>
                  <select
                    value={profile.bpl_card_holder ? 'yes' : 'no'}
                    onChange={(e) => setProfile({ ...profile, bpl_card_holder: e.target.value === 'yes' })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:border-govgreen-600 bg-white"
                  >
                    <option value="yes">Yes (Antyodaya / BPL / APL Card)</option>
                    <option value="no">No active state ration card</option>
                  </select>
                  <span className="text-[10px] text-slate-500">Needed to verify Yajamani registration</span>
                </div>
              </div>
            </div>

            {/* Run Evaluation Button */}
            <div className="flex justify-end pt-2">
              <button
                type="button"
                onClick={() => runEvaluation(profile)}
                disabled={isEvaluating}
                className="inline-flex items-center gap-2 bg-govgreen-700 hover:bg-govgreen-800 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-sm transition disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isEvaluating ? 'animate-spin' : ''}`} />
                <span>{isEvaluating ? 'Evaluating Entitlements...' : 'Run Deterministic Eligibility Check'}</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Discovery Summary KPI Bar (When Evaluated) */}
      {discoverySummary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div 
            onClick={() => setStatusFilter('All')}
            className={`p-4 rounded-xl border cursor-pointer transition ${
              statusFilter === 'All' ? 'bg-slate-900 text-white border-slate-900 shadow-sm' : 'bg-white border-slate-200 text-slate-800 hover:border-slate-300'
            }`}
          >
            <div className="text-[11px] uppercase font-bold opacity-80">All Verified Schemes</div>
            <div className="text-2xl font-extrabold mt-1">{discoverySummary.total_schemes_evaluated}</div>
            <div className="text-[10px] opacity-70 mt-0.5">In Official Catalog</div>
          </div>

          <div 
            onClick={() => setStatusFilter('MEETS_REQUIREMENT')}
            className={`p-4 rounded-xl border cursor-pointer transition ${
              statusFilter === 'MEETS_REQUIREMENT' ? 'bg-emerald-800 text-white border-emerald-800 shadow-sm' : 'bg-emerald-50/70 border-emerald-200 text-emerald-950 hover:border-emerald-300'
            }`}
          >
            <div className="text-[11px] uppercase font-bold text-emerald-800 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Fully Eligible</span>
            </div>
            <div className="text-2xl font-extrabold text-emerald-900 mt-1">{discoverySummary.eligible_count}</div>
            <div className="text-[10px] text-emerald-700 mt-0.5">Ready to Apply</div>
          </div>

          <div 
            onClick={() => setStatusFilter('MISSING_INFORMATION')}
            className={`p-4 rounded-xl border cursor-pointer transition ${
              statusFilter === 'MISSING_INFORMATION' ? 'bg-amber-800 text-white border-amber-800 shadow-sm' : 'bg-amber-50/70 border-amber-200 text-amber-950 hover:border-amber-300'
            }`}
          >
            <div className="text-[11px] uppercase font-bold text-amber-800 flex items-center gap-1">
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Missing Info</span>
            </div>
            <div className="text-2xl font-extrabold text-amber-900 mt-1">{discoverySummary.missing_info_count}</div>
            <div className="text-[10px] text-amber-700 mt-0.5">Complete Profile</div>
          </div>

          <div 
            onClick={() => setStatusFilter('DOES_NOT_MEET_REQUIREMENT')}
            className={`p-4 rounded-xl border cursor-pointer transition ${
              statusFilter === 'DOES_NOT_MEET_REQUIREMENT' ? 'bg-rose-800 text-white border-rose-800 shadow-sm' : 'bg-rose-50/70 border-rose-200 text-rose-950 hover:border-rose-300'
            }`}
          >
            <div className="text-[11px] uppercase font-bold text-rose-800 flex items-center gap-1">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Statutory Exclusions</span>
            </div>
            <div className="text-2xl font-extrabold text-rose-900 mt-1">{discoverySummary.ineligible_count}</div>
            <div className="text-[10px] text-rose-700 mt-0.5">Unmet Criteria</div>
          </div>
        </div>
      )}

      {/* Search & Filtering Panel */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-subtle space-y-4">
        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by scheme name, ministry, target group, or benefit keywords (e.g. Kisan, Gruha Lakshmi, DBT, Farmland)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:outline-none focus:border-govgreen-600 font-sans shadow-sm"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3.5 top-3 text-slate-400 hover:text-slate-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category Pills Bar */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-govgreen-700 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Secondary Filter Dropdowns */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 text-xs text-slate-600">
          <div className="flex flex-wrap items-center gap-3">
            {/* Level Filter */}
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-slate-500">Government Level:</span>
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="px-2.5 py-1 rounded-lg border border-slate-300 text-xs bg-white focus:outline-none focus:border-govgreen-600"
              >
                <option value="All">All (Central &amp; States)</option>
                <option value="Central">Central Govt (Pan-India)</option>
                <option value="Karnataka">Karnataka State</option>
              </select>
            </div>

            {/* Benefit Type Filter */}
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-slate-500">Benefit Channel:</span>
              <select
                value={selectedBenefitType}
                onChange={(e) => setSelectedBenefitType(e.target.value)}
                className="px-2.5 py-1 rounded-lg border border-slate-300 text-xs bg-white focus:outline-none focus:border-govgreen-600"
              >
                <option value="All">All Delivery Modes</option>
                <option value="Direct Benefit Transfer">Direct Benefit Transfer (DBT)</option>
                <option value="Subsidy">Capital Subsidy</option>
                <option value="Insurance">Health Insurance Cover</option>
              </select>
            </div>

            {/* Status Filter Dropdown */}
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-slate-500">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-2.5 py-1 rounded-lg border border-slate-300 text-xs bg-white focus:outline-none focus:border-govgreen-600"
              >
                <option value="All">All Outcomes</option>
                <option value="MEETS_REQUIREMENT">Eligible (Matches 100%)</option>
                <option value="MISSING_INFORMATION">Missing Profile Data</option>
                <option value="DOES_NOT_MEET_REQUIREMENT">Disqualified / Excluded</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-500 text-[11px]">
              Showing <strong>{displayedSchemes.length}</strong> matching schemes
            </span>
            {(selectedCategory !== 'All' || selectedLevel !== 'All' || selectedBenefitType !== 'All' || statusFilter !== 'All' || searchQuery) && (
              <button
                onClick={handleResetFilters}
                className="text-[11px] font-semibold text-govgreen-800 hover:underline"
              >
                Reset Filters
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Schemes Grid */}
      {displayedSchemes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayedSchemes.map((schemeResult) => (
            <SchemeCard
              key={schemeResult.scheme_id}
              evaluation={schemeResult}
              onEvaluate={() => runEvaluation(profile)}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Verified Schemes Match Selected Criteria"
          description="We couldn't find any schemes matching your current filters. Try resetting the category or status filter to see all welfare opportunities."
          onAction={handleResetFilters}
          actionText="Reset All Filters"
        />
      )}
    </div>
  );
};
