import { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { resumeAPI } from './config/api-resume-processor.js';
import { useAuth } from './context/AuthContext';
import ResumeUpload from './components/ResumeUpload.jsx';
import UserProfile from './components/UserProfile.jsx';
import NextBestStep from './components/NextBestStep.jsx';
import CareerPathway from './components/CareerPathway.jsx';
import Login from './pages/Login.jsx';
import Signup from './pages/Signup.jsx';
import TOTPSetup from './pages/TOTPSetup.jsx';
import TOTPVerify from './pages/TOTPVerify.jsx';
import ForgotPassword from './pages/ForgotPassword.jsx';
import ResetPassword from './pages/ResetPassword.jsx';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!user) return <Navigate to="/login" />;

  // Force TOTP setup if not yet confirmed
  if (!user.totp_confirmed) return <Navigate to="/totp-setup" />;

  return children;
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

  const updateResumeData = (newData) => {
    setResumeData(newData);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6 flex items-center justify-between">
          <h1 className="text-2xl md:text-3xl font-bold">Career Mentor</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-indigo-100">
              {user.first_name || user.username}
            </span>
            <button
              onClick={logout}
              className="text-sm bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg transition"
            >
              Logout
            </button>
          </div>
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

function GuestOnly({ children }) {
  const { user } = useAuth();
  if (!user) return children;
  return <Navigate to={user.totp_confirmed ? '/' : '/totp-setup'} />;
}

function App() {
  const { user, loading, pendingTotp } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<GuestOnly><Login /></GuestOnly>} />
      <Route path="/signup" element={<GuestOnly><Signup /></GuestOnly>} />
      <Route path="/forgot-password" element={<GuestOnly><ForgotPassword /></GuestOnly>} />
      <Route path="/reset-password/:uid/:token" element={<GuestOnly><ResetPassword /></GuestOnly>} />
      <Route path="/totp-verify" element={pendingTotp ? <TOTPVerify /> : <Navigate to="/login" />} />
      <Route
        path="/totp-setup"
        element={
          user ? (
            user.totp_confirmed ? <Navigate to="/" /> : <TOTPSetup />
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
