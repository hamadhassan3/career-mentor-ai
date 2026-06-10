import { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { resumeAPI as resumeProcessorAPI } from '../config/api-resume-processor.js';
import { resumeAPI } from '../config/api-backend.js';
import { setState } from '../store/avatarSlice';
import ResumeUpload from './ResumeUpload.jsx';
import ResumeHistory from './ResumeHistory.jsx';
import UserProfile from './UserProfile.jsx';
import NextBestStep from './NextBestStep.jsx';
import CareerPathway from './CareerPathway.jsx';
import DailyNudge from './DailyNudge.jsx';

export default function Dashboard({ shouldShowUpload = false, onUploadStateChange, onBackToHistory, onNavigateToProgress }) {
  const [resumeData, setResumeData] = useState(null);
  const [targetDesignation, setTargetDesignation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(shouldShowUpload);
  const dispatch = useDispatch();

  useEffect(() => {
    checkForExistingResumes();
  }, []);

  useEffect(() => {
    setShowUpload(shouldShowUpload);
  }, [shouldShowUpload]);

  const checkForExistingResumes = async () => {
    try {
      const response = await resumeAPI.getActiveResume();
      if (response.data) {
        setResumeData(response.data);
        setTargetDesignation(response.data.target_designation);
      }
    } catch (error) {
      // Fallback to latest resume if no active resume found
      try {
        const fallbackResponse = await resumeAPI.getLatestResume();
        if (fallbackResponse.data) {
          setResumeData(fallbackResponse.data);
          setTargetDesignation(fallbackResponse.data.target_designation);
          }
      } catch (fallbackError) {
      }
    }
  };

  const handleResumeUpload = async (file, designation) => {
    setLoading(true);
    dispatch(setState('thinking'));
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await resumeProcessorAPI.uploadResume(formData);
      
      const resumeDataWithMetadata = {
        ...response.data,
        target_designation: designation,
        original_filename: file.name,
        title: `Resume - ${new Date().toLocaleDateString()}`
      };
      
      const createdResume = await resumeAPI.createResume(resumeDataWithMetadata);

      // Use the backend response (includes is_active, id, etc.) so the UI
      // reflects the active resume immediately without needing a page reload.
      setResumeData(createdResume.data);
      setTargetDesignation(designation);
      setShowUpload(false);
      onUploadStateChange?.(false);
      dispatch(setState('idle'));
    } catch (error) {
      console.error('Upload error:', error);
      dispatch(setState('error'));
      alert('Failed to upload resume. Please try again.');
      setTimeout(() => dispatch(setState('idle')), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleResumeSelect = (selectedResume) => {
    setResumeData(selectedResume);
    setTargetDesignation(selectedResume.target_designation);
  };

  const handleUploadNew = () => {
    setShowUpload(true);
    onUploadStateChange?.(true);
  };

  const handleBackToHistory = () => {
    setShowUpload(false);
    onUploadStateChange?.(false);
    onBackToHistory?.();
  };

  const handleActivateResume = async (resumeId) => {
    try {
      await resumeAPI.activateResume(resumeId);
      // Reload the active resume data
      checkForExistingResumes();
    } catch (error) {
      console.error('Failed to activate resume:', error);
      alert('Failed to activate resume. Please try again.');
    }
  };

  const handleResumeUpdate = (updatedResumeData) => {
    setResumeData(updatedResumeData);
    setTargetDesignation(updatedResumeData.target_designation);
  };

  return (
    <>
      {showUpload ? (
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleBackToHistory}
              className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
            >
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to History
            </button>
          </div>
          <div className="flex justify-center items-center min-h-[65vh] animate-fade-in">
            <ResumeUpload onProceed={handleResumeUpload} loading={loading} />
          </div>
        </div>
      ) : resumeData ? (
        <div className="space-y-6 animate-fade-in-up">
          {!resumeData.is_active && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-100">
                  <svg className="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-amber-800">Viewing Resume in Read-Only Mode</p>
                  <p className="text-xs text-amber-600">Activate this resume to make edits</p>
                </div>
              </div>
              <button
                onClick={() => handleActivateResume(resumeData.id)}
                className="px-3 py-1.5 bg-amber-600 text-white text-sm rounded-lg hover:bg-amber-700 transition-colors"
              >
                Activate Resume
              </button>
            </div>
          )}
          <DailyNudge />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-5 space-y-6">
              <UserProfile 
                resumeData={resumeData} 
                onUpdate={handleResumeUpdate} 
                isReadOnly={!resumeData.is_active}
                onNavigateToProgress={onNavigateToProgress}
              />
            </div>
            <div className="lg:col-span-7 space-y-6">
              <NextBestStep resumeData={resumeData} targetDesignation={targetDesignation} />
              <CareerPathway resumeData={resumeData} targetDesignation={targetDesignation} />
            </div>
          </div>
        </div>
      ) : (
        <div className="flex justify-center items-center min-h-[65vh] animate-fade-in">
          <ResumeHistory 
            onResumeSelect={handleResumeSelect} 
            onUploadNew={handleUploadNew} 
          />
        </div>
      )}
    </>
  );
}