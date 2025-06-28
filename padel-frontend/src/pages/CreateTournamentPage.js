import React, { useState } from 'react';
import { useAuth } from '../components/AuthContext';
import { tournamentAPI } from '../services/api';

const CreateTournamentPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    location: '',
    start_date: '',
    entry_fee: '',
    max_players: '16'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess(false);

      // Validate required fields
      if (!formData.name || !formData.location || !formData.start_date || !formData.entry_fee) {
        setError('Please fill in all required fields');
        return;
      }

      // Prepare tournament data
      const tournamentData = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        location: formData.location.trim(),
        start_date: formData.start_date,
        entry_fee: parseFloat(formData.entry_fee),
        max_players: parseInt(formData.max_players)
      };

      // Create tournament
      await tournamentAPI.createTournament(tournamentData);
      
      setSuccess(true);
      
      // Redirect to dashboard after success
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create tournament');
      console.error('Create tournament error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="container">
        <div className="header">
          <h1>🎾 Tornetic</h1>
        </div>
        <div className="card">
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎉</div>
            <h2 style={{ color: '#2f855a' }}>Tournament Created!</h2>
            <p style={{ color: '#718096' }}>Your tournament has been created successfully.</p>
            <p style={{ color: '#718096' }}>Redirecting to dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🎾 Tornetic</h1>
        <p>Create New Tournament</p>
      </div>

      {/* User Info */}
      <div className="user-info">
        {user?.picture && (
          <img 
            src={user.picture} 
            alt="Profile" 
            className="user-avatar"
          />
        )}
        <div style={{ flex: 1 }}>
          <h3 style={{ margin: 0, color: '#2d3748' }}>
            {user?.full_name || user?.email}
          </h3>
          <p style={{ margin: 0, color: '#718096', fontSize: '14px' }}>
            Tournament Organizer
          </p>
        </div>
        <a href="/dashboard" className="btn btn-secondary" style={{ fontSize: '14px', padding: '8px 16px' }}>
          ← Back to Dashboard
        </a>
      </div>

      {/* Tournament Form */}
      <div className="card">
        <h2 style={{ marginBottom: '24px', color: '#2d3748' }}>
          Tournament Details
        </h2>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Tournament Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g., Summer Padel Championship 2024"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Tell players about your tournament..."
              rows="3"
            />
          </div>

          <div className="form-group">
            <label htmlFor="location">Location *</label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              placeholder="e.g., Madrid Padel Club, Spain"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="start_date">Start Date *</label>
            <input
              type="date"
              id="start_date"
              name="start_date"
              value={formData.start_date}
              onChange={handleInputChange}
              min={new Date().toISOString().split('T')[0]}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label htmlFor="entry_fee">Entry Fee ($) *</label>
              <input
                type="number"
                id="entry_fee"
                name="entry_fee"
                value={formData.entry_fee}
                onChange={handleInputChange}
                placeholder="50"
                min="0"
                step="0.01"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="max_players">Max Players</label>
              <select
                id="max_players"
                name="max_players"
                value={formData.max_players}
                onChange={handleInputChange}
              >
                <option value="8">8 players</option>
                <option value="16">16 players</option>
                <option value="32">32 players</option>
                <option value="64">64 players</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: '32px', display: 'flex', gap: '16px' }}>
            <button
              type="submit"
              className="btn"
              disabled={loading}
              style={{ flex: 1, fontSize: '16px', padding: '16px' }}
            >
              {loading ? '🔄 Creating...' : '🏆 Create Tournament'}
            </button>
            <a
              href="/dashboard"
              className="btn btn-secondary"
              style={{ padding: '16px 24px', fontSize: '16px' }}
            >
              Cancel
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateTournamentPage; 