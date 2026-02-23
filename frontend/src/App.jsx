import { useState } from 'react';
import { resumeAPI } from './config/api-resume-processor.js';
import ResumeUpload from './components/ResumeUpload.jsx';
import UserProfile from './components/UserProfile.jsx';
import NextBestStep from './components/NextBestStep.jsx';
import CareerPathway from './components/CareerPathway.jsx';

function App() {
  const [resumeData, setResumeData] = useState(null);
  const [targetDesignation, setTargetDesignation] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleResumeUpload = async (file, designation) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await resumeAPI.uploadResume(formData);
      setResumeData(response.data);
      setTargetDesignation(designation);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload resume. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateResumeData = (newData) => {
    setResumeData(newData);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-2xl md:text-3xl font-bold text-center">Career Mentor</h1>
        </div>
      </header>
      
      <main className="flex-1 container mx-auto px-4 py-6 md:py-8 max-w-7xl">
        {!resumeData ? (
          <div className="flex justify-center items-center min-h-[60vh]">
            <ResumeUpload 
              onProceed={handleResumeUpload} 
              loading={loading} 
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
            <div className="space-y-6">
              <UserProfile 
                resumeData={resumeData} 
                onUpdate={updateResumeData} 
              />
            </div>
            
            <div className="space-y-6">
              <NextBestStep resumeData={resumeData} targetDesignation={targetDesignation}/>
              <CareerPathway resumeData={resumeData} targetDesignation={targetDesignation}/>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
