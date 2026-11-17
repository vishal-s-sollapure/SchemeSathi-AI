import { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import { AppLayout } from './components/layout/AppLayout';
import { LandingPage } from './pages/LandingPage';
import { apiService } from './services/api';

// Code-split route components for optimized bundle performance & fast initial paint
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const ScholarReadyPage = lazy(() => import('./pages/ScholarReadyPage').then(m => ({ default: m.ScholarReadyPage })));
const SchemeDiscoveryPage = lazy(() => import('./pages/SchemeDiscoveryPage').then(m => ({ default: m.SchemeDiscoveryPage })));
const PolicyExplainerPage = lazy(() => import('./pages/PolicyExplainerPage').then(m => ({ default: m.PolicyExplainerPage })));
const AIAssistantPage = lazy(() => import('./pages/AIAssistantPage').then(m => ({ default: m.AIAssistantPage })));
const DocumentIntelligencePage = lazy(() => import('./pages/DocumentIntelligencePage').then(m => ({ default: m.DocumentIntelligencePage })));
const AboutPage = lazy(() => import('./pages/AboutPage').then(m => ({ default: m.AboutPage })));

function PageLoadingFallback() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] py-12" role="status" aria-live="polite">
      <div className="animate-spin rounded-full h-10 w-10 border-4 border-emerald-600 border-t-transparent mb-3" />
      <p className="text-gray-600 text-sm font-medium">Loading SchemeSathi AI module...</p>
    </div>
  );
}

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
            <Route
              path="/dashboard"
              element={
                <Suspense fallback={<PageLoadingFallback />}>
                  <DashboardPage />
                </Suspense>
              }
            />
            <Route
              path="/scholar-ready"
              element={
                <Suspense fallback={<PageLoadingFallback />}>
                  <ScholarReadyPage />
                </Suspense>
              }
            />
            <Route
              path="/schemes"
              element={
                <Suspense fallback={<PageLoadingFallback />}>
                  <SchemeDiscoveryPage />
                </Suspense>
              }
            />
            <Route
              path="/policy-explainer"
              element={
                <Suspense fallback={<PageLoadingFallback />}>
                  <PolicyExplainerPage />
                </Suspense>
              }
            />
            <Route
              path="/assistant"
              element={
                <Suspense fallback={<PageLoadingFallback />}>
                  <AIAssistantPage />
                </Suspense>
              }
            />
            <Route
              path="/document-intelligence"
              element={
                <Suspense fallback={<PageLoadingFallback />}>
                  <DocumentIntelligencePage />
                </Suspense>
              }
            />
            <Route
              path="/about"
              element={
                <Suspense fallback={<PageLoadingFallback />}>
                  <AboutPage />
                </Suspense>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  );
}
