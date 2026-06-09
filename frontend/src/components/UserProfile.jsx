import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { resumeAPI } from '../config/api-resume-processor';
import { resumeAPI as backendResumeAPI } from '../config/api-backend';
import { setWarning, clearWarning, setEncouraging, setIdle } from '../store/avatarSlice';
import SkillUploadModal from './SkillUploadModal';
import SearchableDropdown from './SearchableDropdown';
import { formatSkill } from '../utils/skills';

const UserProfile = ({ resumeData, onUpdate, isReadOnly = false, onNavigateToProgress }) => {
  const dispatch = useDispatch();
  const [editMode, setEditMode] = useState({});
  const [formData, setFormData] = useState(resumeData);
  const [allSkills, setAllSkills] = useState({});
  const [skillsLoading, setSkillsLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [designations, setDesignations] = useState([]);
  const [designationsLoading, setDesignationsLoading] = useState(false);
  const [pendingDesignationSave, setPendingDesignationSave] = useState(false);
  const [showSkillUploadModal, setShowSkillUploadModal] = useState(false);
  const [lastUpdatedSkill, setLastUpdatedSkill] = useState('');

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

    const fetchDesignations = async () => {
      setDesignationsLoading(true);
      try {
        const response = await resumeAPI.getDesignations();
        const data = response.data?.designations || response.data?.data || response.data || [];
        setDesignations(data);
      } catch (error) {
        console.error('Failed to fetch designations:', error);
      } finally {
        setDesignationsLoading(false);
      }
    };

    fetchAllSkills();
    fetchDesignations();
  }, []);

  useEffect(() => {
    setFormData(resumeData);
  }, [resumeData]);

  const handleEdit = (field) => {
    if (isReadOnly) return;
    setEditMode({ ...editMode, [field]: true });
  };

  const handleSave = async (field) => {
    if (isReadOnly) return;
    
    // Check if this is a target designation change and show warning
    if (field === 'target_designation' && formData.target_designation !== resumeData.target_designation && !pendingDesignationSave) {
      setPendingDesignationSave(true);
      dispatch(setWarning({
        message: "Changing role will clear recommendations. Continue?",
        onConfirm: async () => {
          dispatch(clearWarning());
          setPendingDesignationSave(false);
          
          // Clear recommendations from backend
          try {
            await backendResumeAPI.clearRecommendations();
          } catch (error) {
            console.error('Failed to clear backend recommendations:', error);
          }
          
          performSave(field);
        },
        onCancel: () => {
          dispatch(clearWarning());
          setPendingDesignationSave(false);
          // Reset form data to original value
          setFormData({ ...formData, target_designation: resumeData.target_designation });
        }
      }));
      return;
    }
    
    performSave(field);
  };

  const getSuccessMessage = (field) => {
    const fieldMessages = {
      'target_designation': 'Fawkes updated your target role!',
      'total_exp': 'Fawkes updated your experience!',
      'university': 'Fawkes updated your education!',
      'designition': 'Fawkes updated your roles!',
      'degree': 'Fawkes updated your degrees!',
      'it_skills': 'Fawkes updated your IT skills!',
      'soft_skills': 'Fawkes updated your soft skills!',
      'languages': 'Fawkes updated your languages!'
    };
    return fieldMessages[field] || 'Fawkes updated your profile!';
  };

  const performSave = async (field) => {
    setSaving(true);
    try {
      // Update the resume in the backend
      const response = await backendResumeAPI.updateResume(resumeData.id, formData);
      
      // Update local state
      setEditMode({ ...editMode, [field]: false });
      onUpdate(response.data);
      
      // Show encouraging message for successful update
      dispatch(setEncouraging(getSuccessMessage(field)));
      setTimeout(() => dispatch(setIdle()), 3000);
      
      // Check if this is a skill update and prompt for screenshot upload
      if ((field === 'it_skills' || field === 'soft_skills') && formData[field] && formData[field].length > 0) {
        // Find the newly added skill by comparing with original data
        const newSkills = formData[field].filter(skill => !resumeData[field]?.includes(skill));
        if (newSkills.length > 0) {
          const newestSkill = newSkills[newSkills.length - 1];
          setLastUpdatedSkill(newestSkill);
          setShowSkillUploadModal(true);
        }
      }
    } catch (error) {
      console.error('Failed to update resume:', error);
      const errorMessage = error.response?.data?.error || 'Failed to save changes. Please try again.';
      alert(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleSkillUploadSuccess = (achievement) => {
    setShowSkillUploadModal(false);
    // Navigate to progress tree
    if (onNavigateToProgress) {
      onNavigateToProgress();
    }
  };

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
          {!isEditing && !isReadOnly && (
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
              disabled={saving}
            />
            <button 
              onClick={() => handleSave(field)} 
              disabled={saving}
              className="btn-primary text-sm py-2 px-4 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
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
          {isSkill ? formatSkill(item) : item}
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
          {!isReadOnly && (
            !isEditing ? (
              <button onClick={() => handleEdit(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
            ) : (
              <button 
                onClick={() => handleSave(field)} 
                disabled={saving}
                className="text-xs text-indigo-600 hover:text-indigo-700 font-medium disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Done'}
              </button>
            )
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
    // Flatten the categorised skills object into a single list for the
    // searchable dropdown (same shape the Progress Tree feeds it).
    const flatSkills = [...new Set(Object.values(availableSkills).flat())];

    return (
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500">{label}</span>
          {!isReadOnly && (
            !isEditing ? (
              <button onClick={() => handleEdit(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
            ) : (
              <button 
                onClick={() => handleSave(field)} 
                disabled={saving}
                className="text-xs text-indigo-600 hover:text-indigo-700 font-medium disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Done'}
              </button>
            )
          )}
        </div>
        {isEditing ? (
          <div className="space-y-2 animate-fade-in">
            {array.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {array.map((item, index) => (
                  <span key={index} className="inline-flex items-center gap-1 pl-3 pr-1 py-1 rounded-lg bg-indigo-50 text-indigo-600 text-sm font-medium">
                    {formatSkill(item)}
                    <button
                      type="button"
                      onClick={() => removeArrayItem(field, index)}
                      aria-label={`Remove ${formatSkill(item)}`}
                      className="inline-flex items-center justify-center w-6 h-6 rounded-full text-indigo-400 hover:text-indigo-700 hover:bg-indigo-100 active:bg-indigo-200 transition-colors"
                    >
                      <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M18 6L6 18" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            )}

            {!skillsLoading && flatSkills.length > 0 && (
              <SearchableDropdown
                options={flatSkills.filter((skill) => !array.includes(skill))}
                value=""
                onChange={(value) => {
                  if (value && !array.includes(value)) {
                    setFormData({ ...formData, [field]: [...array, value] });
                  }
                }}
                formatOption={formatSkill}
                placeholder="+ Add a skill"
              />
            )}

            <button onClick={() => fetchSkillsByType(skillType)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
              + Load more skills
            </button>
          </div>
        ) : renderTags(array, field, true)}
      </div>
    );
  };

  const renderTargetDesignation = (label, field, value) => {
    const isEditing = editMode[field];
    return (
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500">{label}</span>
          {!isReadOnly && (
            !isEditing ? (
              <button onClick={() => handleEdit(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
            ) : (
              <button 
                onClick={() => handleSave(field)} 
                disabled={saving}
                className="text-xs text-indigo-600 hover:text-indigo-700 font-medium disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Done'}
              </button>
            )
          )}
        </div>
        {isEditing ? (
          <div className="space-y-2 animate-fade-in">
            {designationsLoading ? (
              <div className="input flex items-center text-gray-400 text-sm">
                <svg className="animate-spin h-4 w-4 mr-2 text-gray-300" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Loading roles...
              </div>
            ) : (
              <select
                value={value || ''}
                onChange={(e) => handleChange(field, e.target.value)}
                className="input text-sm"
                disabled={saving}
              >
                <option value="">Select target role...</option>
                {designations.map((designation, index) => (
                  <option key={index} value={designation}>{designation}</option>
                ))}
              </select>
            )}
          </div>
        ) : (
          <p className="text-gray-900 text-sm">{value || 'No target role set'}</p>
        )}
      </div>
    );
  };

  // Current role — a single designation chosen from the same list as Target
  // Role. Stored as a one-element array since `designition` is an array
  // elsewhere (e.g. CareerPathway reads designition[0]).
  const renderCurrentRole = (label) => {
    const field = 'designition';
    const isEditing = editMode[field];
    const currentValue = formData[field]?.[0] || '';
    return (
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500">{label}</span>
          {!isReadOnly && (
            !isEditing ? (
              <button onClick={() => handleEdit(field)} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
            ) : (
              <button
                onClick={() => handleSave(field)}
                disabled={saving}
                className="text-xs text-indigo-600 hover:text-indigo-700 font-medium disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Done'}
              </button>
            )
          )}
        </div>
        {isEditing ? (
          <div className="space-y-2 animate-fade-in">
            {designationsLoading ? (
              <div className="input flex items-center text-gray-400 text-sm">
                <svg className="animate-spin h-4 w-4 mr-2 text-gray-300" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Loading roles...
              </div>
            ) : (
              <select
                value={currentValue}
                onChange={(e) => setFormData({ ...formData, [field]: e.target.value ? [e.target.value] : [] })}
                className="input text-sm"
                disabled={saving}
              >
                <option value="">Select current role...</option>
                {designations.map((designation, index) => (
                  <option key={index} value={designation}>{designation}</option>
                ))}
              </select>
            )}
          </div>
        ) : (
          <p className="text-gray-900 text-sm">{currentValue || 'No role set'}</p>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Target Role */}
      <div className="card p-5 border-2 border-blue-500">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-base font-medium text-gray-900">Target Role</h3>
          {!isReadOnly && !editMode.target_designation && (
            <button 
              onClick={() => handleEdit('target_designation')} 
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Edit
            </button>
          )}
        </div>
        
        {editMode.target_designation ? (
          <div className="space-y-3">
            <select
              value={formData.target_designation || ''}
              onChange={(e) => handleChange('target_designation', e.target.value)}
              className="input w-full"
              disabled={saving}
            >
              <option value="">Select target role...</option>
              {designations.map((designation, index) => (
                <option key={index} value={designation}>{designation}</option>
              ))}
            </select>
            <div className="flex gap-2">
              <button 
                onClick={() => handleSave('target_designation')} 
                disabled={saving}
                className="btn-primary text-sm py-2 px-4 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button 
                onClick={() => setEditMode({ ...editMode, target_designation: false })}
                disabled={saving}
                className="btn-secondary text-sm py-2 px-4"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div>
            {formData.target_designation ? (
              <p className="text-lg font-medium text-gray-900">{formData.target_designation}</p>
            ) : (
              <p className="text-gray-500 text-sm">No target role set</p>
            )}
          </div>
        )}
      </div>

      {/* Profile Details */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-gray-900">Profile Details</h2>
          {formData.created_at && (
            <span className="text-xs text-gray-400">
              {new Date(formData.created_at).toLocaleDateString()}
            </span>
          )}
        </div>

        <div className="space-y-5 divide-y divide-gray-100 [&>*:not(:first-child)]:pt-5">
          {renderEditableField('Experience', 'total_exp', `${formData.total_exp} years`)}
          {renderEditableArray('Education', 'university', formData.university || [])}
          {renderCurrentRole('Current Role')}
          {renderEditableArray('Degrees', 'degree', formData.degree || [])}
          {renderSkillsArray('IT Skills', 'it_skills', formData.it_skills || [], 'it_skills')}
          {renderSkillsArray('Soft Skills', 'soft_skills', formData.soft_skills || [], 'soft_skills')}
          {renderSkillsArray('Languages', 'languages', formData.languages || [], 'languages')}
        </div>
      </div>

      {/* Skill Upload Modal */}
      <SkillUploadModal
        isOpen={showSkillUploadModal}
        onClose={() => setShowSkillUploadModal(false)}
        onSuccess={handleSkillUploadSuccess}
        preselectedSkill={lastUpdatedSkill}
      />
    </div>
  );
};

export default UserProfile;
