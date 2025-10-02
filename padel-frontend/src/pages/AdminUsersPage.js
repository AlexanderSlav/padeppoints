/**
 * Admin Users Management Page
 *
 * View, search, filter, and manage users.
 * Supports user status changes and deletion.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import adminService from '../services/adminService';
import './AdminUsersPage.css';

const AdminUsersPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [verifiedFilter, setVerifiedFilter] = useState('all');

  // Pagination
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    if (!user?.is_superuser) {
      navigate('/dashboard');
      return;
    }
    fetchUsers();
  }, [user, navigate, search, statusFilter, verifiedFilter, offset]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        limit,
        offset,
      };

      if (search) params.search = search;
      if (statusFilter !== 'all') params.is_active = statusFilter === 'active';
      if (verifiedFilter !== 'all') params.is_verified = verifiedFilter === 'verified';

      const data = await adminService.getUsers(params);
      setUsers(data.users);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleViewUser = async (userId) => {
    try {
      const data = await adminService.getUserDetails(userId);
      setSelectedUser(data);
      setShowModal(true);
    } catch (err) {
      alert('Failed to load user details: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleUpdateStatus = async (userId, updates) => {
    const reason = prompt('Please provide a reason for this status change:');
    if (!reason) return;

    try {
      await adminService.updateUserStatus(userId, { ...updates, reason });
      alert('User status updated successfully');
      fetchUsers();
      if (selectedUser) {
        const updated = await adminService.getUserDetails(userId);
        setSelectedUser(updated);
      }
    } catch (err) {
      alert('Failed to update user: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeleteUser = async (userId, permanent = false) => {
    const confirmMsg = permanent
      ? 'Are you sure you want to PERMANENTLY delete this user? This cannot be undone!'
      : 'Are you sure you want to deactivate this user?';

    if (!window.confirm(confirmMsg)) return;

    const reason = prompt('Please provide a reason for deletion:');
    if (!reason) return;

    try {
      await adminService.deleteUser(userId, permanent, reason);
      alert(permanent ? 'User permanently deleted' : 'User deactivated');
      setShowModal(false);
      fetchUsers();
    } catch (err) {
      alert('Failed to delete user: ' + (err.response?.data?.detail || err.message));
    }
  };

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="admin-users-page">
      <div className="page-header">
        <h1>User Management</h1>
        <button onClick={() => navigate('/admin')} className="back-btn">
          ← Back to Dashboard
        </button>
      </div>

      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Search by name or email..."
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
          <option value="active">Active Only</option>
          <option value="inactive">Inactive Only</option>
        </select>

        <select
          value={verifiedFilter}
          onChange={(e) => {
            setVerifiedFilter(e.target.value);
            setOffset(0);
          }}
          className="filter-select"
        >
          <option value="all">All Verification</option>
          <option value="verified">Verified Only</option>
          <option value="unverified">Unverified Only</option>
        </select>
      </div>

      {/* Results Summary */}
      <div className="results-summary">
        <span>Total: {total} users</span>
        <span>Page {currentPage} of {totalPages}</span>
      </div>

      {/* Users Table */}
      {loading ? (
        <div className="loading">Loading users...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="users-table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Verified</th>
                  <th>Superuser</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.full_name || '(No name)'}</td>
                    <td>{u.email || '(Guest)'}</td>
                    <td>
                      <span className={`status-badge ${u.is_active ? 'active' : 'inactive'}`}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${u.is_verified ? 'verified' : 'unverified'}`}>
                        {u.is_verified ? '✓' : '✗'}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${u.is_superuser ? 'superuser' : ''}`}>
                        {u.is_superuser ? '★' : '-'}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => handleViewUser(u.id)}
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

      {/* User Detail Modal */}
      {showModal && selectedUser && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>User Details</h2>
              <button onClick={() => setShowModal(false)} className="close-btn">
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="user-info">
                <h3>Basic Information</h3>
                <p><strong>ID:</strong> {selectedUser.user.id}</p>
                <p><strong>Name:</strong> {selectedUser.user.full_name || '(No name)'}</p>
                <p><strong>Email:</strong> {selectedUser.user.email || '(Guest)'}</p>
                <p><strong>Active:</strong> {selectedUser.user.is_active ? 'Yes' : 'No'}</p>
                <p><strong>Verified:</strong> {selectedUser.user.is_verified ? 'Yes' : 'No'}</p>
                <p><strong>Superuser:</strong> {selectedUser.user.is_superuser ? 'Yes' : 'No'}</p>
              </div>

              <div className="user-stats">
                <h3>Statistics</h3>
                <p><strong>Tournaments Created:</strong> {selectedUser.statistics.tournaments_created}</p>
                <p><strong>Tournaments Played:</strong> {selectedUser.statistics.tournaments_played}</p>
                <p><strong>Matches Played:</strong> {selectedUser.statistics.matches_played}</p>
                <p><strong>Last Activity:</strong> {selectedUser.statistics.last_activity || 'Never'}</p>
              </div>

              <div className="modal-actions">
                <h3>Admin Actions</h3>
                <div className="action-buttons-grid">
                  {selectedUser.user.is_active ? (
                    <button
                      onClick={() => handleUpdateStatus(selectedUser.user.id, { is_active: false })}
                      className="action-btn warning"
                    >
                      Deactivate User
                    </button>
                  ) : (
                    <button
                      onClick={() => handleUpdateStatus(selectedUser.user.id, { is_active: true })}
                      className="action-btn success"
                    >
                      Activate User
                    </button>
                  )}

                  {!selectedUser.user.is_verified && (
                    <button
                      onClick={() => handleUpdateStatus(selectedUser.user.id, { is_verified: true })}
                      className="action-btn success"
                    >
                      Verify User
                    </button>
                  )}

                  {!selectedUser.user.is_superuser && (
                    <button
                      onClick={() => handleUpdateStatus(selectedUser.user.id, { is_superuser: true })}
                      className="action-btn superuser"
                    >
                      Make Superuser
                    </button>
                  )}

                  <button
                    onClick={() => handleDeleteUser(selectedUser.user.id, false)}
                    className="action-btn danger"
                  >
                    Soft Delete
                  </button>

                  <button
                    onClick={() => handleDeleteUser(selectedUser.user.id, true)}
                    className="action-btn danger-dark"
                  >
                    Permanent Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUsersPage;
