import React, { useEffect, useState, useRef } from 'react';
import { useAuth } from '../components/AuthContext';
import { authAPI } from '../services/api';

const CallbackPage = () => {
  const { login } = useAuth();
  const [status, setStatus] = useState('processing');
  const [error, setError] = useState('');
  const hasRun = useRef(false);

  useEffect(() => {
    console.log('🔄 CallbackPage: Component mounted, handling callback');
    
    // Prevent double execution in React StrictMode
    if (hasRun.current) {
      console.log('🔄 CallbackPage: Already processed, skipping');
      return;
    }
    hasRun.current = true;
    
    handleCallback();
  }, []);

  const handleCallback = async () => {
    try {
      console.log('🔍 CallbackPage: Parsing URL parameters');
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');

      if (!code || !state) {
        console.log('❌ CallbackPage: Missing code or state params');
        setStatus('error');
        setError('Invalid authentication response');
        return;
      }

      const data = await authAPI.completeGoogleLogin(code, state);
      login(data.user, data.access_token);

      setStatus('success');
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1500);

    } catch (err) {
      console.error('❌ CallbackPage: General callback error:', err);
      setStatus('error');
      setError('Authentication failed. Please try again.');
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🎾 Tornetic</h1>
      </div>

      <div className="card">
        {status === 'processing' && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔄</div>
            <h2>Processing Authentication...</h2>
            <p style={{ color: '#718096' }}>Please wait while we log you in.</p>
          </div>
        )}

        {status === 'success' && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
            <h2 style={{ color: '#2f855a' }}>Login Successful!</h2>
            <p style={{ color: '#718096' }}>Redirecting to your dashboard...</p>
          </div>
        )}

        {status === 'error' && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>❌</div>
            <h2 style={{ color: '#c53030' }}>Authentication Failed</h2>
            <div className="error" style={{ marginTop: '16px' }}>
              {error}
            </div>
            <div style={{ marginTop: '24px' }}>
              <a href="/login" className="btn">
                Try Again
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CallbackPage; 
