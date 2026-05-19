import React from 'react';
import { progressService } from '../config/api-progress';

const AchievementDetailModal = ({ 
  isOpen, 
  achievement, 
  onClose, 
  onDelete 
}) => {
  if (!isOpen || !achievement) return null;

  const handleDelete = async () => {
    try {
      await progressService.deleteAchievement(achievement.id);
      onDelete(achievement.id);
      onClose();
    } catch (error) {
      console.error('Failed to delete achievement:', error);
      // You might want to show an error message to the user here
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-2xl font-bold text-gray-900">{achievement.skill}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>
        
        <div className="mb-6">
          <img
            src={achievement.image_url}
            alt={achievement.skill}
            className="w-full h-64 object-cover rounded-lg shadow-lg"
          />
        </div>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Skill</h3>
            <p className="text-gray-600">{achievement.skill}</p>
          </div>
          
          {achievement.description && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Description</h3>
              <p className="text-gray-600">{achievement.description}</p>
            </div>
          )}
          
          {achievement.created_at && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Date Achieved</h3>
              <p className="text-gray-600">{new Date(achievement.created_at).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}</p>
            </div>
          )}
          
          {achievement.category && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Category</h3>
              <p className="text-gray-600">{achievement.category}</p>
            </div>
          )}
        </div>
        
        <div className="mt-6 flex justify-between gap-2">
          <button
            onClick={handleDelete}
            className="bg-red-500 hover:bg-red-600 text-white px-3 py-2 sm:px-6 sm:py-2 rounded-lg transition-colors duration-200 flex items-center gap-1 sm:gap-2 text-sm sm:text-base"
          >
            <span>🗑️</span>
            <span className="hidden sm:inline">Delete Achievement</span>
            <span className="sm:hidden">Delete</span>
          </button>
          
          <button
            onClick={onClose}
            className="btn-primary px-3 py-2 sm:px-6 sm:py-2 text-sm sm:text-base"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AchievementDetailModal;