import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  BookOpen, 
  ShieldCheck, 
  RefreshCw,
  X
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { StatusBadge } from '../components/common/StatusBadge';
import { ChatMessage } from '../components/common/ChatMessage';
import { CitationCard } from '../components/common/CitationCard';
import { LanguageSelector } from '../components/common/LanguageSelector';
import { ChatMessage as ChatMessageType, Citation } from '../types';
import { SAMPLE_CHAT_HISTORY, MOCK_CITATIONS } from '../data/mockData';

export const AIAssistantPage: React.FC = () => {
  const { language } = useLanguage();

  // Initial messages
  const [messages, setMessages] = useState<ChatMessageType[]>([
    {
      id: 'msg-welcome',
      sender: 'assistant',
      content: "Namaste! I am SchemeSathi AI, your source-grounded civic welfare and scholarship guide. Ask me any question in English, Kannada, or Hindi regarding government eligibility criteria, required documents, or official circulars.",
      timestamp: 'Just now',
      language: 'en',
      suggestedFollowUps: [
        "Am I eligible for PM-KISAN if my family has 3 acres of land?",
        "What is the annual income limit for SC/ST Post-Matric Scholarship?",
        "ರೈತ ವಿದ್ಯಾನಿಧಿ ಯೋಜನೆಗೆ ಬೇಕಾಗುವ ದಾಖಲೆಗಳು ಯಾವುವು?"
      ]
    }
  ]);

  const [inputPrompt, setInputPrompt] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [citationsDrawerOpen, setCitationsDrawerOpen] = useState(false);
  const [isThinking, setIsThinking] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  // Handle voice mic placeholder toggle
  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      // Simulate recognized audio prompt after 3 seconds
      setTimeout(() => {
        setIsRecording(false);
        setInputPrompt("What documents do I need to submit on the Karnataka SSP portal?");
      }, 3000);
    } else {
      setIsRecording(false);
    }
  };

  const handleSend = (textToSend?: string) => {
    const query = (textToSend || inputPrompt).trim();
    if (!query) return;

    const userMsg: ChatMessageType = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      language: language
    };

    setMessages(prev => [...prev, userMsg]);
    setInputPrompt('');
    setIsThinking(true);

    // Simulate intelligent response selection based on keywords
    setTimeout(() => {
      let responseText = '';
      let citations: Citation[] = [];
      let followUps: string[] = [];

      const lower = query.toLowerCase();
      if (lower.includes('kisan') || lower.includes('land') || lower.includes('acre')) {
        responseText = SAMPLE_CHAT_HISTORY.kisan.aiResponse;
        citations = SAMPLE_CHAT_HISTORY.kisan.citations;
        followUps = ["How do I complete Aadhaar e-KYC on pmkisan.gov.in?", "Can both husband and wife receive PM-KISAN?"];
      } else if (lower.includes('scholarship') || lower.includes('income limit') || lower.includes('sc') || lower.includes('post-matric')) {
        responseText = SAMPLE_CHAT_HISTORY.scholarship.aiResponse;
        citations = SAMPLE_CHAT_HISTORY.scholarship.citations;
        followUps = ["Is hostel fee included in post-matric assistance?", "How to verify digital income certificate QR?"];
      } else if (query.includes('ರೈತ') || query.includes('ವಿದ್ಯಾನಿಧಿ') || lower.includes('kannada') || lower.includes('karnataka')) {
        responseText = SAMPLE_CHAT_HISTORY.kannada.aiResponse;
        citations = SAMPLE_CHAT_HISTORY.kannada.citations;
        followUps = ["SSP ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ನೋಂದಣಿ ಮಾಡುವುದು ಹೇಗೆ?", "FRUITS FID ಪಡೆಯಲು ಕೃಷಿ ಇಲಾಖೆಗೆ ಭೇಟಿ ನೀಡಬೇಕೆ?"];
      } else {
        responseText = `Based on verified central and state gazette guidelines:\n\n1. **Eligibility Evaluation**: To qualify under this category, your household annual income must adhere to the certified limit specified in the relevant scheme order, with active domicile proof.\n2. **Evidence-Linked Requirement**: Biometric Aadhaar-seeded bank account mapped to NPCI is mandatory for Direct Benefit Transfer.\n3. **Application Verification**: Submission must be processed through the official nodal portal with principal/panchayat attestation.`;
        citations = [MOCK_CITATIONS[0]];
        followUps = ["View full gazette circular", "Check document readiness score"];
      }

      const assistantMsg: ChatMessageType = {
        id: `ast-${Date.now()}`,
        sender: 'assistant',
        content: responseText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        language: language,
        citations: citations,
        suggestedFollowUps: followUps
      };

      setMessages(prev => [...prev, assistantMsg]);
      setIsThinking(false);
    }, 900);
  };

  // Collect all unique citations across current messages
  const allActiveCitations = messages
    .filter(m => m.citations && m.citations.length > 0)
    .flatMap(m => m.citations || []);
  const uniqueCitations = Array.from(new Map(allActiveCitations.map(c => [c.id, c])).values());

  return (
    <div className="space-y-6 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-govgreen-900 via-charcoal-900 to-slate-900 rounded-2xl p-6 text-white shadow-elevated flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold bg-govgreen-800 text-emerald-200 px-2.5 py-0.5 rounded-full border border-govgreen-600">
              Civic AI Assistant
            </span>
            <StatusBadge status="demo" label="Verified Knowledge Mode" />
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight">
            SchemeSathi Multilingual Assistant
          </h1>
          <p className="text-xs text-slate-300">
            Source-grounded assistance with zero hallucinations &bull; English &bull; ಕನ್ನಡ &bull; हिन्दी
          </p>
        </div>

        {/* Right header controls: Language + Citations Drawer Trigger */}
        <div className="flex items-center gap-2.5">
          <LanguageSelector compact />

          <button
            onClick={() => setCitationsDrawerOpen(!citationsDrawerOpen)}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-govgreen-800/80 hover:bg-govgreen-700 text-xs font-semibold text-white border border-govgreen-600 shadow-sm transition"
          >
            <BookOpen className="w-3.5 h-3.5 text-emerald-300" />
            <span>Citations ({uniqueCitations.length})</span>
          </button>
        </div>
      </div>

      {/* Main Chat Workspace Grid (Chat on Left, Citation Drawer on Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Chat Area (12 cols on mobile, 8 or 12 on desktop depending on drawer) */}
        <div className={`${citationsDrawerOpen ? 'lg:col-span-8' : 'lg:col-span-12'} bg-white rounded-2xl border border-slate-200 shadow-subtle flex flex-col h-[650px] overflow-hidden transition-all duration-300`}>
          
          {/* Chat Messages Feed */}
          <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-6 bg-slate-50/40">
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                onFollowUpClick={(prompt) => handleSend(prompt)}
              />
            ))}

            {/* Thinking / Evaluating Indicator */}
            {isThinking && (
              <div className="flex items-center gap-3 animate-in fade-in">
                <div className="w-9 h-9 rounded-xl bg-govgreen-800 text-white flex items-center justify-center flex-shrink-0">
                  <ShieldCheck className="w-5 h-5 text-emerald-300 animate-pulse" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-subtle text-xs text-slate-600 flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-govgreen-700" />
                  <span>Cross-referencing gazette circulars &amp; evaluating eligibility rules...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Voice Recording Active Banner */}
          {isRecording && (
            <div className="bg-rose-50 border-t border-rose-200 px-4 py-2.5 flex items-center justify-between text-xs text-rose-800 animate-pulse">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-rose-600 animate-ping" />
                <span className="font-bold">Listening to Native Voice Query...</span>
                <span className="text-slate-500 text-[11px]">(Simulating speech-to-text in Indian languages)</span>
              </div>
              <button
                onClick={() => setIsRecording(false)}
                className="text-xs font-semibold text-rose-700 hover:text-rose-900 underline"
              >
                Stop
              </button>
            </div>
          )}

          {/* Bottom Chat Input Bar */}
          <div className="p-4 bg-white border-t border-slate-200 space-y-2">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              {/* Voice Microphone Button */}
              <button
                type="button"
                onClick={toggleRecording}
                className={`p-2.5 rounded-xl border transition shadow-sm ${
                  isRecording 
                    ? 'bg-rose-600 text-white border-rose-700' 
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200 hover:text-slate-900'
                }`}
                title="Voice query in native tongue (Microphone placeholder)"
              >
                {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-govgreen-800" />}
              </button>

              {/* Text Input */}
              <input
                type="text"
                placeholder="Ask about schemes, scholarships, required documents, or circular clauses..."
                value={inputPrompt}
                onChange={(e) => setInputPrompt(e.target.value)}
                className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:outline-none focus:border-govgreen-600 shadow-sm"
              />

              {/* Send Button */}
              <button
                type="submit"
                disabled={!inputPrompt.trim() || isThinking}
                className="px-4 sm:px-5 py-2.5 rounded-xl bg-govgreen-700 hover:bg-govgreen-800 disabled:opacity-50 text-white font-bold text-xs sm:text-sm shadow-subtle flex items-center gap-1.5 transition flex-shrink-0"
              >
                <span className="hidden sm:inline">Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>

            <div className="flex items-center justify-between text-[11px] text-slate-400 px-1">
              <span>All replies reference official Gazette orders and circulars.</span>
              <span className="font-mono text-[10px]">Zero Hallucination Grounding</span>
            </div>
          </div>
        </div>

        {/* Right Citation Drawer (4 cols when open) */}
        {citationsDrawerOpen && (
          <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 shadow-subtle p-5 space-y-4 max-h-[650px] overflow-y-auto animate-in slide-in-from-right-2">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-govgreen-700" />
                <h3 className="text-sm font-bold text-charcoal-900">
                  Referenced Citations
                </h3>
              </div>
              <button
                onClick={() => setCitationsDrawerOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-500">
              Official circulars cited by SchemeSathi AI in this session:
            </p>

            <div className="space-y-3">
              {uniqueCitations.length > 0 ? (
                uniqueCitations.map((cite) => (
                  <CitationCard key={cite.id} citation={cite} compact />
                ))
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">
                  Ask a question to load official citations.
                </div>
              )}
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-500">
              Every citation links directly to the published Gazette of India or State Secretariat records.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
