import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  GraduationCap, 
  Search, 
  FileText, 
  Bot, 
  FileSearch, 
  Info, 
  ChevronLeft, 
  ChevronRight,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { t } = useLanguage();

  const links = [
    { to: '/dashboard', label: t('navDashboard'), icon: LayoutDashboard, badge: 'Overview' },
    { to: '/scholar-ready', label: t('navScholarReady'), icon: GraduationCap, badge: 'New' },
    { to: '/schemes', label: t('navSchemes'), icon: Search },
    { to: '/policy-explainer', label: t('navExplainer'), icon: FileText },
    { to: '/assistant', label: t('navAssistant'), icon: Bot, badge: 'AI' },
    { to: '/document-intelligence', label: t('navDocIntel'), icon: FileSearch },
    { to: '/about', label: t('navAbout'), icon: Info }
  ];

  return (
    <aside 
      className={`bg-white border-r border-slate-200 transition-all duration-300 flex flex-col justify-between hidden md:flex ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      <div>
        {/* Workspace Brand / Mode */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          {!collapsed ? (
            <div>
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Civic Platform
              </div>
              <div className="text-sm font-extrabold text-charcoal-900 flex items-center gap-1.5 mt-0.5">
                <span>SchemeSathi Workspace</span>
              </div>
            </div>
          ) : (
            <div className="mx-auto">
              <ShieldCheck className="w-6 h-6 text-govgreen-700" />
            </div>
          )}

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-charcoal-900 hover:bg-slate-100 transition"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Item List */}
        <nav className="p-3 space-y-1">
          {links.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group ${
                    isActive
                      ? 'bg-govgreen-50 text-govgreen-900 font-bold border border-govgreen-200 shadow-subtle'
                      : 'text-slate-600 hover:text-charcoal-900 hover:bg-slate-50'
                  } ${collapsed ? 'justify-center px-2' : ''}`
                }
                title={collapsed ? item.label : undefined}
              >
                {({ isActive }) => (
                  <>
                    <Icon className={`w-4 h-4 flex-shrink-0 ${
                      isActive ? 'text-govgreen-700' : 'text-slate-400 group-hover:text-slate-600'
                    }`} />
                    
                    {!collapsed && (
                      <div className="flex-1 flex items-center justify-between">
                        <span className="truncate">{item.label}</span>
                        {item.badge && (
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                            item.badge === 'AI' 
                              ? 'bg-purple-100 text-purple-800' 
                              : item.badge === 'New' 
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-slate-100 text-slate-600'
                          }`}>
                            {item.badge}
                          </span>
                        )}
                      </div>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom Profile / Quick Status Box */}
      {!collapsed ? (
        <div className="p-3 m-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-bold text-slate-700 text-[11px] uppercase tracking-wider">
              Verification Engine
            </span>
          </div>
          <p className="text-[11px] text-slate-500 leading-snug">
            Deterministic matching with zero hallucination guarantee.
          </p>
          <div className="mt-2 pt-2 border-t border-slate-200/80 flex items-center justify-between text-[10px] text-slate-400">
            <span>Version 0.2.0</span>
            <span className="text-govgreen-800 font-bold">10 Modules Verified</span>
          </div>
        </div>
      ) : (
        <div className="p-2 text-center text-slate-400 pb-4">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 mx-auto" />
        </div>
      )}
    </aside>
  );
};
