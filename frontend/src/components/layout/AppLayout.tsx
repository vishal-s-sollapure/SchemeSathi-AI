import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';
import { DemoBanner } from '../common/DemoBanner';

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-charcoal-900 selection:bg-govgreen-100 selection:text-govgreen-900">
      {/* Explicit Top Demo Notice */}
      <DemoBanner />

      {/* Main Top Navigation */}
      <Navbar />

      {/* Page Body Container */}
      {isLandingPage ? (
        // Full width container for Landing page
        <div className="flex-1 flex flex-col">
          <Outlet />
          <Footer />
        </div>
      ) : (
        // App container with Sidebar for internal workspace
        <div className="flex-1 flex flex-col">
          <div className="flex-1 flex max-w-7xl w-full mx-auto">
            {/* Collapsible Civic Sidebar */}
            <Sidebar />

            {/* Main Content Area */}
            <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0 overflow-y-auto">
              <Outlet />
            </main>
          </div>

          <Footer />
        </div>
      )}
    </div>
  );
};
