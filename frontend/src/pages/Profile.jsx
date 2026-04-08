import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../config/api-backend';
import PasswordInput from '../components/PasswordInput';
import Logo from '../components/Logo';

export default function Profile() {
  const { user, refreshUser, logout } = useAuth();

  const [formData, setFormData] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    email: user.email || '',
  });
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState('');
  const [profileError, setProfileError] = useState('');

  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setProfileError('');
    setProfileSuccess('');
    setProfileSaving(true);
    try {
      await authAPI.updateMe(formData);
      await refreshUser();
      setProfileSuccess('Profile updated.');
      setTimeout(() => setProfileSuccess(''), 3000);
    } catch (err) {
      const errors = err.response?.data;
      if (errors) {
        const firstError = Object.values(errors).flat()[0];
        setProfileError(typeof firstError === 'string' ? firstError : 'Failed to update profile.');
      } else {
        setProfileError('Failed to update profile.');
      }
    } finally {
      setProfileSaving(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (passwords.new_password !== passwords.confirm_password) {
      setPasswordError('New passwords do not match.');
      return;
    }

    setPasswordSaving(true);
    try {
      await authAPI.changePassword({
        current_password: passwords.current_password,
        new_password: passwords.new_password,
      });
      setPasswords({ current_password: '', new_password: '', confirm_password: '' });
      setPasswordSuccess('Password changed.');
      setTimeout(() => setPasswordSuccess(''), 3000);
    } catch (err) {
      setPasswordError(err.response?.data?.detail || 'Failed to change password.');
    } finally {
      setPasswordSaving(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <Logo size="header" />
            <span className="text-xl font-bold text-gray-900 tracking-tight">{process.env.REACT_APP_NAME}</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link to="/" className="btn-ghost text-sm py-1.5 px-3">Dashboard</Link>
            <button onClick={logout} className="btn-ghost text-sm py-1.5 px-3">Log out</button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 max-w-lg w-full mx-auto px-4 sm:px-6 py-8 space-y-6 animate-fade-in-up">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Account</h1>
          <p className="text-sm text-gray-400 mt-0.5">Manage your profile and security</p>
        </div>

        {/* Profile Info */}
        <form onSubmit={handleProfileSubmit} className="card p-5 space-y-4">
          <h2 className="text-sm font-semibold text-gray-900">Profile</h2>

          {profileError && (
            <div className="bg-red-50 text-red-600 px-4 py-2.5 rounded-xl text-sm animate-fade-in">{profileError}</div>
          )}
          {profileSuccess && (
            <div className="bg-emerald-50 text-emerald-600 px-4 py-2.5 rounded-xl text-sm animate-fade-in">{profileSuccess}</div>
          )}

          <div>
            <label className="label">Username</label>
            <div className="input bg-gray-100 text-gray-500 cursor-not-allowed">{user.username}</div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="first_name" className="label">First Name</label>
              <input
                id="first_name"
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label htmlFor="last_name" className="label">Last Name</label>
              <input
                id="last_name"
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div>
            <label htmlFor="email" className="label">Email</label>
            <input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="input"
            />
          </div>

          <button type="submit" disabled={profileSaving} className="btn-primary text-sm">
            {profileSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>

        {/* Change Password */}
        <form onSubmit={handlePasswordSubmit} className="card p-5 space-y-4">
          <h2 className="text-sm font-semibold text-gray-900">Change Password</h2>

          {passwordError && (
            <div className="bg-red-50 text-red-600 px-4 py-2.5 rounded-xl text-sm animate-fade-in">{passwordError}</div>
          )}
          {passwordSuccess && (
            <div className="bg-emerald-50 text-emerald-600 px-4 py-2.5 rounded-xl text-sm animate-fade-in">{passwordSuccess}</div>
          )}

          <div>
            <label htmlFor="current_password" className="label">Current Password</label>
            <PasswordInput
              id="current_password"
              required
              value={passwords.current_password}
              onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })}
              placeholder="Enter current password"
            />
          </div>

          <div>
            <label htmlFor="new_password" className="label">New Password</label>
            <PasswordInput
              id="new_password"
              required
              minLength={8}
              value={passwords.new_password}
              onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })}
              placeholder="At least 8 characters"
            />
          </div>

          <div>
            <label htmlFor="confirm_password" className="label">Confirm New Password</label>
            <PasswordInput
              id="confirm_password"
              required
              value={passwords.confirm_password}
              onChange={(e) => setPasswords({ ...passwords, confirm_password: e.target.value })}
              placeholder="Re-enter new password"
            />
          </div>

          <button type="submit" disabled={passwordSaving} className="btn-primary text-sm">
            {passwordSaving ? 'Changing...' : 'Change Password'}
          </button>
        </form>

        {/* Security Info */}
        <div className="card p-5 space-y-3">
          <h2 className="text-sm font-semibold text-gray-900">Security</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-700">Two-factor authentication</p>
              <p className="text-xs text-gray-400">Authenticator app</p>
            </div>
            <span className="tag tag-green">Enabled</span>
          </div>
        </div>
      </main>
    </div>
  );
}
