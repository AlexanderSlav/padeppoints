import React, { useState, useEffect } from 'react';
import { tournamentAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';

const TournamentDiscoveryPage = () => {
  const { user } = useAuth();
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    format: '',
    status: 'active_pending',  // Default to showing only active and pending
    location: '',
    created_by_me: false,
    limit: 20,
    offset: 0
  });
  const [showCompleted, setShowCompleted] = useState(false);
  const [formats, setFormats] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadFormatsAndStatuses();
  }, []);

  useEffect(() => {
    loadTournaments();
  }, [filters]);

  const loadFormatsAndStatuses = async () => {
    try {
      const [formatsData, statusesData] = await Promise.all([
        tournamentAPI.getTournamentFormats(),
        tournamentAPI.getTournamentStatuses()
      ]);
      setFormats(formatsData.formats || []);
      setStatuses(statusesData.statuses || []);
    } catch (err) {
      console.error('Failed to load formats/statuses:', err);
    }
  };

  const loadTournaments = async () => {
    try {
      setLoading(true);
      const response = await tournamentAPI.getTournaments(filters);
      setTournaments(response.tournaments || []);
      setTotal(response.total || 0);
    } catch (err) {
      setError('Failed to load tournaments');
      console.error('Load tournaments error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      offset: 0 // Reset to first page when filtering
    }));
  };

  const clearFilters = () => {
    setFilters({
      format: '',
      status: 'active_pending',  // Reset to default active & pending
      location: '',
      created_by_me: false,
      limit: 20,
      offset: 0
    });
  };

  const handleJoinTournament = async (tournamentId) => {
    try {
      await tournamentAPI.joinTournament(tournamentId);
      // Refresh tournaments to show updated player count
      loadTournaments();
    } catch (err) {
      console.error('Failed to join tournament:', err);
    }
  };

  const handleLeaveTournament = async (tournamentId) => {
    try {
      await tournamentAPI.leaveTournament(tournamentId);
      // Refresh tournaments to show updated player count
      loadTournaments();
    } catch (err) {
      console.error('Failed to leave tournament:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#fbbf24';
      case 'active': return '#10b981';
      case 'completed': return '#6b7280';
      default: return '#d1d5db';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f7fafc', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '8px', 
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          marginBottom: '24px'
        }}>
          <h1 style={{ 
            fontSize: '28px', 
            fontWeight: '600', 
            color: '#111827', 
            margin: '0 0 8px 0' 
          }}>
            Discover Tournaments
          </h1>
          <p style={{ color: '#6b7280', fontSize: '14px', margin: 0 }}>
            Find and join padel tournaments near you
          </p>
        </div>

        {/* Filters */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
          marginBottom: '24px'
        }}>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px',
            marginBottom: '16px'
          }}>
            {/* Format Filter */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '4px' }}>
                Format
              </label>
              <select
                value={filters.format}
                onChange={(e) => handleFilterChange('format', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px'
                }}
              >
                <option value="">All Formats</option>
                {formats.map(format => (
                  <option key={format.value} value={format.value}>
                    {format.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '4px' }}>
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px'
                }}
              >
                <option value="active_pending">Active & Pending</option>
                <option value="">All Statuses</option>
                <option value="pending">Pending Only</option>
                <option value="active">Active Only</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Location Filter */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '4px' }}>
                Location
              </label>
              <input
                type="text"
                value={filters.location}
                onChange={(e) => handleFilterChange('location', e.target.value)}
                placeholder="Search by location..."
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px'
                }}
              />
            </div>

            {/* My Tournaments Toggle */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                <input
                  type="checkbox"
                  checked={filters.created_by_me}
                  onChange={(e) => handleFilterChange('created_by_me', e.target.checked)}
                  style={{ marginRight: '8px' }}
                />
                My Tournaments Only
              </label>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <button
              onClick={clearFilters}
              style={{
                padding: '8px 16px',
                backgroundColor: '#f7fafc',
                color: '#4a5568',
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Clear Filters
            </button>
            <span style={{ fontSize: '14px', color: '#718096' }}>
              {total} tournaments found
            </span>
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#718096' }}>
            Loading tournaments...
          </div>
        ) : error ? (
          <div style={{ 
            backgroundColor: '#fed7d7', 
            color: '#c53030', 
            padding: '16px', 
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            {error}
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {tournaments.map(tournament => (
              <TournamentCard
                key={tournament.id}
                tournament={tournament}
                onJoin={handleJoinTournament}
                onLeave={handleLeaveTournament}
                currentUserId={user?.id}
                getStatusColor={getStatusColor}
                formatDate={formatDate}
              />
            ))}

            {tournaments.length === 0 && (
              <div style={{ 
                backgroundColor: 'white', 
                padding: '40px', 
                borderRadius: '12px', 
                textAlign: 'center', 
                color: '#718096' 
              }}>
                No tournaments found matching your criteria.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const TournamentCard = ({ tournament, onJoin, onLeave, currentUserId, getStatusColor, formatDate }) => {
  const [joinStatus, setJoinStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkJoinStatus();
  }, [tournament.id]);

  const checkJoinStatus = async () => {
    try {
      const status = await tournamentAPI.canJoinTournament(tournament.id);
      setJoinStatus(status);
    } catch (err) {
      console.error('Failed to check join status:', err);
    }
  };

  const handleJoinClick = async () => {
    setLoading(true);
    try {
      await onJoin(tournament.id);
      await checkJoinStatus(); // Refresh status
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveClick = async () => {
    setLoading(true);
    try {
      await onLeave(tournament.id);
      await checkJoinStatus(); // Refresh status
    } finally {
      setLoading(false);
    }
  };

  const isCreatedByMe = tournament.created_by === currentUserId;

  return (
    <div style={{ 
      backgroundColor: 'white', 
      padding: '20px', 
      borderRadius: '8px', 
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
      border: '1px solid #e5e7eb',
      transition: 'box-shadow 0.2s',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)'}
    onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)'}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 8px 0' }}>
            <a 
              href={`/tournaments/${tournament.id}`} 
              style={{ color: '#2d3748', textDecoration: 'none' }}
              onMouseEnter={(e) => e.target.style.color = '#4299e1'}
              onMouseLeave={(e) => e.target.style.color = '#2d3748'}
            >
              {tournament.name}
            </a>
          </h3>
          <div style={{ display: 'flex', gap: '8px', fontSize: '13px', color: '#6b7280' }}>
            <span>{tournament.location}</span>
            <span>•</span>
            <span>{formatDate(tournament.start_date)}</span>
            <span>•</span>
            <span>${tournament.entry_fee}</span>
            <span>•</span>
            <span>{tournament.system}</span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            backgroundColor: getStatusColor(tournament.status),
            color: 'white',
            padding: '4px 12px',
            borderRadius: '6px',
            fontSize: '11px',
            fontWeight: '500',
            textTransform: 'uppercase'
          }}>
            {tournament.status}
          </div>
          {isCreatedByMe && (
            <div style={{
              backgroundColor: '#f3f4f6',
              color: '#6b7280',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '11px',
              fontWeight: '500'
            }}>
              MY TOURNAMENT
            </div>
          )}
        </div>
      </div>

      {tournament.description && (
        <p style={{ color: '#4a5568', fontSize: '14px', marginBottom: '16px', margin: '0 0 16px 0' }}>
          {tournament.description}
        </p>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '24px', fontSize: '14px' }}>
          <span style={{ color: '#4a5568' }}>
            <strong>Players:</strong> {tournament.current_players || 0} / {tournament.max_players}
          </span>
          <span style={{ color: '#4a5568' }}>
            <strong>Round:</strong> {tournament.current_round || 1}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <a
            href={`/tournaments/${tournament.id}`}
            style={{
              padding: '8px 16px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '600',
              display: 'inline-block',
              transition: 'transform 0.2s, box-shadow 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            View Details
          </a>
          
          {!isCreatedByMe && joinStatus && (
            <>
              {joinStatus.is_already_joined ? (
                <button
                  onClick={handleLeaveClick}
                  disabled={loading || tournament.status !== 'pending'}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#fed7d7',
                    color: '#c53030',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: tournament.status === 'pending' ? 'pointer' : 'not-allowed',
                    fontSize: '14px',
                    fontWeight: '600',
                    opacity: loading ? 0.6 : 1
                  }}
                >
                  {loading ? 'Leaving...' : 'Leave'}
                </button>
              ) : (
                <button
                  onClick={handleJoinClick}
                  disabled={loading || !joinStatus.can_join}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: joinStatus.can_join ? '#10b981' : '#9ca3af',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: joinStatus.can_join ? 'pointer' : 'not-allowed',
                    fontSize: '14px',
                    fontWeight: '500',
                    opacity: loading ? 0.6 : 1
                  }}
                >
                  {loading ? 'Joining...' : joinStatus.can_join ? 'Quick Join' : joinStatus.reason}
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TournamentDiscoveryPage; 