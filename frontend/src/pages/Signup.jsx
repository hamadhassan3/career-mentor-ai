import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import PasswordInput from '../components/PasswordInput';
import Logo from '../components/Logo';

export default function Signup() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const { confirmPassword, ...data } = formData;
      await register(data);
      navigate('/totp-setup');
    } catch (err) {
      const errors = err.response?.data;
      if (errors) {
        const firstError = Object.values(errors).flat()[0];
        setError(typeof firstError === 'string' ? firstError : 'Registration failed. Please try again.');
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-sm animate-fade-in-up">
        <div className="text-center mb-8">
          <Logo size="lg" className="mb-4" />
          <h1 className="text-2xl font-semibold text-gray-900">Create account</h1>
          <p className="text-gray-500 mt-1 text-sm">Get started with {process.env.REACT_APP_NAME}</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm animate-fade-in">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="first_name" className="label">First Name</label>
              <input id="first_name" name="first_name" type="text" value={formData.first_name} onChange={handleChange} className="input" placeholder="John" />
            </div>
            <div>
              <label htmlFor="last_name" className="label">Last Name</label>
              <input id="last_name" name="last_name" type="text" value={formData.last_name} onChange={handleChange} className="input" placeholder="Doe" />
            </div>
          </div>

          <div>
            <label htmlFor="username" className="label">Username</label>
            <input id="username" name="username" type="text" required value={formData.username} onChange={handleChange} className="input" placeholder="johndoe" />
          </div>

          <div>
            <label htmlFor="email" className="label">Email</label>
            <input id="email" name="email" type="email" required value={formData.email} onChange={handleChange} className="input" placeholder="john@example.com" />
          </div>

          <div>
            <label htmlFor="password" className="label">Password</label>
            <PasswordInput id="password" name="password" required minLength={8} value={formData.password} onChange={handleChange} placeholder="At least 8 characters" />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="label">Confirm Password</label>
            <PasswordInput id="confirmPassword" name="confirmPassword" required value={formData.confirmPassword} onChange={handleChange} placeholder="Re-enter your password" />
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                Creating account...
              </span>
            ) : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
