import React, { useRef } from 'react';

const ResumeUpload = ({ onUpload, loading }) => {
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      onUpload(file);
    } else {
      alert('Please select a PDF file');
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      onUpload(file);
    } else {
      alert('Please drop a PDF file');
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  return (
    <div className="w-full max-w-lg mx-auto p-4">
      <div 
        className="border-2 border-dashed border-gray-300 hover:border-indigo-500 rounded-xl p-8 md:p-12 text-center bg-white transition-all duration-300 hover:bg-indigo-50 cursor-pointer"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={handleButtonClick}
      >
        <div className="text-4xl md:text-5xl mb-4">📄</div>
        <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-2">Upload Your Resume</h2>
        <p className="text-gray-600 mb-6 text-sm md:text-base">
          Drag and drop your PDF resume here or click to browse
        </p>
        
        <button 
          className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 disabled:cursor-not-allowed"
          onClick={handleButtonClick}
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Choose File'}
        </button>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <p className="text-gray-500 text-xs md:text-sm mt-4">Only PDF files are supported</p>
      </div>
    </div>
  );
};

export default ResumeUpload;