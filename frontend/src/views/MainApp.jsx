import { useState } from 'react';
import Header from '../components/Header.jsx';
import Dashboard from '../components/Dashboard.jsx';

export default function MainApp() {
  // const [activeTab, setActiveTab] = useState('dashboard');

  // const renderActiveTab = () => {
  //   switch (activeTab) {
  //     case 'dashboard':
  //       return <Dashboard />;
  //     // Future tabs can be added here
  //     // case 'analytics':
  //     //   return <Analytics />;
  //     // case 'settings':
  //     //   return <Settings />;
  //     default:
  //       return <Dashboard />;
  //   }
  // };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      {/* Tab Navigation - Ready for future tabs */}
      {/* 
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex space-x-8">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'dashboard' 
                  ? 'border-indigo-500 text-indigo-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Dashboard
            </button>
            // Add more tabs here
          </div>
        </div>
      </nav>
      */}

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 md:py-8">
        <Dashboard />
      </main>
    </div>
  );
}