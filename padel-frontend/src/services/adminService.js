/**
 * Admin Service
 *
 * API service for admin panel operations including statistics,
 * user management, tournament management, and audit logging.
 *
 * All endpoints require superuser authentication.
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with auth interceptor
const adminApi = axios.create({
  baseURL: `${API_BASE_URL}/admin`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
adminApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors
adminApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Statistics API
// ============================================================================

/**
 * Get overview statistics for admin dashboard
 * @returns {Promise} Overview stats with users, tournaments, activity, system health
 */
export const getOverviewStats = async () => {
  const response = await adminApi.get('/stats/overview');
  return response.data;
};

/**
 * Get growth data for charts
 * @param {string} period - 'daily', 'weekly', or 'monthly'
 * @returns {Promise} Growth data for user signups and tournament creation
 */
export const getGrowthStats = async (period = 'daily') => {
  const response = await adminApi.get('/stats/growth', {
    params: { period },
  });
  return response.data;
};

/**
 * Get user engagement metrics
 * @returns {Promise} Engagement metrics with top users and organizers
 */
export const getEngagementMetrics = async () => {
  const response = await adminApi.get('/stats/engagement');
  return response.data;
};

// ============================================================================
// User Management API
// ============================================================================

/**
 * Get paginated list of users with filtering
 * @param {Object} params - Query parameters
 * @param {string} params.search - Search by name or email
 * @param {boolean} params.is_active - Filter by active status
 * @param {boolean} params.is_verified - Filter by verified status
 * @param {boolean} params.is_superuser - Filter by superuser status
 * @param {number} params.limit - Max results (default 50)
 * @param {number} params.offset - Skip results (default 0)
 * @returns {Promise} Paginated user list
 */
export const getUsers = async (params = {}) => {
  const response = await adminApi.get('/users', { params });
  return response.data;
};

/**
 * Get detailed information about a specific user
 * @param {string} userId - User ID
 * @returns {Promise} User details with statistics
 */
export const getUserDetails = async (userId) => {
  const response = await adminApi.get(`/users/${userId}`);
  return response.data;
};

/**
 * Update user status
 * @param {string} userId - User ID
 * @param {Object} updates - Status updates
 * @param {boolean} updates.is_active - Active status
 * @param {boolean} updates.is_verified - Verified status
 * @param {boolean} updates.is_superuser - Superuser status
 * @param {string} updates.reason - Reason for change (for audit)
 * @returns {Promise} Updated user
 */
export const updateUserStatus = async (userId, updates) => {
  const response = await adminApi.patch(`/users/${userId}`, updates);
  return response.data;
};

/**
 * Delete a user
 * @param {string} userId - User ID
 * @param {boolean} permanent - If true, hard delete. Otherwise soft delete.
 * @param {string} reason - Reason for deletion (for audit)
 * @returns {Promise} Action response
 */
export const deleteUser = async (userId, permanent = false, reason = '') => {
  const response = await adminApi.delete(`/users/${userId}`, {
    data: { permanent, reason },
  });
  return response.data;
};

// ============================================================================
// Tournament Management API
// ============================================================================

/**
 * Get paginated list of tournaments with filtering
 * @param {Object} params - Query parameters
 * @param {string} params.search - Search by tournament name
 * @param {string} params.status - Filter by status
 * @param {string} params.tournament_system - Filter by system
 * @param {string} params.creator_id - Filter by creator
 * @param {number} params.limit - Max results (default 50)
 * @param {number} params.offset - Skip results (default 0)
 * @returns {Promise} Paginated tournament list
 */
export const getTournaments = async (params = {}) => {
  const response = await adminApi.get('/tournaments', { params });
  return response.data;
};

/**
 * Update a match result
 * @param {string} tournamentId - Tournament ID
 * @param {string} roundId - Round/Match ID
 * @param {Object} resultUpdate - New scores and reason
 * @param {number} resultUpdate.team1_score - Team 1 score
 * @param {number} resultUpdate.team2_score - Team 2 score
 * @param {string} resultUpdate.reason - Reason for change (required)
 * @returns {Promise} Action response
 */
export const updateMatchResult = async (tournamentId, roundId, resultUpdate) => {
  const response = await adminApi.patch(
    `/tournaments/${tournamentId}/results/${roundId}`,
    resultUpdate
  );
  return response.data;
};

/**
 * Recalculate all scores for a tournament
 * @param {string} tournamentId - Tournament ID
 * @param {string} reason - Reason for recalculation (required)
 * @returns {Promise} Action response
 */
export const recalculateTournamentScores = async (tournamentId, reason) => {
  const response = await adminApi.post(
    `/tournaments/${tournamentId}/recalculate`,
    { reason }
  );
  return response.data;
};

/**
 * Force a tournament status change
 * @param {string} tournamentId - Tournament ID
 * @param {string} status - New status ('pending', 'active', or 'completed')
 * @param {string} reason - Reason for change (required)
 * @returns {Promise} Action response
 */
export const forceTournamentStatusChange = async (tournamentId, status, reason) => {
  const response = await adminApi.patch(
    `/tournaments/${tournamentId}/status`,
    { status, reason }
  );
  return response.data;
};

// ============================================================================
// Audit Log API
// ============================================================================

/**
 * Get paginated audit logs with filtering
 * @param {Object} params - Query parameters
 * @param {string} params.admin_id - Filter by admin user ID
 * @param {string} params.action_type - Filter by action type
 * @param {string} params.target_type - Filter by target type
 * @param {string} params.start_date - Filter by start date
 * @param {string} params.end_date - Filter by end date
 * @param {number} params.limit - Max results (default 50)
 * @param {number} params.offset - Skip results (default 0)
 * @returns {Promise} Paginated audit log list
 */
export const getAuditLogs = async (params = {}) => {
  const response = await adminApi.get('/audit/logs', { params });
  return response.data;
};

/**
 * Get audit log statistics
 * @returns {Promise} Audit statistics
 */
export const getAuditStats = async () => {
  const response = await adminApi.get('/audit/stats');
  return response.data;
};

/**
 * Get complete audit history for a specific target entity
 * @param {string} targetType - Type of target ('user', 'tournament', etc.)
 * @param {string} targetId - ID of target entity
 * @returns {Promise} List of audit logs for the target
 */
export const getTargetHistory = async (targetType, targetId) => {
  const response = await adminApi.get(`/audit/target/${targetType}/${targetId}`);
  return response.data;
};

// Export default object with all methods
const adminService = {
  // Statistics
  getOverviewStats,
  getGrowthStats,
  getEngagementMetrics,

  // User Management
  getUsers,
  getUserDetails,
  updateUserStatus,
  deleteUser,

  // Tournament Management
  getTournaments,
  updateMatchResult,
  recalculateTournamentScores,
  forceTournamentStatusChange,

  // Audit Logs
  getAuditLogs,
  getAuditStats,
  getTargetHistory,
};

export default adminService;
