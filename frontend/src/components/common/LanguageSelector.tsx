import React, { useState, useRef, useEffect } from 'react';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { useLanguage, SUPPORTED_LANGUAGES } from '../../context/LanguageContext';
import { LanguageCode } from '../../types';

interface LanguageSelectorProps {
  compact?: boolean;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({ compact = false }) => {
  const { language, setLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLang = SUPPORTED_LANGUAGES.find(l => l.code === language) || SUPPORTED_LANGUAGES[0];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (code: LanguageCode) => {
    setLanguage(code);
    setIsOpen(false);
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        className={`inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 transition shadow-subtle text-slate-800 ${
          compact ? 'px-2.5 py-1.5 text-xs font-medium' : 'px-3 py-2 text-sm font-semibold'
        }`}
      >
        <Globe className="w-4 h-4 text-govgreen-700 flex-shrink-0" />
        <span className="hidden sm:inline text-slate-600 text-xs font-normal">Language:</span>
        <span className="font-semibold text-charcoal-900">{currentLang.nativeLabel}</span>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1.5 w-52 origin-top-right rounded-xl bg-white border border-slate-200 shadow-premium z-50 py-1.5 focus:outline-none animate-in fade-in slide-in-from-top-1">
          <div className="px-3 py-1.5 border-b border-slate-100 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Select Civic Language
          </div>
          <div className="max-h-60 overflow-y-auto py-1">
            {SUPPORTED_LANGUAGES.map((lang) => {
              const isSelected = lang.code === language;
              return (
                <button
                  key={lang.code}
                  onClick={() => handleSelect(lang.code)}
                  className={`w-full text-left px-3.5 py-2 text-xs flex items-center justify-between transition ${
                    isSelected 
                      ? 'bg-govgreen-50 text-govgreen-800 font-semibold' 
                      : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{lang.nativeLabel}</span>
                    <span className="text-[10px] text-slate-500">{lang.label}</span>
                  </div>
                  {isSelected && <Check className="w-4 h-4 text-govgreen-700" />}
                </button>
              );
            })}
          </div>
          <div className="px-3 py-1.5 bg-slate-50 border-t border-slate-100 text-[10px] text-slate-500">
            Multilingual support with direct gazette citations.
          </div>
        </div>
      )}
    </div>
  );
};
