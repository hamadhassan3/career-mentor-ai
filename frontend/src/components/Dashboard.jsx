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

export default function Dashboard({ shouldShowUpload = false, onUploadStateChange, onBackToHistory }) {
  const [resumeData, setResumeData] = useState(null);
  const [targetDesignation, setTargetDesignation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(shouldShowUpload);
  const [hasResumes, setHasResumes] = useState(false);
  const dispatch = useDispatch();

  useEffect(() => {
    checkForExistingResumes();
  }, []);

  useEffect(() => {
    setShowUpload(shouldShowUpload);
  }, [shouldShowUpload]);

  const checkForExistingResumes = async () => {
    try {
      const response = await resumeAPI.getLatestResume();
      if (response.data) {
        setResumeData(response.data);
        setTargetDesignation(response.data.target_designation);
        setHasResumes(true);
      }
    } catch (error) {
      setHasResumes(false);
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
      
      await resumeAPI.createResume(resumeDataWithMetadata);
      
      setResumeData(resumeDataWithMetadata);
      setTargetDesignation(designation);
      setShowUpload(false);
      onUploadStateChange?.(false);
      setHasResumes(true);
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
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-5 space-y-6">
              <UserProfile resumeData={resumeData} onUpdate={setResumeData} />
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