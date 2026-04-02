import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../config/api-backend';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  // Holds { totp_required, totp_token } when 2FA is needed during login
  const [pendingTotp, setPendingTotp] = useState(null);

  useEffect(() => {
    const tokens = localStorage.getItem('tokens');
    if (tokens) {
      authAPI.me()
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('tokens');
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    const res = await authAPI.login({ username, password });

    if (res.data.totp_required) {
      // Credentials valid but need TOTP verification
      setPendingTotp({ totp_token: res.data.totp_token });
      return { totp_required: true };
    }

    // No TOTP yet — tokens issued, may need TOTP setup
    localStorage.setItem('tokens', JSON.stringify({
      access: res.data.access,
      refresh: res.data.refresh,
    }));
    const userRes = await authAPI.me();
    setUser(userRes.data);
    return { totp_setup_required: res.data.totp_setup_required || false };
  };

  const verifyTotpLogin = async (code) => {
    if (!pendingTotp) throw new Error('No pending TOTP verification.');
    const res = await authAPI.totpLoginVerify({
      totp_token: pendingTotp.totp_token,
      code,
    });
    localStorage.setItem('tokens', JSON.stringify({
      access: res.data.access,
      refresh: res.data.refresh,
    }));
    setPendingTotp(null);
    const userRes = await authAPI.me();
    setUser(userRes.data);
  };

  const register = async (data) => {
    await authAPI.register(data);
    return await login(data.username, data.password);
  };

  const refreshUser = async () => {
    const res = await authAPI.me();
    setUser(res.data);
  };

  const logout = () => {
    localStorage.removeItem('tokens');
    setUser(null);
    setPendingTotp(null);
  };

  return (
    <AuthContext.Provider value={{
      user, loading, pendingTotp,
      login, verifyTotpLogin, register, refreshUser, logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
