import React, { useState } from 'react';
import { 
  ShieldCheck, 
  User, 
  Copy, 
  Check, 
  Volume2, 
  BookOpen, 
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../../types';
import { CitationCard } from './CitationCard';
import { StatusBadge } from './StatusBadge';

interface ChatMessageProps {
  message: ChatMessageType;
  onFollowUpClick?: (prompt: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, onFollowUpClick }) => {
  const isAssistant = message.sender === 'assistant';
  const [copied, setCopied] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = () => {
    setSpeaking(true);
    setTimeout(() => setSpeaking(false), 3000);
  };

  return (
    <div className={`flex gap-3 sm:gap-4 ${isAssistant ? 'justify-start' : 'justify-end'} animate-in fade-in`}>
      {/* Assistant Avatar */}
      {isAssistant && (
        <div className="w-9 h-9 rounded-xl bg-govgreen-800 text-white flex items-center justify-center flex-shrink-0 shadow-subtle mt-0.5">
          <ShieldCheck className="w-5 h-5 text-emerald-300" />
        </div>
      )}

      {/* Message Bubble Container */}
      <div className={`max-w-2xl sm:max-w-3xl space-y-3 ${isAssistant ? 'w-full' : ''}`}>
        <div 
          className={`rounded-2xl p-4 sm:p-5 shadow-subtle ${
            isAssistant 
              ? 'bg-white border border-slate-200 text-charcoal-900' 
              : 'bg-charcoal-900 text-white ml-auto'
          }`}
        >
          {/* Header Row for Assistant */}
          {isAssistant && (
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-govgreen-900 tracking-tight">
                  SchemeSathi AI Assistant
                </span>
                <span className="text-[10px] bg-govgreen-50 text-govgreen-800 px-2 py-0.5 rounded-full font-semibold border border-govgreen-200">
                  Verified Official Knowledge
                </span>
              </div>

              <div className="flex items-center gap-2 text-slate-400">
                <button
                  onClick={handleSpeak}
                  className="hover:text-govgreen-800 p-1 rounded hover:bg-slate-50 transition"
                  title="Listen to native voice playback"
                >
                  <Volume2 className={`w-3.5 h-3.5 ${speaking ? 'text-govgreen-700 animate-pulse' : ''}`} />
                </button>
                <button
                  onClick={handleCopy}
                  className="hover:text-govgreen-800 p-1 rounded hover:bg-slate-50 transition"
                  title="Copy explanation"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
                <span className="text-[10px] text-slate-400">{message.timestamp}</span>
              </div>
            </div>
          )}

          {/* Content Body */}
          <div className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap space-y-2">
            {message.content}
          </div>

          {/* User message timestamp */}
          {!isAssistant && (
            <div className="text-[10px] text-slate-400 mt-2 text-right">
              {message.timestamp}
            </div>
          )}
        </div>

        {/* Embedded Official Gazette Citations if Assistant */}
        {isAssistant && message.citations && message.citations.length > 0 && (
          <div className="space-y-2 pl-1 sm:pl-2">
            <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5 text-govgreen-700" />
              <span>Grounding Sources ({message.citations.length} Official Reference{message.citations.length > 1 ? 's' : ''})</span>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {message.citations.map((cite) => (
                <CitationCard key={cite.id} citation={cite} />
              ))}
            </div>
          </div>
        )}

        {/* Suggested Follow-Ups */}
        {isAssistant && message.suggestedFollowUps && message.suggestedFollowUps.length > 0 && (
          <div className="space-y-1.5 pt-1 pl-1">
            <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              Suggested Follow-up Inquiries:
            </div>
            <div className="flex flex-wrap gap-1.5">
              {message.suggestedFollowUps.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => onFollowUpClick && onFollowUpClick(prompt)}
                  className="text-left text-xs bg-white hover:bg-govgreen-50 text-slate-700 hover:text-govgreen-900 border border-slate-200 hover:border-govgreen-300 px-3 py-1.5 rounded-lg transition shadow-subtle flex items-center gap-1.5"
                >
                  <span>{prompt}</span>
                  <ArrowRight className="w-3 h-3 text-slate-400 flex-shrink-0" />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* User Avatar */}
      {!isAssistant && (
        <div className="w-9 h-9 rounded-xl bg-slate-200 text-charcoal-800 flex items-center justify-center flex-shrink-0 shadow-subtle mt-0.5">
          <User className="w-5 h-5 text-slate-600" />
        </div>
      )}
    </div>
  );
};
