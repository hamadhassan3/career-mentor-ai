import React, { useRef, useState, useEffect } from "react";
import SearchableDropdown from "./SearchableDropdown";
import { resumeAPI } from "../config/api-resume-processor";

const ResumeUpload = ({ loading, onProceed }) => {
  const fileInputRef = useRef(null);

  const [resume, setResume] = useState(null);
  const [designation, setDesignation] = useState("");

  const [designations, setDesignations] = useState([]);
  const [designationLoading, setDesignationLoading] = useState(true);

  /* ---------------- Fetch Designations ---------------- */
  useEffect(() => {
    const fetchDesignations = async () => {
      try {
        setDesignationLoading(true);

        const response = await resumeAPI.getDesignations();

        const data =
          response.data?.designations ||
          response.data?.data ||
          response.data ||
          [];

        setDesignations(data);
      } catch (err) {
        console.error("Failed to load designations", err);
        alert("Unable to load designations");
      } finally {
        setDesignationLoading(false);
      }
    };

    fetchDesignations();
  }, []);

  /* ---------------- File Handling ---------------- */

  const handleFile = (file) => {
    if (file && file.type === "application/pdf") {
      setResume(file);
    } else {
      alert("Please select a PDF file");
    }
  };

  const handleFileSelect = (event) => {
    handleFile(event.target.files[0]);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    handleFile(event.dataTransfer.files[0]);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleClickUpload = () => {
    fileInputRef.current.click();
  };

  /* ---------------- Validation ---------------- */

  const canProceed = Boolean(resume && designation);

  /* ---------------- UI ---------------- */

  return (
    <div className="w-full max-w-lg mx-auto p-4 space-y-6">

      {/* Target Designation */}
      <div>
        <h3 className="text-lg font-semibold mb-2">
          Target Designation
        </h3>

        {designationLoading ? (
          <div className="border rounded-lg px-4 py-3 text-gray-500">
            Loading designations...
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
      <div
        className="border-2 border-dashed border-gray-300 hover:border-indigo-500 rounded-xl p-8 md:p-12 text-center bg-white transition-all duration-300 hover:bg-indigo-50 cursor-pointer"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={handleClickUpload}
      >
        <div className="text-4xl md:text-5xl mb-4">📄</div>

        <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-2">
          Upload Your Resume
        </h2>

        <p className="text-gray-600 mb-6">
          Drag & drop your PDF resume here or click to browse
        </p>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className="hidden"
        />

        <p className="text-gray-500 text-sm">
          Only PDF files are supported
        </p>

        {resume && (
          <p className="mt-4 text-green-600 text-sm font-medium">
            ✅ {resume.name}
          </p>
        )}
      </div>

      {/* Proceed Button */}
      <button
        onClick={() => onProceed?.(resume, designation)}
        disabled={!canProceed || loading}
        className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition"
      >
        {loading ? "Processing..." : "Proceed"}
      </button>
    </div>
  );
};

export default ResumeUpload;