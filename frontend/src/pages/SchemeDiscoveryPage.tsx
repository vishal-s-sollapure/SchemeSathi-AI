import React, { useState } from 'react';
import { 
  Search, 
  Building2, 
  X
} from 'lucide-react';
import { SchemeCard } from '../components/common/SchemeCard';
import { EligibilityCard } from '../components/common/EligibilityCard';
import { EmptyState } from '../components/common/EmptyState';
import { MOCK_SCHEMES } from '../data/mockData';
import { Scheme } from '../types';

export const SchemeDiscoveryPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedLevel, setSelectedLevel] = useState<string>('All');
  const [selectedBenefitType, setSelectedBenefitType] = useState<string>('All');
  const [evaluatedScheme, setEvaluatedScheme] = useState<Scheme | null>(null);

  const categories: string[] = [
    'All',
    'Agriculture & Farming',
    'Healthcare & Ayushman',
    'Education & Scholarships',
    'MSME & Entrepreneurship',
    'Housing & Rural Development'
  ];

  const filteredSchemes = MOCK_SCHEMES.filter(scheme => {
    if (selectedCategory !== 'All' && scheme.category !== selectedCategory) return false;
    if (selectedLevel !== 'All' && !scheme.level.includes(selectedLevel)) return false;
    if (selectedBenefitType !== 'All' && !scheme.benefitType.includes(selectedBenefitType)) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        scheme.title.toLowerCase().includes(q) ||
        scheme.description.toLowerCase().includes(q) ||
        scheme.ministry.toLowerCase().includes(q) ||
        scheme.targetBeneficiaries.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('All');
    setSelectedLevel('All');
    setSelectedBenefitType('All');
  };

  const handleEvaluate = (scheme: Scheme) => {
    setEvaluatedScheme(scheme);
  };

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-govgreen-900 via-govgreen-800 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-elevated relative overflow-hidden">
        <div className="relative max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold bg-govgreen-700/80 text-emerald-100 px-3 py-1 rounded-full border border-govgreen-500">
            <Building2 className="w-4 h-4 text-emerald-300" />
            <span>Civic Welfare Scheme Catalog</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Government Scheme Discovery
          </h1>
          <p className="text-xs sm:text-sm text-emerald-100/90 leading-relaxed">
            Discover central and state government entitlements across farming, healthcare, MSME credit, and social welfare with exact eligibility requirements and direct official portal citations.
          </p>
        </div>
      </div>

      {/* Evaluated Scheme Banner (if user clicked Check Eligibility) */}
      {evaluatedScheme && (
        <div className="relative">
          <div className="flex justify-end mb-2">
            <button
              onClick={() => setEvaluatedScheme(null)}
              className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1"
            >
              <X className="w-3.5 h-3.5" />
              <span>Dismiss Evaluation</span>
            </button>
          </div>
          <EligibilityCard
            overallStatus="eligible"
            overallScore={96}
            schemeTitle={evaluatedScheme.title}
            issuingBody={evaluatedScheme.ministry}
            criteriaResults={[
              {
                ruleName: 'Landholding & Domicile Criterion',
                userValue: 'Verified Farmland (2.5 Acres, Belagavi, Karnataka)',
                requiredValue: 'Cultivable Farmland in Family Record',
                status: 'passed',
                explanation: 'Your land record is active in the state revenue portal and satisfies the primary landholding condition.',
                officialCitationReference: 'Operational Guidelines Section 4.1'
              },
              {
                ruleName: 'Income Tax Exclusion Check',
                userValue: 'Annual Family Income ₹1.80L (Non-assessee)',
                requiredValue: 'No Income Tax Assessee in Family',
                status: 'passed',
                explanation: 'Family annual income is below the tax threshold. You satisfy exclusion Clause 5.',
                officialCitationReference: 'Clause 5 (Exclusion Criteria)'
              },
              {
                ruleName: 'Aadhaar Payment Bridge (APB) Linkage',
                userValue: 'Aadhaar Seeded with State Bank of India Account',
                requiredValue: 'Mandatory NPCI Active Mapping',
                status: 'passed',
                explanation: 'Direct Benefit Transfer (DBT) bank route is active.',
                officialCitationReference: 'DBT Gazette Mandate'
              }
            ]}
            recommendationText="Your profile meets all primary legal criteria for this scheme. You can proceed directly to the official portal to complete your registration."
          />
        </div>
      )}

      {/* Search & Filtering Panel */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-subtle space-y-4">
        {/* Top Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by scheme name, ministry, target beneficiary, or keywords (e.g. Kisan, Solar, Women, Credit)..."
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
              <span className="font-semibold text-slate-500">Benefit Type:</span>
              <select
                value={selectedBenefitType}
                onChange={(e) => setSelectedBenefitType(e.target.value)}
                className="px-2.5 py-1 rounded-lg border border-slate-300 text-xs bg-white focus:outline-none focus:border-govgreen-600"
              >
                <option value="All">All Modes</option>
                <option value="Direct Benefit Transfer">Direct Benefit Transfer (DBT)</option>
                <option value="Subsidy">Capital Subsidy</option>
                <option value="Health Insurance">Health Cover</option>
                <option value="Credit">Credit / Loan Support</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-500 text-[11px]">
              Showing <strong>{filteredSchemes.length}</strong> verified entries
            </span>
            {(selectedCategory !== 'All' || selectedLevel !== 'All' || selectedBenefitType !== 'All' || searchQuery) && (
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
      {filteredSchemes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSchemes.map((scheme) => (
            <SchemeCard
              key={scheme.id}
              scheme={scheme}
              onEvaluate={handleEvaluate}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Schemes Match Your Filter Criteria"
          description="We couldn't find any schemes matching the selected category and benefit type. Try resetting filters or searching for general terms like 'PM' or 'Farmer'."
          onAction={handleResetFilters}
          actionText="Reset All Filters"
        />
      )}
    </div>
  );
};
