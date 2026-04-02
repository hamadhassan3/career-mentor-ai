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
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-sm animate-fade-in-up">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-indigo-600 mb-4">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-gray-900">Two-factor setup</h1>
          <p className="text-gray-500 mt-1 text-sm">Secure your account with an authenticator app</p>
        </div>

        <div className="card p-6 space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm animate-fade-in">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <p className="text-sm text-gray-500 text-center">
              Scan with Google Authenticator, Authy, or similar:
            </p>
            {provisioningUri && (
              <div className="flex justify-center p-4 bg-white rounded-xl border border-gray-100">
                <QRCodeSVG value={provisioningUri} size={180} />
              </div>
            )}
            <details className="group">
              <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-500 text-center list-none">
                Can't scan? Enter key manually
              </summary>
              <div className="mt-2 font-mono text-xs bg-gray-50 px-3 py-2 rounded-lg select-all break-all text-gray-600 text-center animate-fade-in">
                {secret}
              </div>
            </details>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="code" className="label text-center w-full">Verification Code</label>
              <input
                id="code"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                required
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                className="input text-center text-xl tracking-[0.3em] font-medium"
                placeholder="000000"
              />
            </div>

            <button type="submit" disabled={loading || code.length !== 6} className="btn-primary w-full">
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                  Verifying...
                </span>
              ) : 'Enable Two-Factor Auth'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
