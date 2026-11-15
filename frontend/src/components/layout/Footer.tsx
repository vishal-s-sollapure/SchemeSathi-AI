import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, ExternalLink, Heart, Globe, BookOpen } from 'lucide-react';
import { DEMO_DATA_DISCLAIMER } from '../../data/mockData';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-charcoal-900 text-slate-300 border-t border-charcoal-800 pt-12 pb-8 text-xs font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-charcoal-800">
          {/* Brand Info */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-govgreen-700 text-white flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-emerald-200" />
              </div>
              <span className="text-base font-bold text-white tracking-tight">
                Scheme<span className="text-emerald-400">Sathi</span> AI
              </span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              Understand Your Rights. Discover Your Benefits. Apply with Confidence.
            </p>
            <div className="text-[11px] text-slate-400 leading-snug">
              Democratizing civic welfare and educational scholarship readiness for citizens across India through deterministic AI.
            </div>
          </div>

          {/* Core Modules */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
              Platform Features
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/scholar-ready" className="hover:text-emerald-400 transition">
                  ScholarReady™ Student Readiness
                </Link>
              </li>
              <li>
                <Link to="/schemes" className="hover:text-emerald-400 transition">
                  Government Scheme Discovery
                </Link>
              </li>
              <li>
                <Link to="/policy-explainer" className="hover:text-emerald-400 transition">
                  Policy & Circular Explainer
                </Link>
              </li>
              <li>
                <Link to="/assistant" className="hover:text-emerald-400 transition">
                  Multilingual AI Assistant
                </Link>
              </li>
              <li>
                <Link to="/document-intelligence" className="hover:text-emerald-400 transition">
                  Document Intelligence Pipeline
                </Link>
              </li>
            </ul>
          </div>

          {/* Official Indian Civic Sources Directory */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <span>Official Portals Reference</span>
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>
                <a 
                  href="https://www.myscheme.gov.in" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <span>myScheme Portal (MeitY)</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a 
                  href="https://scholarships.gov.in" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <span>National Scholarship Portal (NSP)</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a 
                  href="https://ssp.postmatric.karnataka.gov.in" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <span>Karnataka State Scholarship Portal</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a 
                  href="https://egazette.gov.in" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <span>The Gazette of India (eGazette)</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a 
                  href="https://www.digilocker.gov.in" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <span>DigiLocker Citizen Locker</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
            </ul>
          </div>

          {/* Disclaimer & Transparency */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
              Official Disclaimer
            </h4>
            <div className="bg-charcoal-800/80 p-3 rounded-lg border border-charcoal-700 text-[11px] text-slate-400 leading-relaxed">
              SchemeSathi AI is an independent assistive intelligence application developed for the NxtWave IDEA//FORGE Hackathon. We are not an official government entity. All evaluations reference official gazettes and portals.
            </div>
            <div className="text-[10px] text-purple-300">
              {DEMO_DATA_DISCLAIMER}
            </div>
          </div>
        </div>

        {/* Bottom Credits & Copyright */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 gap-3">
          <div>
            &copy; {new Date().getFullYear()} SchemeSathi AI &bull; Built with FastCivic Architecture
          </div>
          <div className="flex items-center gap-4">
            <Link to="/about" className="hover:text-white transition">
              About & Methodology
            </Link>
            <span>&bull;</span>
            <span className="text-emerald-400 font-semibold">
              Deterministic Verification Active
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
