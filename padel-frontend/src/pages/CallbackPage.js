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
      const success = urlParams.get('success');
      const token = urlParams.get('token');
      const error = urlParams.get('error');

      if (error) {
        setStatus('error');
        switch (error) {
          case 'token_failed':
            setError('Failed to get access token from Google');
            break;
          case 'auth_failed':
            setError('Authentication failed. Please try again.');
            break;
          default:
            setError('Authentication was cancelled or failed');
        }
        return;
      }

      if (!success || !token) {
        setStatus('error');
        setError('Invalid authentication response');
        return;
      }

      // Decode the user info from the JWT token
      try {
        const tokenParts = token.split('.');
        const payload = JSON.parse(atob(tokenParts[1]));
        
        const userData = {
          id: payload.sub,
          email: payload.email,
          full_name: payload.full_name
        };

        // Store token and user data
        login(userData, token);
        
        setStatus('success');
        
        // Redirect to dashboard after a short delay
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1500);

      } catch (jwtError) {
        console.error('JWT decode error:', jwtError);
        setStatus('error');
        setError('Invalid token received');
      }

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