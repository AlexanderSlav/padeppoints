/**
 * Admin Audit Log Page
 *
 * View complete audit trail of all admin actions.
 * Filter by admin, action type, date range, etc.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import adminService from '../services/adminService';
import './AdminAuditPage.css';

const AdminAuditPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Filters
  const [actionTypeFilter, setActionTypeFilter] = useState('all');
  const [targetTypeFilter, setTargetTypeFilter] = useState('all');

  // Pagination
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 50;

  useEffect(() => {
    if (!user?.is_superuser) {
      navigate('/dashboard');
      return;
    }
    fetchAuditLogs();
  }, [user, navigate, actionTypeFilter, targetTypeFilter, offset]);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        limit,
        offset,
      };

      if (actionTypeFilter !== 'all') params.action_type = actionTypeFilter;
      if (targetTypeFilter !== 'all') params.target_type = targetTypeFilter;

      const data = await adminService.getAuditLogs(params);
      setLogs(data.logs);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
      setError(err.response?.data?.detail || 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (log) => {
    setSelectedLog(log);
    setShowModal(true);
  };

  const getActionIcon = (actionType) => {
    const icons = {
      'user_delete': '🗑️',
      'user_update': '✏️',
      'user_status_change': '🔄',
      'tournament_result_edit': '🎯',
      'tournament_score_recalc': '🧮',
      'tournament_status_change': '📊',
      'tournament_delete': '❌',
      'system_config_change': '⚙️',
    };
    return icons[actionType] || '📝';
  };

  const getActionColor = (actionType) => {
    if (actionType.includes('delete')) return 'danger';
    if (actionType.includes('update') || actionType.includes('edit')) return 'warning';
    if (actionType.includes('status')) return 'info';
    return 'default';
  };

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="admin-audit-page">
      <div className="page-header">
        <h1>Audit Logs</h1>
        <button onClick={() => navigate('/admin')} className="back-btn">
          ← Back to Dashboard
        </button>
      </div>

      {/* Filters */}
      <div className="filters">
        <select
          value={actionTypeFilter}
          onChange={(e) => {
            setActionTypeFilter(e.target.value);
            setOffset(0);
          }}
          className="filter-select"
        >
          <option value="all">All Actions</option>
          <option value="user_delete">User Delete</option>
          <option value="user_update">User Update</option>
          <option value="user_status_change">User Status Change</option>
          <option value="tournament_result_edit">Tournament Result Edit</option>
          <option value="tournament_score_recalc">Score Recalculation</option>
          <option value="tournament_status_change">Tournament Status Change</option>
        </select>

        <select
          value={targetTypeFilter}
          onChange={(e) => {
            setTargetTypeFilter(e.target.value);
            setOffset(0);
          }}
          className="filter-select"
        >
          <option value="all">All Targets</option>
          <option value="user">User</option>
          <option value="tournament">Tournament</option>
          <option value="match">Match</option>
          <option value="system">System</option>
        </select>

        <button onClick={fetchAuditLogs} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      {/* Results Summary */}
      <div className="results-summary">
        <span>Total: {total} audit entries</span>
        <span>Page {currentPage} of {totalPages}</span>
      </div>

      {/* Audit Logs Table */}
      {loading ? (
        <div className="loading">Loading audit logs...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : logs.length === 0 ? (
        <div className="no-logs">
          <p>No audit logs found.</p>
          <p className="hint">Admin actions will appear here once performed.</p>
        </div>
      ) : (
        <>
          <div className="audit-table-container">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Admin</th>
                  <th>Action</th>
                  <th>Target</th>
                  <th>IP Address</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className="timestamp">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td>{log.admin_name || log.admin_id || 'System'}</td>
                    <td>
                      <span className={`action-badge ${getActionColor(log.action_type)}`}>
                        {getActionIcon(log.action_type)} {log.action_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td>
                      <span className="target-info">
                        {log.target_type}
                        <br />
                        <small>{log.target_id.substring(0, 8)}...</small>
                      </span>
                    </td>
                    <td>{log.ip_address || 'N/A'}</td>
                    <td>
                      <button
                        onClick={() => handleViewDetails(log)}
                        className="action-btn-small view"
                      >
                        View
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

      {/* Audit Log Detail Modal */}
      {showModal && selectedLog && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Audit Log Details</h2>
              <button onClick={() => setShowModal(false)} className="close-btn">
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="audit-detail">
                <h3>Basic Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <strong>Log ID:</strong>
                    <span>{selectedLog.id}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Timestamp:</strong>
                    <span>{new Date(selectedLog.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Admin:</strong>
                    <span>{selectedLog.admin_name || selectedLog.admin_id}</span>
                  </div>
                  <div className="detail-item">
                    <strong>IP Address:</strong>
                    <span>{selectedLog.ip_address || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Action Type:</strong>
                    <span className={`action-badge ${getActionColor(selectedLog.action_type)}`}>
                      {selectedLog.action_type.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="detail-item">
                    <strong>Target Type:</strong>
                    <span>{selectedLog.target_type}</span>
                  </div>
                </div>

                <div className="detail-item full-width">
                  <strong>Target ID:</strong>
                  <span className="monospace">{selectedLog.target_id}</span>
                </div>
              </div>

              {selectedLog.details && (
                <div className="audit-detail">
                  <h3>Action Details</h3>

                  {selectedLog.details.reason && (
                    <div className="reason-box">
                      <strong>Reason:</strong>
                      <p>{selectedLog.details.reason}</p>
                    </div>
                  )}

                  {selectedLog.details.old_values && (
                    <div className="values-section">
                      <h4>Old Values:</h4>
                      <pre className="json-display">
                        {JSON.stringify(selectedLog.details.old_values, null, 2)}
                      </pre>
                    </div>
                  )}

                  {selectedLog.details.new_values && (
                    <div className="values-section">
                      <h4>New Values:</h4>
                      <pre className="json-display">
                        {JSON.stringify(selectedLog.details.new_values, null, 2)}
                      </pre>
                    </div>
                  )}

                  {!selectedLog.details.old_values && !selectedLog.details.new_values && (
                    <pre className="json-display">
                      {JSON.stringify(selectedLog.details, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminAuditPage;
