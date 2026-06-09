import React, { useState } from 'react';
import SearchableDropdown from './SearchableDropdown';
import { progressService } from '../config/api-progress';
import { formatSkill } from '../utils/skills';

const AddAchievementModal = ({ 
  isOpen, 
  onClose, 
  itSkills, 
  softSkills, 
  loadingSkills, 
  onAchievementAdded 
}) => {
  const [selectedSkillType, setSelectedSkillType] = useState('it');
  const [selectedSkill, setSelectedSkill] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploading, setUploading] = useState(false);

  const availableSkills = selectedSkillType === 'it' ? itSkills : softSkills;

  const handleImageSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    } else {
      alert('Please select an image file');
    }
  };

  const handleSubmit = async () => {
    if (!selectedSkill || !selectedImage) {
      alert('Please select both a skill and an image');
      return;
    }

    setUploading(true);
    try {
      const newAchievement = await progressService.createAchievement(selectedSkill, selectedImage);
      onAchievementAdded(newAchievement);
      handleClose();
    } catch (error) {
      console.error('Failed to add achievement:', error);
      const errorMessage = error.response?.data?.error || 'Failed to add achievement. Please try again.';
      alert(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setSelectedSkillType('it');
    setSelectedSkill('');
    setSelectedImage(null);
    setImagePreview(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Add New Achievement</h3>
        
        <div className="space-y-4">
          <div>
            <label className="label">Skill Type</label>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setSelectedSkillType('it');
                  setSelectedSkill('');
                }}
                className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                  selectedSkillType === 'it'
                    ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-300'
                    : 'bg-gray-50 text-gray-600 border-2 border-gray-200 hover:bg-gray-100'
                }`}
              >
                💻 IT Skills
              </button>
              <button
                type="button"
                onClick={() => {
                  setSelectedSkillType('soft');
                  setSelectedSkill('');
                }}
                className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                  selectedSkillType === 'soft'
                    ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-300'
                    : 'bg-gray-50 text-gray-600 border-2 border-gray-200 hover:bg-gray-100'
                }`}
              >
                🤝 Soft Skills
              </button>
            </div>
          </div>
          
          <div>
            <label className="label">
              {selectedSkillType === 'it' ? 'IT Skill' : 'Soft Skill'} Learned
            </label>
            {loadingSkills ? (
              <div className="input flex items-center text-gray-400 text-sm">
                <svg className="animate-spin h-4 w-4 mr-2 text-gray-300" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Loading skills...
              </div>
            ) : (
              <div>
                <SearchableDropdown
                  options={availableSkills}
                  value={selectedSkill}
                  onChange={setSelectedSkill}
                  formatOption={formatSkill}
                  placeholder={`Select ${selectedSkillType === 'it' ? 'an IT' : 'a soft'} skill...`}
                />
                {availableSkills.length === 0 && !loadingSkills && (
                  <p className="text-xs text-gray-500 mt-1">
                    No {selectedSkillType === 'it' ? 'IT' : 'soft'} skills available
                  </p>
                )}
              </div>
            )}
          </div>

          <div>
            <label className="label">Achievement Screenshot</label>
            <div
              className="border-2 border-dashed border-gray-200 rounded-lg p-4 text-center cursor-pointer hover:border-gray-300 transition-colors"
              onClick={() => document.getElementById('imageInput').click()}
            >
              <input
                id="imageInput"
                type="file"
                accept="image/*"
                onChange={(e) => handleImageSelect(e.target.files[0])}
                className="hidden"
              />
              
              {imagePreview ? (
                <div className="space-y-2">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-20 h-20 object-cover rounded-lg mx-auto"
                  />
                  <p className="text-sm text-gray-600">Click to change image</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="w-12 h-12 bg-gray-100 rounded-lg mx-auto flex items-center justify-center">
                    <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p className="text-sm text-gray-500">Upload achievement screenshot</p>
                  <p className="text-xs text-gray-400">PNG, JPEG, or WebP (Max 5MB)</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={handleClose}
            className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!selectedSkill || !selectedImage || uploading}
            className="flex-1 btn-primary"
          >
            {uploading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Adding...
              </span>
            ) : (
              'Add Achievement'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddAchievementModal;