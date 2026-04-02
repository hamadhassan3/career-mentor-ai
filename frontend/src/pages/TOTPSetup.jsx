import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import { authAPI } from '../config/api-backend';
import { useAuth } from '../context/AuthContext';

export default function TOTPSetup() {
  const [provisioningUri, setProvisioningUri] = useState('');
  const [secret, setSecret] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const { refreshUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    authAPI.totpSetup()
      .then((res) => {
        setProvisioningUri(res.data.provisioning_uri);
        setSecret(res.data.secret);
      })
      .catch(() => setError('Failed to load TOTP setup.'))
      .finally(() => setPageLoading(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authAPI.totpConfirm({ code });
      await refreshUser();
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (pageLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Career Mentor
          </h1>
          <p className="text-slate-500 mt-2">Set up two-factor authentication</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="text-center space-y-4">
            <p className="text-sm text-slate-600">
              Scan this QR code with your authenticator app (e.g. Google Authenticator, Authy):
            </p>
            {provisioningUri && (
              <div className="flex justify-center">
                <QRCodeSVG value={provisioningUri} size={200} />
              </div>
            )}
            <div className="text-xs text-slate-400">
              <p>Can't scan? Enter this key manually:</p>
              <p className="font-mono bg-slate-100 px-3 py-1.5 rounded mt-1 select-all break-all">
                {secret}
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="code" className="block text-sm font-medium text-slate-700 mb-1">
                Verification Code
              </label>
              <input
                id="code"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                required
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition text-center text-2xl tracking-widest"
                placeholder="000000"
              />
            </div>

            <button
              type="submit"
              disabled={loading || code.length !== 6}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2.5 rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Verifying...' : 'Enable Two-Factor Authentication'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
