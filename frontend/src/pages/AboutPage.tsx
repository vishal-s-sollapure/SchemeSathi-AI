import React from 'react';
import { 
  ShieldCheck, 
  Building2, 
  FileText, 
  CheckCircle2, 
  Award, 
  Code2, 
  Server, 
  Lock, 
  Sparkles,
  Info
} from 'lucide-react';
import { DEMO_DATA_DISCLAIMER } from '../data/mockData';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-10 animate-in fade-in pb-16 max-w-5xl mx-auto">
      {/* 1. PRODUCT IDENTITY & MISSION BANNER */}
      <section className="bg-gradient-to-r from-govgreen-950 via-govgreen-900 to-charcoal-900 rounded-3xl p-8 sm:p-12 text-white shadow-premium relative overflow-hidden">
        <div className="relative space-y-4 max-w-3xl">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold bg-govgreen-800 text-emerald-200 px-3 py-1 rounded-full border border-govgreen-600">
            <ShieldCheck className="w-4 h-4 text-emerald-300" />
            <span>Civic-Tech Platform Identity</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight">
            SchemeSathi AI
          </h1>

          <p className="text-base sm:text-xl text-emerald-100 font-medium italic">
            &ldquo;Understand Your Rights. Discover Your Benefits. Apply with Confidence.&rdquo;
          </p>

          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed pt-2">
            SchemeSathi AI is an assistive civic-intelligence platform designed to bridge the persistent gap between Indian citizens, students, and life-changing public welfare entitlements. We combine deterministic eligibility rules, official gazette grounding, and regional language models to eliminate the frustration, bureaucracy, and disqualification caused by unverified guidance.
          </p>
        </div>
      </section>

      {/* 2. CORE PHILOSOPHY & PILLARS */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-govgreen-800 bg-govgreen-50 px-3 py-1 rounded-full border border-govgreen-200">
            Our Civic Engineering Philosophy
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900 tracking-tight">
            Built on Verifiable Truth, Not Generative Guesses
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-3">
            <div className="w-12 h-12 rounded-xl bg-govgreen-100 text-govgreen-800 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-govgreen-700" />
            </div>
            <h3 className="text-base font-bold text-charcoal-900">
              Deterministic Verification
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              When determining whether a student meets the income cap or an applicant qualifies for DBT subsidies, we use mathematical, rule-based logic rather than speculative LLM generation. If a criteria says &le; ₹2.5 Lakhs, it is strictly validated.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-3">
            <div className="w-12 h-12 rounded-xl bg-ashoka-100 text-ashoka-800 flex items-center justify-center">
              <FileText className="w-6 h-6 text-ashoka-700" />
            </div>
            <h3 className="text-base font-bold text-charcoal-900">
              Source-Grounded Citations
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Every assertion made by SchemeSathi AI is tied directly to a verifiable clause number, gazette notification date, and official issuing ministry document, providing transparent proof of public rights.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center">
              <Lock className="w-6 h-6 text-emerald-700" />
            </div>
            <h3 className="text-base font-bold text-charcoal-900">
              Privacy by Default
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Citizen economic, caste, and personal document data belong to the citizen. Document OCR parsing and profile simulations run with client-side isolation, storing no citizen records permanently without explicit consent.
            </p>
          </div>
        </div>
      </section>

      {/* 3. TECHNICAL ARCHITECTURE */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-subtle space-y-6">
        <div className="pb-4 border-b border-slate-100">
          <span className="text-xs font-bold text-ashoka-800 bg-ashoka-50 px-2.5 py-0.5 rounded border border-ashoka-200">
            Technical Architecture
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-charcoal-900 mt-1">
            Engineered with Modern Full-Stack Civics
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Phase 1 &bull; Phase 2 FastCivic Architecture Breakdown
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <div className="font-bold text-charcoal-900 flex items-center gap-2">
              <Server className="w-4 h-4 text-ashoka-700" />
              <span>FastAPI + Python Backend</span>
            </div>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              High-throughput asynchronous REST API serving deterministic evaluation endpoints, health checks, and semantic matching.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <div className="font-bold text-charcoal-900 flex items-center gap-2">
              <Code2 className="w-4 h-4 text-govgreen-700" />
              <span>React 18 + Vite + TypeScript</span>
            </div>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Componentized, type-safe frontend UI with responsive client-side routing, accessible color contrast, and instant reactivity.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <div className="font-bold text-charcoal-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-700" />
              <span>Tailwind CSS &amp; Lucide Icons</span>
            </div>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Civic color system combining deep forest emerald, dark charcoal accents, and clean typography designed for government credibility.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <div className="font-bold text-charcoal-900 flex items-center gap-2">
              <FileText className="w-4 h-4 text-govgreen-700" />
              <span>PyMuPDF Document Parser</span>
            </div>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Extracts text, multi-column tables, and clauses from state and central PDF circulars with high bilingual fidelity.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <div className="font-bold text-charcoal-900 flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-700" />
              <span>ScholarReady™ Engine</span>
            </div>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Dynamic readiness calculator that maps student marks, income, and domicile to generate actionable document checklists.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <div className="font-bold text-charcoal-900 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-emerald-700" />
              <span>SQLite Persistence</span>
            </div>
            <p className="text-slate-600 leading-relaxed text-[11px]">
              Lightweight, zero-configuration embedded database for scheme catalogs, eligibility rules, and audit logs.
            </p>
          </div>
        </div>
      </section>

      {/* 4. DATA TRANSPARENCY & OFFICIAL DISCLAIMER */}
      <section className="bg-purple-950 text-purple-100 rounded-2xl p-6 sm:p-8 border border-purple-800/80 space-y-4">
        <div className="flex items-center gap-2.5">
          <Info className="w-5 h-5 text-purple-300" />
          <h2 className="text-lg font-bold text-white uppercase tracking-wide">
            Data Transparency &amp; Non-Government Disclaimer
          </h2>
        </div>

        <p className="text-xs sm:text-sm text-purple-200/90 leading-relaxed">
          {DEMO_DATA_DISCLAIMER}
        </p>

        <p className="text-xs text-purple-300/80 leading-relaxed">
          SchemeSathi AI is an independent civic-tech assistive tool. We do not represent any government ministry, department, or administrative agency. All recommendations, deadlines, and criteria must be cross-verified on official portals such as{' '}
          <a href="https://www.myscheme.gov.in" target="_blank" rel="noopener noreferrer" className="underline text-white font-semibold">myScheme</a>,{' '}
          <a href="https://scholarships.gov.in" target="_blank" rel="noopener noreferrer" className="underline text-white font-semibold">NSP</a>, or{' '}
          <a href="https://ssp.postmatric.karnataka.gov.in" target="_blank" rel="noopener noreferrer" className="underline text-white font-semibold">Karnataka SSP</a> before submitting financial or academic applications.
        </p>
      </section>

      {/* 5. HACKATHON & PROJECT CREDITS */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 text-center space-y-3 shadow-subtle">
        <div className="inline-flex items-center gap-2 text-xs font-bold text-slate-700 bg-slate-100 px-3 py-1 rounded-full">
          <Award className="w-4 h-4 text-amber-600" />
          <span>NxtWave IDEA//FORGE Hackathon Project</span>
        </div>
        <p className="text-xs sm:text-sm text-slate-600 max-w-xl mx-auto leading-relaxed">
          Developed as part of the NxtWave IDEA//FORGE Hackathon to demonstrate how AI and deterministic systems can empower civic rights, higher education access, and public welfare transparency in India.
        </p>
        <div className="text-[11px] text-slate-400">
          Phase 2: Professional Frontend Development Completed &bull; Ready for Evaluation
        </div>
      </section>
    </div>
  );
};
