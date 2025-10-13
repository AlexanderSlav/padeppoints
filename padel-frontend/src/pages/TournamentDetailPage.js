import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { tournamentAPI, userAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';
import './TournamentDetailPage.css';
import { FaMapMarkerAlt, FaCalendarAlt, FaDollarSign, FaBaseballBall, FaRocket, FaFlag, FaEdit, FaUsers, FaSearch, FaLightbulb, FaTrophy, FaPlusCircle, FaMinusCircle, FaCheckCircle, FaExclamationTriangle, FaTimes } from 'react-icons/fa';

const TournamentDetailPage = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [tournament, setTournament] = useState(null);
  const [players, setPlayers] = useState([]);
  const [allRounds, setAllRounds] = useState([]);
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [notification, setNotification] = useState(null);
  const [estimatedDuration, setEstimatedDuration] = useState(null);
  const [showFinishConfirm, setShowFinishConfirm] = useState(false);
  const [currentRoundView, setCurrentRoundView] = useState(null);

  useEffect(() => {
    if (id) {
      loadTournamentData();
    }
  }, [id]);

  // Estimate duration when tournament data changes
  useEffect(() => {
    const estimateTournamentDuration = async () => {
      if (tournament && players.length >= 4) {
        try {
          const duration = await tournamentAPI.estimateDuration(
            tournament.system, 
            players.length, 
            tournament.courts || 1, 
            tournament.points_per_match || 32
          );
          setEstimatedDuration(duration);
        } catch (err) {
          console.error('Failed to estimate duration:', err);
          setEstimatedDuration(null);
        }
      }
    };

    estimateTournamentDuration();
  }, [tournament, players]);

  const loadTournamentData = async () => {
    try {
      setLoading(true);
      const [tournamentData, playersData, roundsData] = await Promise.all([
        tournamentAPI.getTournament(id),
        tournamentAPI.getTournamentPlayers(id),
        tournamentAPI.getAllRounds(id)
      ]);
      
      setTournament(tournamentData);
      setPlayers(playersData.players || []);
      setAllRounds(roundsData || []);

      // Debug log to check if average_player_rating is present
      console.log('Tournament data received:', tournamentData);
      console.log('Average player rating:', tournamentData.average_player_rating);


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

  const handleGenerateNextRound = async () => {
    try {
      await tournamentAPI.generateNextRound(id);
      await loadTournamentData();
      setNotification({ type: 'success', message: 'Next round generated successfully!' });
    } catch (err) {
      setNotification({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to generate next round'
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

      // Reload tournament data
      const [tournamentData, playersData, roundsData] = await Promise.all([
        tournamentAPI.getTournament(id),
        tournamentAPI.getTournamentPlayers(id),
        tournamentAPI.getAllRounds(id)
      ]);

      setTournament(tournamentData);
      setPlayers(playersData.players || []);
      setAllRounds(roundsData || []);

      // Reload leaderboard if tournament is active
      if (tournamentData.status === 'active' || tournamentData.status === 'completed') {
        try {
          const leaderboardData = await tournamentAPI.getTournamentLeaderboard(id);
          setLeaderboard(leaderboardData);
        } catch (err) {
          console.log('No leaderboard data found');
        }
      }

      // Sync frontend view with backend's current round
      // Backend auto-advances rounds for Americano (not Mexicano - that's manual)
      if (tournamentData.current_round && tournamentData.current_round !== currentRoundView) {
        setCurrentRoundView(tournamentData.current_round);
        // Only show auto-advance message for non-Mexicano tournaments
        if (tournamentData.system !== 'MEXICANO') {
          setNotification({ type: 'success', message: 'Round completed! Advanced to next round.' });
        } else {
          setNotification({ type: 'success', message: 'Match result recorded successfully!' });
        }
      } else {
        setNotification({ type: 'success', message: 'Match result recorded successfully!' });
      }
    } catch (err) {
      setNotification({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to record match result'
      });
    }
  };

  const handleFinishTournament = async () => {
    try {
      await tournamentAPI.finishTournament(id);
      setShowFinishConfirm(false);
      loadTournamentData();
      setNotification({ type: 'success', message: 'Tournament finished successfully!' });
    } catch (err) {
      setShowFinishConfirm(false);
      setNotification({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to finish tournament'
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
      <div className="tournament-detail-page">
        <div className="loading-state">
          Loading tournament details...
        </div>
      </div>
    );
  }

  if (error || !tournament) {
    return (
      <div className="tournament-detail-page">
        <div className="error-state">
          {error || 'Tournament not found'}
        </div>
      </div>
    );
  }

  const isCreatedByMe = tournament.created_by === user?.id;
  const isPlayerInTournament = players.some(player => player.id === user?.id);

  // Debug: Check tournament state right before render
  console.log('Rendering with tournament state:', tournament);
  console.log('Average rating in render:', tournament?.average_player_rating);

  return (
    <div className="tournament-detail-page">
      <div className="tournament-detail-container">

        {/* Notification */}
        {notification && (
          <div className={`notification ${notification.type}`}>
            <div className="notification-content">
              <span>{notification.message}</span>
              <button
                onClick={() => setNotification(null)}
                className="notification-close"
              >
                ×
              </button>
            </div>
          </div>
        )}
        {/* Header */}
        <div style={{
          backgroundColor: 'white',
          padding: '32px',
          borderRadius: '16px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.07)',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
            <div>
              <h1 style={{
                fontSize: '36px',
                fontWeight: '800',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                margin: '0 0 16px 0',
                letterSpacing: '-0.5px'
              }}>
                {tournament.name}
              </h1>
              <div style={{ display: 'flex', gap: '20px', fontSize: '15px', marginBottom: '20px', flexWrap: 'wrap' }}>
                <span style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  backgroundColor: '#f7fafc',
                  borderRadius: '20px',
                  color: '#4a5568',
                  fontWeight: '600',
                  border: '1px solid #e2e8f0'
                }}>
                  <FaMapMarkerAlt /> {tournament.location}
                </span>
                <span style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  backgroundColor: '#f7fafc',
                  borderRadius: '20px',
                  color: '#4a5568',
                  fontWeight: '600',
                  border: '1px solid #e2e8f0'
                }}>
                  <FaCalendarAlt /> {formatDate(tournament.start_date)}
                </span>
                <span style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  backgroundColor: '#f7fafc',
                  borderRadius: '20px',
                  color: '#4a5568',
                  fontWeight: '600',
                  border: '1px solid #e2e8f0'
                }}>
                  <FaDollarSign /> ${tournament.entry_fee}
                </span>
                <span style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  backgroundColor: '#f7fafc',
                  borderRadius: '20px',
                  color: '#4a5568',
                  fontWeight: '600',
                  border: '1px solid #e2e8f0'
                }}>
                  <FaBaseballBall /> {tournament.system}
                </span>
              </div>
              {tournament.description && (
                <p style={{
                  color: '#64748b',
                  fontSize: '16px',
                  margin: 0,
                  lineHeight: '1.6'
                }}>
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
                fontSize: '13px',
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                {tournament.status}
              </div>
              {isCreatedByMe && (
                <div style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  padding: '8px 16px',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: '600',
                  letterSpacing: '0.5px'
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
            gap: '24px',
            marginTop: '32px',
            marginBottom: '32px'
          }}>
            <div style={{
              textAlign: 'center',
              padding: '20px',
              backgroundColor: 'white',
              borderRadius: '12px',
              border: '2px solid #edf2f7'
            }}>
              <div style={{
                fontSize: '32px',
                fontWeight: '700',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                {players.length}/{tournament.max_players}
              </div>
              <div style={{ fontSize: '14px', color: '#718096', fontWeight: '600', marginTop: '4px' }}>Players</div>
            </div>
            <div style={{
              textAlign: 'center',
              padding: '20px',
              backgroundColor: 'white',
              borderRadius: '12px',
              border: '2px solid #edf2f7'
            }}>
              <div style={{
                fontSize: '32px',
                fontWeight: '700',
                color: '#4299e1'
              }}>
                {tournament.current_round || 1}
              </div>
              <div style={{ fontSize: '14px', color: '#718096', fontWeight: '600', marginTop: '4px' }}>Current Round</div>
            </div>
            {estimatedDuration && (
              <div style={{
                textAlign: 'center',
                padding: '20px',
                backgroundColor: 'white',
                borderRadius: '12px',
                border: '2px solid #edf2f7'
              }}>
                <div style={{
                  fontSize: '32px',
                  fontWeight: '700',
                  color: '#48bb78'
                }}>
                  {Math.floor(estimatedDuration.estimated_minutes / 60)}h {estimatedDuration.estimated_minutes % 60}m
                </div>
                <div style={{ fontSize: '14px', color: '#718096', fontWeight: '600', marginTop: '4px' }}>Estimated Duration</div>
              </div>
            )}
            {tournament && tournament.average_player_rating && (
              <div style={{
                textAlign: 'center',
                padding: '20px',
                backgroundColor: 'white',
                borderRadius: '12px',
                border: '2px solid #edf2f7'
              }}>
                <div style={{
                  fontSize: '32px',
                  fontWeight: '700',
                  color: '#805ad5'
                }}>
                  {Math.round(tournament.average_player_rating)}
                </div>
                <div style={{ fontSize: '14px', color: '#718096', fontWeight: '600', marginTop: '4px' }}>Average ELO</div>
              </div>
            )}
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
                  fontSize: '15px',
                  fontWeight: '600',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#38a169';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#48bb78';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <FaRocket /> Start Tournament
              </button>
            )}

            {isCreatedByMe && tournament.status === 'active' && tournament.system === 'MEXICANO' &&
             allRounds.filter(r => r.round_number === tournament.current_round).length > 0 &&
             allRounds.filter(r => r.round_number === tournament.current_round).every(m => m.is_completed) && (
              <button
                onClick={handleGenerateNextRound}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '15px',
                  fontWeight: '600',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#5a67d8';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#667eea';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <FaRocket /> Generate Next Round
              </button>
            )}

            {isCreatedByMe && tournament.status === 'active' && (
              <button
                onClick={() => setShowFinishConfirm(true)}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#ed8936',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '15px',
                  fontWeight: '600',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#dd6b20';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#ed8936';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <FaFlag /> Finish Tournament
              </button>
            )}

            
            {!isCreatedByMe && tournament.status === 'pending' && !isPlayerInTournament && players.length < tournament.max_players && (
              <button
                onClick={handleJoinTournament}
                style={{
                  padding: '12px 24px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '15px',
                  fontWeight: '600',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '0.9';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '1';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <FaPlusCircle /> Join Tournament
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
                  fontSize: '15px',
                  fontWeight: '600',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#e53e3e';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f56565';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <FaMinusCircle /> Leave Tournament
              </button>
            )}

          </div>
        </div>

        {/* Tabs */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.07)',
          overflow: 'hidden'
        }}>
          <div style={{
            display: 'flex',
            borderBottom: '2px solid #edf2f7'
          }}>
            {['overview', 'players', 'schedule', 'leaderboard'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  flex: 1,
                  padding: '16px 20px',
                  backgroundColor: 'transparent',
                  color: activeTab === tab ? '#667eea' : '#718096',
                  border: 'none',
                  borderBottom: activeTab === tab ? '2px solid #667eea' : '2px solid transparent',
                  marginBottom: '-2px',
                  cursor: 'pointer',
                  fontSize: '15px',
                  fontWeight: activeTab === tab ? '600' : '500',
                  textTransform: 'capitalize',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== tab) {
                    e.currentTarget.style.color = '#4a5568';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== tab) {
                    e.currentTarget.style.color = '#718096';
                  }
                }}
              >
                {tab}
              </button>
            ))}
          </div>

          <div style={{ padding: '32px' }}>
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
            

            {activeTab === 'schedule' && (
              <ScheduleTab
                rounds={allRounds}
                onRecordResult={handleRecordResult}
                tournament={tournament}
                isCreatedByMe={isCreatedByMe}
                isPlayerInTournament={isPlayerInTournament}
                currentRoundView={currentRoundView}
                setCurrentRoundView={setCurrentRoundView}
              />
            )}

            {activeTab === 'leaderboard' && (
              <LeaderboardTab leaderboard={leaderboard} tournament={tournament} />
            )}
          </div>
        </div>

        {/* Finish Tournament Confirmation Modal */}
        {showFinishConfirm && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '32px',
              maxWidth: '500px',
              width: '90%',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
            }}>
              <h3 style={{
                margin: '0 0 16px 0',
                fontSize: '20px',
                fontWeight: '600',
                color: '#1a202c'
              }}>
                Finish Tournament?
              </h3>
              <p style={{
                margin: '0 0 24px 0',
                fontSize: '14px',
                color: '#4a5568',
                lineHeight: '1.6'
              }}>
                Are you sure you want to finish this tournament? This will mark the tournament as completed and lock all results. This action cannot be undone.
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => setShowFinishConfirm(false)}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
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
                  Cancel
                </button>
                <button
                  onClick={handleFinishTournament}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#ed8936',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#dd6b20';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = '#ed8936';
                  }}
                >
                  Yes, Finish Tournament
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

