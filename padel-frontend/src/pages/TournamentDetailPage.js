import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { tournamentAPI, userAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';

const TournamentDetailPage = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [tournament, setTournament] = useState(null);
  const [players, setPlayers] = useState([]);
  const [matches, setMatches] = useState([]);
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    if (id) {
      loadTournamentData();
    }
  }, [id]);

  const loadTournamentData = async () => {
    try {
      setLoading(true);
      const [tournamentData, playersData] = await Promise.all([
        tournamentAPI.getTournament(id),
        tournamentAPI.getTournamentPlayers(id)
      ]);
      
      setTournament(tournamentData);
      setPlayers(playersData.players || []);

      // Load matches if tournament is active
      if (tournamentData.status === 'active') {
        try {
          const matchesData = await tournamentAPI.getCurrentRoundMatches(id);
          setMatches(matchesData || []);
        } catch (err) {
          console.log('No current matches found');
        }
      }

      // Load leaderboard if tournament has started
      if (tournamentData.status === 'active' || tournamentData.status === 'completed') {
        try {
          const leaderboardData = await tournamentAPI.getTournamentLeaderboard(id);
          setLeaderboard(leaderboardData);
        } catch (err) {
          console.log('No leaderboard data found');
        }
      }

    } catch (err) {
      setError('Failed to load tournament data');
      console.error('Load tournament error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartTournament = async () => {
    try {
      await tournamentAPI.startTournament(id);
      loadTournamentData();
      setNotification({ type: 'success', message: 'Tournament started successfully!' });
    } catch (err) {
      setNotification({ 
        type: 'error', 
        message: err.response?.data?.detail || 'Failed to start tournament' 
      });
    }
  };

  const handleJoinTournament = async () => {
    try {
      await tournamentAPI.joinTournament(id);
      // Show success message and reload data
      loadTournamentData();
      setNotification({ type: 'success', message: 'Successfully joined tournament!' });
    } catch (err) {
      setNotification({ 
        type: 'error', 
        message: err.response?.data?.detail || 'Failed to join tournament' 
      });
    }
  };

  const handleLeaveTournament = async () => {
    try {
      await tournamentAPI.leaveTournament(id);
      // Show success message and reload data
      loadTournamentData();
      setNotification({ type: 'success', message: 'Successfully left tournament!' });
    } catch (err) {
      setNotification({ 
        type: 'error', 
        message: err.response?.data?.detail || 'Failed to leave tournament' 
      });
    }
  };

  const handleRecordResult = async (matchId, team1Score, team2Score) => {
    try {
      await tournamentAPI.recordMatchResult(matchId, parseInt(team1Score), parseInt(team2Score));
      loadTournamentData();
      setNotification({ type: 'success', message: 'Match result recorded successfully!' });
    } catch (err) {
      setNotification({ 
        type: 'error', 
        message: err.response?.data?.detail || 'Failed to record match result' 
      });
    }
  };

  // Auto-hide notification after 5 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#f6ad55';
      case 'active': return '#68d391';
      case 'completed': return '#9ca3af';
      default: return '#e2e8f0';
    }
  };

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#f7fafc', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <div style={{ textAlign: 'center', color: '#718096' }}>
          Loading tournament details...
        </div>
      </div>
    );
  }

  if (error || !tournament) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#f7fafc', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <div style={{ 
          backgroundColor: '#fed7d7', 
          color: '#c53030', 
          padding: '20px', 
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          {error || 'Tournament not found'}
        </div>
      </div>
    );
  }

  const isCreatedByMe = tournament.created_by === user?.id;
  const isPlayerInTournament = players.some(player => player.id === user?.id);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f7fafc', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Notification */}
        {notification && (
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            backgroundColor: notification.type === 'success' ? '#48bb78' : '#f56565',
            color: 'white',
            padding: '16px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            zIndex: 1000,
            maxWidth: '400px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>{notification.message}</span>
              <button
                onClick={() => setNotification(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'white',
                  fontSize: '18px',
                  cursor: 'pointer',
                  marginLeft: '12px'
                }}
              >
                ×
              </button>
            </div>
          </div>
        )}
        {/* Header */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '30px', 
          borderRadius: '12px', 
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
            <div>
              <h1 style={{ 
                fontSize: '32px', 
                fontWeight: 'bold', 
                color: '#2d3748', 
                margin: '0 0 12px 0' 
              }}>
                {tournament.name}
              </h1>
              <div style={{ display: 'flex', gap: '20px', fontSize: '16px', color: '#718096', marginBottom: '16px' }}>
                <span>📍 {tournament.location}</span>
                <span>📅 {formatDate(tournament.start_date)}</span>
                <span>💰 ${tournament.entry_fee}</span>
                <span>🎾 {tournament.system}</span>
              </div>
              {tournament.description && (
                <p style={{ color: '#4a5568', fontSize: '16px', margin: 0 }}>
                  {tournament.description}
                </p>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                backgroundColor: getStatusColor(tournament.status),
                color: 'white',
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '14px',
                fontWeight: '600',
                textTransform: 'uppercase'
              }}>
                {tournament.status}
              </div>
              {isCreatedByMe && (
                <div style={{
                  backgroundColor: '#e2e8f0',
                  color: '#4a5568',
                  padding: '8px 16px',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  MY TOURNAMENT
                </div>
              )}
            </div>
          </div>

          {/* Stats */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
            gap: '20px',
            marginBottom: '24px'
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2d3748' }}>
                {players.length}/{tournament.max_players}
              </div>
              <div style={{ fontSize: '14px', color: '#718096' }}>Players</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2d3748' }}>
                {tournament.current_round || 1}
              </div>
              <div style={{ fontSize: '14px', color: '#718096' }}>Current Round</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2d3748' }}>
                {matches.length}
              </div>
              <div style={{ fontSize: '14px', color: '#718096' }}>Active Matches</div>
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {isCreatedByMe && tournament.status === 'pending' && players.length >= 4 && (
              <button
                onClick={handleStartTournament}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#48bb78',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: '600'
                }}
              >
                🚀 Start Tournament
              </button>
            )}
            
            {!isCreatedByMe && tournament.status === 'pending' && !isPlayerInTournament && players.length < tournament.max_players && (
              <button
                onClick={handleJoinTournament}
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
                ➕ Join Tournament
              </button>
            )}

            {!isCreatedByMe && tournament.status === 'pending' && isPlayerInTournament && (
              <button
                onClick={handleLeaveTournament}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#f56565',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: '600'
                }}
              >
                ➖ Leave Tournament
              </button>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '12px', 
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          <div style={{ 
            display: 'flex', 
            borderBottom: '1px solid #e2e8f0' 
          }}>
            {['overview', 'players', 'matches', 'leaderboard'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  flex: 1,
                  padding: '16px',
                  backgroundColor: activeTab === tab ? '#4299e1' : 'transparent',
                  color: activeTab === tab ? 'white' : '#4a5568',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: '600',
                  textTransform: 'capitalize'
                }}
              >
                {tab}
              </button>
            ))}
          </div>

          <div style={{ padding: '24px' }}>
            {activeTab === 'overview' && (
              <OverviewTab tournament={tournament} />
            )}
            
            {activeTab === 'players' && (
              <PlayersTab 
                players={players} 
                tournament={tournament} 
                isCreatedByMe={isCreatedByMe}
                onPlayersChanged={loadTournamentData}
              />
            )}
            
            {activeTab === 'matches' && (
              <MatchesTab 
                matches={matches} 
                tournament={tournament}
                isCreatedByMe={isCreatedByMe}
                onRecordResult={handleRecordResult}
              />
            )}
            
            {activeTab === 'leaderboard' && (
              <LeaderboardTab leaderboard={leaderboard} tournament={tournament} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Tab Components
const OverviewTab = ({ tournament }) => (
  <div>
    <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#2d3748', marginBottom: '16px' }}>
      Tournament Overview
    </h3>
    <div style={{ display: 'grid', gap: '16px' }}>
      <div>
        <strong style={{ color: '#4a5568' }}>Format:</strong> {tournament.system}
      </div>
      <div>
        <strong style={{ color: '#4a5568' }}>Entry Fee:</strong> ${tournament.entry_fee}
      </div>
      <div>
        <strong style={{ color: '#4a5568' }}>Max Players:</strong> {tournament.max_players}
      </div>
      <div>
        <strong style={{ color: '#4a5568' }}>Start Date:</strong> {new Date(tournament.start_date).toLocaleDateString()}
      </div>
      {tournament.description && (
        <div>
          <strong style={{ color: '#4a5568' }}>Description:</strong>
          <p style={{ margin: '8px 0 0 0', color: '#718096' }}>{tournament.description}</p>
        </div>
      )}
    </div>
  </div>
);

const PlayersTab = ({ players, tournament, isCreatedByMe, onPlayersChanged }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [showAddPlayer, setShowAddPlayer] = useState(false);

  const searchUsers = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setSearchLoading(true);
    try {
      const response = await userAPI.searchUsers(query, 10);
      // Filter out players already in tournament
      const filtered = response.users.filter(user => 
        !players.some(player => player.id === user.id)
      );
      setSearchResults(filtered);
    } catch (err) {
      console.error('Search failed:', err);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleAddPlayer = async (playerId) => {
    try {
      await tournamentAPI.addPlayerToTournament(tournament.id, playerId);
      setSearchQuery('');
      setSearchResults([]);
      setShowAddPlayer(false);
      onPlayersChanged(); // Refresh tournament data
    } catch (err) {
      console.error('Failed to add player:', err);
    }
  };

  const handleRemovePlayer = async (playerId) => {
    if (!confirm('Are you sure you want to remove this player?')) {
      return;
    }

    try {
      await tournamentAPI.removePlayerFromTournament(tournament.id, playerId);
      onPlayersChanged(); // Refresh tournament data
    } catch (err) {
      console.error('Failed to remove player:', err);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchUsers(searchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#2d3748', margin: 0 }}>
          Players ({players.length}/{tournament.max_players})
        </h3>
        {isCreatedByMe && tournament.status === 'pending' && players.length < tournament.max_players && (
          <button
            onClick={() => setShowAddPlayer(!showAddPlayer)}
            style={{
              padding: '8px 16px',
              backgroundColor: '#48bb78',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            {showAddPlayer ? 'Cancel' : '+ Add Player'}
          </button>
        )}
      </div>

      {/* Add Player Interface */}
      {showAddPlayer && (
        <div style={{
          backgroundColor: '#f0fff4',
          border: '1px solid #9ae6b4',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '16px'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#2d3748' }}>Add Player to Tournament</h4>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search players by name or email..."
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '2px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
            
            {/* Search Results */}
            {(searchResults.length > 0 || searchLoading) && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                zIndex: 10,
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                {searchLoading ? (
                  <div style={{ padding: '12px', textAlign: 'center', color: '#718096' }}>
                    Searching...
                  </div>
                ) : (
                  searchResults.map(user => (
                    <div
                      key={user.id}
                      onClick={() => handleAddPlayer(user.id)}
                      style={{
                        padding: '12px',
                        borderBottom: '1px solid #f7fafc',
                        cursor: 'pointer',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}
                      onMouseEnter={(e) => e.target.style.backgroundColor = '#f7fafc'}
                      onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
                    >
                      <div>
                        <div style={{ fontWeight: '600', color: '#2d3748' }}>
                          {user.full_name || user.email}
                        </div>
                        <div style={{ fontSize: '12px', color: '#718096' }}>
                          {user.email}
                        </div>
                      </div>
                      <button
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#48bb78',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                      >
                        Add
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Players List */}
      {players.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
          No players have joined yet.
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '12px' }}>
          {players.map((player, index) => (
            <div 
              key={player.id} 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '12px',
                padding: '12px',
                backgroundColor: '#f7fafc',
                borderRadius: '8px'
              }}
            >
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#4299e1',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold'
              }}>
                {index + 1}
              </div>
              <div style={{ flex: 1 }}>
                              <div style={{ fontWeight: '600', color: '#2d3748' }}>
                {player.full_name || player.email}
              </div>
                <div style={{ fontSize: '14px', color: '#718096' }}>
                  {player.email}
                </div>
              </div>
              {isCreatedByMe && tournament.status === 'pending' && (
                <button
                  onClick={() => handleRemovePlayer(player.id)}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: '#f56565',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const MatchesTab = ({ matches, tournament, isCreatedByMe, onRecordResult }) => {
  const [results, setResults] = useState({});

  const handleResultChange = (matchId, field, value) => {
    setResults(prev => ({
      ...prev,
      [matchId]: {
        ...prev[matchId],
        [field]: value
      }
    }));
  };

  const handleSubmitResult = (matchId) => {
    const result = results[matchId];
    if (result && result.team1Score !== undefined && result.team2Score !== undefined) {
      onRecordResult(matchId, result.team1Score, result.team2Score);
    }
  };

  return (
    <div>
      <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#2d3748', marginBottom: '16px' }}>
        Current Round Matches
      </h3>
      {tournament.status === 'pending' ? (
        <div style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
          Tournament hasn't started yet. Matches will appear here once the tournament begins.
        </div>
      ) : matches.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
          No matches found for current round.
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '16px' }}>
          {matches.map(match => (
            <div 
              key={match.id}
              style={{
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '20px',
                backgroundColor: match.is_completed ? '#f0fff4' : '#fff'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ fontSize: '16px', fontWeight: '600', color: '#2d3748' }}>
                  Round {match.round_number} - Match
                </div>
                {match.is_completed && (
                  <div style={{
                    backgroundColor: '#48bb78',
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    COMPLETED
                  </div>
                )}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '20px', alignItems: 'center' }}>
                {/* Team 1 */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontWeight: '600', color: '#2d3748', marginBottom: '4px' }}>Team 1</div>
                  <div style={{ fontSize: '14px', color: '#4a5568' }}>
                    {match.team1_player1.full_name || match.team1_player1.email}
                  </div>
                  <div style={{ fontSize: '14px', color: '#4a5568' }}>
                    {match.team1_player2.full_name || match.team1_player2.email}
                  </div>
                </div>

                {/* Score */}
                <div style={{ textAlign: 'center' }}>
                  {match.is_completed ? (
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2d3748' }}>
                      {match.team1_score} - {match.team2_score}
                    </div>
                  ) : isCreatedByMe ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="number"
                        min="0"
                        placeholder="0"
                        value={results[match.id]?.team1Score || ''}
                        onChange={(e) => handleResultChange(match.id, 'team1Score', e.target.value)}
                        style={{
                          width: '50px',
                          padding: '4px 8px',
                          border: '1px solid #e2e8f0',
                          borderRadius: '4px',
                          textAlign: 'center'
                        }}
                      />
                      <span>-</span>
                      <input
                        type="number"
                        min="0"
                        placeholder="0"
                        value={results[match.id]?.team2Score || ''}
                        onChange={(e) => handleResultChange(match.id, 'team2Score', e.target.value)}
                        style={{
                          width: '50px',
                          padding: '4px 8px',
                          border: '1px solid #e2e8f0',
                          borderRadius: '4px',
                          textAlign: 'center'
                        }}
                      />
                      <button
                        onClick={() => handleSubmitResult(match.id)}
                        disabled={!results[match.id]?.team1Score || !results[match.id]?.team2Score}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#4299e1',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        Submit
                      </button>
                    </div>
                  ) : (
                    <div style={{ fontSize: '18px', color: '#718096' }}>
                      vs
                    </div>
                  )}
                </div>

                {/* Team 2 */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontWeight: '600', color: '#2d3748', marginBottom: '4px' }}>Team 2</div>
                  <div style={{ fontSize: '14px', color: '#4a5568' }}>
                    {match.team2_player1.full_name || match.team2_player1.email}
                  </div>
                  <div style={{ fontSize: '14px', color: '#4a5568' }}>
                    {match.team2_player2.full_name || match.team2_player2.email}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const LeaderboardTab = ({ leaderboard, tournament }) => (
  <div>
    <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#2d3748', marginBottom: '16px' }}>
      Tournament Leaderboard
    </h3>
    {!leaderboard || leaderboard.entries.length === 0 ? (
      <div style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
        No leaderboard data available yet.
      </div>
    ) : (
      <div>
        {leaderboard.winner && (
          <div style={{
            backgroundColor: '#fef5e7',
            border: '2px solid #f6ad55',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '24px',
            textAlign: 'center'
          }}>
            <h4 style={{ fontSize: '18px', fontWeight: 'bold', color: '#2d3748', margin: '0 0 8px 0' }}>
              🏆 Tournament Winner
            </h4>
            <div style={{ fontSize: '16px', color: '#4a5568' }}>
              {leaderboard.winner.player_name} - {leaderboard.winner.score} points
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gap: '8px' }}>
          {leaderboard.entries.map((entry, index) => (
            <div 
              key={entry.player_id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '16px',
                backgroundColor: index === 0 ? '#fef5e7' : '#f7fafc',
                borderRadius: '8px',
                border: index === 0 ? '2px solid #f6ad55' : '1px solid #e2e8f0'
              }}
            >
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: index === 0 ? '#f6ad55' : index === 1 ? '#c0c0c0' : index === 2 ? '#cd7f32' : '#4299e1',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '16px'
              }}>
                {entry.rank}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: '600', color: '#2d3748', fontSize: '16px' }}>
                  {entry.player_name}
                </div>
                <div style={{ fontSize: '14px', color: '#718096' }}>
                  {entry.email}
                </div>
              </div>
              <div style={{ 
                fontSize: '18px', 
                fontWeight: 'bold', 
                color: '#2d3748' 
              }}>
                {entry.score} pts
              </div>
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
);

export default TournamentDetailPage; 