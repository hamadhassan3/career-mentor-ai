import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Avatar from './components/Avatar.jsx';
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
        <Route path="/" element={<ProtectedRoute><MainApp /></ProtectedRoute>} />
      </Routes>
      
      {user && user.totp_confirmed && <Avatar />}
    </>
  );
}

export default App;