// Tab Components
const OverviewTab = ({ tournament }) => (
  <div>
    <h3 style={{
      fontSize: '22px',
      fontWeight: '600',
      color: '#2d3748',
      marginBottom: '24px'
    }}>
      Tournament Overview
    </h3>
    <div style={{ display: 'grid', gap: '16px' }}>
      {[
        { label: 'Format', value: tournament.system, icon: <FaBaseballBall /> },
        { label: 'Entry Fee', value: `$${tournament.entry_fee}`, icon: <FaDollarSign /> },
        { label: 'Max Players', value: tournament.max_players, icon: <FaUsers /> },
        { label: 'Start Date', value: new Date(tournament.start_date).toLocaleDateString(), icon: <FaCalendarAlt /> }
      ].map((item, index) => (
        <div key={index} style={{
          display: 'flex',
          alignItems: 'center',
          padding: '16px 20px',
          backgroundColor: '#f7fafc',
          borderRadius: '10px',
          border: '1px solid #e2e8f0'
        }}>
          <span style={{ fontSize: '24px', marginRight: '16px' }}>{item.icon}</span>
          <div>
            <div style={{ fontSize: '13px', color: '#718096', fontWeight: '500', marginBottom: '4px' }}>
              {item.label}
            </div>
            <div style={{ fontSize: '16px', color: '#2d3748', fontWeight: '600' }}>
              {item.value}
            </div>
          </div>
        </div>
      ))}
      {tournament.description && (
        <div style={{
          padding: '20px',
          backgroundColor: '#f7fafc',
          borderRadius: '10px',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ fontSize: '13px', color: '#718096', fontWeight: '600', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FaEdit /> Description
          </div>
          <p style={{ margin: 0, color: '#4a5568', lineHeight: '1.6' }}>
            {tournament.description}
          </p>
        </div>
      )}
    </div>
  </div>
);

const PlayersTab = ({ players, tournament, isCreatedByMe, onPlayersChanged }) => {
  const [playerName, setPlayerName] = useState('');
  const [showAddPlayer, setShowAddPlayer] = useState(false);
  const [addingPlayer, setAddingPlayer] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searching, setSearching] = useState(false);
  const [playerError, setPlayerError] = useState('');
  const [playerSuccess, setPlayerSuccess] = useState('');
  const [removeConfirm, setRemoveConfirm] = useState(null);

  // Clear error messages when tournament status or player count changes
  React.useEffect(() => {
    setPlayerError('');
    setPlayerSuccess('');
  }, [tournament.status, players.length]);

  const handleFillWithTestPlayers = async () => {
    try {
      console.log('Filling tournament with test players');
      const result = await tournamentAPI.fillTournamentWithTestPlayers(tournament.id);
      setPlayerSuccess(`Tournament filled with ${result.total_players} players!`);
      setTimeout(() => setPlayerSuccess(''), 5000);
      // Reload tournament data
      await onPlayersChanged();
    } catch (err) {
      console.error('Fill test players error:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to fill tournament with test players';
      setPlayerError(errorMsg);
      setTimeout(() => setPlayerError(''), 5000);
    }
  };

  // Debounced search function
  const searchUsers = async (query) => {
    if (!query.trim() || query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    setSearching(true);
    try {
      const response = await userAPI.searchUsers(query, 5);
      setSuggestions(response.users);
      setShowSuggestions(true);
    } catch (err) {
      console.error('Failed to search users:', err);
      setSuggestions([]);
    } finally {
      setSearching(false);
    }
  };

  // Debounce search
  const debouncedSearch = React.useCallback(
    React.useMemo(() => {
      let timeoutId;
      return (query) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => searchUsers(query), 300);
      };
    }, []),
    []
  );

  const handlePlayerNameChange = (e) => {
    const value = e.target.value;
    setPlayerName(value);
    debouncedSearch(value);
  };

  const handleSuggestionClick = (suggestion) => {
    setPlayerName(suggestion.full_name);
    setShowSuggestions(false);
    setSuggestions([]);
  };

  const handleAddPlayer = async () => {
    if (!playerName.trim()) {
      return;
    }

    setAddingPlayer(true);
    setShowSuggestions(false);
    setSuggestions([]);
    setPlayerError('');
    setPlayerSuccess('');

    try {
      await tournamentAPI.addPlayerByName(tournament.id, playerName.trim());
      setPlayerName('');
      setShowAddPlayer(false);
      setPlayerSuccess('Player added successfully!');
      setTimeout(() => setPlayerSuccess(''), 3000);
      onPlayersChanged(); // Refresh tournament data
    } catch (err) {
      console.error('Failed to add player:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to add player';
      setPlayerError(errorMsg);
      setTimeout(() => setPlayerError(''), 5000);
    } finally {
      setAddingPlayer(false);
    }
  };

  const handleRemovePlayer = async (playerId) => {
    try {
      await tournamentAPI.removePlayerFromTournament(tournament.id, playerId);
      setRemoveConfirm(null);
      setPlayerSuccess('Player removed successfully!');
      setTimeout(() => setPlayerSuccess(''), 3000);
      onPlayersChanged(); // Refresh tournament data
    } catch (err) {
      console.error('Failed to remove player:', err);
      setRemoveConfirm(null);
      setPlayerError('Failed to remove player');
      setTimeout(() => setPlayerError(''), 5000);
    }
  };



  return (
    <div>
      {/* Success Message */}
      {playerSuccess && (
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#d4edda',
          border: '1px solid #c3e6cb',
          borderRadius: '8px',
          color: '#155724',
          marginBottom: '16px',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <FaCheckCircle /> {playerSuccess}
        </div>
      )}

      {/* Error Message */}
      {playerError && (
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '8px',
          color: '#721c24',
          marginBottom: '16px',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <FaExclamationTriangle /> {playerError}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h3 style={{
          fontSize: '24px',
          fontWeight: '800',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          margin: 0
        }}>
          Players ({players.length}/{tournament.max_players})
        </h3>
        {isCreatedByMe && tournament.status === 'pending' && players.length < tournament.max_players && (
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={handleFillWithTestPlayers}
              style={{
                padding: '10px 20px',
                backgroundColor: '#f59e0b',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#d97706';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#f59e0b';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              🧪 Fill with Test Players
            </button>
            <button
              onClick={() => setShowAddPlayer(!showAddPlayer)}
              style={{
                padding: '10px 20px',
                backgroundColor: '#48bb78',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#38a169';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#48bb78';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              {showAddPlayer ? 'Cancel' : '+ Add Player'}
            </button>
          </div>
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
            <div style={{ display: 'flex', gap: '8px' }}>
              <div style={{ flex: 1, position: 'relative' }}>
                <input
                  type="text"
                  value={playerName}
                  onChange={handlePlayerNameChange}
                  placeholder="Enter player name (e.g., 'Andrey A', 'Alex B')"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '2px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    boxSizing: 'border-box'
                  }}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && playerName.trim()) {
                      handleAddPlayer();
                    }
                  }}
                  onFocus={() => {
                    if (suggestions.length > 0) {
                      setShowSuggestions(true);
                    }
                  }}
                  onBlur={() => {
                    // Delay hiding suggestions to allow clicking on them
                    setTimeout(() => setShowSuggestions(false), 200);
                  }}
                />
                
                {/* Suggestions Dropdown */}
                {showSuggestions && suggestions.length > 0 && (
                  <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                    zIndex: 1000,
                    maxHeight: '200px',
                    overflowY: 'auto'
                  }}>
                    {suggestions.map((suggestion, index) => (
                      <div
                        key={suggestion.id}
                        onClick={() => handleSuggestionClick(suggestion)}
                        style={{
                          padding: '8px 12px',
                          cursor: 'pointer',
                          borderBottom: index < suggestions.length - 1 ? '1px solid #f1f5f9' : 'none',
                          backgroundColor: '#f8fafc',
                          ':hover': {
                            backgroundColor: '#e2e8f0'
                          }
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.backgroundColor = '#e2e8f0';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.backgroundColor = '#f8fafc';
                        }}
                      >
                        <div style={{ fontWeight: '500', color: '#2d3748' }}>
                          {suggestion.full_name}
                        </div>
                        {suggestion.email && (
                          <div style={{ fontSize: '12px', color: '#718096' }}>
                            {suggestion.email}
                          </div>
                        )}
                        {!suggestion.email && (
                          <div style={{ fontSize: '12px', color: '#48bb78' }}>
                            Guest User
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Loading indicator */}
                {searching && (
                  <div style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: '#718096'
                  }}>
                    <FaSearch />
                  </div>
                )}
              </div>
              
              <button
                onClick={handleAddPlayer}
                disabled={!playerName.trim() || addingPlayer}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#48bb78',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  opacity: (!playerName.trim() || addingPlayer) ? 0.6 : 1
                }}
              >
                {addingPlayer ? 'Adding...' : 'Add'}
              </button>
            </div>

            <div style={{ fontSize: '12px', color: '#718096', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FaLightbulb /> Tip: Start typing to see existing users, or enter a new name to create a guest player.
            </div>
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
                gap: '16px',
                padding: '16px 20px',
                backgroundColor: '#f7fafc',
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#edf2f7';
                e.currentTarget.style.transform = 'translateX(2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#f7fafc';
                e.currentTarget.style.transform = 'translateX(0)';
              }}
            >
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                {index + 1}
              </div>
              {/* Profile Picture */}
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                overflow: 'hidden',
                backgroundColor: '#e2e8f0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px',
                fontWeight: 'bold',
                color: '#4a5568'
              }}>
                {player.picture ? (
                  <img 
                    src={player.picture} 
                    alt={player.full_name || 'Player'} 
                    style={{ 
                      width: '100%', 
                      height: '100%', 
                      objectFit: 'cover' 
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.parentElement.textContent = (player.full_name || player.email || 'P')[0].toUpperCase();
                    }}
                  />
                ) : (
                  (player.full_name || player.email || 'P')[0].toUpperCase()
                )}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Link 
                    to={`/users/${player.id}/profile`}
                    style={{ 
                      textDecoration: 'none', 
                      color: '#2d3748',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                  >
                    {player.full_name || player.email}
                  </Link>
                  {/* ELO Rating Badge */}
                  <span style={{
                    backgroundColor: '#805ad5',
                    color: 'white',
                    padding: '3px 8px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    {Math.round(player.rating || 1000)}
                  </span>
                </div>
                <div style={{ fontSize: '14px', color: '#718096' }}>
                  {player.email}
                </div>
              </div>
              {isCreatedByMe && tournament.status === 'pending' && (
                <button
                  onClick={() => setRemoveConfirm(player)}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: '#f56565',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: '600',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e53e3e'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f56565'}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Remove Player Confirmation Modal */}
      {removeConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '32px',
            maxWidth: '450px',
            width: '90%',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }}>
            <h3 style={{
              margin: '0 0 16px 0',
              fontSize: '20px',
              fontWeight: '600',
              color: '#1a202c'
            }}>
              Remove Player?
            </h3>
            <p style={{
              margin: '0 0 24px 0',
              fontSize: '14px',
              color: '#4a5568',
              lineHeight: '1.6'
            }}>
              Are you sure you want to remove <strong>{removeConfirm.full_name || removeConfirm.email}</strong> from this tournament?
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setRemoveConfirm(null)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
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
                Cancel
              </button>
              <button
                onClick={() => handleRemovePlayer(removeConfirm.id)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#f56565',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#e53e3e';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#f56565';
                }}
              >
                Yes, Remove Player
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


// Player Card Component for Court Visualization
const PlayerCard = ({ player, isLeft }) => {
  const bgColor = isLeft ? 'rgba(72, 187, 120, 0.9)' : 'rgba(66, 153, 225, 0.9)';
  
  return (
    <div style={{
      backgroundColor: bgColor,
      color: 'white',
      padding: '10px 14px',
      borderRadius: '6px',
      minWidth: '120px',
      textAlign: 'center',
      boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
      border: '2px solid rgba(255, 255, 255, 0.3)'
    }}>
      <div style={{ 
        fontSize: '14px', 
        fontWeight: '600',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis'
      }}>
        {player ? (player.full_name || player.email || 'Unknown') : 'TBD'}
      </div>
    </div>
  );
};

const ScheduleTab = ({ rounds, onRecordResult, tournament, isCreatedByMe, isPlayerInTournament, currentRoundView, setCurrentRoundView }) => {
  const [editingScores, setEditingScores] = useState({});
  const [submittingResults, setSubmittingResults] = useState({});


  if (!rounds || rounds.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
        No rounds generated yet.
      </div>
    );
  }

  const grouped = rounds.reduce((acc, match) => {
    acc[match.round_number] = acc[match.round_number] || [];
    acc[match.round_number].push(match);
    return acc;
  }, {});

  const roundNumbers = Object.keys(grouped).map(Number).sort((a, b) => a - b);

  // Auto-select first incomplete round on initial load (only if not already set)
  if (currentRoundView === null && roundNumbers.length > 0) {
    const firstIncompleteRound = roundNumbers.find(roundNum =>
      grouped[roundNum].some(match => match.team1_score === null || match.team2_score === null)
    ) || roundNumbers[0];
    setCurrentRoundView(firstIncompleteRound);
    return null; // Re-render after setting initial round
  }

  // If currentRoundView is set but that round no longer exists, reset to first round
  if (currentRoundView !== null && !roundNumbers.includes(currentRoundView)) {
    setCurrentRoundView(roundNumbers[0]);
    return null;
  }

  const handleScoreChange = (matchId, field, value) => {
    setEditingScores(prev => ({
      ...prev,
      [matchId]: {
        ...prev[matchId],
        [field]: value
      }
    }));
  };

  const handleSubmitResult = async (match) => {
    const scores = editingScores[match.id];

    // Check team1_score is provided
    if (!scores || scores.team1_score === undefined || scores.team1_score === '') {
      alert('Please enter team 1 score');
      return;
    }

    const team1Score = parseInt(scores.team1_score);

    // Validate team1_score
    if (isNaN(team1Score) || team1Score < 0) {
      alert('Please enter a valid non-negative score for team 1');
      return;
    }

    // For formats with auto-calculation, team2_score is optional
    let team2Score = null;
    const hasAutoCalculation = (tournament.system === 'AMERICANO' || tournament.system === 'MEXICANO') &&
                                tournament.points_per_match;

    if (hasAutoCalculation) {
      // If team2_score is provided, use it; otherwise backend will auto-calculate
      if (scores.team2_score !== undefined && scores.team2_score !== '') {
        team2Score = parseInt(scores.team2_score);
        if (isNaN(team2Score) || team2Score < 0) {
          alert('Please enter a valid non-negative score for team 2');
          return;
        }
        // Validate sum if both provided
        if (team1Score + team2Score !== tournament.points_per_match) {
          alert(`For ${tournament.system} format, scores must sum to ${tournament.points_per_match} points`);
          return;
        }
      }
      // If team2_score not provided, backend will calculate it
    } else {
      // For other formats, team2_score is required
      if (scores.team2_score === undefined || scores.team2_score === '') {
        alert('Please enter both team scores');
        return;
      }
      team2Score = parseInt(scores.team2_score);
      if (isNaN(team2Score) || team2Score < 0) {
        alert('Please enter valid non-negative scores');
        return;
      }
    }

    setSubmittingResults(prev => ({ ...prev, [match.id]: true }));

    try {
      await onRecordResult(match.id, team1Score, team2Score);
      // Clear editing scores after successful submission
      setEditingScores(prev => {
        const newScores = { ...prev };
        delete newScores[match.id];
        return newScores;
      });
    } catch (error) {
      console.error('Failed to submit result:', error);
    } finally {
      setSubmittingResults(prev => ({ ...prev, [match.id]: false }));
    }
  };

  const startEditing = (match) => {
    setEditingScores(prev => ({
      ...prev,
      [match.id]: {
        team1_score: match.team1_score || '',
        team2_score: match.team2_score || ''
      }
    }));
  };

  const cancelEditing = (matchId) => {
    setEditingScores(prev => {
      const newScores = { ...prev };
      delete newScores[matchId];
      return newScores;
    });
  };

  const canEditResults = isCreatedByMe || isPlayerInTournament;
  const isEditing = (matchId) => editingScores[matchId] !== undefined;

  const currentRoundIndex = roundNumbers.indexOf(currentRoundView);
  const hasPrevious = currentRoundIndex > 0;
  const hasNext = currentRoundIndex < roundNumbers.length - 1;

  const goToPreviousRound = () => {
    if (hasPrevious) {
      setCurrentRoundView(roundNumbers[currentRoundIndex - 1]);
    }
  };

  const goToNextRound = () => {
    if (hasNext) {
      setCurrentRoundView(roundNumbers[currentRoundIndex + 1]);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{
          fontSize: '24px',
          fontWeight: '800',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          margin: 0
        }}>
          Tournament Schedule & Results
        </h3>

        {/* Round Navigation */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={goToPreviousRound}
            disabled={!hasPrevious}
            style={{
              padding: '8px 16px',
              backgroundColor: hasPrevious ? 'white' : '#f7fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              color: hasPrevious ? '#4a5568' : '#cbd5e0',
              cursor: hasPrevious ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s'
            }}
          >
            ← Previous
          </button>

          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#667eea',
            minWidth: '100px',
            textAlign: 'center'
          }}>
            Round {currentRoundView} of {roundNumbers.length}
          </div>

          <button
            onClick={goToNextRound}
            disabled={!hasNext}
            style={{
              padding: '8px 16px',
              backgroundColor: hasNext ? 'white' : '#f7fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              color: hasNext ? '#4a5568' : '#cbd5e0',
              cursor: hasNext ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s'
            }}
          >
            Next →
          </button>
        </div>
      </div>
      {[currentRoundView].map(num => (
        <div key={num} style={{ marginBottom: '32px' }}>
          <h4 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#2d3748',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '32px',
              height: '32px',
              backgroundColor: '#667eea',
              borderRadius: '50%',
              color: 'white',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              {num}
            </span>
            Round {num}
          </h4>
          <div style={{ display: 'grid', gap: '12px' }}>
            {grouped[num].map(match => (
              <div
                key={match.id}
                style={{
                  position: 'relative',
                  backgroundColor: match.is_completed ? '#f0fff4' : 'white',
                  border: match.is_completed ? '1px solid #9ae6b4' : '1px solid #e2e8f0',
                  borderRadius: '12px',
                  padding: '20px',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.07)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {/* Court Number Badge */}
                {match.court_number && (
                  <div style={{
                    position: 'absolute',
                    top: '12px',
                    right: '12px',
                    backgroundColor: '#667eea',
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    Court {match.court_number}
                  </div>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '20px', alignItems: 'center' }}>
                  {/* Team 1 */}
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontWeight: '600', color: '#2d3748', marginBottom: '4px' }}>Team 1</div>
                    <div style={{ fontSize: '14px', color: '#4a5568' }}>
                      {match.team1_player1 ? (match.team1_player1.full_name || match.team1_player1.email || 'Unknown Player') : 'Unknown Player'}
                    </div>
                    <div style={{ fontSize: '14px', color: '#4a5568' }}>
                      {match.team1_player2 ? (match.team1_player2.full_name || match.team1_player2.email || 'Unknown Player') : 'Unknown Player'}
                    </div>
                  </div>

                  {/* Score Section */}
                  <div style={{ textAlign: 'center', minWidth: '200px' }}>
                  {isEditing(match.id) ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', alignItems: 'center' }}>
                        <input
                          type="number"
                          value={editingScores[match.id]?.team1_score || ''}
                          onChange={(e) => handleScoreChange(match.id, 'team1_score', e.target.value)}
                          placeholder="Team 1"
                          min="0"
                          style={{
                            width: '60px',
                            padding: '4px 8px',
                            border: '1px solid #e2e8f0',
                            borderRadius: '4px',
                            textAlign: 'center',
                            fontSize: '16px'
                          }}
                        />
                        <span style={{ color: '#718096', fontSize: '16px' }}>-</span>
                        <input
                          type="number"
                          value={editingScores[match.id]?.team2_score || ''}
                          onChange={(e) => handleScoreChange(match.id, 'team2_score', e.target.value)}
                          placeholder="Team 2"
                          min="0"
                          style={{
                            width: '60px',
                            padding: '4px 8px',
                            border: '1px solid #e2e8f0',
                            borderRadius: '4px',
                            textAlign: 'center',
                            fontSize: '16px'
                          }}
                        />
                      </div>
                      <div style={{ display: 'flex', gap: '4px', justifyContent: 'center' }}>
                        <button
                          onClick={() => handleSubmitResult(match)}
                          disabled={submittingResults[match.id]}
                          style={{
                            padding: '4px 12px',
                            backgroundColor: '#48bb78',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px',
                            fontWeight: '600',
                            opacity: submittingResults[match.id] ? 0.6 : 1
                          }}
                        >
                          {submittingResults[match.id] ? 'Saving...' : 'Save'}
                        </button>
                        <button
                          onClick={() => cancelEditing(match.id)}
                          disabled={submittingResults[match.id]}
                          style={{
                            padding: '4px 12px',
                            backgroundColor: '#f56565',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px',
                            fontWeight: '600'
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      {match.is_completed ? (
                        <div>
                          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2d3748' }}>
                            {match.team1_score} - {match.team2_score}
                          </div>
                          <div style={{
                            backgroundColor: '#48bb78',
                            color: 'white',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: '600',
                            marginTop: '8px'
                          }}>
                            COMPLETED
                          </div>
                          {canEditResults && tournament.status !== 'completed' && (
                            <button
                              onClick={() => startEditing(match)}
                              style={{
                                padding: '4px 12px',
                                backgroundColor: '#4299e1',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                                fontWeight: '600',
                                marginTop: '8px'
                              }}
                            >
                              Edit Result
                            </button>
                          )}
                        </div>
                      ) : (
                        <div>
                          <div style={{ fontSize: '18px', color: '#718096', marginBottom: '8px' }}>
                            vs
                          </div>
                          {canEditResults && tournament.status !== 'completed' && (
                            <button
                              onClick={() => startEditing(match)}
                              style={{
                                padding: '8px 16px',
                                backgroundColor: '#4299e1',
                                color: 'white',
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '14px',
                                fontWeight: '600'
                              }}
                            >
                              Enter Result
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                  {/* Team 2 */}
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontWeight: '600', color: '#2d3748', marginBottom: '4px' }}>Team 2</div>
                    <div style={{ fontSize: '14px', color: '#4a5568' }}>
                      {match.team2_player1 ? (match.team2_player1.full_name || match.team2_player1.email || 'Unknown Player') : 'Unknown Player'}
                    </div>
                    <div style={{ fontSize: '14px', color: '#4a5568' }}>
                      {match.team2_player2 ? (match.team2_player2.full_name || match.team2_player2.email || 'Unknown Player') : 'Unknown Player'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

const LeaderboardTab = ({ leaderboard, tournament }) => (
  <div>
    <h3 style={{
      fontSize: '24px',
      fontWeight: '800',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
      marginBottom: '24px'
    }}>
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
            padding: '24px',
            marginBottom: '24px',
            textAlign: 'center'
          }}>
            <h4 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#2d3748',
              margin: '0 0 12px 0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}>
              <FaTrophy /> Tournament Winner
            </h4>
            <div style={{
              fontSize: '18px',
              color: '#744210',
              fontWeight: '600'
            }}>
              {leaderboard.winner.player_name} - {leaderboard.winner.score} points
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gap: '8px' }}>
          {/* Header row */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '60px 1fr 80px 100px 120px',
            gap: '16px',
            padding: '12px 20px',
            backgroundColor: '#f7fafc',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: '600',
            color: '#718096',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '16px'
          }}>
            <div>Rank</div>
            <div>Player</div>
            <div>Points</div>
            <div>Difference</div>
            <div>W-L-T</div>
          </div>
          
          {leaderboard.entries.map((entry, index) => (
            <div
              key={entry.player_id}
              style={{
                display: 'grid',
                gridTemplateColumns: '60px 1fr 80px 100px 120px',
                gap: '16px',
                alignItems: 'center',
                padding: '16px 20px',
                backgroundColor: index === 0 ? '#fef5e7' : 'white',
                borderRadius: '10px',
                border: index === 0 ? '2px solid #f6ad55' : '1px solid #e2e8f0',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateX(2px)';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateX(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: index === 0 ? '#f6ad55' : index === 1 ? '#cbd5e0' : index === 2 ? '#cd7f32' : '#667eea',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                {entry.rank}
              </div>
              <div>
                <div style={{ fontWeight: '600', fontSize: '16px' }}>
                  <Link 
                    to={`/users/${entry.player_id}/profile`}
                    style={{ 
                      textDecoration: 'none', 
                      color: '#2d3748',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.textDecoration = 'underline';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.textDecoration = 'none';
                    }}
                  >
                    {entry.player_name}
                  </Link>
                </div>
                <div style={{ fontSize: '14px', color: '#718096' }}>
                  {entry.email}
                </div>
              </div>
              <div style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#2d3748',
                textAlign: 'center'
              }}>
                {entry.score}
              </div>
              <div style={{
                fontSize: '16px',
                fontWeight: '700',
                color: entry.points_difference >= 0 ? '#10b981' : '#ef4444',
                textAlign: 'center',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px'
              }}>
                {entry.points_difference >= 0 ? '↑' : '↓'}
                {Math.abs(entry.points_difference || 0)}
              </div>
              <div style={{
                fontSize: '14px',
                textAlign: 'center',
                color: '#4a5568'
              }}>
                <span style={{ color: '#48bb78', fontWeight: '600' }}>{entry.wins || 0}</span>-
                <span style={{ color: '#f56565', fontWeight: '600' }}>{entry.losses || 0}</span>-
                <span style={{ color: '#718096', fontWeight: '600' }}>{entry.ties || 0}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
);

export default TournamentDetailPage; 