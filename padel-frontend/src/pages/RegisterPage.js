import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import { FaTrophy, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';
import '../styles/globals.css';
import './RegisterPage.css';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      await authAPI.register(email, password, fullName);
      setSuccess(true);
    } catch (err) {
      console.error('Registration error:', err);

      // Parse error message from backend
      let errorMessage = 'Registration failed. Please try again.';

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        // Handle specific error codes
        if (detail === 'REGISTER_USER_ALREADY_EXISTS') {
          errorMessage = 'An account with this email already exists. Please sign in instead.';
        } else if (detail === 'REGISTER_INVALID_PASSWORD') {
          errorMessage = 'Password must be at least 8 characters long.';
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      } else if (err.response?.status === 400) {
        errorMessage = 'Invalid registration data. Please check your information.';
      } else if (err.response?.status === 422) {
        errorMessage = 'Please provide a valid email address and password.';
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="register-page">
        <div className="register-container">
          <div className="success-card card">
            <div className="success-icon"><FaCheckCircle /></div>
            <h2 className="card-title">Account Created!</h2>
            <p className="card-subtitle">Your account has been successfully created. Please log in with your credentials.</p>
            <button onClick={() => navigate('/login')} className="btn btn-primary btn-lg">
              Go to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-brand">
          <span className="brand-logo"><FaTrophy /></span>
          <h1 className="brand-name gradient-text">Tornetic</h1>
          <p className="brand-tagline">Join the tournament revolution</p>
        </div>

        <div className="register-card card">
          <div className="card-header">
            <h2 className="card-title text-center">Create Account</h2>
            <p className="card-subtitle text-center">Start organizing tournaments in minutes</p>
          </div>
          
          {error && (
            <div className="alert alert-error">
              <FaExclamationTriangle />
              <div>
                {error}
                {error.includes('already exists') && (
                  <div style={{ marginTop: '8px' }}>
                    <button
                      onClick={() => navigate('/login')}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#fff',
                        color: '#e53e3e',
                        border: '1px solid #e53e3e',
                        borderRadius: '4px',
                        fontSize: '13px',
                        fontWeight: '500',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.backgroundColor = '#e53e3e';
                        e.target.style.color = '#fff';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.backgroundColor = '#fff';
                        e.target.style.color = '#e53e3e';
                      }}
                    >
                      Go to Sign In
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
          
          <form onSubmit={handleRegister} className="register-form">
            <div className="form-group">
              <label className="form-label">Full Name (Optional)</label>
              <input
                type="text"
                className="form-input"
                placeholder="Enter your full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            
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
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <p className="form-helper">Must be at least 8 characters</p>
            </div>
            
            <button 
              className="btn btn-primary btn-full btn-lg" 
              type="submit" 
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
          
          <div className="register-footer">
            <p className="text-center text-muted">
              Already have an account?
            </p>
            <button 
              onClick={() => navigate('/login')}
              className="btn btn-ghost btn-full"
            >
              Sign In Instead
            </button>
          </div>
        </div>
        
        <div className="register-links">
          <button onClick={() => navigate('/')} className="link-button">
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
