import React, { useEffect, useState } from 'react';
import { useAuth } from '../components/AuthContext';

const CallbackPage = () => {
  const { login } = useAuth();
  const [status, setStatus] = useState('processing');
  const [error, setError] = useState('');

  useEffect(() => {
    handleCallback();
  }, []);

  const handleCallback = async () => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const error = urlParams.get('error');

      if (error) {
        setStatus('error');
        setError('Authentication was cancelled or failed');
        return;
      }

      if (!code) {
        setStatus('error');
        setError('No authorization code received');
        return;
      }

      // Call your backend's callback endpoint
      const response = await fetch('http://localhost:8000/api/v1/auth/google/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, state }),
      });

      if (!response.ok) {
        throw new Error('Authentication failed');
      }

      const data = await response.json();
      
      // Store token and user data
      login(data.user, data.access_token);
      
      setStatus('success');
      
      // Redirect to dashboard after a short delay
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);

    } catch (err) {
      console.error('Callback error:', err);
      setStatus('error');
      setError('Authentication failed. Please try again.');
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🎾 Padel Points</h1>
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