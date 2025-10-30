import React, { useState } from 'react';

const NextBestStep = ({ resumeData }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateRecommendations = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API endpoint when available
      // This is a mock implementation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setRecommendations({
        title: "Enhance Your Cloud Skills",
        description: "Based on your profile, focusing on cloud technologies would significantly boost your career prospects.",
        steps: [
          "Complete AWS Solutions Architect certification",
          "Build a cloud-native project using microservices",
          "Learn Infrastructure as Code (Terraform/CloudFormation)",
          "Practice with containerization (Docker/Kubernetes)"
        ],
        timeline: "3-6 months",
        impact: "High"
      });
    } catch (error) {
      console.error('Failed to generate recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="border-b border-gray-200 pb-4 mb-6">
        <h3 className="text-xl font-semibold text-gray-800">Next Best Step</h3>
        <p className="text-sm text-gray-600 mt-1">Get personalized recommendations for your career growth</p>
      </div>

      {!recommendations ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🎯</div>
          <p className="text-gray-600 mb-6 text-sm md:text-base max-w-sm mx-auto leading-relaxed">
            Click below to get AI-powered recommendations tailored to your profile
          </p>
          <button 
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-lg transition-all duration-200 disabled:cursor-not-allowed transform hover:scale-105 disabled:transform-none"
            onClick={generateRecommendations}
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Next Best Step'}
          </button>
        </div>
      ) : (
        <div className="animate-fade-in">
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-4">
              <h4 className="text-lg font-semibold text-gray-800 mb-2 sm:mb-0">{recommendations.title}</h4>
              <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-medium">
                {recommendations.impact} Impact
              </span>
            </div>
            
            <p className="text-gray-600 mb-6 leading-relaxed">{recommendations.description}</p>
            
            <div className="mb-6">
              <h5 className="text-base font-medium text-gray-800 mb-3">Recommended Actions:</h5>
              <ul className="space-y-2">
                {recommendations.steps.map((step, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="bg-green-100 text-green-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium mt-0.5 flex-shrink-0">
                      {index + 1}
                    </span>
                    <span className="text-gray-700 text-sm">{step}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="text-sm text-gray-600 mb-6">
              <strong>Timeline:</strong> {recommendations.timeline}
            </div>
            
            <button 
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:cursor-not-allowed text-sm"
              onClick={generateRecommendations}
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate New Recommendation'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default NextBestStep;