import React, { useState } from 'react';
import { authAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';

const LoginPage = () => {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      
      const { authorization_url } = await authAPI.getGoogleLoginUrl();
      
      // Redirect to Google OAuth
      window.location.href = authorization_url;
    } catch (err) {
      setError('Failed to start Google login');
      console.error('Google login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');

      const { access_token } = await authAPI.loginWithEmail(email, password);
      localStorage.setItem('access_token', access_token);
      const userData = await authAPI.getCurrentUser();
      login(userData, access_token);
    } catch (err) {
      setError('Email login failed');
      console.error('Email login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🎾 Tornetic</h1>
        <p>Tournament Management Made Simple</p>
      </div>

      <div className="card">
        <h2 style={{ marginBottom: '24px', textAlign: 'center', color: '#2d3748' }}>
          Welcome Back!
        </h2>
        
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <button
            className="btn"
            onClick={handleGoogleLogin}
            disabled={loading}
            style={{ width: '100%', fontSize: '18px', padding: '16px' }}
          >
            {loading ? '🔄 Loading...' : '🔐 Login with Google'}
          </button>

          <div style={{ textAlign: 'center', color: '#718096', margin: '16px 0' }}>
            — OR —
          </div>

          <form onSubmit={handleEmailLogin} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ padding: '8px', fontSize: '16px' }}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ padding: '8px', fontSize: '16px' }}
            />
            <button
              className="btn btn-secondary"
              type="submit"
              disabled={loading}
              style={{ width: '100%', fontSize: '16px' }}
            >
              {loading ? '🔄 Loading...' : 'Login'}
            </button>
          </form>
        </div>

        <div style={{ marginTop: '32px', textAlign: 'center', color: '#718096' }}>
          <p>New to Tornetic?</p>
          <a href="/register">Create an account</a> or use Google
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 