import React, { useState, useEffect } from 'react';
import { progressService } from '../config/api-progress';
import { resumeAPI as resumeProcessorAPI } from '../config/api-resume-processor';
import AddAchievementModal from './AddAchievementModal';
import AchievementDetailModal from './AchievementDetailModal';

const ProgressTree = () => {
  const [achievements, setAchievements] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [itSkills, setItSkills] = useState([]);
  const [softSkills, setSoftSkills] = useState([]);
  const [loadingSkills, setLoadingSkills] = useState(true);
  const [selectedAchievement, setSelectedAchievement] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const getAvatarAnimation = (avatarType) => {
    switch(avatarType) {
      case 'celebrating': return 'bounce-celebration';
      case 'thinking': return 'pulse-thinking';
      case 'analyzing': return 'rotate-analyzing';
      case 'presenting': return 'scale-presenting';
      case 'encouraging': return 'float-encouraging';
      case 'idle': return 'sway-idle';
      case 'listening': return 'wiggle-listening';
      default: return 'float';
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch skills and achievements in parallel
        const [itSkillsResponse, softSkillsResponse, achievementsResponse] = await Promise.all([
          resumeProcessorAPI.getITSkills(),
          resumeProcessorAPI.getSoftSkills(),
          progressService.getAchievements()
        ]);
        
        // Flatten the skills objects into arrays for the dropdown
        const flattenSkills = (skillsObj) => {
          if (Array.isArray(skillsObj)) return skillsObj;
          if (typeof skillsObj === 'object' && skillsObj !== null) {
            return Object.values(skillsObj).flat();
          }
          return [];
        };
        
        const flattenedItSkills = flattenSkills(itSkillsResponse.data);
        const flattenedSoftSkills = flattenSkills(softSkillsResponse.data);
        
        setItSkills(flattenedItSkills);
        setSoftSkills(flattenedSoftSkills);
        setAchievements(achievementsResponse || []);
      } catch (err) {
        console.error("Failed to load data", err);
      } finally {
        setLoadingSkills(false);
      }
    };
    
    fetchData();
  }, []);

  const handleAchievementAdded = (newAchievement) => {
    setAchievements(prev => [...prev, newAchievement]);
  };

  const handleAchievementClick = (achievement) => {
    setSelectedAchievement(achievement);
    setShowDetailModal(true);
  };

  const handleDeleteAchievement = (achievementId) => {
    setAchievements(prev => prev.filter(achievement => achievement.id !== achievementId));
    setShowDetailModal(false);
    setSelectedAchievement(null);
  };

  const EmptyState = () => (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <div className="relative mb-8">
        <div className="w-32 h-32 rounded-full bg-gradient-to-br from-green-100 to-emerald-100 flex items-center justify-center shadow-lg">
          <span className="text-6xl">🌱</span>
        </div>
        <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
          <span className="text-lg">✨</span>
        </div>
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Start Growing Your Tree</h2>
      <p className="text-gray-600 mb-2 max-w-md">
        Every skill you learn is a new leaf on your progress tree. Upload screenshots of your achievements 
        and watch your tree flourish!
      </p>
      <p className="text-sm text-gray-500 mb-8">
        Complete skills on your dashboard or add them directly here.
      </p>
      
      <button
        onClick={() => setShowAddModal(true)}
        className="btn-primary flex items-center gap-2 px-6 py-3"
      >
        <span>🌿</span>
        Add Your First Achievement
      </button>
    </div>
  );

  const TreeView = () => (
    <div className="min-h-[70vh] flex flex-col items-center relative py-8 overflow-hidden max-w-7xl mx-auto">
      {/* Header Section */}
      <div className="text-center mb-8 px-4">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">Your Progress Tree</h1>
        <p className="text-gray-600 text-sm md:text-base mb-6 max-w-2xl">
          Watch your achievements grow into a beautiful tree! Each skill you learn becomes a new leaf. 
          Upload screenshots of your accomplishments to see your tree flourish and track your learning journey.
        </p>
        
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2 px-6 py-3 mx-auto"
        >
          <span>🍃</span>
          Add New Achievement
        </button>
      </div>
      {/* Enhanced tree trunk area */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10">
        {/* Main trunk */}
        <div className="relative">
          <div className="w-24 h-32 bg-gradient-to-t from-amber-800 to-amber-600 rounded-t-lg shadow-lg"></div>
          
          {/* Root system */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2">
            <div className="w-32 h-8 bg-gradient-to-b from-amber-700 to-amber-900 rounded-b-full opacity-80"></div>
            <div className="absolute top-2 left-2 w-28 h-6 bg-gradient-to-b from-amber-600 to-amber-800 rounded-b-full opacity-60"></div>
            <div className="absolute top-4 left-4 w-24 h-4 bg-gradient-to-b from-amber-500 to-amber-700 rounded-b-full opacity-40"></div>
          </div>
          
          {/* Texture lines on trunk */}
          <div className="absolute inset-2 flex flex-col justify-evenly">
            <div className="w-full h-0.5 bg-amber-900 opacity-30 rounded"></div>
            <div className="w-full h-0.5 bg-amber-900 opacity-20 rounded"></div>
            <div className="w-full h-0.5 bg-amber-900 opacity-25 rounded"></div>
            <div className="w-full h-0.5 bg-amber-900 opacity-15 rounded"></div>
          </div>
          
          {/* Small decorative elements */}
          <div className="absolute -left-6 top-8 w-3 h-3 bg-green-400 rounded-full animate-pulse opacity-60" style={{ animationDelay: '1s' }}></div>
          <div className="absolute -right-5 top-12 w-2 h-2 bg-yellow-400 rounded-full animate-pulse opacity-50" style={{ animationDelay: '2s' }}></div>
          <div className="absolute -left-4 top-20 w-2 h-2 bg-emerald-400 rounded-full animate-pulse opacity-70" style={{ animationDelay: '3s' }}></div>
        </div>
      </div>
      
      {/* Tree growing vertically upwards in zig-zag */}
      <div className="flex flex-col-reverse gap-12 sm:gap-10 md:gap-8 lg:gap-6 xl:gap-5 mb-40 sm:mb-32 relative z-20 w-full max-w-6xl mx-auto">
        {achievements.map((achievement, index) => {
          const shouldShowAvatar = index % 2 === 0; // Show on 1st, 3rd, 5th, etc. (every other starting from first)
          const isEven = index % 2 === 0;
          
          // Cycle through different avatar types (excluding warning, error, and analyzing)
          const avatarTypes = ['celebrating', 'thinking', 'presenting', 'encouraging', 'idle', 'listening'];
          const avatarType = avatarTypes[Math.floor(index / 2) % avatarTypes.length];
          
          return (
            <div
              key={index}
              className={`relative w-full flex ${isEven ? 'justify-end pr-8 sm:pr-12 md:pr-16' : 'justify-start pl-8 sm:pl-12 md:pl-16'} animate-bounce-in`}
              style={{ 
                animationDelay: `${index * 300}ms`,
                animation: `float ${2 + (index % 3) * 0.5}s ease-in-out infinite, bounce-in 0.6s ease-out forwards`
              }}
            >
              {/* Achievement image - rectangular with zig-zag positioning */}
              <div className="relative group p-4 sm:p-6 md:p-8 lg:p-10 xl:p-12" style={{ 
                animation: `sway ${2.5 + (index % 2) * 0.5}s ease-in-out infinite, wobble ${3 + (index % 3) * 0.5}s ease-in-out infinite`
              }}>
                {/* Connecting branch line */}
                <div className={`absolute ${isEven ? 'right-full mr-5 sm:mr-7 md:mr-11 lg:mr-13 xl:mr-15' : 'left-full ml-5 sm:ml-7 md:ml-11 lg:ml-13 xl:ml-15'} top-1/2 transform -translate-y-1/2 w-16 sm:w-24 md:w-32 lg:w-36 xl:w-40 h-1 sm:h-1.5 md:h-2 lg:h-2.5 xl:h-3 bg-gradient-to-r ${isEven ? 'from-green-400 to-transparent' : 'from-transparent to-green-400'} rounded-full`}></div>
                
                <div className="relative w-64 h-48 sm:w-80 sm:h-60 md:w-96 md:h-72 lg:w-112 lg:h-80 xl:w-120 xl:h-88">
                  {/* Leaf background - different images for left/right sides */}
                  <img
                    src={isEven ? "/leaf_right.png" : "/leaf_left.png"}
                    alt="Leaf background"
                    className="absolute inset-0 w-full h-full object-contain z-0"
                  />
                  
                  {/* Achievement container - centered on top of leaf */}
                  <div 
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-20 sm:w-36 sm:h-24 md:w-40 md:h-28 lg:w-44 lg:h-30 xl:w-48 xl:h-32 rounded-lg overflow-hidden shadow-xl border-2 sm:border-3 md:border-4 border-green-400 bg-white hover:scale-110 sm:hover:scale-125 transition-all duration-500 hover:shadow-2xl hover:rotate-3 z-10 cursor-pointer"
                    onClick={() => handleAchievementClick(achievement)}
                  >
                    <img
                      src={achievement.image_url}
                      alt={achievement.skill}
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
                
                {/* Enhanced floating particles */}
                <div className="absolute -top-3 -right-3 w-4 h-4 bg-yellow-400 rounded-full animate-ping" style={{ animationDelay: `${index * 400}ms` }}></div>
                <div className="absolute -bottom-2 -left-2 w-3 h-3 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: `${index * 600}ms` }}></div>
                <div className="absolute top-1 -left-3 w-2 h-2 bg-blue-400 rounded-full animate-ping" style={{ animationDelay: `${index * 800}ms` }}></div>
                <div className="absolute -top-1 left-1/2 w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: `${index * 1000}ms` }}></div>
                
                {/* Achievement name and date labels - always visible */}
                <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 z-30 flex flex-col items-center gap-1">
                  <div className="bg-white/95 backdrop-blur-sm text-gray-800 text-xs sm:text-sm font-medium px-3 py-1.5 rounded-full border border-green-300 shadow-lg whitespace-nowrap max-w-32 sm:max-w-36 md:max-w-40 truncate text-center">
                    {achievement.skill}
                  </div>
                  {achievement.created_at && (
                    <div className="bg-gray-100/90 backdrop-blur-sm text-gray-600 text-xs px-2 py-1 rounded-full border border-gray-200 shadow-sm whitespace-nowrap">
                      {new Date(achievement.created_at).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </div>
                  )}
                </div>
              </div>
              
              {/* Avatar positioned within bounds - alternating sides */}
              {shouldShowAvatar && (
                <div 
                  className={`absolute ${Math.floor(index / 2) % 2 === 0 ? 'left-2 sm:left-4 md:left-2 lg:left-4 xl:left-6' : 'right-2 sm:right-4 md:right-2 lg:right-4 xl:right-6'} top-2 sm:top-4 md:top-1/2 md:transform md:-translate-y-1/2`} 
                  style={{ 
                    animation: `${getAvatarAnimation(avatarType)} ${2 + (index % 4) * 0.3}s ease-in-out infinite` 
                  }}
                >
                  <div className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 lg:w-26 lg:h-26 xl:w-28 xl:h-28 rounded-full overflow-hidden shadow-xl sm:shadow-2xl border-2 sm:border-3 md:border-4 border-indigo-500 bg-gradient-to-br from-indigo-100 to-indigo-200">
                    <img
                      src={`/avatar/${avatarType}.png`}
                      alt={`Achievement Avatar ${avatarType}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 bg-gradient-to-br from-yellow-400 to-orange-400 rounded-full border-1 sm:border-2 border-white"></div>
                  <div className="absolute -bottom-0.5 -left-0.5 sm:-bottom-1 sm:-left-1 w-3 h-3 sm:w-4 sm:h-4 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0.5s' }}></div>
                </div>
              )}
              
              {/* Connecting line to trunk - hidden on mobile */}
              {index === 0 && (
                <div className="hidden sm:block absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-12 bg-gradient-to-b from-green-400 to-amber-600"></div>
              )}
              {index > 0 && (
                <div className="hidden sm:block absolute top-full left-1/2 transform -translate-x-1/2 w-1 h-10 bg-gradient-to-b from-green-300 to-green-400"></div>
              )}
            </div>
          );
        })}
      </div>
      
      
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          25% { transform: translateY(-15px) rotate(-2deg); }
          50% { transform: translateY(-20px) rotate(2deg); }
          75% { transform: translateY(-10px) rotate(-1deg); }
        }
        
        @keyframes sway {
          0%, 100% { transform: rotate(-5deg) scale(1); }
          25% { transform: rotate(3deg) scale(1.02); }
          50% { transform: rotate(5deg) scale(1); }
          75% { transform: rotate(-3deg) scale(1.02); }
        }
        
        @keyframes wobble {
          0%, 100% { transform: translateX(0px) rotate(0deg); }
          25% { transform: translateX(-3px) rotate(-1deg); }
          50% { transform: translateX(3px) rotate(1deg); }
          75% { transform: translateX(-2px) rotate(-0.5deg); }
        }
        
        @keyframes bounce-in {
          0% { opacity: 0; transform: scale(0.3) translateY(50px) rotate(-10deg); }
          50% { opacity: 0.8; transform: scale(1.05) rotate(2deg); }
          100% { opacity: 1; transform: scale(1) translateY(0px) rotate(0deg); }
        }
        
        /* Avatar-specific animations */
        @keyframes bounce-celebration {
          0%, 100% { transform: translateY(0px) scale(1) rotate(0deg); }
          25% { transform: translateY(-12px) scale(1.1) rotate(-5deg); }
          50% { transform: translateY(-20px) scale(1.15) rotate(5deg); }
          75% { transform: translateY(-8px) scale(1.05) rotate(-2deg); }
        }
        
        @keyframes pulse-thinking {
          0%, 100% { transform: scale(1) rotate(0deg); opacity: 1; }
          50% { transform: scale(1.08) rotate(2deg); opacity: 0.9; }
        }
        
        @keyframes rotate-analyzing {
          0% { transform: rotate(0deg) scale(1); }
          25% { transform: rotate(5deg) scale(1.02); }
          50% { transform: rotate(-3deg) scale(1.05); }
          75% { transform: rotate(2deg) scale(1.02); }
          100% { transform: rotate(0deg) scale(1); }
        }
        
        @keyframes scale-presenting {
          0%, 100% { transform: scale(1) translateY(0px); }
          33% { transform: scale(1.1) translateY(-5px); }
          66% { transform: scale(0.95) translateY(2px); }
        }
        
        @keyframes float-encouraging {
          0%, 100% { transform: translateY(0px) translateX(0px) rotate(0deg); }
          25% { transform: translateY(-8px) translateX(-3px) rotate(-2deg); }
          50% { transform: translateY(-15px) translateX(3px) rotate(2deg); }
          75% { transform: translateY(-5px) translateX(-2px) rotate(-1deg); }
        }
        
        @keyframes sway-idle {
          0%, 100% { transform: rotate(0deg) translateY(0px); }
          25% { transform: rotate(-3deg) translateY(-3px); }
          50% { transform: rotate(3deg) translateY(-5px); }
          75% { transform: rotate(-2deg) translateY(-2px); }
        }
        
        @keyframes wiggle-listening {
          0%, 100% { transform: translateX(0px) rotate(0deg) scale(1); }
          20% { transform: translateX(-2px) rotate(-1deg) scale(1.02); }
          40% { transform: translateX(2px) rotate(1deg) scale(1.05); }
          60% { transform: translateX(-3px) rotate(-0.5deg) scale(1.02); }
          80% { transform: translateX(1px) rotate(0.5deg) scale(1.03); }
        }
      `}</style>
    </div>
  );

  return (
    <div className="w-full">
      {achievements.length === 0 ? <EmptyState /> : <TreeView />}
      <AddAchievementModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        itSkills={itSkills}
        softSkills={softSkills}
        loadingSkills={loadingSkills}
        onAchievementAdded={handleAchievementAdded}
      />
      
      <AchievementDetailModal
        isOpen={showDetailModal}
        achievement={selectedAchievement}
        onClose={() => setShowDetailModal(false)}
        onDelete={handleDeleteAchievement}
      />
    </div>
  );
};

export default ProgressTree;