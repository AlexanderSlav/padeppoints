import React, { useEffect, useState, useRef } from 'react';
import { useAuth } from '../components/AuthContext';

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
      const success = urlParams.get('success');
      const token = urlParams.get('token');
      const error = urlParams.get('error');

      console.log('🔍 CallbackPage: URL params - success:', success, 'token:', token ? 'EXISTS' : 'MISSING', 'error:', error);

      if (error) {
        console.log('❌ CallbackPage: Error in URL params:', error);
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
        console.log('❌ CallbackPage: Missing success or token params');
        setStatus('error');
        setError('Invalid authentication response');
        return;
      }

      // Decode the user info from the JWT token
      try {
        console.log('🔍 CallbackPage: Decoding JWT token');
        const tokenParts = token.split('.');
        const payload = JSON.parse(atob(tokenParts[1]));
        console.log('🔍 CallbackPage: JWT payload:', payload);
        
        const userData = {
          id: payload.sub,
          email: payload.email,
          full_name: payload.full_name
        };

        console.log('🔍 CallbackPage: Extracted user data:', userData);

        // Store token and user data
        console.log('✅ CallbackPage: Calling login() with user data and token');
        login(userData, token);
        
        setStatus('success');
        console.log('✅ CallbackPage: Login successful, redirecting in 1.5s');
        
        // Redirect to dashboard after a short delay
        setTimeout(() => {
          console.log('🔄 CallbackPage: Redirecting to dashboard');
          window.location.href = '/dashboard';
        }, 1500);

      } catch (jwtError) {
        console.error('❌ CallbackPage: JWT decode error:', jwtError);
        setStatus('error');
        setError('Invalid token received');
      }

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