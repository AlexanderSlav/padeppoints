import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { playerAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';

const PlayerProfilePage = () => {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const isOwnProfile = !userId || userId === currentUser?.id;

  useEffect(() => {
    loadProfile();
  }, [userId]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = isOwnProfile 
        ? await playerAPI.getMyProfile()
        : await playerAPI.getProfile(userId);
      setProfile(data);
    } catch (err) {
      setError('Failed to load player profile');
      console.error('Load profile error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRatingColor = (rating) => {
    if (rating >= 2000) return '#f59e0b'; // Gold
    if (rating >= 1700) return '#8b5cf6'; // Purple
    if (rating >= 1500) return '#3b82f6'; // Blue
    if (rating >= 1300) return '#10b981'; // Green
    return '#6b7280'; // Gray
  };

  const getRatingTitle = (rating) => {
    if (rating >= 2000) return 'Master';
    if (rating >= 1700) return 'Expert';
    if (rating >= 1500) return 'Advanced';
    if (rating >= 1300) return 'Intermediate';
    return 'Beginner';
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f7fafc', padding: '20px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '32px', marginBottom: '16px' }}>⏳</div>
          <p>Loading player profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f7fafc', padding: '20px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>😕</div>
          <h2>{error || 'Player not found'}</h2>
          <button 
            onClick={() => navigate('/dashboard')}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              backgroundColor: '#4299e1',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const { user, rating, statistics, podium, recent_history } = profile;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f7fafc', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header with player info */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '30px', 
          borderRadius: '12px', 
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            {user.picture && (
              <img 
                src={user.picture} 
                alt={user.full_name}
                style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '50%',
                  objectFit: 'cover',
                  border: `4px solid ${getRatingColor(rating.current)}`
                }}
              />
            )}
            <div style={{ flex: 1 }}>
              <h1 style={{ 
                fontSize: '32px', 
                fontWeight: 'bold', 
                color: '#2d3748', 
                margin: '0 0 8px 0' 
              }}>
                {user.full_name}
                {isOwnProfile && <span style={{ fontSize: '16px', marginLeft: '12px', color: '#718096' }}>(You)</span>}
              </h1>
              <p style={{ color: '#718096', fontSize: '16px', margin: 0 }}>
                {user.email}
              </p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                fontSize: '48px', 
                fontWeight: 'bold', 
                color: getRatingColor(rating.current) 
              }}>
                {rating.current}
              </div>
              <div style={{ 
                fontSize: '14px', 
                color: '#718096',
                fontWeight: '600'
              }}>
                {getRatingTitle(rating.current)} Rating
              </div>
            </div>
          </div>
        </div>

        {/* Statistics Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '20px',
          marginBottom: '24px'
        }}>
          {/* Rating Card */}
          <div style={{ 
            backgroundColor: 'white', 
            padding: '24px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ margin: '0 0 16px 0', color: '#2d3748', fontSize: '18px' }}>
              📊 ELO Rating
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Current:</span>
                <span style={{ fontWeight: 'bold', color: getRatingColor(rating.current) }}>
                  {rating.current}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Peak:</span>
                <span style={{ fontWeight: 'bold', color: '#10b981' }}>{rating.peak}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Lowest:</span>
                <span style={{ color: '#ef4444' }}>{rating.lowest}</span>
              </div>
            </div>
          </div>

          {/* Match Statistics */}
          <div style={{ 
            backgroundColor: 'white', 
            padding: '24px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ margin: '0 0 16px 0', color: '#2d3748', fontSize: '18px' }}>
              🎾 Match Statistics
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Matches Played:</span>
                <span style={{ fontWeight: 'bold' }}>{statistics.matches_played}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Matches Won:</span>
                <span style={{ fontWeight: 'bold' }}>{statistics.matches_won}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Win Rate:</span>
                <span style={{ 
                  fontWeight: 'bold',
                  color: statistics.win_rate >= 50 ? '#10b981' : '#ef4444'
                }}>
                  {statistics.win_rate}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Avg Point %:</span>
                <span style={{ fontWeight: 'bold' }}>
                  {statistics.average_point_percentage}%
                </span>
              </div>
            </div>
          </div>

          {/* Podium Finishes */}
          <div style={{ 
            backgroundColor: 'white', 
            padding: '24px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ margin: '0 0 16px 0', color: '#2d3748', fontSize: '18px' }}>
              🏆 Podium Finishes
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#718096' }}>🥇 First:</span>
                <span style={{ fontWeight: 'bold', color: '#fbbf24' }}>{podium.first}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#718096' }}>🥈 Second:</span>
                <span style={{ fontWeight: 'bold', color: '#9ca3af' }}>{podium.second}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#718096' }}>🥉 Third:</span>
                <span style={{ fontWeight: 'bold', color: '#f59e0b' }}>{podium.third}</span>
              </div>
              <div style={{ 
                paddingTop: '12px', 
                borderTop: '1px solid #e5e7eb',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <span style={{ color: '#718096' }}>Total Podiums:</span>
                <span style={{ fontWeight: 'bold', color: '#8b5cf6' }}>{podium.total}</span>
              </div>
            </div>
          </div>

          {/* Tournament Stats */}
          <div style={{ 
            backgroundColor: 'white', 
            padding: '24px', 
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ margin: '0 0 16px 0', color: '#2d3748', fontSize: '18px' }}>
              🎯 Tournament Stats
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Tournaments:</span>
                <span style={{ fontWeight: 'bold' }}>{statistics.tournaments_played}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#718096' }}>Podium Rate:</span>
                <span style={{ fontWeight: 'bold' }}>
                  {statistics.tournaments_played > 0 
                    ? Math.round((podium.total / statistics.tournaments_played) * 100) 
                    : 0}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Rating History */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '12px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ margin: '0 0 20px 0', color: '#2d3748', fontSize: '20px' }}>
            📈 Recent Rating History
          </h3>
          {recent_history && recent_history.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#374151' }}>Date</th>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#374151' }}>Match Result</th>
                    <th style={{ padding: '12px', textAlign: 'center', color: '#374151' }}>Old Rating</th>
                    <th style={{ padding: '12px', textAlign: 'center', color: '#374151' }}>New Rating</th>
                    <th style={{ padding: '12px', textAlign: 'center', color: '#374151' }}>Change</th>
                  </tr>
                </thead>
                <tbody>
                  {recent_history.map((entry, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px', color: '#6b7280' }}>
                        {new Date(entry.date).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'left' }}>
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '4px',
                          backgroundColor: '#f3f4f6',
                          fontSize: '14px',
                          fontWeight: '600'
                        }}>
                          {entry.match_result}
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', color: '#6b7280' }}>
                        {entry.old_rating}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', fontWeight: 'bold' }}>
                        {entry.new_rating}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'center',
                        fontWeight: 'bold',
                        color: entry.change > 0 ? '#10b981' : entry.change < 0 ? '#ef4444' : '#6b7280'
                      }}>
                        {entry.change > 0 && '+'}{entry.change}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: '#718096', textAlign: 'center', padding: '40px' }}>
              No match history yet. Play some matches to see your rating progress!
            </p>
          )}
        </div>

        {/* Actions */}
        <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button 
            onClick={() => navigate('/leaderboard')}
            style={{
              padding: '12px 24px',
              backgroundColor: '#8b5cf6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            🏅 View Leaderboard
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

export default PlayerProfilePage;