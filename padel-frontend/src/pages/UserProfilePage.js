import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { userAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';

const UserProfilePage = () => {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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

  const { user, statistics, recent_tournaments } = profile;

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{ 
        backgroundColor: '#f7fafc', 
        padding: '24px', 
        borderRadius: '12px', 
        marginBottom: '24px',
        border: '1px solid #e2e8f0'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
          <div style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            backgroundColor: user.is_guest ? '#48bb78' : '#4299e1',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '32px',
            fontWeight: 'bold'
          }}>
            {user.full_name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 style={{ margin: '0 0 8px 0', fontSize: '28px', color: '#2d3748' }}>
              {user.full_name}
            </h1>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {user.is_guest ? (
                <span style={{ 
                  backgroundColor: '#48bb78', 
                  color: 'white', 
                  padding: '4px 8px', 
                  borderRadius: '12px', 
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  Guest User
                </span>
              ) : (
                <span style={{ 
                  backgroundColor: '#4299e1', 
                  color: 'white', 
                  padding: '4px 8px', 
                  borderRadius: '12px', 
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  Registered User
                </span>
              )}
              {user.email && (
                <span style={{ color: '#718096', fontSize: '14px' }}>
                  {user.email}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        {/* Tournaments Created */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '12px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ margin: '0 0 16px 0', color: '#2d3748', fontSize: '18px' }}>
            Tournaments Created
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2d3748' }}>
                {statistics.tournaments_created.total}
              </div>
              <div style={{ fontSize: '12px', color: '#718096' }}>Total</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4299e1' }}>
                {statistics.tournaments_created.active}
              </div>
              <div style={{ fontSize: '12px', color: '#718096' }}>Active</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#48bb78' }}>
                {statistics.tournaments_created.completed}
              </div>
              <div style={{ fontSize: '12px', color: '#718096' }}>Completed</div>
            </div>
          </div>
        </div>

        {/* Tournaments Joined */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '12px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ margin: '0 0 16px 0', color: '#2d3748', fontSize: '18px' }}>
            Tournaments Joined
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2d3748' }}>
                {statistics.tournaments_joined.total}
              </div>
              <div style={{ fontSize: '12px', color: '#718096' }}>Total</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4299e1' }}>
                {statistics.tournaments_joined.active}
              </div>
              <div style={{ fontSize: '12px', color: '#718096' }}>Active</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#48bb78' }}>
                {statistics.tournaments_joined.completed}
              </div>
              <div style={{ fontSize: '12px', color: '#718096' }}>Completed</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Tournaments */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Recent Created */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '12px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ margin: '0 0 16px 0', color: '#2d3748', fontSize: '18px' }}>
            Recent Tournaments Created
          </h3>
          {recent_tournaments.created.length === 0 ? (
            <div style={{ color: '#718096', textAlign: 'center', padding: '20px' }}>
              No tournaments created yet
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {recent_tournaments.created.map((tournament) => (
                <Link 
                  key={tournament.id} 
                  to={`/tournaments/${tournament.id}`}
                  style={{ 
                    textDecoration: 'none', 
                    color: 'inherit',
                    padding: '8px',
                    borderRadius: '6px',
                    border: '1px solid #e2e8f0',
                    ':hover': { backgroundColor: '#f7fafc' }
                  }}
                >
                  <div style={{ fontWeight: '600', color: '#2d3748' }}>
                    {tournament.name}
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    {tournament.location} • {tournament.status}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Recent Joined */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '12px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ margin: '0 0 16px 0', color: '#2d3748', fontSize: '18px' }}>
            Recent Tournaments Joined
          </h3>
          {recent_tournaments.joined.length === 0 ? (
            <div style={{ color: '#718096', textAlign: 'center', padding: '20px' }}>
              No tournaments joined yet
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {recent_tournaments.joined.map((tournament) => (
                <Link 
                  key={tournament.id} 
                  to={`/tournaments/${tournament.id}`}
                  style={{ 
                    textDecoration: 'none', 
                    color: 'inherit',
                    padding: '8px',
                    borderRadius: '6px',
                    border: '1px solid #e2e8f0',
                    ':hover': { backgroundColor: '#f7fafc' }
                  }}
                >
                  <div style={{ fontWeight: '600', color: '#2d3748' }}>
                    {tournament.name}
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    {tournament.location} • {tournament.status}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage; 