import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { resumeAPI } from '../config/api-resume-processor.js';
import { setState } from '../store/avatarSlice';
import ResumeUpload from './ResumeUpload.jsx';
import UserProfile from './UserProfile.jsx';
import NextBestStep from './NextBestStep.jsx';
import CareerPathway from './CareerPathway.jsx';

export default function Dashboard() {
  const [resumeData, setResumeData] = useState(null);
  const [targetDesignation, setTargetDesignation] = useState(null);
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();

  const handleResumeUpload = async (file, designation) => {
    setLoading(true);
    dispatch(setState('thinking'));
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await resumeAPI.uploadResume(formData);
      setResumeData(response.data);
      setTargetDesignation(designation);
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

  return (
    <>
      {!resumeData ? (
        <div className="flex justify-center items-center min-h-[65vh] animate-fade-in">
          <ResumeUpload onProceed={handleResumeUpload} loading={loading} />
        </div>
      ) : (
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
      )}
    </>
  );
}