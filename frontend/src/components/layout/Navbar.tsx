import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  ShieldCheck, 
  Menu, 
  X, 
  GraduationCap, 
  Search, 
  FileText, 
  Bot, 
  LayoutDashboard, 
  Info,
  FileSearch
} from 'lucide-react';
import { LanguageSelector } from '../common/LanguageSelector';
import { useLanguage } from '../../context/LanguageContext';

export const Navbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { t } = useLanguage();

  const navLinks = [
    { to: '/', label: 'Home', icon: ShieldCheck },
    { to: '/dashboard', label: t('navDashboard'), icon: LayoutDashboard },
    { to: '/scholar-ready', label: t('navScholarReady'), icon: GraduationCap },
    { to: '/schemes', label: t('navSchemes'), icon: Search },
    { to: '/policy-explainer', label: t('navExplainer'), icon: FileText },
    { to: '/assistant', label: t('navAssistant'), icon: Bot },
    { to: '/document-intelligence', label: t('navDocIntel'), icon: FileSearch },
    { to: '/about', label: t('navAbout'), icon: Info }
  ];

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/90 shadow-subtle">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Identity */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-govgreen-800 text-white flex items-center justify-center shadow-subtle group-hover:bg-govgreen-900 transition-colors">
              <ShieldCheck className="w-6 h-6 text-emerald-300" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-lg sm:text-xl font-extrabold tracking-tight text-charcoal-900">
                  Scheme<span className="text-govgreen-700">Sathi</span> <span className="text-ashoka-700">AI</span>
                </span>
                <span className="hidden sm:inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-govgreen-50 text-govgreen-800 border border-govgreen-200">
                  Civic-Tech
                </span>
              </div>
              <p className="text-[10px] text-slate-500 hidden md:block tracking-tight font-medium">
                Understand Rights &bull; Discover Benefits &bull; Apply with Confidence
              </p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            {navLinks.slice(1, 7).map((item) => {
              const active = isActive(item.to);
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                    active
                      ? 'bg-govgreen-50 text-govgreen-800 font-bold border border-govgreen-200/80 shadow-subtle'
                      : 'text-slate-600 hover:text-charcoal-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${active ? 'text-govgreen-700' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right Action Area */}
          <div className="flex items-center gap-2.5">
            {/* Language Selector */}
            <LanguageSelector compact />

            {/* Quick Link to About */}
            <Link
              to="/about"
              className={`hidden sm:flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                isActive('/about')
                  ? 'bg-slate-100 text-slate-900'
                  : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Info className="w-3.5 h-3.5" />
              <span>About</span>
            </Link>

            {/* Mobile Menu Trigger */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg text-slate-600 hover:text-charcoal-900 hover:bg-slate-100 transition"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-200 bg-white px-4 py-4 space-y-2 animate-in fade-in shadow-premium">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-2">
            Navigation
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
            {navLinks.map((item) => {
              const active = isActive(item.to);
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-3 py-2.5 rounded-xl text-xs font-semibold flex items-center gap-2.5 transition ${
                    active
                      ? 'bg-govgreen-50 text-govgreen-900 border border-govgreen-200'
                      : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-govgreen-700' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 px-2">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              FastAPI Core Online
            </span>
            <span className="font-mono text-[10px]">Phase 2 Preview</span>
          </div>
        </div>
      )}
    </header>
  );
};
