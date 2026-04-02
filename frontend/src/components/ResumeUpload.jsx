import React, { useRef, useState, useEffect } from "react";
import SearchableDropdown from "./SearchableDropdown";
import { resumeAPI } from "../config/api-resume-processor";

const ResumeUpload = ({ loading, onProceed }) => {
  const fileInputRef = useRef(null);
  const [resume, setResume] = useState(null);
  const [designation, setDesignation] = useState("");
  const [designations, setDesignations] = useState([]);
  const [designationLoading, setDesignationLoading] = useState(true);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    const fetchDesignations = async () => {
      try {
        setDesignationLoading(true);
        const response = await resumeAPI.getDesignations();
        const data = response.data?.designations || response.data?.data || response.data || [];
        setDesignations(data);
      } catch (err) {
        console.error("Failed to load designations", err);
      } finally {
        setDesignationLoading(false);
      }
    };
    fetchDesignations();
  }, []);

  const handleFile = (file) => {
    if (file && file.type === "application/pdf") {
      setResume(file);
    } else {
      alert("Please select a PDF file");
    }
  };

  const canProceed = Boolean(resume && designation);

  return (
    <div className="w-full max-w-md space-y-5">
      <div className="text-center mb-2">
        <h2 className="text-xl font-semibold text-gray-900">Get started</h2>
        <p className="text-sm text-gray-500 mt-1">Upload your resume and select your target role</p>
      </div>

      {/* Target Designation */}
      <div>
        <label className="label">Target Role</label>
        {designationLoading ? (
          <div className="input flex items-center text-gray-400 text-sm">
            <svg className="animate-spin h-4 w-4 mr-2 text-gray-300" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
            Loading roles...
          </div>
        ) : (
          <SearchableDropdown
            options={designations}
            value={designation}
            onChange={setDesignation}
            placeholder="Select target role..."
          />
        )}
      </div>

      {/* Upload Area */}
      <div>
        <label className="label">Resume</label>
        <div
          className={`
            relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer
            transition-all duration-200
            ${dragOver
              ? 'border-indigo-400 bg-indigo-50'
              : resume
                ? 'border-emerald-300 bg-emerald-50/50'
                : 'border-gray-200 bg-gray-50/50 hover:border-gray-300 hover:bg-gray-50'
            }
          `}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onClick={() => fileInputRef.current.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={(e) => handleFile(e.target.files[0])}
            className="hidden"
          />

          {resume ? (
            <div className="animate-fade-in space-y-2">
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-emerald-100">
                <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-700">{resume.name}</p>
              <p className="text-xs text-gray-400">Click to change file</p>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-gray-100">
                <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <p className="text-sm text-gray-500">
                <span className="font-medium text-indigo-600">Upload</span> or drag & drop
              </p>
              <p className="text-xs text-gray-400">PDF only</p>
            </div>
          )}
        </div>
      </div>

      {/* Proceed */}
      <button
        onClick={() => onProceed?.(resume, designation)}
        disabled={!canProceed || loading}
        className="btn-primary w-full"
      >
        {loading ? (
          <span className="inline-flex items-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
            Processing...
          </span>
        ) : 'Continue'}
      </button>
    </div>
  );
};

export default ResumeUpload;
