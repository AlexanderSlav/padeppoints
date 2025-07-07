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
      
      const { auth_url } = await authAPI.getGoogleLoginUrl();
      
      // Redirect to Google OAuth
      window.location.href = auth_url;
    } catch (err) {
      setError('Failed to start Google login');
      console.error('Google login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEmailLogin = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await authAPI.login(email, password);
      login(response.user, response.access_token);
    } catch (err) {
      setError('Login failed');
      console.error('Login error:', err);
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

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: '12px', fontSize: '16px' }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '12px', fontSize: '16px' }}
          />
          <button
            className="btn btn-secondary"
            onClick={handleEmailLogin}
            disabled={loading}
            style={{ width: '100%', fontSize: '16px' }}
          >
            {loading ? '🔄 Loading...' : 'Login'}
          </button>
        </div>

        <div style={{ marginTop: '32px', textAlign: 'center', color: '#718096' }}>
          <p>New to Tornetic?</p>
          <p>Just click "Login with Google" to get started!</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 
