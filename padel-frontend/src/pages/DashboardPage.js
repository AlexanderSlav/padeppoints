import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import { tournamentAPI } from '../services/api';
import TournamentAdviceCalculator from '../components/TournamentAdviceCalculator';
import '../styles/globals.css';
import './DashboardPage.css';

const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAdviceModal, setShowAdviceModal] = useState(false);
  const [showCompleted, setShowCompleted] = useState(false);

  useEffect(() => {
    loadTournaments();
  }, []);

  const loadTournaments = async () => {
    try {
      setLoading(true);
      const myTournaments = await tournamentAPI.getMyTournaments();
      setTournaments(myTournaments);
    } catch (err) {
      setError('Failed to load tournaments');
      console.error('Load tournaments error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch(status) {
      case 'active': return 'badge badge-success';
      case 'pending': return 'badge badge-warning';
      case 'completed': return 'badge badge-info';
      default: return 'badge';
    }
  };

  const filteredTournaments = tournaments.filter(t => 
    showCompleted ? t.status === 'completed' : t.status !== 'completed'
  );

  return (
    <div className="dashboard-page">
      <div className="dashboard-container container">
        {/* Welcome Section */}
        <div className="welcome-section">
          <h1 className="welcome-title">
            Welcome back, {user?.full_name || user?.email?.split('@')[0]}!
          </h1>
          <p className="welcome-subtitle">
            Manage your tournaments and track your progress
          </p>
        </div>

        {/* Quick Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-icon">🏆</span>
            <div className="stat-content">
              <span className="stat-value">{tournaments.filter(t => t.status === 'active').length}</span>
              <span className="stat-label">Active Tournaments</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">⏳</span>
            <div className="stat-content">
              <span className="stat-value">{tournaments.filter(t => t.status === 'pending').length}</span>
              <span className="stat-label">Pending</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">✅</span>
            <div className="stat-content">
              <span className="stat-value">{tournaments.filter(t => t.status === 'completed').length}</span>
              <span className="stat-label">Completed</span>
            </div>
          </div>
        </div>

        {/* Quick Actions - Desktop Only */}
        <div className="quick-actions hide-mobile">
          <h2 className="section-title">Quick Actions</h2>
          <div className="action-grid">
            <button 
              onClick={() => navigate('/tournaments')}
              className="action-card"
            >
              <span className="action-icon">🔍</span>
              <span className="action-text">Discover Tournaments</span>
            </button>
            <button 
              onClick={() => navigate('/create-tournament')}
              className="action-card action-primary"
            >
              <span className="action-icon">➕</span>
              <span className="action-text">Create Tournament</span>
            </button>
            <button 
              onClick={() => setShowAdviceModal(true)}
              className="action-card"
            >
              <span className="action-icon">💡</span>
              <span className="action-text">Get Planning Advice</span>
            </button>
          </div>
        </div>

        {/* Tournaments Section */}
        <div className="tournaments-section">
          <div className="section-header">
            <h2 className="section-title">Your Tournaments</h2>
            <button
              onClick={() => setShowCompleted(!showCompleted)}
              className={`filter-btn ${showCompleted ? 'active' : ''}`}
            >
              {showCompleted ? 'Hide Completed' : 'Show Completed'}
            </button>
          </div>

          {error && (
            <div className="alert alert-error">
              <span>⚠️</span>
              {error}
            </div>
          )}

          {loading ? (
            <div className="loading-state">
              <div className="loading-icon animate-pulse">🔄</div>
              <p>Loading tournaments...</p>
            </div>
          ) : filteredTournaments.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🏆</div>
              <h3>{showCompleted ? 'No completed tournaments' : 'No active tournaments'}</h3>
              <p>{showCompleted ? 'Your completed tournaments will appear here.' : 'Create your first tournament to get started!'}</p>
              {!showCompleted && (
                <button 
                  onClick={() => navigate('/create-tournament')}
                  className="btn btn-primary btn-lg mt-lg"
                >
                  Create Your First Tournament
                </button>
              )}
            </div>
          ) : (
            <div className="tournament-grid">
              {filteredTournaments.map((tournament) => (
                <div key={tournament.id} className="tournament-card card">
                  <div className="tournament-header">
                    <div>
                      <h3 className="tournament-name">{tournament.name}</h3>
                      {tournament.description && (
                        <p className="tournament-description">{tournament.description}</p>
                      )}
                    </div>
                    <span className={getStatusBadgeClass(tournament.status)}>
                      {tournament.status.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="tournament-details">
                    <div className="detail-item">
                      <span className="detail-icon">📍</span>
                      <span>{tournament.location}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">📅</span>
                      <span>{new Date(tournament.start_date).toLocaleDateString()}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">👥</span>
                      <span>{tournament.max_players} players</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">💰</span>
                      <span>${tournament.entry_fee}</span>
                    </div>
                  </div>
                  
                  <div className="tournament-actions">
                    <button 
                      onClick={() => navigate(`/tournaments/${tournament.id}`)}
                      className="btn btn-primary btn-full"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Mobile Create Button */}
        <button 
          onClick={() => navigate('/create-tournament')}
          className="mobile-fab hide-desktop"
        >
          <span>➕</span>
        </button>
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

export default DashboardPage;