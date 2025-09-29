import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';
import '../styles/globals.css';
import './LoginPage.css';

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
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
    <div className="login-page">
      <div className="login-container">
        <div className="login-brand">
          <span className="brand-logo">🏆</span>
          <h1 className="brand-name gradient-text">Tornetic</h1>
          <p className="brand-tagline">Tournament Management Made Simple</p>
        </div>

        <div className="login-card card">
          <div className="card-header">
            <h2 className="card-title text-center">Welcome Back!</h2>
            <p className="card-subtitle text-center">Sign in to continue to your dashboard</p>
          </div>
          
          {error && (
            <div className="alert alert-error">
              <span>⚠️</span>
              {error}
            </div>
          )}

          <div className="login-methods">
            <button
              className="btn btn-primary btn-full btn-lg"
              onClick={handleGoogleLogin}
              disabled={loading}
            >
              <span>🔐</span>
              {loading ? 'Loading...' : 'Continue with Google'}
            </button>

            <div className="divider">
              <span>OR</span>
            </div>

            <form onSubmit={handleEmailLogin} className="login-form">
              <div className="form-group">
                <label className="form-label">Email</label>
                <input
                  type="email"
                  className="form-input"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              
              <button
                className="btn btn-primary btn-full btn-lg"
                type="submit"
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>
          </div>

          <div className="login-footer">
            <p className="text-center text-muted">
              New to Tornetic?
            </p>
            <button 
              onClick={() => navigate('/register')}
              className="btn btn-ghost btn-full"
            >
              Create an account
            </button>
          </div>
        </div>
        
        <div className="login-links">
          <button onClick={() => navigate('/')} className="link-button">
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 