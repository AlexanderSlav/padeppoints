import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { userAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import EloRatingExplanation from '../components/EloRatingExplanation';

const UserProfilePage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const isOwnProfile = currentUser && currentUser.id === userId;

  useEffect(() => {
    if (userId) {
      loadUserProfile();
    }
  }, [userId]);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      const profileData = await userAPI.getUserProfile(userId);
      setProfile(profileData);
    } catch (err) {
      setError('Failed to load user profile');
      console.error('Load profile error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  const formatRatingData = (ratingHistory) => {
    if (!ratingHistory || ratingHistory.length === 0) {
      // Return default data if no history
      return [{ index: 0, rating: 1000, label: 'Initial', tournamentName: 'Initial Rating' }];
    }
    
    // Use actual rating history from backend (now filtered to show only tournament final ratings)
    const data = [];
    
    // Add initial 1000 rating point
    data.push({ 
      index: 0, 
      rating: 1000, 
      label: 'Initial',
      tournamentName: 'Initial Rating'
    });
    
    // Add tournament final ratings
    ratingHistory.forEach((point, idx) => {
      data.push({
        index: idx + 1,
        rating: point.rating,
        label: `T${idx + 1}`,
        tournamentName: point.tournament_name || `Tournament ${idx + 1}`
      });
    });
    
    return data;
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Loading profile...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#e53e3e' }}>
        <div>{error}</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Profile not found</div>
      </div>
    );
  }

  const { user, statistics } = profile;
  const { tournament_stats, elo_rating } = statistics;
  const ratingData = formatRatingData(elo_rating.rating_history);

  // Determine badge colors based on skill level
  const skillLevelColors = {
    'Beginner': '#48bb78',
    'Novice': '#68d391',
    'Improver': '#9ae6b4',
    'Weak Intermediate': '#f6e05e',
    'Intermediate': '#f6ad55',
    'Strong Intermediate': '#ed8936',
    'Weak Advanced': '#fc8181',
    'Advanced': '#f56565',
    'Strong Advanced': '#e53e3e',
    'Weak Expert': '#c53030',
    'Expert': '#9b2c2c'
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Profile Header */}
      <div style={{ 
        backgroundColor: 'white', 
        padding: '32px', 
        borderRadius: '16px', 
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
            {/* Avatar */}
            <div style={{
              width: '120px',
              height: '120px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '48px',
              fontWeight: 'bold',
              position: 'relative'
            }}>
              {user.full_name ? user.full_name.charAt(0).toUpperCase() : '?'}
              {/* Camera icon placeholder */}
              <div style={{
                position: 'absolute',
                bottom: '5px',
                right: '5px',
                width: '32px',
                height: '32px',
                backgroundColor: 'white',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}>
                📷
              </div>
            </div>

            {/* User Info */}
            <div>
              <h1 style={{ margin: '0 0 8px 0', fontSize: '32px', fontWeight: 'bold', color: '#1a202c' }}>
                {user.full_name || 'Unknown User'}
              </h1>
              <div style={{ color: '#718096', marginBottom: '12px' }}>
                {user.email || 'No email'}
              </div>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{ 
                  backgroundColor: user.is_active ? '#48bb78' : '#e53e3e', 
                  color: 'white', 
                  padding: '6px 12px', 
                  borderRadius: '20px', 
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  {user.is_active ? 'Active Player' : 'Inactive'}
                </span>
                <span style={{ 
                  backgroundColor: skillLevelColors[elo_rating.skill_level] || '#718096', 
                  color: 'white', 
                  padding: '6px 12px', 
                  borderRadius: '20px', 
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  {elo_rating.skill_level}
                </span>
                {statistics.member_since && (
                  <span style={{ color: '#718096', fontSize: '14px' }}>
                    Member since {formatDate(statistics.member_since)}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Edit Profile Button */}
          {isOwnProfile && (
            <button
              onClick={() => navigate('/profile/edit')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '600',
                color: '#4a5568',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#f7fafc';
                e.target.style.borderColor = '#cbd5e0';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'white';
                e.target.style.borderColor = '#e2e8f0';
              }}
            >
              ✏️ Edit Profile
            </button>
          )}
        </div>

        {/* Key Stats Row */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(4, 1fr)', 
          gap: '24px', 
          marginTop: '32px',
          paddingTop: '24px',
          borderTop: '1px solid #e2e8f0'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#48bb78' }}>
              {tournament_stats.total_played}
            </div>
            <div style={{ color: '#718096', fontSize: '14px', marginTop: '4px' }}>
              Tournaments
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#4299e1' }}>
              {tournament_stats.tournaments_won}
            </div>
            <div style={{ color: '#718096', fontSize: '14px', marginTop: '4px' }}>
              Wins
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#805ad5' }}>
              {elo_rating.current_rating.toFixed(0)}
            </div>
            <div style={{ color: '#718096', fontSize: '14px', marginTop: '4px' }}>
              ELO Rating
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#ed8936' }}>
              {tournament_stats.podium_finishes}
            </div>
            <div style={{ color: '#718096', fontSize: '14px', marginTop: '4px' }}>
              Podium Finishes
            </div>
          </div>
        </div>
      </div>

      {/* Recent Tournaments Section */}
      {profile.recent_tournaments && profile.recent_tournaments.joined && profile.recent_tournaments.joined.length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '16px',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ 
            margin: '0 0 20px 0', 
            fontSize: '20px', 
            fontWeight: 'bold',
            color: '#1a202c',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            🏓 Recent Tournaments
          </h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#718096', fontSize: '14px', fontWeight: '600' }}>Tournament</th>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#718096', fontSize: '14px', fontWeight: '600' }}>Location</th>
                  <th style={{ padding: '12px', textAlign: 'center', color: '#718096', fontSize: '14px', fontWeight: '600' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'center', color: '#718096', fontSize: '14px', fontWeight: '600' }}>Place</th>
                </tr>
              </thead>
              <tbody>
                {profile.recent_tournaments.joined.slice(0, 5).map((tournament, index) => {
                  // Use user_placement from backend if available
                  const userPlacement = tournament.user_placement;
                  
                  return (
                    <tr key={tournament.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '12px' }}>
                        <Link 
                          to={`/tournaments/${tournament.id}`}
                          style={{ 
                            color: '#4299e1', 
                            textDecoration: 'none',
                            fontWeight: '500',
                            fontSize: '14px'
                          }}
                        >
                          {tournament.name}
                        </Link>
                      </td>
                      <td style={{ padding: '12px', color: '#4a5568', fontSize: '14px' }}>
                        {tournament.location}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '600',
                          backgroundColor: 
                            tournament.status === 'completed' ? '#c6f6d5' :
                            tournament.status === 'active' ? '#bee3f8' :
                            '#feebc8',
                          color:
                            tournament.status === 'completed' ? '#22543d' :
                            tournament.status === 'active' ? '#2a4e7c' :
                            '#744210'
                        }}>
                          {tournament.status.charAt(0).toUpperCase() + tournament.status.slice(1)}
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        {tournament.status === 'completed' && userPlacement ? (
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '4px'
                          }}>
                            {userPlacement === 1 ? (
                              <span style={{ fontSize: '18px' }}>🥇</span>
                            ) : userPlacement === 2 ? (
                              <span style={{ fontSize: '18px' }}>🥈</span>
                            ) : userPlacement === 3 ? (
                              <span style={{ fontSize: '18px' }}>🥉</span>
                            ) : null}
                            <span style={{
                              fontSize: '14px',
                              fontWeight: '600',
                              color: 
                                userPlacement === 1 ? '#d69e2e' :
                                userPlacement === 2 ? '#718096' :
                                userPlacement === 3 ? '#c05621' :
                                '#4a5568'
                            }}>
                              {userPlacement}/{tournament.max_players || tournament.current_players}
                            </span>
                          </div>
                        ) : tournament.status === 'active' ? (
                          <span style={{ color: '#4a5568', fontSize: '14px' }}>
                            -/{tournament.max_players}
                          </span>
                        ) : (
                          <span style={{ color: '#cbd5e0', fontSize: '14px' }}>
                            -/{tournament.max_players}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Statistics Sections */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Tournament Statistics */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '16px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ 
            margin: '0 0 24px 0', 
            fontSize: '20px', 
            fontWeight: 'bold',
            color: '#1a202c',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            🏆 Tournament Statistics
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#4a5568' }}>Total Played</span>
              <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#1a202c' }}>
                {tournament_stats.total_played}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#4a5568' }}>Tournaments Won</span>
              <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#48bb78' }}>
                {tournament_stats.tournaments_won}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#4a5568' }}>Podium Finishes</span>
              <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#4299e1' }}>
                {tournament_stats.podium_finishes}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#4a5568' }}>Avg Points Percentage</span>
              <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#805ad5' }}>
                {tournament_stats.average_points_percentage.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* ELO Rating */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '16px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ 
            margin: '0 0 24px 0', 
            fontSize: '20px', 
            fontWeight: 'bold',
            color: '#1a202c',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            📈 ELO Rating
          </h2>

          {/* Current Rating Display */}
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#805ad5' }}>
              {elo_rating.current_rating.toFixed(0)}
            </div>
            <div style={{ 
              color: 'white',
              backgroundColor: skillLevelColors[elo_rating.skill_level] || '#718096',
              padding: '4px 12px',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '600',
              display: 'inline-block',
              marginTop: '8px'
            }}>
              {elo_rating.skill_level}
            </div>
          </div>

          {/* Rating Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
            <div>
              <div style={{ color: '#718096', fontSize: '12px', marginBottom: '4px' }}>Peak Rating</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1a202c' }}>
                {elo_rating.peak_rating.toFixed(0)}
              </div>
            </div>
            <div>
              <div style={{ color: '#718096', fontSize: '12px', marginBottom: '4px' }}>Recent Change</div>
              <div style={{ 
                fontSize: '20px', 
                fontWeight: 'bold', 
                color: elo_rating.recent_change >= 0 ? '#48bb78' : '#e53e3e' 
              }}>
                {elo_rating.recent_change >= 0 ? '+' : ''}{elo_rating.recent_change.toFixed(1)}
              </div>
            </div>
            {elo_rating.playtomic_level && (
              <div>
                <div style={{ color: '#718096', fontSize: '12px', marginBottom: '4px' }}>Playtomic Level</div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#805ad5' }}>
                  ~{elo_rating.playtomic_level}
                </div>
              </div>
            )}
            {elo_rating.percentile && (
              <div>
                <div style={{ color: '#718096', fontSize: '12px', marginBottom: '4px' }}>Percentile</div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#4299e1' }}>
                  {elo_rating.percentile}%
                </div>
              </div>
            )}
          </div>

          {/* Rating History Chart */}
          <div style={{ marginTop: '24px' }}>
            <div style={{ color: '#718096', fontSize: '14px', marginBottom: '12px' }}>
              Rating History (Last 10 Tournaments)
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={ratingData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="index" 
                  tick={{ fontSize: 12 }}
                  stroke="#718096"
                />
                <YAxis 
                  domain={['dataMin - 50', 'dataMax + 50']}
                  tick={{ fontSize: 12 }}
                  stroke="#718096"
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px'
                  }}
                  formatter={(value) => [`${Math.round(value)}`, 'Rating']}
                  labelFormatter={(label) => {
                    const point = ratingData.find(d => d.index === label);
                    return point ? point.tournamentName : `Tournament ${label}`;
                  }}
                />
                {/* Initial rating reference line */}
                <ReferenceLine 
                  y={1000} 
                  stroke="#cbd5e0" 
                  strokeDasharray="5 5" 
                  label={{ value: "Initial (1000)", position: "left", fontSize: 10, fill: '#718096' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="rating" 
                  stroke="#805ad5" 
                  strokeWidth={3}
                  dot={{ fill: '#805ad5', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* ELO Rating Explanation Section */}
      <EloRatingExplanation />
    </div>
  );
};

export default UserProfilePage;