import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  GraduationCap, 
  Search, 
  FileText, 
  Bot, 
  ArrowRight, 
  CheckCircle2, 
  Sparkles, 
  Lock, 
  BookOpen
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { StatusBadge } from '../components/common/StatusBadge';
import { MOCK_SCHEMES, MOCK_SCHOLARSHIPS, MOCK_CITATIONS } from '../data/mockData';
import { SchemeCard } from '../components/common/SchemeCard';
import { ScholarshipCard } from '../components/common/ScholarshipCard';
import { CitationCard } from '../components/common/CitationCard';

export const LandingPage: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="space-y-20 py-8 sm:py-12">
      {/* 1. HERO SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-white via-slate-50 to-emerald-50/40 border border-slate-200/90 p-8 sm:p-14 lg:p-16 shadow-elevated hero-grid-pattern">
          {/* Decorative Corner Glow */}
          <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 rounded-full bg-govgreen-200/30 blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-80 h-80 rounded-full bg-ashoka-200/20 blur-3xl pointer-events-none" />

          <div className="relative max-w-3xl mx-auto text-center space-y-6">
            {/* Top Badge */}
            <div className="inline-flex items-center gap-2 bg-govgreen-100/90 text-govgreen-900 border border-govgreen-300/80 px-3.5 py-1.5 rounded-full text-xs font-semibold shadow-subtle">
              <ShieldCheck className="w-4 h-4 text-govgreen-700" />
              <span>Public Civic Intelligence &amp; Student Welfare Platform</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-charcoal-900 tracking-tight leading-[1.15]">
              Understand Your Rights.{' '}
              <span className="text-govgreen-800 underline decoration-govgreen-400 decoration-wavy decoration-2">
                Discover Your Benefits.
              </span>{' '}
              Apply with Confidence.
            </h1>

            {/* Tagline / Subtitle */}
            <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
              SchemeSathi AI bridges Indian citizens and students to government welfare schemes and higher-education scholarships through <strong>deterministic eligibility calculation</strong>, source-grounded gazette citations, and multilingual intelligence.
            </p>

            {/* Dual CTAs */}
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3.5">
              <Link
                to="/schemes"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-govgreen-700 hover:bg-govgreen-800 text-white font-bold text-sm sm:text-base px-6 py-3.5 rounded-xl shadow-elevated transition hover:scale-[1.02] active:scale-[0.99]"
              >
                <Search className="w-4 h-4" />
                <span>Explore Government Schemes</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <Link
                to="/scholar-ready"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-ashoka-800 border border-slate-300 font-bold text-sm sm:text-base px-6 py-3.5 rounded-xl shadow-subtle transition hover:border-ashoka-400"
              >
                <GraduationCap className="w-5 h-5 text-ashoka-700" />
                <span>ScholarReady Student Check</span>
              </Link>
            </div>

            {/* Verified Trust Stats */}
            <div className="pt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-slate-200/80 text-left">
              <div>
                <div className="text-xl sm:text-2xl font-extrabold text-charcoal-900">100%</div>
                <div className="text-xs text-slate-500 font-medium mt-0.5">Gazette Grounded</div>
              </div>
              <div>
                <div className="text-xl sm:text-2xl font-extrabold text-govgreen-800">0%</div>
                <div className="text-xs text-slate-500 font-medium mt-0.5">Hallucination Guarantee</div>
              </div>
              <div>
                <div className="text-xl sm:text-2xl font-extrabold text-ashoka-800">6+</div>
                <div className="text-xs text-slate-500 font-medium mt-0.5">Indian Languages</div>
              </div>
              <div>
                <div className="text-xl sm:text-2xl font-extrabold text-charcoal-900">Deterministic</div>
                <div className="text-xs text-slate-500 font-medium mt-0.5">Rule Verification</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. PRODUCT INTRODUCTION & THE CIVIC PROBLEM */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-govgreen-800 bg-govgreen-50 px-3 py-1 rounded-full border border-govgreen-200">
              <Sparkles className="w-3.5 h-3.5 text-govgreen-700" />
              <span>Built for Every Indian Citizen</span>
            </div>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-charcoal-900 tracking-tight">
              Why Billions in Welfare &amp; Scholarships Go Unclaimed Every Year
            </h2>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
              India operates over 1,500 central and state welfare initiatives. Yet, millions of deserving students, smallholder farmers, and rural families miss out due to <strong>complex legal gazettes, ambiguous eligibility criteria, and missing document awareness</strong>.
            </p>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
              SchemeSathi AI replaces guesswork with a <strong>dual-engine civic architecture</strong>: deterministic rules evaluate eligibility without hallucinations, while multilingual AI simplifies bureaucratic circulars into clear citizen roadmaps.
            </p>

            <div className="pt-2 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-semibold text-charcoal-900">
              <div className="flex items-center gap-2 p-2.5 rounded-lg bg-white border border-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Deterministic Income &amp; Category Filters</span>
              </div>
              <div className="flex items-center gap-2 p-2.5 rounded-lg bg-white border border-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Evidence-Linked Clause Citations</span>
              </div>
              <div className="flex items-center gap-2 p-2.5 rounded-lg bg-white border border-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Dynamic Document Readiness Checklist</span>
              </div>
              <div className="flex items-center gap-2 p-2.5 rounded-lg bg-white border border-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Voice Q&amp;A in Regional Languages</span>
              </div>
            </div>
          </div>

          {/* Interactive Visual Preview Box */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-elevated p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-xs font-bold text-slate-800">
                  Real-time Grounded Citation Sample
                </span>
              </div>
              <StatusBadge status="demo" label="Demo Verification" />
            </div>

            <CitationCard citation={MOCK_CITATIONS[0]} />

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
              <ShieldCheck className="w-4 h-4 text-govgreen-700 flex-shrink-0 mt-0.5" />
              <span>
                Unlike standard generative chatbots, SchemeSathi AI highlights exact paragraph and clause numbers from published government orders before advising citizens.
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. HOW IT WORKS (STEP-BY-STEP WORKFLOW) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto space-y-3 mb-12">
          <span className="text-xs font-bold uppercase tracking-wider text-govgreen-800 bg-govgreen-50 px-3 py-1 rounded-full border border-govgreen-200">
            Civic Process
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900 tracking-tight">
            How SchemeSathi AI Guides Your Journey
          </h2>
          <p className="text-sm text-slate-600">
            From entering your basic civic details to completing your application readiness checklist in 4 deterministic steps.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Step 1 */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle hover:border-govgreen-400 transition flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-govgreen-100 text-govgreen-800 font-extrabold text-sm flex items-center justify-center">
                01
              </div>
              <h3 className="text-base font-bold text-charcoal-900">
                Profile &amp; Needs Input
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Provide your state of domicile, annual household income, student or citizen status, and caste category with full client-side privacy.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-semibold text-govgreen-800">
              No login required for preview
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle hover:border-govgreen-400 transition flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-ashoka-100 text-ashoka-800 font-extrabold text-sm flex items-center justify-center">
                02
              </div>
              <h3 className="text-base font-bold text-charcoal-900">
                Deterministic Rule Matching
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Our rule engine evaluates eligibility without LLM hallucination: testing income caps, age limits, marks percentages, and state quotas.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-semibold text-ashoka-800">
              4-status evaluation engine
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle hover:border-govgreen-400 transition flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 font-extrabold text-sm flex items-center justify-center">
                03
              </div>
              <h3 className="text-base font-bold text-charcoal-900">
                Document Readiness Score
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Review dynamic document readiness: mark certificates as ready, identify missing items (e.g. Caste QR certificate), and resolve bottlenecks.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-semibold text-emerald-800">
              Prevents portal rejections
            </div>
          </div>

          {/* Step 4 */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle hover:border-govgreen-400 transition flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-800 font-extrabold text-sm flex items-center justify-center">
                04
              </div>
              <h3 className="text-base font-bold text-charcoal-900">
                Apply With Confidence
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Get direct official portal links (NSP, SSP, myScheme), verified circular citations, and multilingual explanations in your mother tongue.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-semibold text-purple-800">
              Direct to government links
            </div>
          </div>
        </div>
      </section>

      {/* 4. SCHOLARREADY FEATURE SPOTLIGHT */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-ashoka-900 via-ashoka-800 to-slate-900 rounded-3xl p-8 sm:p-12 text-white shadow-premium">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-ashoka-200 bg-ashoka-700/60 px-3 py-1 rounded-full border border-ashoka-500">
                <GraduationCap className="w-4 h-4 text-emerald-300" />
                <span>Specialized Module for Students</span>
              </div>
              <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
                ScholarReady™: Every Student Deserves Their Rightful Scholarship
              </h2>
              <p className="text-sm sm:text-base text-ashoka-100/90 leading-relaxed">
                Navigating the National Scholarship Portal (NSP) and state portals like Karnataka SSP can be confusing. ScholarReady calculates your eligibility across merit, means, girls&apos; STEM education, and post-matric fee reimbursements, while generating an actionable document preparation checklist.
              </p>

              <div className="space-y-2 text-xs text-ashoka-100 pt-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Cross-matches Central Sector, AICTE Pragati, &amp; State Schemes</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>Aadhaar-NPCI bank seeding readiness check</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>College bonafide and income threshold verification</span>
                </div>
              </div>

              <div className="pt-4">
                <Link
                  to="/scholar-ready"
                  className="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-charcoal-900 font-extrabold text-xs sm:text-sm px-5 py-3 rounded-xl shadow-lg transition"
                >
                  <span>Launch ScholarReady Workspace</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>

            {/* Preview Card */}
            <div className="bg-white text-charcoal-900 rounded-2xl p-5 shadow-elevated">
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Featured Student Scholarship Preview
                </span>
                <StatusBadge status="high_match" label="98% Match" />
              </div>
              <ScholarshipCard scholarship={MOCK_SCHOLARSHIPS[0]} />
            </div>
          </div>
        </div>
      </section>

      {/* 5. GOVERNMENT SCHEME DISCOVERY SPOTLIGHT */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-govgreen-800 bg-govgreen-50 px-3 py-1 rounded-full border border-govgreen-200">
              Civic Welfare Discovery
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900 tracking-tight mt-2">
              Explore Central &amp; State Welfare Benefits
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-xl">
              Categorized by agriculture, health cover, pensions, housing, and entrepreneurship credit schemes.
            </p>
          </div>

          <Link
            to="/schemes"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-govgreen-800 hover:text-govgreen-900 bg-govgreen-50 hover:bg-govgreen-100 px-4 py-2 rounded-lg border border-govgreen-200 transition"
          >
            <span>View All Schemes</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* 3 Sample Scheme Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {MOCK_SCHEMES.slice(0, 3).map((scheme) => (
            <SchemeCard key={scheme.id} scheme={scheme} />
          ))}
        </div>
      </section>

      {/* 6. POLICY EXPLAINER & DOCUMENT INTELLIGENCE HIGHLIGHT */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl bg-slate-900 text-white p-8 sm:p-12 border border-slate-800 shadow-premium">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 bg-emerald-950 px-3 py-1 rounded-full border border-emerald-800">
                <FileText className="w-3.5 h-3.5" />
                <span>PyMuPDF &amp; Deep Intelligence Engine</span>
              </div>
              <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
                Policy Explainer: Turning 20-Page Government Circulars into Plain Language
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                Upload scanned state gazettes, central guidelines, or eligibility circulars. Our document intelligence engine parses eligibility clauses, deadlines, and mandatory checklists in seconds.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
                <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700">
                  <div className="font-bold text-white mb-0.5">Clause Extraction</div>
                  <div className="text-slate-400 text-[11px]">Identifies binding legal conditions</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700">
                  <div className="font-bold text-white mb-0.5">Ambiguity Detection</div>
                  <div className="text-slate-400 text-[11px]">Flags edge cases and renewal rules</div>
                </div>
              </div>

              <div className="pt-4 flex items-center gap-3">
                <Link
                  to="/policy-explainer"
                  className="inline-flex items-center gap-1.5 bg-govgreen-600 hover:bg-govgreen-500 text-white font-bold text-xs sm:text-sm px-4 py-2.5 rounded-xl transition"
                >
                  <FileText className="w-4 h-4" />
                  <span>Open Policy Explainer</span>
                </Link>
                <Link
                  to="/document-intelligence"
                  className="inline-flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-xs sm:text-sm px-4 py-2.5 rounded-xl transition"
                >
                  <span>Doc Intelligence Pipeline</span>
                </Link>
              </div>
            </div>

            {/* Document Breakdown Preview */}
            <div className="bg-white text-charcoal-900 rounded-2xl p-5 shadow-elevated space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Circular Intelligence Sample
                </span>
                <StatusBadge status="demo" label="Verified PDF" />
              </div>
              <div className="font-bold text-sm text-charcoal-900">
                Karnataka_Raita_Vidya_Nidhi_Gazette_Circular_2024.pdf
              </div>
              <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200">
                &ldquo;Direct financial assistance from ₹2,500 to ₹11,000/yr for wards of verified farmers with active FID. Concurrent receipt with other central merit grants is expressly permitted.&rdquo;
              </p>
              <div className="text-[11px] text-govgreen-800 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-govgreen-700" />
                <span>Extracted 4 Mandatory Rules &bull; 0 Discrepancies</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. SUPPORTED REGIONAL LANGUAGES */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto space-y-3 mb-10">
          <span className="text-xs font-bold uppercase tracking-wider text-ashoka-800 bg-ashoka-50 px-3 py-1 rounded-full border border-ashoka-200">
            Multilingual Inclusion
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900 tracking-tight">
            Civic Intelligence in Your Mother Tongue
          </h2>
          <p className="text-xs sm:text-sm text-slate-600">
            Government circulars are published across languages. SchemeSathi AI speaks to citizens and students in their preferred tongue with high translation fidelity.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { code: 'en', name: 'English', script: 'English', tag: 'Central & Pan-India' },
            { code: 'kn', name: 'Kannada', script: 'ಕನ್ನಡ', tag: 'Karnataka Portal Focus' },
            { code: 'hi', name: 'Hindi', script: 'हिन्दी', tag: 'National & Central Hub' },
            { code: 'te', name: 'Telugu', script: 'తెలుగు', tag: 'AP & Telangana Schemes' },
            { code: 'ta', name: 'Tamil', script: 'தமிழ்', tag: 'Tamil Nadu Circulars' },
            { code: 'mr', name: 'Marathi', script: 'मराठी', tag: 'Maharashtra DBTs' }
          ].map((lang) => {
            const isCurrent = language === lang.code;
            return (
              <button
                key={lang.code}
                onClick={() => setLanguage(lang.code as any)}
                className={`p-4 rounded-xl border text-center transition-all ${
                  isCurrent 
                    ? 'bg-govgreen-50 border-govgreen-500 shadow-elevated scale-[1.02]' 
                    : 'bg-white border-slate-200 hover:border-govgreen-300 hover:bg-slate-50'
                }`}
              >
                <div className="text-lg font-extrabold text-charcoal-900">{lang.script}</div>
                <div className="text-xs font-semibold text-slate-700 mt-0.5">{lang.name}</div>
                <div className="text-[10px] text-slate-500 mt-1">{lang.tag}</div>
                {isCurrent && (
                  <div className="mt-2 text-[10px] font-bold text-govgreen-800 bg-govgreen-100/80 rounded py-0.5">
                    Active
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </section>

      {/* 8. TRUST, OFFICIAL SOURCES & NO HALLUCINATION PLEDGE */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-3xl border border-slate-200 p-8 sm:p-12 shadow-elevated">
          <div className="max-w-3xl mx-auto text-center space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-govgreen-100 text-govgreen-800 flex items-center justify-center mx-auto shadow-subtle">
              <ShieldCheck className="w-6 h-6 text-govgreen-700" />
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900">
              The SchemeSathi Zero-Hallucination Civic Guarantee
            </h2>

            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              When citizens apply for public subsidies or students seek scholarships to fund their education, wrong advice leads to disqualified applications and wasted time. We adhere to three rigorous civic engineering standards:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-4 text-left">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                <div className="font-bold text-charcoal-900 text-sm flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-govgreen-700" />
                  <span>Deterministic Rules</span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Mathematical evaluation of income, age, and academic percentiles using strict logic, not unverified generative guessing.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                <div className="font-bold text-charcoal-900 text-sm flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4 text-govgreen-700" />
                  <span>Gazette Citations</span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Every eligibility condition points to its official order number, gazette notification date, and issuing authority.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                <div className="font-bold text-charcoal-900 text-sm flex items-center gap-1.5">
                  <Lock className="w-4 h-4 text-govgreen-700" />
                  <span>Transparent Disclaimers</span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  We explicitly distinguish verified rules from simulated demonstration data, providing direct links to official portals.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 9. BOTTOM CALL TO ACTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-govgreen-800 to-emerald-900 rounded-3xl p-8 sm:p-12 text-center text-white shadow-premium space-y-6">
          <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            Ready to Check Your Government Benefits or Scholarship?
          </h2>
          <p className="text-xs sm:text-base text-emerald-100 max-w-xl mx-auto">
            Explore our interactive prototype dashboard and test eligibility with full source grounding.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white text-govgreen-900 font-extrabold text-sm px-6 py-3.5 rounded-xl shadow-lg hover:bg-emerald-50 transition"
            >
              <span>Go to Civic Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/assistant"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-govgreen-950/70 hover:bg-govgreen-950 text-white font-bold text-sm px-6 py-3.5 rounded-xl border border-govgreen-600 transition"
            >
              <Bot className="w-4 h-4 text-emerald-300" />
              <span>Ask AI Assistant</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
