import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import { AppLayout } from './components/layout/AppLayout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ScholarReadyPage } from './pages/ScholarReadyPage';
import { SchemeDiscoveryPage } from './pages/SchemeDiscoveryPage';
import { PolicyExplainerPage } from './pages/PolicyExplainerPage';
import { AIAssistantPage } from './pages/AIAssistantPage';
import { DocumentIntelligencePage } from './pages/DocumentIntelligencePage';
import { AboutPage } from './pages/AboutPage';
import { apiService } from './services/api';

export default function App() {
  useEffect(() => {
    // Non-blocking background health check
    apiService.checkHealth().catch(() => {});
  }, []);

  return (
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/scholar-ready" element={<ScholarReadyPage />} />
            <Route path="/schemes" element={<SchemeDiscoveryPage />} />
            <Route path="/policy-explainer" element={<PolicyExplainerPage />} />
            <Route path="/assistant" element={<AIAssistantPage />} />
            <Route path="/document-intelligence" element={<DocumentIntelligencePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  );
}
