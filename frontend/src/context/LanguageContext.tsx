import React, { createContext, useContext, useState } from 'react';
import { LanguageCode, LanguageOption } from '../types';

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'en', label: 'English', nativeLabel: 'English' },
  { code: 'kn', label: 'Kannada', nativeLabel: 'ಕನ್ನಡ' },
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी' },
  { code: 'te', label: 'Telugu', nativeLabel: 'తెలుగు' },
  { code: 'ta', label: 'Tamil', nativeLabel: 'தமிழ்' },
  { code: 'mr', label: 'Marathi', nativeLabel: 'मराठी' }
];

interface LanguageContextType {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  t: (key: string) => string;
}

const UI_TRANSLATIONS: Record<LanguageCode, Record<string, string>> = {
  en: {
    appTitle: 'SchemeSathi AI',
    tagline: 'Understand Your Rights. Discover Your Benefits. Apply with Confidence.',
    navDashboard: 'Dashboard',
    navScholarReady: 'ScholarReady',
    navSchemes: 'Scheme Discovery',
    navExplainer: 'Policy Explainer',
    navAssistant: 'AI Assistant',
    navDocIntel: 'Document Intelligence',
    navAbout: 'About',
    btnExplore: 'Explore Schemes',
    btnScholarReady: 'Check Scholarship Readiness',
    btnAskAI: 'Ask SchemeSathi AI',
    btnUploadDoc: 'Upload Circular / PDF',
    demoNotice: 'Demonstration Mode: Showing simulated data for interface design evaluation. Not an official government record.',
    searchPlaceholder: 'Search government schemes, scholarships, keywords, or departments...',
    filterByCategory: 'Category',
    filterByState: 'Region / State',
    filterByIncome: 'Max Family Income',
    allCategories: 'All Categories',
    allStates: 'All States / Central',
    verifiedCitations: 'Source Grounded Official Citations',
    applicationReadiness: 'Application Readiness Score',
    missingDocs: 'Missing Required Documents',
    readyToApply: 'Ready to Apply'
  },
  kn: {
    appTitle: 'ಸ್ಕೀಮ್‌ಸಾಥಿ AI',
    tagline: 'ನಿಮ್ಮ ಹಕ್ಕುಗಳನ್ನು ಅರಿಯಿರಿ. ಸವಲತ್ತುಗಳನ್ನು ಶೋಧಿಸಿ. ಆತ್ಮವಿಶ್ವಾಸದಿಂದ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.',
    navDashboard: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
    navScholarReady: 'ವಿದ್ಯಾರ್ಥಿವೇತನ ಸಿದ್ಧತೆ',
    navSchemes: 'ಯೋಜನೆಗಳ ಶೋಧನೆ',
    navExplainer: 'ನೀತಿ ವಿವರಣೆಗಾರ',
    navAssistant: 'AI ಸಹಾಯಕ',
    navDocIntel: 'ದಾಖಲೆ ವಿಶ್ಲೇಷಣೆ',
    navAbout: 'ನಮ್ಮ ಬಗ್ಗೆ',
    btnExplore: 'ಯೋಜನೆಗಳನ್ನು ನೋಡಿ',
    btnScholarReady: 'ವಿದ್ಯಾರ್ಥಿವೇತನ ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ',
    btnAskAI: 'ಸ್ಕೀಮ್‌ಸಾಥಿ AI ಯನ್ನು ಕೇಳಿ',
    btnUploadDoc: 'ಸುತ್ತೋಲೆ / PDF ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
    demoNotice: 'ಪ್ರಾಯೋಗಿಕ ಮಾದರಿ: ಇಂಟರ್‌ಫೇಸ್ ವಿನ್ಯಾಸ ಮೌಲ್ಯಮಾಪನಕ್ಕಾಗಿ ನಕಲಿ ಡೇಟಾವನ್ನು ಪ್ರದರ್ಶಿಸಲಾಗುತ್ತಿದೆ. ಇದು ಅಧಿಕೃತ ಸರ್ಕಾರಿ ದಾಖಲೆಯಲ್ಲ.',
    searchPlaceholder: 'ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ವಿದ್ಯಾರ್ಥಿವೇತನ ಅಥವಾ ಕೀವರ್ಡ್ ಹುಡುಕಿ...',
    filterByCategory: 'ವರ್ಗ',
    filterByState: 'ರಾಜ್ಯ / ಕೇಂದ್ರ',
    filterByIncome: 'ಗರಿಷ್ಠ ಕುಟುಂಬ ವಾರ್ಷಿಕ ಆದಾಯ',
    allCategories: 'ಎಲ್ಲಾ ವರ್ಗಗಳು',
    allStates: 'ಎಲ್ಲಾ ರಾಜ್ಯಗಳು / ಕೇಂದ್ರ',
    verifiedCitations: 'ಅಧಿಕೃತ ಗೆಜೆಟ್ ಆಧಾರಿತ ಉಲ್ಲೇಖಗಳು',
    applicationReadiness: 'ಅರ್ಜಿ ಸಿದ್ಧತಾ ಸ್ಕೋರ್',
    missingDocs: 'ಬಾಕಿ ಇರುವ ಅಗತ್ಯ ದಾಖಲೆಗಳು',
    readyToApply: 'ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಸಿದ್ಧವಾಗಿದೆ'
  },
  hi: {
    appTitle: 'स्कीमसाथी AI',
    tagline: 'अपने अधिकार समझें। लाभ खोजें। आत्मविश्वास से आवेदन करें।',
    navDashboard: 'डैशबोर्ड',
    navScholarReady: 'स्कॉलर-रेडी',
    navSchemes: 'कल्याणकारी योजनाएं',
    navExplainer: 'नीति विश्लेषक',
    navAssistant: 'AI सहायक',
    navDocIntel: 'दस्तावेज़ विश्लेषण',
    navAbout: 'हमारे बारे में',
    btnExplore: 'योजनाएं खोजें',
    btnScholarReady: 'छात्रवृत्ति पात्रता जांचें',
    btnAskAI: 'स्कीमसाथी AI से पूछें',
    btnUploadDoc: 'सरकारी परिपत्र / PDF अपलोड करें',
    demoNotice: 'डेमो मोड: इंटरफ़ेस मूल्यांकन के लिए सिम्युलेटेड डेटा दिखाया जा रहा है। यह आधिकारिक सरकारी रिकॉर्ड नहीं है।',
    searchPlaceholder: 'सरकारी योजनाएं, छात्रवृत्तियां या विभाग खोजें...',
    filterByCategory: 'श्रेणी',
    filterByState: 'राज्य / केंद्र',
    filterByIncome: 'अधिकतम पारिवारिक आय',
    allCategories: 'सभी श्रेणियां',
    allStates: 'सभी राज्य / केंद्र',
    verifiedCitations: 'सत्यापित आधिकारिक उद्धरण',
    applicationReadiness: 'आवेदन तत्परता स्कोर',
    missingDocs: 'आवश्यक लंबित दस्तावेज़',
    readyToApply: 'आवेदन के लिए तैयार'
  },
  te: {
    appTitle: 'స్కీమ్‌సాథి AI',
    tagline: 'మీ హక్కులను అర్థం చేసుకోండి. ప్రయోజనాలను పొందండి. నమ్మకంతో దరఖాస్తు చేయండి.',
    navDashboard: 'డ్యాష్‌బోర్డ్',
    navScholarReady: 'స్కాలర్‌రెడీ',
    navSchemes: 'పథకాల శోధన',
    navExplainer: 'విధాన వివరణ',
    navAssistant: 'AI సహాయకుడు',
    navDocIntel: 'డాక్యుమెంట్ మేధస్సు',
    navAbout: 'గురించి',
    btnExplore: 'పథకాలను చూడండి',
    btnScholarReady: 'స్కాలర్‌షిప్ అర్హత తనిఖీ',
    btnAskAI: 'స్కీమ్‌సాథి AI ని అడగండి',
    btnUploadDoc: 'PDF అప్‌లోడ్ చేయండి',
    demoNotice: 'డెమో మోడ్: ఇంటర్‌ఫేస్ రూపకల్పన కోసం నమూనా డేటా. అధికారిక ప్రభుత్వ సమాచారం కాదు.',
    searchPlaceholder: 'పథకాలు, స్కాలర్‌షిప్‌లు శోధించండి...',
    filterByCategory: 'వర్గం',
    filterByState: 'రాష్ట్రం / కేంద్రం',
    filterByIncome: 'గరిష్ట ఆదాయం',
    allCategories: 'అన్ని వర్గాలు',
    allStates: 'అన్ని రాష్ట్రాలు',
    verifiedCitations: 'అధికారిక ఆధారాలు',
    applicationReadiness: 'దరఖాస్తు సంసిద్ధత స్కోర్',
    missingDocs: 'పెండింగ్ పత్రాలు',
    readyToApply: 'దరఖాస్తుకు సిద్ధంగా ఉంది'
  },
  ta: {
    appTitle: 'ஸ்கீம்சாதி AI',
    tagline: 'உங்கள் உரிமைகளைப் புரிந்து கொள்ளுங்கள். நன்மைகளைக் கண்டறியுங்கள். நம்பிக்கையுடன் விண்ணப்பியுங்கள்.',
    navDashboard: 'முகப்பு',
    navScholarReady: 'ஸ்காலர்-ரெடி',
    navSchemes: 'திட்டங்கள்',
    navExplainer: 'கொள்கை விளக்கம்',
    navAssistant: 'AI உதவியாளர்',
    navDocIntel: 'ஆவண நுண்ணறிவு',
    navAbout: 'பற்றி',
    btnExplore: 'திட்டங்களை ஆராய்க',
    btnScholarReady: 'உதவித்தொகை தகுதி சரிபார்ப்பு',
    btnAskAI: 'ஸ்கீம்சாதி AI யிடம் கேட்கவும்',
    btnUploadDoc: 'சுற்றறிக்கை பதிவேற்றவும்',
    demoNotice: 'டெமோ பயன்முறை: இடைமுக மதிப்பீட்டிற்கான மாதிரி தரவு. உத்தியோகபூர்வ அரசு தகவல் அல்ல.',
    searchPlaceholder: 'அரசு திட்டங்கள், உதவித்தொகைகளைத் தேடுங்கள்...',
    filterByCategory: 'பிரிவு',
    filterByState: 'மாநிலம் / மத்திய',
    filterByIncome: 'வருமான வரம்பு',
    allCategories: 'அனைத்து பிரிவுகள்',
    allStates: 'அனைத்து மாநிலங்கள்',
    verifiedCitations: 'உத்தியோகபூர்வ மேற்கோள்கள்',
    applicationReadiness: 'விண்ணப்ப தயார்நிலை',
    missingDocs: 'தேவையான ஆவணங்கள்',
    readyToApply: 'விண்ணப்பிக்க தயார்'
  },
  mr: {
    appTitle: 'स्कीमसाथी AI',
    tagline: 'आपले हक्क समजून घ्या. योजनांचे लाभ शोधा. आत्मविश्वासाने अर्ज करा.',
    navDashboard: 'डॅशबोर्ड',
    navScholarReady: 'स्कॉलर-रेडी',
    navSchemes: 'योजना शोध',
    navExplainer: 'धोरण स्पष्टीकरण',
    navAssistant: 'AI सहाय्यक',
    navDocIntel: 'दस्तऐवज विश्लेषण',
    navAbout: 'माहिती',
    btnExplore: 'योजना पहा',
    btnScholarReady: 'शिष्यवृत्ती पात्रता तपासा',
    btnAskAI: 'स्कीमसाथी AI ला विचारा',
    btnUploadDoc: 'परिपत्रक अपलोड करा',
    demoNotice: 'डेमो मोड: इंटरफेस मूल्यांकनासाठी नमुना डेटा. अधिकृत सरकारी रेकॉर्ड नाही.',
    searchPlaceholder: 'सरकारी योजना, शिष्यवृत्ती शोधा...',
    filterByCategory: 'प्रवर्ग',
    filterByState: 'राज्य / केंद्र',
    filterByIncome: 'कौटुंबिक उत्पन्न',
    allCategories: 'सर्व प्रवर्ग',
    allStates: 'सर्व राज्ये',
    verifiedCitations: 'अधिकृत सरकारी संदर्भ',
    applicationReadiness: 'अर्ज सिद्धता स्कोअर',
    missingDocs: 'प्रलंबित आवश्यक कागदपत्रे',
    readyToApply: 'अर्जासाठी सज्ज'
  }
};

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<LanguageCode>('en');

  const t = (key: string): string => {
    return UI_TRANSLATIONS[language]?.[key] || UI_TRANSLATIONS['en']?.[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
