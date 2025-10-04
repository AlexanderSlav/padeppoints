/**
 * Admin Dashboard Page
 *
 * Main admin panel showing overview statistics, user metrics,
 * tournament metrics, and quick access to admin functions.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import adminService from '../services/adminService';
import './AdminDashboardPage.css';

const AdminDashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is superuser
    if (!user?.is_superuser) {
      navigate('/dashboard');
      return;
    }

    fetchDashboardStats();
  }, [user, navigate]);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminService.getOverviewStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch dashboard stats:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="loading">Loading admin dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <div className="error-message">
          <h3>Error Loading Dashboard</h3>
          <p>{error}</p>
          <button onClick={fetchDashboardStats}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <div className="admin-nav">
          <button onClick={() => navigate('/admin/users')} className="nav-btn">
            👥 Users
          </button>
          <button onClick={() => navigate('/admin/tournaments')} className="nav-btn">
            🏆 Tournaments
          </button>
          <button onClick={() => navigate('/admin/audit')} className="nav-btn">
            📋 Audit Logs
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        {/* User Stats */}
        <div className="stat-card">
          <h3>Total Users</h3>
          <div className="stat-value">{stats?.users?.total || 0}</div>
          <div className="stat-details">
            <span className="stat-detail green">
              Active: {stats?.users?.active || 0}
            </span>
            <span className="stat-detail gray">
              Inactive: {stats?.users?.inactive || 0}
            </span>
          </div>
        </div>

        <div className="stat-card">
          <h3>Verified Users</h3>
          <div className="stat-value">{stats?.users?.verified || 0}</div>
          <div className="stat-details">
            <span className="stat-detail orange">
              Unverified: {stats?.users?.unverified || 0}
            </span>
          </div>
        </div>

        <div className="stat-card">
          <h3>New Users (Week)</h3>
          <div className="stat-value">{stats?.users?.new_this_week || 0}</div>
          <div className="stat-details">
            <span className="stat-detail">
              Month: {stats?.users?.new_this_month || 0}
            </span>
          </div>
        </div>

        {/* Tournament Stats */}
        <div className="stat-card">
          <h3>Total Tournaments</h3>
          <div className="stat-value">{stats?.tournaments?.total || 0}</div>
          <div className="stat-details">
            <span className="stat-detail blue">
              Active: {stats?.tournaments?.active || 0}
            </span>
            <span className="stat-detail gray">
              Pending: {stats?.tournaments?.pending || 0}
            </span>
          </div>
        </div>

        <div className="stat-card">
          <h3>Completed Tournaments</h3>
          <div className="stat-value">{stats?.tournaments?.completed || 0}</div>
          <div className="stat-details">
            {stats?.tournaments?.by_format && (
              <>
                <span className="stat-detail">
                  Americano: {stats.tournaments.by_format.AMERICANO || 0}
                </span>
                <span className="stat-detail">
                  Mexicano: {stats.tournaments.by_format.MEXICANO || 0}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Activity Stats */}
        <div className="stat-card">
          <h3>Matches This Week</h3>
          <div className="stat-value">{stats?.activity?.matches_this_week || 0}</div>
          <div className="stat-details">
            <span className="stat-detail">
              Today: {stats?.activity?.matches_today || 0}
            </span>
          </div>
        </div>

        <div className="stat-card">
          <h3>Avg Players/Tournament</h3>
          <div className="stat-value">
            {stats?.activity?.avg_players_per_tournament?.toFixed(1) || '0.0'}
          </div>
        </div>

        <div className="stat-card">
          <h3>Peak Concurrent</h3>
          <div className="stat-value">
            {stats?.activity?.peak_concurrent_tournaments || 0}
          </div>
          <div className="stat-details">
            <span className="stat-detail">Active tournaments</span>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="system-health">
        <h2>System Health</h2>
        <div className="health-grid">
          <div className="health-item">
            <span className="health-label">Database Status</span>
            <span className={`health-value ${stats?.system?.database_status === 'healthy' ? 'green' : 'red'}`}>
              {stats?.system?.database_status || 'Unknown'}
            </span>
          </div>
          <div className="health-item">
            <span className="health-label">API Version</span>
            <span className="health-value">{stats?.system?.api_version || 'N/A'}</span>
          </div>
          <div className="health-item">
            <span className="health-label">Total Users</span>
            <span className="health-value">{stats?.system?.total_users || 0}</span>
          </div>
          <div className="health-item">
            <span className="health-label">Total Tournaments</span>
            <span className="health-value">{stats?.system?.total_tournaments || 0}</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-buttons">
          <button
            className="action-btn"
            onClick={() => navigate('/admin/users')}
          >
            <span className="action-icon">👥</span>
            <span className="action-text">Manage Users</span>
          </button>
          <button
            className="action-btn"
            onClick={() => navigate('/admin/tournaments')}
          >
            <span className="action-icon">🏆</span>
            <span className="action-text">Manage Tournaments</span>
          </button>
          <button
            className="action-btn"
            onClick={() => navigate('/admin/audit')}
          >
            <span className="action-icon">📋</span>
            <span className="action-text">View Audit Logs</span>
          </button>
          <button
            className="action-btn"
            onClick={fetchDashboardStats}
          >
            <span className="action-icon">🔄</span>
            <span className="action-text">Refresh Stats</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;
