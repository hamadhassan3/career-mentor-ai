import { useState } from 'react';
import Dashboard from '../components/Dashboard.jsx';
import ResumeHistory from '../components/ResumeHistory.jsx';
import ProgressTree from '../components/ProgressTree.jsx';

export default function MainApp({ activeTab, onTabChange }) {
  const [shouldShowUpload, setShouldShowUpload] = useState(false);

  const handleResumeSelect = () => {
    setShouldShowUpload(false);
    onTabChange('dashboard');
  };

  const handleUploadNew = () => {
    setShouldShowUpload(true);
    onTabChange('dashboard');
  };

  const handleBackToHistory = () => {
    setShouldShowUpload(false);
    onTabChange('history');
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard shouldShowUpload={shouldShowUpload} onUploadStateChange={setShouldShowUpload} onBackToHistory={handleBackToHistory} onNavigateToProgress={() => onTabChange('progress')} />;
      case 'history':
        return (
          <div className="flex justify-center items-start min-h-[65vh] animate-fade-in">
            <ResumeHistory 
              onResumeSelect={handleResumeSelect} 
              onUploadNew={handleUploadNew} 
            />
          </div>
        );
      case 'progress':
        return (
          <div className="flex justify-center items-start min-h-[65vh] animate-fade-in">
            <ProgressTree />
          </div>
        );
      case 'events':
        return <div className="text-center py-12 text-gray-500">Events tab coming soon...</div>;
      default:
        return <Dashboard shouldShowUpload={shouldShowUpload} onUploadStateChange={setShouldShowUpload} onBackToHistory={handleBackToHistory} onNavigateToProgress={() => onTabChange('progress')} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 md:py-8">
        {renderActiveTab()}
      </main>
    </div>
  );
}