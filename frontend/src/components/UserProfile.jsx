import React, { useState, useEffect } from 'react';
import { resumeAPI } from '../config/api-resume-processor';

const UserProfile = ({ resumeData, onUpdate }) => {
  const [editMode, setEditMode] = useState({});
  const [formData, setFormData] = useState(resumeData);
  const [allSkills, setAllSkills] = useState({});
  const [skillsLoading, setSkillsLoading] = useState(false);

  useEffect(() => {
    fetchAllSkills();
  }, []);

  const fetchAllSkills = async () => {
    setSkillsLoading(true);
    try {
      const response = await resumeAPI.getAllSkills();
      setAllSkills(response.data);
    } catch (error) {
      console.error('Failed to fetch skills:', error);
    } finally {
      setSkillsLoading(false);
    }
  };

  const handleEdit = (field) => {
    setEditMode({ ...editMode, [field]: true });
  };

  const handleSave = (field) => {
    setEditMode({ ...editMode, [field]: false });
    onUpdate(formData);
  };

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleArrayChange = (field, index, value) => {
    const newArray = [...formData[field]];
    newArray[index] = value;
    setFormData({ ...formData, [field]: newArray });
  };

  const addArrayItem = (field) => {
    setFormData({ ...formData, [field]: [...formData[field], ''] });
  };

  const removeArrayItem = (field, index) => {
    const newArray = formData[field].filter((_, i) => i !== index);
    setFormData({ ...formData, [field]: newArray });
  };

  const renderEditableField = (label, field, value) => {
    const isEditing = editMode[field];
    
    return (
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
        <div className="flex items-center gap-2">
          {isEditing ? (
            <div className="flex flex-col sm:flex-row gap-2 w-full">
              <input
                type="text"
                value={value}
                onChange={(e) => handleChange(field, e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <button 
                onClick={() => handleSave(field)} 
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Save
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between w-full">
              <span className="text-gray-900">{value}</span>
              <button 
                onClick={() => handleEdit(field)} 
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-md text-sm font-medium transition-colors"
              >
                Edit
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderEditableArray = (label, field, array) => {
    const isEditing = editMode[field];
    
    return (
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
        <div className="space-y-2">
          {isEditing ? (
            <div className="space-y-3">
              {array.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={item}
                    onChange={(e) => handleArrayChange(field, index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                  <button 
                    onClick={() => removeArrayItem(field, index)} 
                    className="bg-red-500 hover:bg-red-600 text-white w-8 h-8 rounded-md flex items-center justify-center transition-colors"
                  >
                    ×
                  </button>
                </div>
              ))}
              <div className="flex flex-col sm:flex-row gap-2">
                <button 
                  onClick={() => addArrayItem(field)} 
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  + Add
                </button>
                <button 
                  onClick={() => handleSave(field)} 
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Save
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2">
                {array.map((item, index) => (
                  <span key={index} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-md text-sm">
                    {item}
                  </span>
                ))}
              </div>
              <button 
                onClick={() => handleEdit(field)} 
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-md text-sm font-medium transition-colors"
              >
                Edit
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderSkillsArray = (label, field, array, skillType) => {
    const isEditing = editMode[field];
    const availableSkills = allSkills[skillType] || {};
    
    return (
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
        <div className="space-y-2">
          {isEditing ? (
            <div className="space-y-3">
              {array.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <select
                    value={item}
                    onChange={(e) => handleArrayChange(field, index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
                  >
                    <option value={item}>{item}</option>
                    {Object.entries(availableSkills).map(([category, skills]) => (
                      <optgroup key={category} label={category}>
                        {skills.filter(skill => !array.includes(skill)).map(skill => (
                          <option key={skill} value={skill}>{skill}</option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                  <button 
                    onClick={() => removeArrayItem(field, index)} 
                    className="bg-red-500 hover:bg-red-600 text-white w-8 h-8 rounded-md flex items-center justify-center transition-colors"
                  >
                    ×
                  </button>
                </div>
              ))}
              
              {skillsLoading ? (
                <div className="text-gray-500 text-sm italic text-center py-2">Loading skills...</div>
              ) : Object.keys(availableSkills).length > 0 ? (
                <div className="mb-2">
                  <select 
                    onChange={(e) => {
                      if (e.target.value && !array.includes(e.target.value)) {
                        setFormData({ ...formData, [field]: [...array, e.target.value] });
                      }
                      e.target.value = '';
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
                  >
                    <option value="">+ Add a skill</option>
                    {Object.entries(availableSkills).map(([category, skills]) => (
                      <optgroup key={category} label={category}>
                        {skills.filter(skill => !array.includes(skill)).map(skill => (
                          <option key={skill} value={skill}>{skill}</option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                </div>
              ) : null}
              
              <div className="flex flex-col sm:flex-row gap-2">
                <button 
                  onClick={() => addArrayItem(field)} 
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  + Add Custom
                </button>
                <button 
                  onClick={() => handleSave(field)} 
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Save
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2">
                {array.map((item, index) => (
                  <span key={index} className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-md text-sm">
                    {item}
                  </span>
                ))}
              </div>
              <button 
                onClick={() => handleEdit(field)} 
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-md text-sm font-medium transition-colors"
              >
                Edit
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="border-b border-gray-200 pb-4 mb-6">
        <h2 className="text-xl md:text-2xl font-semibold text-gray-800">Your Profile</h2>
        <div className="text-sm text-gray-500 mt-1">
          Uploaded: {new Date(formData.created_at).toLocaleDateString()}
        </div>
      </div>

      <div className="space-y-6">
        {renderEditableField('Total Experience', 'total_exp', `${formData.total_exp} years`)}
        
        {renderEditableArray('University', 'university', formData.university || [])}
        
        {renderEditableArray('Designations', 'designition', formData.designition || [])}
        
        {renderEditableArray('Degrees', 'degree', formData.degree || [])}
        
        {renderSkillsArray('IT Skills', 'it_skills', formData.it_skills || [], 'it_skills')}
        
        {renderSkillsArray('Soft Skills', 'soft_skills', formData.soft_skills || [], 'soft_skills')}
        
        {renderSkillsArray('Languages', 'languages', formData.languages || [], 'languages')}
      </div>
    </div>
  );
};

export default UserProfile;