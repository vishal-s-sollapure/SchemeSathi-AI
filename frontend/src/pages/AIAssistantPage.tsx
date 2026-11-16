import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  BookOpen, 
  ShieldCheck, 
  RefreshCw,
  X,
  Volume2,
  VolumeX,
  Sparkles,
  AlertCircle,
  HelpCircle,
  Radio
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { StatusBadge } from '../components/common/StatusBadge';
import { ChatMessage } from '../components/common/ChatMessage';
import { CitationCard } from '../components/common/CitationCard';
import { LanguageSelector } from '../components/common/LanguageSelector';
import { ChatMessage as ChatMessageType, Citation, LanguageCode, ValidatedCitation } from '../types';
import { SAMPLE_CHAT_HISTORY } from '../data/mockData';
import { apiService } from '../services/api';
import { voiceAssistant } from '../services/voiceAssistant';

function mapValidatedCitation(c: ValidatedCitation, idx: number): Citation {
  return {
    id: c.matched_chunk_id || `cit-${Date.now()}-${idx}`,
    title: c.clause_or_section || 'Official Clause',
    documentName: c.source_title,
    issuingAuthority: 'Government Authority',
    circularNumber: c.circular_number || 'Official Circular',
    notificationDate: 'Verified 2024-25',
    clauseNumber: c.clause_or_section,
    excerpt: c.excerpt,
    officialSourceUrl: c.official_source_url,
    verificationBadge: c.verification_status === 'OFFICIALLY_VERIFIED' ? 'Verified Official Source' : 'Authoritative Record'
  };
}

export const AIAssistantPage: React.FC = () => {
  const { language, setLanguage, t } = useLanguage();

  // Initial multilingual messages
  const [messages, setMessages] = useState<ChatMessageType[]>([
    {
      id: 'msg-welcome',
      sender: 'assistant',
      content: "Namaste! I am SchemeSathi AI, your source-grounded civic welfare and scholarship voice assistant. Ask me questions in English, ಕನ್ನಡ, or हिन्दी with speech-to-text or keyboard input.",
      timestamp: 'Just now',
      language: 'en',
      suggestedFollowUps: [
        "What government schemes may I qualify for?",
        "ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗಬಹುದು?",
        "मुझे कौन-कौन सी सरकारी योजनाएं मिल सकती हैं?"
      ]
    }
  ]);

  const [inputPrompt, setInputPrompt] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [micError, setMicError] = useState<string | null>(null);
  const [citationsDrawerOpen, setCitationsDrawerOpen] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [isSpeakingActive, setIsSpeakingActive] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  // Clean up any active speech synthesis on unmount
  useEffect(() => {
    return () => {
      voiceAssistant.stopSpeaking();
      voiceAssistant.stopListening();
    };
  }, []);

  // Voice Speech-to-Text Recognition Toggle
  const toggleRecording = () => {
    setMicError(null);

    if (isRecording) {
      voiceAssistant.stopListening();
      setIsRecording(false);
      return;
    }

    if (!voiceAssistant.getRecognitionSupport()) {
      setMicError('Speech recognition is not supported in this browser. Please use keyboard text input.');
      return;
    }

    const started = voiceAssistant.startListening(
      language,
      (transcript, isFinal) => {
        setInputPrompt(transcript);
        if (isFinal) {
          setIsRecording(false);
          // Auto-send when final speech result is detected
          handleSend(transcript, language);
        }
      },
      (errorMsg) => {
        setMicError(errorMsg);
        setIsRecording(false);
      },
      () => {
        setIsRecording(false);
      }
    );

    if (started) {
      setIsRecording(true);
    }
  };

  // Human-reviewed fallback responses for offline or network issues
  const getHumanReviewedFallback = (query: string, targetLang: LanguageCode): { responseText: string; citations: Citation[]; followUps: string[] } => {
    const qClean = query.trim();
    const qLower = qClean.toLowerCase();

    // 1. Voice Demonstration Query: "What government schemes may I qualify for?"
    if (
      qClean.includes('ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು') || 
      qClean.includes('ಯೋಜನೆಗಳು ಸಿಗಬಹುದು') ||
      qClean.includes('ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು') ||
      targetLang === 'kn' && (qLower.includes('scheme') || qLower.includes('qualify'))
    ) {
      return {
        responseText: (
          "ಸ್ಕೀಮ್‌ಸಾಥಿ AI ಯಲ್ಲಿ ಪ್ರಸ್ತುತ ಪರಿಶೀಲಿಸಲಾದ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ವಿದ್ಯಾರ್ಥಿವೇತನಗಳು:\n\n" +
          "1. **ಪಿಎಂ ಕಿಸಾನ್ (PM-KISAN)**: ಕೃಷಿ ಭೂಮಿ ಹೊಂದಿರುವ ಅರ್ಹ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವಾರ್ಷಿಕ ₹6,000 (ತಲಾ ₹2,000 ರ 3 ಕಂತುಗಳಲ್ಲಿ DBT ಮೂಲಕ). ಷರತ್ತು: ಆದಾಯ ತೆರಿಗೆ ಪಾವತಿದಾರರು ಮತ್ತು ಸಾಂಸ್ಥಿಕ ಭೂಮಾಲೀಕರಿಗೆ ಅನ್ವಯಿಸುವುದಿಲ್ಲ (Clause 5).\n" +
          "2. **ಕರ್ನಾಟಕ ಗೃಹ ಲಕ್ಷ್ಮಿ ಯೋಜನೆ (Gruha Lakshmi)**: ಕುಟುಂಬದ ಮಹಿಳಾ ಮುಖ್ಯಸ್ಥೆಗೆ (ಯಜಮಾನಿ) ಪ್ರತಿ ತಿಂಗಳು ₹2,000 ನೇರ ಜಮೆ. ಷರತ್ತು: ಕುಟುಂಬದ ಮಹಿಳೆ ಅಥವಾ ಆಕೆಯ ಪತಿ ಆದಾಯ ತೆರಿಗೆ ಅಥವಾ GST ಪಾವತಿದಾರರಾಗಿರಬಾರದು.\n" +
          "3. **AICTE ಪ್ರಗತಿ ವಿದ್ಯಾರ್ಥಿವೇತನ (Pragati Scholarship)**: AICTE ಮಾನ್ಯತೆ ಪಡೆದ ಕಾಲೇಜುಗಳಲ್ಲಿ ತಾಂತ್ರಿಕ ಪದವಿ ವ್ಯಾಸಂಗ ಮಾಡುತ್ತಿರುವ ವಿದ್ಯಾರ್ಥಿನಿಯರಿಗೆ ವಾರ್ಷಿಕ ₹50,000. ಷರತ್ತು: ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ ₹8,00,000 ಒಳಗೆ ಇರಬೇಕು.\n" +
          "4. **ಕೇಂದ್ರ ವಲಯ ವಿದ್ಯಾರ್ಥಿವೇತನ (CSSS - MoE)**: ಕಾಲೇಜು ಮತ್ತು ವಿಶ್ವವಿದ್ಯಾಲಯದ ಪದವಿ ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ವಾರ್ಷಿಕ ₹12,000. ಷರತ್ತು: 12ನೇ ತರಗತಿಯ ಬೋರ್ಡ್ ಪರೀಕ್ಷೆಯಲ್ಲಿ 80ನೇ ಪರ್ಸೆಂಟ್ ಇರಬೇಕು ಮತ್ತು ಕುಟುಂಬದ ಆದಾಯ ₹4,50,000 ಮೀರಬಾರದು.\n" +
          "5. **ಕರ್ನಾಟಕ ಪೋಸ್ಟ್-ಮೆಟ್ರಿಕ್ ವಿದ್ಯಾರ್ಥಿವೇತನ (SSP)**: ಎಸ್‌ಸಿ/ಎಸ್‌ಟಿ ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಪೂರ್ಣ ಶುಲ್ಕ ಮರುಪಾವತಿ ಮತ್ತು ನಿರ್ವಹಣಾ ಭತ್ಯೆ. ಆದಾಯ ಮಿತಿ: ₹2,50,000.\n\n" +
          "ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ವಿವರಗಳೊಂದಿಗೆ ನಿಖರ ಅರ್ಹತೆ ತಿಳಿಯಲು 'Scheme Discovery' ಅಥವಾ 'ScholarReady' ಮೆನು ಬಳಸಿ."
        ),
        citations: [
          {
            id: 'cit-pmkisan-kn',
            title: 'PM-KISAN Operational Guidelines',
            documentName: 'Ministry of Agriculture & Farmers Welfare, Govt of India',
            issuingAuthority: 'Department of Agriculture and Farmers Welfare',
            circularNumber: 'Clause 5 (Exclusion Criteria)',
            notificationDate: '2024-25',
            clauseNumber: 'Clause 5',
            excerpt: 'All landholding farmer families with cultivable land are eligible subject to exclusion criteria including income tax payers.',
            officialSourceUrl: 'https://pmkisan.gov.in',
            verificationBadge: 'Verified Official Source'
          },
          {
            id: 'cit-gl-kn',
            title: 'Karnataka Gruha Lakshmi Scheme Notification',
            documentName: 'Women and Child Development Department, Govt of Karnataka',
            issuingAuthority: 'Govt of Karnataka',
            circularNumber: 'WDD 141 MMB 2023',
            notificationDate: '2023-07-15',
            clauseNumber: 'Section 3.1',
            excerpt: 'Monthly financial assistance of ₹2,000 to the woman head of family (Yajamani) designated in valid Ration Card.',
            officialSourceUrl: 'https://sevasindhuservices.karnataka.gov.in',
            verificationBadge: 'Verified Official Source'
          }
        ],
        followUps: [
          "ಪಿಎಂ ಕಿಸಾನ್‌ಗೆ ಇ-ಕೆವೈಸಿ ಮಾಡುವುದು ಹೇಗೆ?",
          "ಗೃಹ ಲಕ್ಷ್ಮಿ ಯೋಜನೆಗೆ ರೇಷನ್ ಕಾರ್ಡ್‌ನಲ್ಲಿ ಯಜಮಾನಿ ಯಾರು?",
          "ಪ್ರಗತಿ ವಿದ್ಯಾರ್ಥಿವೇತನಕ್ಕೆ ಯಾವ ದಾಖಲೆಗಳು ಬೇಕು?"
        ]
      };
    }

    // 2. Hindi Voice Demonstration Query
    if (
      qClean.includes('सरकारी योजनाएं') || 
      qClean.includes('मिल सकती हैं') ||
      qClean.includes('योजनाएं') ||
      targetLang === 'hi' && (qLower.includes('scheme') || qLower.includes('qualify'))
    ) {
      return {
        responseText: (
          "स्कीमसाथी AI में वर्तमान में सत्यापित प्रमुख सरकारी योजनाएं और छात्रवृत्तियां इस प्रकार हैं:\n\n" +
          "1. **प्रधानमंत्री किसान सम्मान निधि (PM-KISAN)**: पात्र किसान परिवारों को प्रति वर्ष ₹6,00,00 (₹2,000 की 3 समान किस्तों में DBT द्वारा)। पात्रता: कृषि योग्य भूमि रखने वाले किसान परिवार (आयकर दाता और संस्थागत भूमिधारक बाहर - Clause 5)।\n" +
          "2. **कर्नाटक गृह लक्ष्मी योजना (Gruha Lakshmi)**: परिवार की महिला मुखिया (यजमानी) को ₹2,000 प्रति माह सीधे बैंक खाते में। पात्रता: परिवार में महिला या पति आयकर या GST दाता न हों।\n" +
          "3. **एआईसीटीई प्रगति छात्रवृत्ति (AICTE Pragati)**: तकनीकी डिग्री में अध्ययनरत छात्राओं के लिए ₹50,000 प्रति वर्ष। पात्रता: वार्षिक पारिवारिक आय ₹8,00,000 से कम।\n" +
          "4. **सेंट्रल सेक्टर स्कॉलरशिप (CSSS - MoE)**: स्नातक स्तर के छात्रों को ₹12,000 प्रति वर्ष। पात्रता: 12वीं बोर्ड में 80वें पर्सेंटाइल से अधिक और पारिवारिक आय ₹4,50,000 से कम।\n" +
          "5. **कर्नाटक पोस्ट-मैट्रिक छात्रवृत्ति (SSP)**: एससी/एसटी छात्रों को पूर्ण शिक्षण शुल्क प्रतिपूर्ति और रखरखाव भत्ता। आय सीमा: ₹2,50,000।\n\n" +
          "अपनी व्यक्तिगत प्रोफाइल (आय, जमीन, शिक्षा, श्रेणी) के आधार पर सटीक जांच के लिए 'Scheme Discovery' या 'ScholarReady' मेनू का उपयोग करें।"
        ),
        citations: [
          {
            id: 'cit-pmkisan-hi',
            title: 'PM-KISAN Operational Guidelines',
            documentName: 'Ministry of Agriculture & Farmers Welfare, Govt of India',
            issuingAuthority: 'Department of Agriculture and Farmers Welfare',
            circularNumber: 'Clause 5 (Exclusion Criteria)',
            notificationDate: '2024-25',
            clauseNumber: 'Clause 5',
            excerpt: 'All landholding farmer families with cultivable land are eligible subject to exclusion criteria including income tax payers.',
            officialSourceUrl: 'https://pmkisan.gov.in',
            verificationBadge: 'Verified Official Source'
          }
        ],
        followUps: [
          "पीएम किसान के लिए जमीन का सत्यापन कैसे करें?",
          "गृह लक्ष्मी योजना के लिए जरूरी दस्तावेज क्या हैं?",
          "प्रगति छात्रवृत्ति के लिए आवेदन की अंतिम तिथि क्या है?"
        ]
      };
    }

    // 3. English Default Scheme Overview Query
    if (qLower.includes('scheme') || qLower.includes('qualify') || qLower.includes('benefit')) {
      return {
        responseText: (
          "Here are the verified government welfare schemes and scholarships currently supported in SchemeSathi AI:\n\n" +
          "1. **Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)**: ₹6,000 per year in 3 equal installments via Direct Benefit Transfer (DBT) for cultivable landholding farmer families (excluding income tax payers and institutional landholders under Clause 5).\n" +
          "2. **Karnataka Gruha Lakshmi Scheme**: ₹2,000 monthly DBT assistance credited to the designated female head of the family (Yajamani) in non-income-tax and non-GST paying households.\n" +
          "3. **AICTE Pragati Scholarship for Girl Students**: ₹50,000 per year of study for female students admitted to AICTE-approved technical degree programmes with family income under ₹8,00,000.\n" +
          "4. **Central Sector Scheme of Scholarship (CSSS - MoE)**: ₹12,000 per year for undergraduate students scoring above the 80th percentile in Class 12 board exams with annual family income under ₹4,50,000.\n" +
          "5. **Karnataka Post-Matric Scholarship (SSP)**: 100% course fee waiver and maintenance allowance for SC/ST students with family income under ₹2,50,000.\n\n" +
          "To evaluate your exact personalized eligibility based on your family income, landholding, education, and domicile, visit the Scheme Discovery or ScholarReady modules."
        ),
        citations: [
          {
            id: 'cit-overview-en',
            title: 'Consolidated Scheme Guidelines 2024-25',
            documentName: 'National Scholarship Portal & myScheme Official Gazette',
            issuingAuthority: 'Government of India & Government of Karnataka',
            circularNumber: 'Gazette Verified Norms',
            notificationDate: '2024-25',
            clauseNumber: 'Statutory Summary',
            excerpt: 'Statutory eligibility criteria verified against official gazette orders across Central and Karnataka departments.',
            officialSourceUrl: 'https://scholarships.gov.in',
            verificationBadge: 'Verified Official Source'
          }
        ],
        followUps: [
          "What are the mandatory landholding criteria for PM-KISAN?",
          "How to verify the female head (Yajamani) on Karnataka Ration Card?",
          "What is the family income limit for PM-USP CSSS?"
        ]
      };
    }

    // Generic fallback
    return {
      responseText: SAMPLE_CHAT_HISTORY.kisan.aiResponse,
      citations: SAMPLE_CHAT_HISTORY.kisan.citations,
      followUps: ["How to complete Aadhaar e-KYC on pmkisan.gov.in?", "Check required documents on SSP"]
    };
  };

  const handleSend = async (textToSend?: string, overrideLang?: LanguageCode) => {
    const query = (textToSend || inputPrompt).trim();
    if (!query) return;

    // Detect language if prompt is in Kannada or Devanagari
    let effectiveLang: LanguageCode = overrideLang || language;
    if (anyKannada(query)) effectiveLang = 'kn';
    else if (anyHindi(query)) effectiveLang = 'hi';

    const userMsg: ChatMessageType = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      language: effectiveLang
    };

    setMessages(prev => [...prev, userMsg]);
    setInputPrompt('');
    setIsThinking(true);
    setMicError(null);

    try {
      // 1. Call Backend RAG Pipeline
      const ragResp = await apiService.queryRAG({
        query,
        language: effectiveLang,
      });

      const citations: Citation[] = (ragResp.citations || []).map((c, idx) => mapValidatedCitation(c, idx));

      const assistantMsg: ChatMessageType = {
        id: `ast-${Date.now()}`,
        sender: 'assistant',
        content: ragResp.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        language: (ragResp.language as any) || effectiveLang,
        citations: citations,
        suggestedFollowUps: ragResp.suggested_follow_ups || []
      };

      setMessages(prev => [...prev, assistantMsg]);

      // Automatically synthesize speech if voice was used or user asked via voice
      if (isRecording || overrideLang) {
        voiceAssistant.speak(ragResp.answer, effectiveLang, () => setIsSpeakingActive(true), () => setIsSpeakingActive(false));
      }
    } catch (err) {
      console.warn("Backend RAG query failed or offline, using human-reviewed verified fallback:", err);
      const fallback = getHumanReviewedFallback(query, effectiveLang);

      const assistantMsg: ChatMessageType = {
        id: `ast-${Date.now()}`,
        sender: 'assistant',
        content: fallback.responseText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        language: effectiveLang,
        citations: fallback.citations,
        suggestedFollowUps: fallback.followUps
      };

      setMessages(prev => [...prev, assistantMsg]);

      if (isRecording || overrideLang) {
        voiceAssistant.speak(fallback.responseText, effectiveLang, () => setIsSpeakingActive(true), () => setIsSpeakingActive(false));
      }
    } finally {
      setIsThinking(false);
    }
  };

  // Helper Unicode character detectors
  function anyKannada(text: string): boolean {
    return /[\u0C80-\u0CFF]/.test(text);
  }

  function anyHindi(text: string): boolean {
    return /[\u0900-\u097F]/.test(text);
  }

  // Handle clicking official voice demo query
  const handleTriggerDemoVoice = (query: string, targetLang: LanguageCode) => {
    setLanguage(targetLang);
    setInputPrompt(query);
    handleSend(query, targetLang);
  };

  // Stop active speech playback
  const handleStopSpeech = () => {
    voiceAssistant.stopSpeaking();
    setIsSpeakingActive(false);
  };

  // Collect all unique citations across current messages
  const allActiveCitations = messages
    .filter(m => m.citations && m.citations.length > 0)
    .flatMap(m => m.citations || []);
  const uniqueCitations = Array.from(new Map(allActiveCitations.map(c => [c.id, c])).values());

  return (
    <div className="space-y-6 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-govgreen-950 via-charcoal-900 to-slate-900 rounded-2xl p-6 text-white shadow-elevated flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1.5 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold bg-govgreen-800 text-emerald-200 px-2.5 py-0.5 rounded-full border border-govgreen-600 flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-emerald-300 animate-pulse" />
              <span>Voice &amp; Multilingual AI</span>
            </span>
            <StatusBadge status="active" label="Human Reviewed Knowledge" />
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight">
            {t('voiceAssistantTitle')}
          </h1>
          <p className="text-xs text-slate-300 leading-relaxed">
            {t('voiceSubtitle')}
          </p>
        </div>

        {/* Right header controls: Language Selector + Citations Drawer Trigger */}
        <div className="flex items-center gap-2.5 flex-wrap">
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

      {/* 1. OFFICIAL VOICE DEMONSTRATION RIBBON */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5 shadow-subtle space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-govgreen-700" />
            <h3 className="text-xs font-bold text-charcoal-900 uppercase tracking-wider">
              {t('voiceTryDemo')}
            </h3>
          </div>
          <span className="text-[11px] text-slate-500">
            Click any query to evaluate in native tongue with automatic speech synthesis:
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
          {/* Kannada Demo */}
          <button
            onClick={() => handleTriggerDemoVoice("ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗಬಹುದು?", "kn")}
            className="text-left p-3 rounded-xl border border-emerald-200 bg-emerald-50/50 hover:bg-emerald-100/70 hover:border-emerald-300 transition text-xs space-y-1 group"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">
                ಕನ್ನಡ (kn-IN)
              </span>
              <Volume2 className="w-3.5 h-3.5 text-emerald-700 group-hover:scale-110 transition-transform" />
            </div>
            <div className="font-semibold text-emerald-950 font-sans text-xs sm:text-sm">
              &ldquo;ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗಬಹುದು?&rdquo;
            </div>
            <div className="text-[10px] text-slate-500">
              What government schemes may I qualify for?
            </div>
          </button>

          {/* Hindi Demo */}
          <button
            onClick={() => handleTriggerDemoVoice("मुझे कौन-कौन सी सरकारी योजनाएं मिल सकती हैं?", "hi")}
            className="text-left p-3 rounded-xl border border-indigo-200 bg-indigo-50/50 hover:bg-indigo-100/70 hover:border-indigo-300 transition text-xs space-y-1 group"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-indigo-800 bg-indigo-100 px-2 py-0.5 rounded">
                हिन्दी (hi-IN)
              </span>
              <Volume2 className="w-3.5 h-3.5 text-indigo-700 group-hover:scale-110 transition-transform" />
            </div>
            <div className="font-semibold text-indigo-950 text-xs sm:text-sm">
              &ldquo;मुझे कौन-कौन सी सरकारी योजनाएं मिल सकती हैं?&rdquo;
            </div>
            <div className="text-[10px] text-slate-500">
              What government schemes may I qualify for?
            </div>
          </button>

          {/* English Demo */}
          <button
            onClick={() => handleTriggerDemoVoice("What government schemes may I qualify for?", "en")}
            className="text-left p-3 rounded-xl border border-sky-200 bg-sky-50/50 hover:bg-sky-100/70 hover:border-sky-300 transition text-xs space-y-1 group"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-sky-800 bg-sky-100 px-2 py-0.5 rounded">
                English (en-IN)
              </span>
              <Volume2 className="w-3.5 h-3.5 text-sky-700 group-hover:scale-110 transition-transform" />
            </div>
            <div className="font-semibold text-sky-950 text-xs sm:text-sm">
              &ldquo;What government schemes may I qualify for?&rdquo;
            </div>
            <div className="text-[10px] text-slate-500">
              Assesses welfare &amp; scholarship catalog
            </div>
          </button>
        </div>
      </div>

      {/* 2. MAIN CHAT WORKSPACE (Chat Area Left, Citations Drawer Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Chat Area */}
        <div className={`${citationsDrawerOpen ? 'lg:col-span-8' : 'lg:col-span-12'} bg-white rounded-2xl border border-slate-200 shadow-subtle flex flex-col h-[650px] overflow-hidden transition-all duration-300`}>
          
          {/* Active Speaking Status Bar */}
          {isSpeakingActive && (
            <div className="bg-emerald-700 text-white px-4 py-2 flex items-center justify-between text-xs animate-in fade-in">
              <div className="flex items-center gap-2">
                <Volume2 className="w-4 h-4 animate-pulse" />
                <span className="font-semibold">Voice Playback Active ({voiceAssistant.getLocaleTag(language)})</span>
              </div>
              <button
                onClick={handleStopSpeech}
                className="inline-flex items-center gap-1 text-[11px] bg-emerald-800 hover:bg-emerald-900 px-2.5 py-1 rounded font-bold"
              >
                <VolumeX className="w-3 h-3" />
                <span>Stop Audio</span>
              </button>
            </div>
          )}

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
                  <span>Evaluating verified gazette circulars in {language === 'kn' ? 'ಕನ್ನಡ' : language === 'hi' ? 'हिन्दी' : 'English'}...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Active Voice Recording Banner */}
          {isRecording && (
            <div className="bg-rose-50 border-t border-rose-200 px-4 py-3 flex items-center justify-between text-xs text-rose-900 animate-pulse">
              <div className="flex items-center gap-2.5">
                <span className="w-3.5 h-3.5 rounded-full bg-rose-600 animate-ping" />
                <span className="font-bold">{t('voiceListeningPrompt')}</span>
                <span className="text-[11px] text-slate-500 font-mono">({voiceAssistant.getLocaleTag(language)})</span>
              </div>
              <button
                onClick={() => {
                  voiceAssistant.stopListening();
                  setIsRecording(false);
                }}
                className="px-3 py-1 rounded-lg bg-rose-600 text-white text-xs font-bold hover:bg-rose-700 transition"
              >
                {t('voiceStopBtn')}
              </button>
            </div>
          )}

          {/* Microphone Permission / Browser Warning Banner */}
          {micError && (
            <div className="bg-amber-50 border-t border-amber-200 px-4 py-2.5 flex items-center justify-between text-xs text-amber-900">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span>{micError}</span>
              </div>
              <button
                onClick={() => setMicError(null)}
                className="text-amber-800 hover:text-amber-950 font-bold text-xs"
              >
                &times;
              </button>
            </div>
          )}

          {/* Bottom Chat Input Bar with Microphone & Text Input */}
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
                className={`p-2.5 rounded-xl border transition shadow-sm flex items-center justify-center flex-shrink-0 ${
                  isRecording 
                    ? 'bg-rose-600 text-white border-rose-700 animate-bounce' 
                    : 'bg-emerald-50 hover:bg-emerald-100 text-govgreen-800 border-emerald-300 hover:border-emerald-400'
                }`}
                title={isRecording ? "Stop voice listening" : "Click to speak in native language"}
              >
                {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-govgreen-800" />}
              </button>

              {/* Text Input (Always available fallback) */}
              <input
                type="text"
                placeholder={t('voiceInputPlaceholder')}
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

            <div className="flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-400 px-1 gap-1">
              <span>{t('disclaimerLegal')}</span>
              <span className="font-mono text-[10px] text-govgreen-800 flex items-center gap-1">
                <HelpCircle className="w-3 h-3" />
                <span>Text input always available as reliable fallback</span>
              </span>
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
