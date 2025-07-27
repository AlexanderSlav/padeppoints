import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';
import { tournamentAPI } from '../services/api';

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const [tournaments, setTournaments] = useState([]);
  const [joinedTournaments, setJoinedTournaments] = useState([]);
  const [upcomingTournaments, setUpcomingTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTournaments();
  }, []);

  const loadTournaments = async () => {
    try {
      setLoading(true);
      // Load tournaments created by me
      const myTournaments = await tournamentAPI.getMyTournaments();
      setTournaments(myTournaments);
    } catch (err) {
      setError('Failed to load tournaments');
      console.error('Load tournaments error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🎾 Tornetic</h1>
        <p>Tournament Management Dashboard</p>
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
            Welcome, {user?.full_name || user?.email}!
          </h3>
          <p style={{ margin: 0, color: '#718096', fontSize: '14px' }}>
            {user?.email}
          </p>
        </div>
        <button 
          className="btn btn-secondary"
          onClick={handleLogout}
          style={{ fontSize: '14px', padding: '8px 16px' }}
        >
          Logout
        </button>
      </div>

      {/* Navigation */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 16px 0', color: '#2d3748' }}>Quick Actions</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '16px'
        }}>
          <a href="/tournaments" style={{
            display: 'block',
            padding: '16px 24px',
            backgroundColor: '#4299e1',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '8px',
            textAlign: 'center',
            fontSize: '16px',
            fontWeight: '600'
          }}>
            🔍 Discover Tournaments
          </a>
          <a href="/create-tournament" style={{
            display: 'block',
            padding: '16px 24px',
            backgroundColor: '#48bb78',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '8px',
            textAlign: 'center',
            fontSize: '16px',
            fontWeight: '600'
          }}>
            + Create Tournament
          </a>
        </div>
      </div>

      {/* My Tournaments */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 style={{ margin: 0, color: '#2d3748' }}>Your Tournaments</h2>
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '32px', marginBottom: '16px' }}>🔄</div>
            <p>Loading tournaments...</p>
          </div>
        ) : tournaments.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#718096' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏆</div>
            <h3>No tournaments yet</h3>
            <p>Create your first tournament to get started!</p>
            <div style={{ marginTop: '24px' }}>
              <a href="/create-tournament" className="btn">
                Create Your First Tournament
              </a>
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {tournaments.map((tournament) => (
              <div 
                key={tournament.id} 
                style={{ 
                  border: '1px solid #e2e8f0', 
                  borderRadius: '8px', 
                  padding: '16px',
                  background: '#f7fafc'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ margin: '0 0 8px 0', color: '#2d3748' }}>
                      {tournament.name}
                    </h3>
                    {tournament.description && (
                      <p style={{ margin: '0 0 8px 0', color: '#718096' }}>
                        {tournament.description}
                      </p>
                    )}
                    <div style={{ fontSize: '14px', color: '#718096' }}>
                      📍 {tournament.location} • 📅 {new Date(tournament.start_date).toLocaleDateString()}
                    </div>
                    <div style={{ fontSize: '14px', color: '#718096', marginTop: '4px' }}>
                      👥 {tournament.max_players} players • 💰 ${tournament.entry_fee}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <a 
                      href={`/tournaments/${tournament.id}`}
                      className="btn btn-secondary"
                      style={{ fontSize: '14px', padding: '6px 12px', textDecoration: 'none' }}
                    >
                      View Details
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage; 