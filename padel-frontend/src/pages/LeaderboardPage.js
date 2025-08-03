import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { playerAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';

const LeaderboardPage = () => {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await playerAPI.getLeaderboard(50);
      setLeaderboard(data);
    } catch (err) {
      setError('Failed to load leaderboard');
      console.error('Load leaderboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRankColor = (rank) => {
    if (rank === 1) return '#fbbf24'; // Gold
    if (rank === 2) return '#9ca3af'; // Silver
    if (rank === 3) return '#f59e0b'; // Bronze
    return '#374151';
  };

  const getRankEmoji = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return '';
  };

  const getRatingColor = (rating) => {
    if (rating >= 2000) return '#f59e0b'; // Gold
    if (rating >= 1700) return '#8b5cf6'; // Purple
    if (rating >= 1500) return '#3b82f6'; // Blue
    if (rating >= 1300) return '#10b981'; // Green
    return '#6b7280'; // Gray
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f7fafc', padding: '20px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '32px', marginBottom: '16px' }}>⏳</div>
          <p>Loading leaderboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f7fafc', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '30px', 
          borderRadius: '12px', 
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          marginBottom: '24px'
        }}>
          <h1 style={{ 
            fontSize: '32px', 
            fontWeight: 'bold', 
            color: '#2d3748', 
            margin: '0 0 8px 0' 
          }}>
            🏅 ELO Leaderboard
          </h1>
          <p style={{ color: '#718096', fontSize: '16px', margin: 0 }}>
            Top rated players • Minimum 5 matches played
          </p>
        </div>

        {error && (
          <div style={{
            backgroundColor: '#fee2e2',
            color: '#991b1b',
            padding: '16px',
            borderRadius: '8px',
            marginBottom: '24px'
          }}>
            {error}
          </div>
        )}

        {/* Top 3 Podium */}
        {leaderboard.length >= 3 && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '20px',
            marginBottom: '32px'
          }}>
            {leaderboard.slice(0, 3).map((player) => (
              <div 
                key={player.user.id}
                onClick={() => navigate(`/player/${player.user.id}`)}
                style={{ 
                  backgroundColor: 'white', 
                  padding: '24px', 
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  cursor: 'pointer',
                  border: `3px solid ${getRankColor(player.rank)}`,
                  transition: 'transform 0.2s',
                  ':hover': { transform: 'scale(1.02)' }
                }}
              >
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '48px', marginBottom: '12px' }}>
                    {getRankEmoji(player.rank)}
                  </div>
                  {player.user.picture && (
                    <img 
                      src={player.user.picture} 
                      alt={player.user.full_name}
                      style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '50%',
                        margin: '0 auto 12px',
                        border: `3px solid ${getRankColor(player.rank)}`
                      }}
                    />
                  )}
                  <h3 style={{ 
                    margin: '0 0 8px 0', 
                    color: '#2d3748',
                    fontSize: '20px'
                  }}>
                    {player.user.full_name}
                    {player.user.id === currentUser?.id && 
                      <span style={{ fontSize: '14px', marginLeft: '8px', color: '#718096' }}>(You)</span>
                    }
                  </h3>
                  <div style={{ 
                    fontSize: '32px', 
                    fontWeight: 'bold',
                    color: getRatingColor(player.rating),
                    marginBottom: '8px'
                  }}>
                    {player.rating}
                  </div>
                  <div style={{ fontSize: '14px', color: '#718096' }}>
                    {player.matches_played} matches • {player.win_rate}% win rate
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Full Leaderboard Table */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '12px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
                <th style={{ padding: '16px', textAlign: 'center', color: '#374151', fontWeight: '600' }}>
                  Rank
                </th>
                <th style={{ padding: '16px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>
                  Player
                </th>
                <th style={{ padding: '16px', textAlign: 'center', color: '#374151', fontWeight: '600' }}>
                  Rating
                </th>
                <th style={{ padding: '16px', textAlign: 'center', color: '#374151', fontWeight: '600' }}>
                  Matches
                </th>
                <th style={{ padding: '16px', textAlign: 'center', color: '#374151', fontWeight: '600' }}>
                  Win Rate
                </th>
                <th style={{ padding: '16px', textAlign: 'center', color: '#374151', fontWeight: '600' }}>
                  Trend
                </th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((player, index) => (
                <tr 
                  key={player.user.id}
                  onClick={() => navigate(`/player/${player.user.id}`)}
                  style={{ 
                    borderBottom: '1px solid #f3f4f6',
                    cursor: 'pointer',
                    backgroundColor: player.user.id === currentUser?.id ? '#fef3c7' : 'transparent',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    if (player.user.id !== currentUser?.id) {
                      e.currentTarget.style.backgroundColor = '#f9fafb';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (player.user.id !== currentUser?.id) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  <td style={{ 
                    padding: '16px', 
                    textAlign: 'center',
                    fontWeight: 'bold',
                    fontSize: '20px',
                    color: getRankColor(player.rank)
                  }}>
                    {getRankEmoji(player.rank)} {player.rank}
                  </td>
                  <td style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      {player.user.picture && (
                        <img 
                          src={player.user.picture} 
                          alt={player.user.full_name}
                          style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '50%'
                          }}
                        />
                      )}
                      <div>
                        <div style={{ fontWeight: '600', color: '#2d3748' }}>
                          {player.user.full_name}
                          {player.user.id === currentUser?.id && 
                            <span style={{ fontSize: '12px', marginLeft: '8px', color: '#718096' }}>(You)</span>
                          }
                        </div>
                      </div>
                    </div>
                  </td>
                  <td style={{ 
                    padding: '16px', 
                    textAlign: 'center',
                    fontSize: '20px',
                    fontWeight: 'bold',
                    color: getRatingColor(player.rating)
                  }}>
                    {player.rating}
                  </td>
                  <td style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}>
                    {player.matches_played}
                  </td>
                  <td style={{ 
                    padding: '16px', 
                    textAlign: 'center',
                    fontWeight: '600',
                    color: player.win_rate >= 50 ? '#10b981' : '#ef4444'
                  }}>
                    {player.win_rate}%
                  </td>
                  <td style={{ padding: '16px', textAlign: 'center' }}>
                    <span style={{
                      fontSize: '20px',
                      color: player.trend === 'up' ? '#10b981' : '#ef4444'
                    }}>
                      {player.trend === 'up' ? '↑' : '↓'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {leaderboard.length === 0 && (
            <div style={{ padding: '60px', textAlign: 'center', color: '#718096' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏆</div>
              <p>No players with enough matches yet.</p>
              <p>Play at least 5 matches to appear on the leaderboard!</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div style={{ marginTop: '32px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button 
            onClick={() => navigate('/profile')}
            style={{
              padding: '12px 24px',
              backgroundColor: '#4299e1',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            👤 My Profile
          </button>
          <button 
            onClick={() => navigate('/dashboard')}
            style={{
              padding: '12px 24px',
              backgroundColor: '#e5e7eb',
              color: '#374151',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default LeaderboardPage;