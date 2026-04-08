import { useState, useEffect } from 'react';
import { resumeAPI } from '../config/api-backend';

const ResumeHistory = ({ onResumeSelect, onUploadNew }) => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      const response = await resumeAPI.getResumes();
      setResumes(response.data);
    } catch (err) {
      setError('Failed to load resume history');
      console.error('Failed to fetch resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResumeSelect = async (resumeId) => {
    try {
      const response = await resumeAPI.getResume(resumeId);
      onResumeSelect(response.data);
    } catch (err) {
      console.error('Failed to load resume:', err);
      alert('Failed to load selected resume');
    }
  };

  const handleDeleteResume = async (resumeId, event) => {
    event.stopPropagation();
    if (window.confirm('Are you sure you want to delete this resume?')) {
      try {
        await resumeAPI.deleteResume(resumeId);
        setResumes(resumes.filter(resume => resume.id !== resumeId));
      } catch (err) {
        console.error('Failed to delete resume:', err);
        alert('Failed to delete resume');
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <svg className="animate-spin h-8 w-8 mx-auto text-gray-400" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-sm text-gray-500 mt-2">Loading your resumes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button onClick={fetchResumes} className="btn-secondary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (resumes.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center space-y-4 max-w-md">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100">
            <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">No resumes yet</h3>
            <p className="text-sm text-gray-500 mt-1">Upload your first resume to get started with career insights</p>
          </div>
          <button onClick={onUploadNew} className="btn-primary">
            Upload Resume
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Your Resumes</h2>
          <p className="text-sm text-gray-500 mt-1">Select a resume to view insights or upload a new one</p>
        </div>
        <button onClick={onUploadNew} className="btn-secondary">
          Upload New Resume
        </button>
      </div>

      <div className="grid gap-4">
        {resumes.map((resume) => (
          <div
            key={resume.id}
            onClick={() => handleResumeSelect(resume.id)}
            className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all cursor-pointer group"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-start space-x-3">
                  <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-100 group-hover:bg-indigo-200 transition-colors">
                    <svg className="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {resume.title || resume.original_filename || `Resume ${resume.id}`}
                    </h3>
                    {resume.target_designation && (
                      <p className="text-xs text-indigo-600 mt-1">
                        Target: {resume.target_designation}
                      </p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(resume.created_at)}
                      {resume.updated_at !== resume.created_at && (
                        <span> · Updated {formatDate(resume.updated_at)}</span>
                      )}
                    </p>
                  </div>
                </div>
              </div>
              <button
                onClick={(e) => handleDeleteResume(resume.id, e)}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 text-gray-400 hover:text-red-500"
                title="Delete resume"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResumeHistory;