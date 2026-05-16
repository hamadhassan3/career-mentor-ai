import { useState, useEffect } from 'react';
import { nudgeAPI } from '../config/api-backend';
import ReactMarkdown from 'react-markdown';

const DailyNudge = () => {
  const [nudge, setNudge] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState(null);

  const avatarName = process.env.REACT_APP_AVATAR_NAME || 'Fawkes';

  const loadNudge = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await nudgeAPI.getNudge();
      setNudge(response.data);
    } catch (err) {
      console.error('Error loading nudge:', err);
      setError('Failed to load your daily motivation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const regenerateNudge = async () => {
    setIsRegenerating(true);
    setError(null);
    
    try {
      const response = await nudgeAPI.regenerateNudge();
      setNudge(response.data);
    } catch (err) {
      console.error('Error regenerating nudge:', err);
      setError('Failed to generate new motivation. Please try again.');
    } finally {
      setIsRegenerating(false);
    }
  };

  useEffect(() => {
    loadNudge();
  }, []);

  if (isLoading) {
    return (
      <div className="card p-5">
        <div className="mb-5">
          <h3 className="text-lg font-semibold text-gray-900">Daily Motivation</h3>
          <p className="text-xs text-gray-400 mt-0.5">Your personalized career nudge</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-full overflow-hidden bg-indigo-100 flex-shrink-0 flex items-center justify-center">
            <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div className="flex-1">
            <div className="bg-gray-200 rounded h-5 animate-pulse mb-2"></div>
            <div className="bg-gray-100 rounded h-4 animate-pulse w-3/4"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !nudge) {
    return (
      <div className="card p-5">
        <div className="mb-5">
          <h3 className="text-lg font-semibold text-gray-900">Daily Motivation</h3>
          <p className="text-xs text-gray-400 mt-0.5">Your personalized career nudge</p>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-full overflow-hidden bg-red-100 flex-shrink-0">
              <img
                src="/avatar/error.png"
                alt={avatarName}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-600">{error}</p>
            </div>
          </div>
          <button
            onClick={loadNudge}
            className="btn-secondary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden rounded-2xl">
      {/* Subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-90"></div>
      
      <div className="relative p-6 text-white">
        <div className="mb-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-400 to-pink-500 rounded-full blur-md opacity-40"></div>
                <div className="relative w-16 h-16 rounded-full overflow-hidden bg-gradient-to-r from-white to-yellow-100 border-3 border-white shadow-xl">
                  <img
                    src="/avatar/encouraging.png"
                    alt={avatarName}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = "/avatar/idle.png";
                    }}
                  />
                </div>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">{avatarName}'s Boost ✨</h3>
                <p className="text-lg text-white text-opacity-90 font-medium">Your daily motivation</p>
              </div>
            </div>
            {nudge?.is_new && (
              <span className="bg-green-400 text-green-900 text-xs font-bold px-3 py-1 rounded-full shadow-sm">
                NEW
              </span>
            )}
          </div>
        </div>
        
        {/* Content */}
        <div className="mb-3 sm:mb-4">
          {nudge?.nudge ? (
            <div className="bg-white bg-opacity-95 backdrop-blur-sm rounded-xl p-4 sm:p-5 shadow-lg">
              <div className="text-lg leading-relaxed text-gray-900">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                    em: ({ children }) => <em className="italic text-gray-800">{children}</em>,
                    code: ({ children }) => <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-gray-800">{children}</code>,
                  }}
                >
                  {nudge.nudge}
                </ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="bg-white bg-opacity-30 backdrop-blur-sm rounded-xl h-16 sm:h-20 animate-pulse"></div>
          )}
        </div>

        <div className="flex items-center justify-end">
          <button
            onClick={regenerateNudge}
            disabled={isRegenerating}
            className={`flex items-center space-x-2 bg-white bg-opacity-20 backdrop-blur-sm text-white font-medium px-4 py-2 sm:px-5 sm:py-3 rounded-lg hover:bg-opacity-30 transition-all duration-200 text-sm sm:text-base ${
              isRegenerating ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isRegenerating ? (
              <>
                <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>New Nudge</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-500 bg-opacity-90 backdrop-blur-sm border border-red-300 rounded-xl">
            <p className="text-white font-medium">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DailyNudge;