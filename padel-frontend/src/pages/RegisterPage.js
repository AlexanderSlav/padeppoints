import React, { useState } from 'react';
import { authAPI } from '../services/api';

const RegisterPage = () => {
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
      setError('Registration failed');
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center' }}>
          <h2>Account created!</h2>
          <p>Please log in with your credentials.</p>
          <a href="/login" className="btn">Go to Login</a>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🎾 Tornetic</h1>
      </div>
      <div className="card">
        <h2 style={{ marginBottom: '24px', textAlign: 'center', color: '#2d3748' }}>Create Account</h2>
        {error && <div className="error">{error}</div>}
        <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <input
            type="text"
            placeholder="Full name (optional)"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            style={{ padding: '8px', fontSize: '16px' }}
          />
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
          <button className="btn" type="submit" disabled={loading} style={{ fontSize: '16px' }}>
            {loading ? '🔄 Loading...' : 'Register'}
          </button>
        </form>
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <a href="/login">Back to login</a>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
