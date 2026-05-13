import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from './context/AuthContext';
import Avatar from './components/Avatar.jsx';
import Header from './components/Header.jsx';
import MainApp from './views/MainApp.jsx';
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


function App() {
  const { user, loading, pendingTotp } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');

  if (loading) return <Spinner />;

  const isProtectedRoute = location.pathname === '/' || location.pathname === '/profile';
  const showHeader = user && user.totp_confirmed && isProtectedRoute;

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    if (location.pathname === '/profile') {
      navigate('/');
    }
  };

  return (
    <>
      {showHeader && (
        <Header 
          activeTab={activeTab} 
          onTabChange={handleTabChange}
          showTabs={true}
        />
      )}
      
      <div className={user && user.totp_confirmed ? "pb-32" : ""}>
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
          <Route path="/" element={<ProtectedRoute><MainApp activeTab={activeTab} onTabChange={handleTabChange} /></ProtectedRoute>} />
        </Routes>
      </div>
      
      {user && user.totp_confirmed && <Avatar />}
    </>
  );
}

export default App;
