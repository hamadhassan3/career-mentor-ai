import React, { useState, useEffect } from 'react';
import { progressService } from '../config/api-progress';
import { resumeAPI as resumeProcessorAPI } from '../config/api-resume-processor';
import AddAchievementModal from './AddAchievementModal';

const ProgressTree = () => {
  const [achievements, setAchievements] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [itSkills, setItSkills] = useState([]);
  const [softSkills, setSoftSkills] = useState([]);
  const [loadingSkills, setLoadingSkills] = useState(true);

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
    <div className="min-h-[70vh] flex flex-col items-center justify-center relative">
      {/* Tree trunk */}
      <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
        <div className="w-8 h-32 bg-gradient-to-t from-amber-800 to-amber-600 rounded-t-lg"></div>
      </div>
      
      {/* Tree leaves/achievements */}
      <div className="flex flex-wrap justify-center items-center gap-4 mb-32">
        {achievements.map((achievement, index) => (
          <div
            key={index}
            className="relative group animate-bounce-in"
            style={{ animationDelay: `${index * 200}ms` }}
          >
            <div className="w-20 h-20 rounded-full overflow-hidden shadow-lg border-4 border-green-300 bg-white">
              <img
                src={achievement.image_url}
                alt={achievement.skill}
                className="w-full h-full object-cover"
              />
            </div>
            
            {/* Avatar next to every second leaf */}
            {index % 2 === 1 && (
              <div className="absolute -right-8 top-1/2 transform -translate-y-1/2">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="text-sm">👨‍💻</span>
                </div>
              </div>
            )}
            
            {/* Tooltip */}
            <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-black text-white text-xs px-2 py-1 rounded whitespace-nowrap">
              {achievement.skill}
            </div>
          </div>
        ))}
      </div>
      
      <button
        onClick={() => setShowAddModal(true)}
        className="btn-primary flex items-center gap-2 mb-8"
      >
        <span>🍃</span>
        Add New Achievement
      </button>
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
    </div>
  );
};

export default ProgressTree;