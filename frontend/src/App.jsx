import { useState } from 'react';
import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { resumeAPI } from './config/api-resume-processor.js';
import { useAuth } from './context/AuthContext';
import ResumeUpload from './components/ResumeUpload.jsx';
import UserProfile from './components/UserProfile.jsx';
import NextBestStep from './components/NextBestStep.jsx';
import CareerPathway from './components/CareerPathway.jsx';
import Avatar from './components/Avatar.jsx';
import Logo from './components/Logo.jsx';
import Login from './pages/Login.jsx';
import Signup from './pages/Signup.jsx';
import TOTPSetup from './pages/TOTPSetup.jsx';
import TOTPVerify from './pages/TOTPVerify.jsx';
import ForgotPassword from './pages/ForgotPassword.jsx';
import ResetPassword from './pages/ResetPassword.jsx';
import Profile from './pages/Profile.jsx';

function Spinner() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-indigo-600"></div>
    </div>
  );
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" />;
  if (!user.totp_confirmed) return <Navigate to="/totp-setup" />;
  return children;
}

function GuestOnly({ children }) {
  const { user } = useAuth();
  if (!user) return children;
  return <Navigate to={user.totp_confirmed ? '/' : '/totp-setup'} />;
}

function Dashboard() {
  const [resumeData, setResumeData] = useState(null);
  const [targetDesignation, setTargetDesignation] = useState(null);
  const [loading, setLoading] = useState(false);
  const { user, logout } = useAuth();

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

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Logo size="header" />
            <span className="text-xl font-bold text-gray-900 tracking-tight">Career Mentor</span>
          </div>

          <div className="flex items-center gap-1">
            <Link to="/profile" className="btn-ghost text-sm py-1.5 px-3 hidden sm:block">
              {user.first_name || user.username}
            </Link>
            <Link to="/profile" className="btn-ghost py-1.5 px-2 sm:hidden" aria-label="Profile">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </Link>
            <button onClick={logout} className="btn-ghost text-sm py-1.5 px-3">
              Log out
            </button>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 md:py-8">
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
      </main>
    </div>
  );
}

function App() {
  const { user, loading, pendingTotp } = useAuth();

  if (loading) return <Spinner />;

  return (
    <>
      <Routes>
        <Route path="/login" element={<GuestOnly><Login /></GuestOnly>} />
        <Route path="/signup" element={<GuestOnly><Signup /></GuestOnly>} />
        <Route path="/forgot-password" element={<GuestOnly><ForgotPassword /></GuestOnly>} />
        <Route path="/reset-password/:uid/:token" element={<GuestOnly><ResetPassword /></GuestOnly>} />
        <Route path="/totp-verify" element={pendingTotp ? <TOTPVerify /> : <Navigate to="/login" />} />
        <Route
          path="/totp-setup"
          element={user ? (user.totp_confirmed ? <Navigate to="/" /> : <TOTPSetup />) : <Navigate to="/login" />}
        />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      </Routes>
      
      {user && user.totp_confirmed && <Avatar />}
    </>
  );
}

export default App;
