/**
 * Admin Tournaments Management Page
 *
 * View, search, filter, and manage tournaments.
 * Edit match results, recalculate scores, force status changes.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import adminService from '../services/adminService';
import './AdminTournamentsPage.css';

const AdminTournamentsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTournament, setSelectedTournament] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [systemFilter, setSystemFilter] = useState('all');

  // Pagination
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    if (!user?.is_superuser) {
      navigate('/dashboard');
      return;
    }
    fetchTournaments();
  }, [user, navigate, search, statusFilter, systemFilter, offset]);

  const fetchTournaments = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        limit,
        offset,
      };

      if (search) params.search = search;
      if (statusFilter !== 'all') params.status = statusFilter;
      if (systemFilter !== 'all') params.tournament_system = systemFilter;

      const data = await adminService.getTournaments(params);
      setTournaments(data.tournaments);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch tournaments:', err);
      setError(err.response?.data?.detail || 'Failed to load tournaments');
    } finally {
      setLoading(false);
    }
  };

  const handleViewTournament = (tournament) => {
    setSelectedTournament(tournament);
    setShowModal(true);
  };

  const handleForceStatusChange = async (tournamentId, newStatus) => {
    const reason = prompt(`Change status to ${newStatus}. Please provide a reason:`);
    if (!reason) return;

    try {
      await adminService.forceTournamentStatusChange(tournamentId, newStatus, reason);
      alert('Tournament status changed successfully');
      fetchTournaments();
      setShowModal(false);
    } catch (err) {
      alert('Failed to change status: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRecalculateScores = async (tournamentId) => {
    const reason = prompt('Recalculate all scores for this tournament. Please provide a reason:');
    if (!reason) return;

    try {
      await adminService.recalculateTournamentScores(tournamentId, reason);
      alert('Scores recalculated successfully');
      fetchTournaments();
    } catch (err) {
      alert('Failed to recalculate scores: ' + (err.response?.data?.detail || err.message));
    }
  };

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="admin-tournaments-page">
      <div className="page-header">
        <h1>Tournament Management</h1>
        <button onClick={() => navigate('/admin')} className="back-btn">
          ← Back to Dashboard
        </button>
      </div>

      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Search by tournament name..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setOffset(0);
          }}
          className="search-input"
        />

        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setOffset(0);
          }}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
        </select>

        <select
          value={systemFilter}
          onChange={(e) => {
            setSystemFilter(e.target.value);
            setOffset(0);
          }}
          className="filter-select"
        >
          <option value="all">All Formats</option>
          <option value="AMERICANO">Americano</option>
          <option value="MEXICANO">Mexicano</option>
        </select>
      </div>

      {/* Results Summary */}
      <div className="results-summary">
        <span>Total: {total} tournaments</span>
        <span>Page {currentPage} of {totalPages}</span>
      </div>

      {/* Tournaments Table */}
      {loading ? (
        <div className="loading">Loading tournaments...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="tournaments-table-container">
            <table className="tournaments-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Creator</th>
                  <th>Format</th>
                  <th>Status</th>
                  <th>Players</th>
                  <th>Rounds</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tournaments.map((t) => (
                  <tr key={t.id}>
                    <td><strong>{t.name}</strong></td>
                    <td>{t.creator_name || 'Unknown'}</td>
                    <td>
                      <span className="format-badge">{t.tournament_system}</span>
                    </td>
                    <td>
                      <span className={`status-badge ${t.status.toLowerCase()}`}>
                        {t.status}
                      </span>
                    </td>
                    <td>{t.player_count}</td>
                    <td>{t.rounds_completed}/{t.rounds_total}</td>
                    <td>{new Date(t.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        onClick={() => handleViewTournament(t)}
                        className="action-btn-small view"
                      >
                        Manage
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0}
              className="pagination-btn"
            >
              ← Previous
            </button>
            <span className="page-info">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setOffset(offset + limit)}
              disabled={offset + limit >= total}
              className="pagination-btn"
            >
              Next →
            </button>
          </div>
        </>
      )}

      {/* Tournament Management Modal */}
      {showModal && selectedTournament && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedTournament.name}</h2>
              <button onClick={() => setShowModal(false)} className="close-btn">
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="tournament-info">
                <h3>Tournament Information</h3>
                <p><strong>ID:</strong> {selectedTournament.id}</p>
                <p><strong>Creator:</strong> {selectedTournament.creator_name}</p>
                <p><strong>Format:</strong> {selectedTournament.tournament_system}</p>
                <p><strong>Status:</strong> <span className={`status-badge ${selectedTournament.status.toLowerCase()}`}>{selectedTournament.status}</span></p>
                <p><strong>Players:</strong> {selectedTournament.player_count}</p>
                <p><strong>Rounds:</strong> {selectedTournament.rounds_completed}/{selectedTournament.rounds_total} completed</p>
                <p><strong>Created:</strong> {new Date(selectedTournament.created_at).toLocaleString()}</p>
              </div>

              <div className="modal-actions">
                <h3>Admin Actions</h3>
                <div className="action-buttons-grid">
                  {selectedTournament.status !== 'pending' && (
                    <button
                      onClick={() => handleForceStatusChange(selectedTournament.id, 'pending')}
                      className="action-btn warning"
                    >
                      Set to Pending
                    </button>
                  )}

                  {selectedTournament.status !== 'active' && (
                    <button
                      onClick={() => handleForceStatusChange(selectedTournament.id, 'active')}
                      className="action-btn success"
                    >
                      Set to Active
                    </button>
                  )}

                  {selectedTournament.status !== 'completed' && (
                    <button
                      onClick={() => handleForceStatusChange(selectedTournament.id, 'completed')}
                      className="action-btn info"
                    >
                      Set to Completed
                    </button>
                  )}

                  <button
                    onClick={() => handleRecalculateScores(selectedTournament.id)}
                    className="action-btn primary"
                  >
                    Recalculate Scores
                  </button>

                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(selectedTournament.id);
                      alert('Tournament ID copied to clipboard');
                    }}
                    className="action-btn secondary"
                  >
                    Copy Tournament ID
                  </button>

                  <button
                    onClick={() => navigate(`/tournaments/${selectedTournament.id}`)}
                    className="action-btn secondary"
                  >
                    View as User
                  </button>
                </div>

                <div className="info-box">
                  <strong>Note:</strong> To edit individual match results, use the tournament detail page as an organizer.
                  More advanced match editing features coming soon!
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminTournamentsPage;
