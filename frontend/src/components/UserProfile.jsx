import React, { useState, useEffect } from 'react';
import { resumeAPI } from '../config/api-resume-processor';

const UserProfile = ({ resumeData, onUpdate }) => {
  const [editMode, setEditMode] = useState({});
  const [formData, setFormData] = useState(resumeData);
  const [allSkills, setAllSkills] = useState({});
  const [skillsLoading, setSkillsLoading] = useState(false);

  useEffect(() => {
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
    fetchAllSkills();
  }, []);

  const handleEdit = (field) => setEditMode({ ...editMode, [field]: true });
  const handleSave = (field) => { setEditMode({ ...editMode, [field]: false }); onUpdate(formData); };
  const handleChange = (field, value) => setFormData({ ...formData, [field]: value });

  const handleArrayChange = (field, index, value) => {
    const newArray = [...formData[field]];
    newArray[index] = value;
    setFormData({ ...formData, [field]: newArray });
  };

  const addArrayItem = (field) => setFormData({ ...formData, [field]: [...formData[field], ''] });
  const removeArrayItem = (field, index) => setFormData({ ...formData, [field]: formData[field].filter((_, i) => i !== index) });

  const fetchSkillsByType = async (skillType) => {
    setSkillsLoading(true);
    try {
      let response;
      switch (skillType) {
        case 'it_skills': response = await resumeAPI.getITSkills(); break;
        case 'soft_skills': response = await resumeAPI.getSoftSkills(); break;
        case 'languages': response = await resumeAPI.getLanguages(); break;
        default: break;
      }
      if (response?.data) {
        setAllSkills(prev => ({ ...prev, [skillType]: { ...prev[skillType], custom: response.data } }));
      }
    } catch (error) {
      console.error(`Failed to fetch ${skillType}:`, error);
    } finally {
      setSkillsLoading(false);
    }
  };

  const renderEditableField = (label, field, value) => {
    const isEditing = editMode[field];
    return (
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500">{label}</span>
          {!isEditing && (
            <button onClick={() => handleEdit(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
              Edit
            </button>
          )}
        </div>
        {isEditing ? (
          <div className="flex gap-2 animate-fade-in">
            <input
              type="text"
              value={value}
              onChange={(e) => handleChange(field, e.target.value)}
              className="input flex-1"
            />
            <button onClick={() => handleSave(field)} className="btn-primary text-sm py-2 px-4">Save</button>
          </div>
        ) : (
          <p className="text-gray-900 text-sm">{value}</p>
        )}
      </div>
    );
  };

  const renderTags = (array, field, isSkill = false) => (
    <div className="flex flex-wrap gap-1.5">
      {array.map((item, index) => (
        <span key={index} className={`tag ${isSkill ? 'tag-indigo' : ''}`}>
          {item}
        </span>
      ))}
      {array.length === 0 && <span className="text-xs text-gray-400">None listed</span>}
    </div>
  );

  const renderEditableArray = (label, field, array) => {
    const isEditing = editMode[field];
    return (
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500">{label}</span>
          {!isEditing ? (
            <button onClick={() => handleEdit(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
          ) : (
            <button onClick={() => handleSave(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Done</button>
          )}
        </div>
        {isEditing ? (
          <div className="space-y-2 animate-fade-in">
            {array.map((item, index) => (
              <div key={index} className="flex items-center gap-2">
                <input type="text" value={item} onChange={(e) => handleArrayChange(field, index, e.target.value)} className="input flex-1 text-sm" />
                <button onClick={() => removeArrayItem(field, index)} className="w-8 h-8 rounded-lg bg-red-50 text-red-400 hover:bg-red-100 hover:text-red-500 flex items-center justify-center transition-colors text-sm">
                  &times;
                </button>
              </div>
            ))}
            <button onClick={() => addArrayItem(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
              + Add item
            </button>
          </div>
        ) : renderTags(array, field)}
      </div>
    );
  };

  const renderSkillsArray = (label, field, array, skillType) => {
    const isEditing = editMode[field];
    const availableSkills = allSkills[skillType] || {};

    return (
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500">{label}</span>
          {!isEditing ? (
            <button onClick={() => handleEdit(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
          ) : (
            <button onClick={() => handleSave(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Done</button>
          )}
        </div>
        {isEditing ? (
          <div className="space-y-2 animate-fade-in">
            {array.map((item, index) => (
              <div key={index} className="flex items-center gap-2">
                <select
                  value={item}
                  onChange={(e) => handleArrayChange(field, index, e.target.value)}
                  className="input flex-1 text-sm"
                >
                  <option value={item}>{item}</option>
                  {Object.entries(availableSkills).map(([category, skills]) => (
                    <optgroup key={category} label={category}>
                      {skills.map(skill => (
                        <option key={skill} value={skill}>{skill}</option>
                      ))}
                    </optgroup>
                  ))}
                </select>
                <button onClick={() => removeArrayItem(field, index)} className="w-8 h-8 rounded-lg bg-red-50 text-red-400 hover:bg-red-100 hover:text-red-500 flex items-center justify-center transition-colors text-sm">
                  &times;
                </button>
              </div>
            ))}

            {!skillsLoading && Object.keys(availableSkills).length > 0 && (
              <select
                onChange={(e) => {
                  if (e.target.value && !array.includes(e.target.value)) {
                    setFormData({ ...formData, [field]: [...array, e.target.value] });
                  }
                  e.target.value = '';
                }}
                className="input text-sm text-gray-400"
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
            )}

            <button onClick={() => fetchSkillsByType(skillType)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
              + Load more skills
            </button>
          </div>
        ) : renderTags(array, field, true)}
      </div>
    );
  };

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-semibold text-gray-900">Profile</h2>
        <span className="text-xs text-gray-400">
          {new Date(formData.created_at).toLocaleDateString()}
        </span>
      </div>

      <div className="space-y-5 divide-y divide-gray-100 [&>*:not(:first-child)]:pt-5">
        {renderEditableField('Experience', 'total_exp', `${formData.total_exp} years`)}
        {renderEditableArray('Education', 'university', formData.university || [])}
        {renderEditableArray('Roles', 'designition', formData.designition || [])}
        {renderEditableArray('Degrees', 'degree', formData.degree || [])}
        {renderSkillsArray('IT Skills', 'it_skills', formData.it_skills || [], 'it_skills')}
        {renderSkillsArray('Soft Skills', 'soft_skills', formData.soft_skills || [], 'soft_skills')}
        {renderSkillsArray('Languages', 'languages', formData.languages || [], 'languages')}
      </div>
    </div>
  );
};

export default UserProfile;
