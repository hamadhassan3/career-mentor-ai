import { useState } from 'react';
import Header from '../components/Header.jsx';
import Dashboard from '../components/Dashboard.jsx';
import ResumeHistory from '../components/ResumeHistory.jsx';

export default function MainApp() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleResumeSelect = () => {
    setActiveTab('dashboard');
  };

  const handleUploadNew = () => {
    setActiveTab('dashboard');
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
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
        return <div className="text-center py-12 text-gray-500">Progress tab coming soon...</div>;
      case 'events':
        return <div className="text-center py-12 text-gray-500">Events tab coming soon...</div>;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 md:py-8">
        {renderActiveTab()}
      </main>
    </div>
  );
}