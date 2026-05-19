import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Logo from './Logo';
import UserAvatar from './UserAvatar';

const tabs = [
  { id: 'dashboard', name: 'Dashboard', icon: '📊' },
  { id: 'history', name: 'History', icon: '📝' },
  { id: 'progress', name: 'My Progress', icon: '🌳' },
  // { id: 'events', name: 'Events', icon: '📅' },
];

export default function Header({ activeTab, onTabChange, showTabs = true }) {
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const TabButton = ({ tab, isActive }) => (
    <button
      key={tab.id}
      onClick={() => {
        onTabChange?.(tab.id);
        setShowDropdown(false);
      }}
      className={`px-3 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-2 ${
        isActive
          ? 'bg-indigo-100 text-indigo-600'
          : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
      }`}
    >
      <span>{tab.name}</span>
    </button>
  );

  const logoElement = (
    <Link to="/" className="flex items-center gap-3 flex-shrink-0">
      <Logo size="header" title={process.env.REACT_APP_NAME} />
      <span className="text-xl font-bold text-gray-900 tracking-tight hidden sm:inline">{process.env.REACT_APP_NAME}</span>
    </Link>
  );

  const currentTab = tabs.find(tab => tab.id === activeTab) || tabs[0];

  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-gray-100 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        {logoElement}
        
        <div className="flex items-center gap-3 flex-shrink-0">
          {showTabs && (
            <>
              {/* Desktop: Show all tabs */}
              <div className="hidden md:flex items-center gap-2">
                {tabs.map(tab => (
                  <TabButton key={tab.id} tab={tab} isActive={activeTab === tab.id} />
                ))}
              </div>

              {/* Mobile: Single dropdown with current tab */}
              <div className="relative md:hidden" ref={dropdownRef}>
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="px-3 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-2 bg-indigo-100 text-indigo-600"
                >
                  <span className="text-sm">{currentTab.icon}</span>
                  <span>{currentTab.name}</span>
                  <svg className={`w-4 h-4 transition-transform ${showDropdown ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {showDropdown && (
                  <div className="absolute top-full right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    {tabs.map(tab => (
                      <button
                        key={tab.id}
                        onClick={() => {
                          onTabChange?.(tab.id);
                          setShowDropdown(false);
                        }}
                        className={`w-full text-left px-4 py-2 text-sm transition-colors flex items-center gap-3 ${
                          activeTab === tab.id
                            ? 'bg-indigo-50 text-indigo-600'
                            : 'text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <span>{tab.icon}</span>
                        <span>{tab.name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}

          <UserAvatar />
        </div>
      </div>
    </header>
  );
}