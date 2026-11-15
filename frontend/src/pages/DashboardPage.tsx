import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  GraduationCap, 
  Search, 
  FileText, 
  Bot, 
  CheckCircle2, 
  Clock, 
  FileWarning, 
  Sparkles,
  ChevronRight,
  User
} from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { MOCK_SCHEMES, MOCK_SCHOLARSHIPS } from '../data/mockData';
import { SchemeCard } from '../components/common/SchemeCard';
import { ScholarshipCard } from '../components/common/ScholarshipCard';

export const DashboardPage: React.FC = () => {
  // Active Profile State for demo
  const [profile] = useState({
    name: 'Ananya Sharma',
    role: 'Undergraduate Engineering Student & Farmer Ward',
    state: 'Karnataka',
    category: 'OBC (Category 3A)',
    incomeBracket: '₹1.80 Lakh / year',
    academicMarks: '84.5%',
    institution: 'VTU Affiliated College, Belagavi'
  });

  const readinessScore = 80; // 80% ready

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* 1. WELCOME SECTION */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-subtle flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        {/* Accent background decoration */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-govgreen-50/50 rounded-full blur-2xl pointer-events-none" />

        <div className="space-y-2 relative">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-govgreen-800 bg-govgreen-50 border border-govgreen-200 px-2.5 py-0.5 rounded-full">
              Civic Dashboard &bull; Phase 2 Preview
            </span>
            <StatusBadge status="demo" label="Demo Profile" />
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900 tracking-tight">
            Namaste, {profile.name} 👋
          </h1>

          <p className="text-xs sm:text-sm text-slate-600 max-w-xl">
            Your active profile is matched against <strong>6 central and state schemes</strong>. You have <strong>2 high-priority scholarship deadlines</strong> approaching.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2 text-xs text-slate-500">
            <span className="flex items-center gap-1 font-medium text-slate-700">
              <User className="w-3.5 h-3.5 text-slate-400" />
              {profile.role}
            </span>
            <span>&bull;</span>
            <span>State: <strong className="text-slate-700">{profile.state}</strong></span>
            <span>&bull;</span>
            <span>Category: <strong className="text-slate-700">{profile.category}</strong></span>
          </div>
        </div>

        {/* Quick Health & Readiness Dial */}
        <div className="flex items-center gap-4 bg-slate-50 border border-slate-200/80 p-4 rounded-xl flex-shrink-0">
          <div className="text-center">
            <div className="text-3xl font-black text-govgreen-800 tracking-tight">
              {readinessScore}%
            </div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mt-0.5">
              Readiness Score
            </div>
          </div>
          <div className="border-l border-slate-200 pl-4 space-y-1 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-800 font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>4 Docs Ready</span>
            </div>
            <div className="flex items-center gap-1.5 text-amber-800 font-semibold">
              <FileWarning className="w-3.5 h-3.5 text-amber-600" />
              <span>1 Doc Missing</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. QUICK ACTIONS BAR */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Link
          to="/scholar-ready"
          className="p-4 rounded-xl bg-white hover:bg-ashoka-50/50 border border-slate-200 hover:border-ashoka-300 transition shadow-subtle group text-left"
        >
          <div className="w-9 h-9 rounded-lg bg-ashoka-100 text-ashoka-800 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div className="text-xs font-bold text-charcoal-900 group-hover:text-ashoka-800">
            Check Scholarship
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Evaluate NSP &amp; SSP
          </div>
        </Link>

        <Link
          to="/policy-explainer"
          className="p-4 rounded-xl bg-white hover:bg-govgreen-50/50 border border-slate-200 hover:border-govgreen-300 transition shadow-subtle group text-left"
        >
          <div className="w-9 h-9 rounded-lg bg-govgreen-100 text-govgreen-800 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
            <FileText className="w-5 h-5" />
          </div>
          <div className="text-xs font-bold text-charcoal-900 group-hover:text-govgreen-800">
            Explain Circular PDF
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Simplify gazette rules
          </div>
        </Link>

        <Link
          to="/schemes"
          className="p-4 rounded-xl bg-white hover:bg-emerald-50/50 border border-slate-200 hover:border-emerald-300 transition shadow-subtle group text-left"
        >
          <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
            <Search className="w-5 h-5" />
          </div>
          <div className="text-xs font-bold text-charcoal-900 group-hover:text-emerald-800">
            Discover Schemes
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Agriculture, Health, MSME
          </div>
        </Link>

        <Link
          to="/assistant"
          className="p-4 rounded-xl bg-white hover:bg-purple-50/50 border border-slate-200 hover:border-purple-300 transition shadow-subtle group text-left"
        >
          <div className="w-9 h-9 rounded-lg bg-purple-100 text-purple-800 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
            <Bot className="w-5 h-5" />
          </div>
          <div className="text-xs font-bold text-charcoal-900 group-hover:text-purple-800">
            Ask AI Assistant
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Voice &amp; Regional Q&amp;A
          </div>
        </Link>
      </div>

      {/* 3. SCHOLARREADY MODULE SUMMARY */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-ashoka-600" />
              <h2 className="text-lg font-bold text-charcoal-900">
                ScholarReady™ Student Status &amp; Matches
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Targeted scholarships matched for Engineering UG &bull; Karnataka Domicile &bull; Income &lt; 2.5L
            </p>
          </div>

          <Link
            to="/scholar-ready"
            className="inline-flex items-center gap-1 text-xs font-bold text-ashoka-700 hover:text-ashoka-800"
          >
            <span>Full ScholarReady Workspace</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Scholarships Grid Preview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {MOCK_SCHOLARSHIPS.slice(0, 2).map((sch) => (
            <ScholarshipCard key={sch.id} scholarship={sch} />
          ))}
        </div>

        {/* Pending Document Alert Banner */}
        <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200/90 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-start gap-2.5">
            <FileWarning className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-amber-900">Action Required:</span>{' '}
              <span className="text-amber-800">
                Current Year College Bonafide Certificate is pending for 100% readiness under Post-Matric SC/ST.
              </span>
            </div>
          </div>
          <Link
            to="/scholar-ready"
            className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-bold flex-shrink-0 text-center transition"
          >
            Upload Bonafide
          </Link>
        </div>
      </section>

      {/* 4. SCHEME DISCOVERY MODULE SUMMARY */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-govgreen-600" />
              <h2 className="text-lg font-bold text-charcoal-900">
                Recommended Citizen Schemes for Your Household
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Based on agricultural landholding record and rural family criteria
            </p>
          </div>

          <Link
            to="/schemes"
            className="inline-flex items-center gap-1 text-xs font-bold text-govgreen-800 hover:text-govgreen-900"
          >
            <span>Browse All 6 Schemes</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {/* 2 Scheme Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {MOCK_SCHEMES.slice(0, 2).map((scheme) => (
            <SchemeCard key={scheme.id} scheme={scheme} />
          ))}
        </div>
      </section>

      {/* 5. RECENT ACTIVITY & VERIFICATION LOG */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold text-charcoal-900 flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              Recent Evaluation &amp; Document Activity
            </h3>
            <span className="text-[10px] text-slate-400">All checks timestamped</span>
          </div>

          <div className="space-y-3">
            {[
              {
                title: 'Karnataka Raita Vidya Nidhi Scheme Evaluated',
                type: 'Eligibility Check',
                time: 'Today at 02:45 PM',
                status: 'Eligible (98% match)',
                badge: 'eligible'
              },
              {
                title: 'Uploaded: Karnataka_Raita_Vidya_Nidhi_Gazette_Circular_2024.pdf',
                type: 'Policy Explainer OCR',
                time: 'Yesterday at 05:12 PM',
                status: '4 Rules Extracted',
                badge: 'active'
              },
              {
                title: 'Q&A Inquiry in Kannada regarding FRUITS FID verification',
                type: 'AI Assistant',
                time: '14 Nov 2026',
                status: '1 Official Citation Grounded',
                badge: 'high_match'
              }
            ].map((act, idx) => (
              <div 
                key={idx}
                className="flex items-start justify-between p-3 rounded-xl bg-slate-50/70 border border-slate-100 text-xs gap-3"
              >
                <div>
                  <div className="font-semibold text-charcoal-900">{act.title}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">
                    {act.type} &bull; {act.time}
                  </div>
                </div>
                <StatusBadge status={act.badge as any} label={act.status} />
              </div>
            ))}
          </div>
        </div>

        {/* Official Gazette Bulletins / Notifications */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
          <div className="pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold text-charcoal-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-govgreen-700" />
              Gazette Bulletin Alert
            </h3>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Live updates from eGazette &amp; state portals
            </p>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-govgreen-50/60 border border-govgreen-200">
              <div className="font-bold text-govgreen-950">
                SSP Karnataka Post-Matric Deadline Extended
              </div>
              <p className="text-[11px] text-govgreen-800 mt-1">
                Last date for principal e-attestation extended to 30 Nov 2026.
              </p>
              <div className="text-[10px] text-govgreen-700 font-mono mt-1">
                Circular: GO-AGRI-44-EDN-2021
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div className="font-bold text-slate-900">
                Aadhaar NPCI Seeding Mandate
              </div>
              <p className="text-[11px] text-slate-600 mt-1">
                DBT transfers require Aadhaar payment bridge enabled accounts.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
