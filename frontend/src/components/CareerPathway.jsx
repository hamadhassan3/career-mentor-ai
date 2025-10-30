import React, { useState } from 'react';

const CareerPathway = ({ resumeData }) => {
  const [pathway, setPathway] = useState(null);
  const [loading, setLoading] = useState(false);

  const generatePathway = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API endpoint when available
      // This is a mock implementation
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      setPathway({
        currentLevel: "Mid-Level Developer",
        targetRole: "Senior Cloud Solutions Architect",
        stages: [
          {
            title: "Cloud Foundation",
            duration: "3-6 months",
            skills: ["AWS Basics", "Docker", "Microservices"],
            milestones: ["AWS Certified Developer", "Deploy containerized app"],
            status: "current"
          },
          {
            title: "Advanced Cloud Architecture",
            duration: "6-12 months", 
            skills: ["Kubernetes", "Terraform", "System Design"],
            milestones: ["AWS Solutions Architect", "Design scalable systems"],
            status: "upcoming"
          },
          {
            title: "Leadership & Strategy",
            duration: "12-18 months",
            skills: ["Team Leadership", "Architecture Strategy", "Cost Optimization"],
            milestones: ["Lead cloud migration", "Mentor junior developers"],
            status: "future"
          }
        ],
        timelineTotal: "2-3 years"
      });
    } catch (error) {
      console.error('Failed to generate pathway:', error);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="border-b border-gray-200 pb-4 mb-6">
        <h3 className="text-xl font-semibold text-gray-800">Career Pathway</h3>
        <p className="text-sm text-gray-600 mt-1">Visualize your long-term career progression</p>
      </div>

      {!pathway ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🗺️</div>
          <p className="text-gray-600 mb-6 text-sm md:text-base max-w-sm mx-auto leading-relaxed">
            Generate a personalized career roadmap based on your skills and goals
          </p>
          <button 
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-lg transition-all duration-200 disabled:cursor-not-allowed transform hover:scale-105 disabled:transform-none"
            onClick={generatePathway}
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Career Pathway'}
          </button>
        </div>
      ) : (
        <div className="animate-fade-in space-y-6">
          <div className="bg-slate-50 rounded-lg p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
              <div className="flex-1">
                <span className="block text-xs text-gray-500 mb-1">Current:</span>
                <span className="text-base font-medium text-gray-800">{pathway.currentLevel}</span>
              </div>
              <div className="text-purple-600 text-2xl hidden sm:block">→</div>
              <div className="flex-1">
                <span className="block text-xs text-gray-500 mb-1">Target:</span>
                <span className="text-base font-medium text-gray-800">{pathway.targetRole}</span>
              </div>
            </div>
            <div className="text-center text-sm font-medium text-gray-700">
              Total Timeline: {pathway.timelineTotal}
            </div>
          </div>

          <div className="space-y-4">
            {pathway.stages.map((stage, index) => {
              const statusColors = {
                current: 'border-green-500 bg-green-50',
                upcoming: 'border-yellow-500 bg-yellow-50', 
                future: 'border-gray-300 bg-white'
              };
              const numberColors = {
                current: 'bg-green-500',
                upcoming: 'bg-yellow-500',
                future: 'bg-gray-400'
              };
              
              return (
                <div key={index} className={`border-2 rounded-lg p-4 ${statusColors[stage.status]}`}>
                  <div className="flex items-start gap-4 mb-4">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${numberColors[stage.status]}`}>
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-gray-800">{stage.title}</h4>
                      <span className="text-sm text-gray-600">{stage.duration}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Key Skills to Develop:</h5>
                      <div className="flex flex-wrap gap-2">
                        {stage.skills.map((skill, skillIndex) => (
                          <span key={skillIndex} className="bg-indigo-100 text-indigo-700 px-2 py-1 rounded-md text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Milestones:</h5>
                      <ul className="space-y-1">
                        {stage.milestones.map((milestone, milestoneIndex) => (
                          <li key={milestoneIndex} className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-green-500 mt-1">•</span>
                            <span>{milestone}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="text-center pt-4">
            <button 
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:cursor-not-allowed text-sm"
              onClick={generatePathway}
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate New Pathway'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CareerPathway;