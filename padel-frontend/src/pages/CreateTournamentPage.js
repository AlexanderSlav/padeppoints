import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';
import { tournamentAPI } from '../services/api';
import TournamentAdviceCalculator from '../components/TournamentAdviceCalculator';

const CreateTournamentPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [estimatedDuration, setEstimatedDuration] = useState(null);
  const [showAdviceModal, setShowAdviceModal] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    location: '',
    start_date: '',
    entry_fee: '',
    max_players: '16',
    points_per_match: '32',
    courts: '1'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      try {
        const players = parseInt(formData.max_players);
        const courts = parseInt(formData.courts);
        const pointsPerMatch = parseInt(formData.points_per_match);
        if (players >= 4 && courts > 0 && pointsPerMatch > 0) {
          const data = await tournamentAPI.estimateDuration('AMERICANO', players, courts, pointsPerMatch);
          setEstimatedDuration(data);
        } else {
          setEstimatedDuration(null);
        }
      } catch (err) {
        console.error('Estimate duration error', err);
        setEstimatedDuration(null);
      }
    }, 500); // 500ms debounce

    return () => clearTimeout(timeoutId);
  }, [formData.max_players, formData.courts, formData.points_per_match]);


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
        max_players: parseInt(formData.max_players),
        points_per_match: parseInt(formData.points_per_match),
        courts: parseInt(formData.courts)
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
          <h1>Tornetic</h1>
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
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => setShowAdviceModal(true)}
            className="btn"
            style={{ 
              fontSize: '14px', 
              padding: '8px 16px',
              backgroundColor: '#805ad5',
              border: 'none'
            }}
          >
            💡 Get Advice
          </button>
          <a href="/dashboard" className="btn btn-secondary" style={{ fontSize: '14px', padding: '8px 16px' }}>
            ← Back to Dashboard
          </a>
        </div>
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
              <option value="4">4 players (1 court)</option>
              <option value="8">8 players (2 courts)</option>
              <option value="12">12 players (3 courts)</option>
              <option value="16">16 players (4 courts)</option>
              <option value="20">20 players (5 courts)</option>
              <option value="24">24 players (6 courts)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="points_per_match">Points per Match</label>
            <input
              type="number"
              id="points_per_match"
              name="points_per_match"
              min="1"
              value={formData.points_per_match}
              onChange={handleInputChange}
              placeholder="32"
            />
          </div>

          <div className="form-group">
            <label htmlFor="courts">Courts</label>
            <input
              type="number"
              id="courts"
              name="courts"
              min="1"
              value={formData.courts}
              onChange={handleInputChange}
            />
            {estimatedDuration && (
              <div style={{ color: '#718096', fontSize: '12px' }}>
                Approx. {Math.floor(estimatedDuration.estimated_minutes/60)}h {estimatedDuration.estimated_minutes%60}m ({estimatedDuration.total_rounds} rounds)
              </div>
            )}
          </div>
        </div>

          <div style={{ marginTop: '32px', display: 'flex', gap: '16px' }}>
            <button
              type="submit"
              className="btn btn-primary"
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

      {/* Advice Modal */}
      {showAdviceModal && (
        <TournamentAdviceCalculator 
          isModal={true}
          onClose={() => setShowAdviceModal(false)}
        />
      )}
    </div>
  );
};

export default CreateTournamentPage; 