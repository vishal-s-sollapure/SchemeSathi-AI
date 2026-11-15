import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  GraduationCap, 
  Building2, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Globe, 
  Sparkles,
  ArrowRight,
  FileCheck2
} from 'lucide-react';
import { apiService, HealthResponse } from './services/api';

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<'en' | 'kn' | 'hi'>('en');

  const testConnection = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.checkHealth();
      setHealth(data);
    } catch (err: any) {
      console.error('Failed to connect to backend:', err);
      setError(
        err.response?.data?.message || 
        err.message || 
        'Could not reach FastAPI backend. Make sure it is running on http://127.0.0.1:8000.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testConnection();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Civic Navigation */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-ashoka-700 text-white flex items-center justify-center shadow-md">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-slate-900">
                  Scheme<span className="text-ashoka-700">Sathi</span> <span className="text-civic-700">AI</span>
                </span>
                <span className="bg-amber-100 text-amber-800 text-xs font-semibold px-2 py-0.5 rounded-full border border-amber-300">
                  Phase 1 Ready
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                AI-Powered Government Benefits & Scholarship Readiness Assistant
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <div className="flex items-center space-x-1.5 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-medium">
              <Globe className="w-3.5 h-3.5 text-slate-500 ml-1.5" />
              <button 
                onClick={() => setLanguage('en')}
                className={`px-2 py-1 rounded transition ${language === 'en' ? 'bg-white text-ashoka-700 font-semibold shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
              >
                English
              </button>
              <button 
                onClick={() => setLanguage('kn')}
                className={`px-2 py-1 rounded transition ${language === 'kn' ? 'bg-white text-ashoka-700 font-semibold shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
              >
                ಕನ್ನಡ
              </button>
              <button 
                onClick={() => setLanguage('hi')}
                className={`px-2 py-1 rounded transition ${language === 'hi' ? 'bg-white text-ashoka-700 font-semibold shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
              >
                हिन्दी
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
        
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center space-x-2 bg-ashoka-50 border border-ashoka-200 text-ashoka-800 px-3 py-1 rounded-full text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>NxtWave IDEA//FORGE Hackathon Project</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
            Bridging Citizens to <span className="text-ashoka-700">Welfare</span> & <span className="text-civic-700">Scholarships</span>
          </h1>
          <p className="text-base sm:text-lg text-slate-600">
            A trustworthy, deterministic eligibility evaluation platform backed by source-grounded official citations, dynamic document readiness checklists, and multilingual intelligence.
          </p>
        </div>

        {/* Live Backend Connection Status Card */}
        <section className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 max-w-2xl mx-auto">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 rounded-full animate-ping bg-emerald-500" />
              <h2 className="text-lg font-bold text-slate-900">
                Backend System Health Status
              </h2>
            </div>
            <button
              onClick={testConnection}
              disabled={loading}
              className="inline-flex items-center space-x-1.5 text-xs font-medium text-ashoka-700 hover:text-ashoka-800 bg-ashoka-50 hover:bg-ashoka-100 px-3 py-1.5 rounded-md border border-ashoka-200 transition disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Testing...' : 'Test Connection'}</span>
            </button>
          </div>

          <div className="mt-6">
            {loading ? (
              <div className="flex items-center justify-center py-6 text-slate-500 text-sm space-x-2">
                <RefreshCw className="w-4 h-4 animate-spin text-ashoka-600" />
                <span>Pinging FastAPI endpoint: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">GET /api/health</code></span>
              </div>
            ) : error ? (
              <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 space-y-2">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
                  <span className="font-semibold text-sm">Connection Failed</span>
                </div>
                <p className="text-xs text-rose-700 font-mono bg-rose-100/50 p-2 rounded">
                  {error}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-start justify-between bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="text-sm font-semibold text-emerald-900">
                        FastAPI Service Online & Connected
                      </h4>
                      <p className="text-xs text-emerald-700 mt-0.5">
                        Frontend successfully communicated with the backend API.
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider bg-emerald-200 text-emerald-900">
                    {health?.status}
                  </span>
                </div>

                <div className="bg-slate-900 text-slate-100 rounded-lg p-4 font-mono text-xs overflow-x-auto shadow-inner">
                  <div className="text-slate-400 mb-1">// Response payload from GET /api/health</div>
                  <pre>{JSON.stringify(health, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Dual Module Architecture Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {/* Module 1: ScholarReady */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-lg bg-ashoka-50 text-ashoka-700 flex items-center justify-center mb-4">
              <GraduationCap className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">ScholarReady</h3>
            <p className="text-sm text-slate-600 mb-4 leading-relaxed">
              Tailored for students across India. Features student profile management, deterministic eligibility calculation across central and state scholarships, missing requirement detection, and dynamic readiness checklists.
            </p>
            <ul className="text-xs text-slate-500 space-y-1.5 mb-6">
              <li className="flex items-center space-x-2">
                <FileCheck2 className="w-3.5 h-3.5 text-ashoka-600" />
                <span>Deterministic 4-status rule evaluation</span>
              </li>
              <li className="flex items-center space-x-2">
                <FileCheck2 className="w-3.5 h-3.5 text-ashoka-600" />
                <span>PyMuPDF supporting document analysis</span>
              </li>
              <li className="flex items-center space-x-2">
                <FileCheck2 className="w-3.5 h-3.5 text-ashoka-600" />
                <span>Evidence-linked eligibility explanations</span>
              </li>
            </ul>
            <div className="inline-flex items-center text-xs font-semibold text-ashoka-700">
              <span>Ready for Phase 2 Seed Data</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          {/* Module 2: SchemeSathi */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition">
            <div className="w-12 h-12 rounded-lg bg-civic-50 text-civic-700 flex items-center justify-center mb-4">
              <Building2 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">SchemeSathi</h3>
            <p className="text-sm text-slate-600 mb-4 leading-relaxed">
              Civic welfare discovery for Indian citizens. Discovers welfare schemes, subsidies, health cards, and rights, coupled with multilingual AI explanations and source-grounded government circular citations.
            </p>
            <ul className="text-xs text-slate-500 space-y-1.5 mb-6">
              <li className="flex items-center space-x-2">
                <FileCheck2 className="w-3.5 h-3.5 text-civic-600" />
                <span>Personalized citizen recommendations</span>
              </li>
              <li className="flex items-center space-x-2">
                <FileCheck2 className="w-3.5 h-3.5 text-civic-600" />
                <span>Complex government PDF simplification</span>
              </li>
              <li className="flex items-center space-x-2">
                <FileCheck2 className="w-3.5 h-3.5 text-civic-600" />
                <span>English, Kannada, and Hindi multilingual Q&A</span>
              </li>
            </ul>
            <div className="inline-flex items-center text-xs font-semibold text-civic-700">
              <span>Ready for Phase 2 Seed Data</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>
        </div>

      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div>
            SchemeSathi AI &bull; NxtWave IDEA//FORGE Hackathon
          </div>
          <div className="flex items-center space-x-4">
            <span>FastAPI + SQLite Backend</span>
            <span>&bull;</span>
            <span>React + Vite + Tailwind Frontend</span>
            <span>&bull;</span>
            <span className="text-emerald-700 font-medium">Architecture Phase 1 Active</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
