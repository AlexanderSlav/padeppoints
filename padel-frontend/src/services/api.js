import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('🔐 API Request: Adding Bearer token to', config.method?.toUpperCase(), config.url);
  } else {
    console.log('🔓 API Request: No token for', config.method?.toUpperCase(), config.url);
  }
  
  // Add cache-busting headers for GET requests to prevent stale data
  if (config.method === 'get') {
    config.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
    config.headers['Pragma'] = 'no-cache';
    config.headers['Expires'] = '0';
  }
  
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response: Success for', response.config.method?.toUpperCase(), response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ API Response: Error for', error.config?.method?.toUpperCase(), error.config?.url, '- Status:', error.response?.status);
    if (error.response?.status === 401) {
      console.log('🚨 API Response: 401 Unauthorized - removing tokens and redirecting to login');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  // Get Google login URL
  getGoogleLoginUrl: async () => {
    console.log('🔍 authAPI: Getting Google login URL');
    const response = await api.get('/auth/google/authorize');
    return response.data;
  },

  // Email/password login
  loginWithEmail: async (email, password) => {
    console.log('🔍 authAPI: Login with email', email);
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const response = await api.post('/auth/jwt/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },

  // Register new user
  register: async (email, password, fullName) => {
    console.log('🔍 authAPI: Register user', email);
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  // Get current user profile
  getCurrentUser: async () => {
    console.log('🔍 authAPI: Getting current user ...');
    const response = await api.get('/users/me');
    return response.data;
  },

  // Check auth status
  getAuthStatus: async () => {
    console.log('🔍 authAPI: Checking authentication');
    try {
      const user = await authAPI.getCurrentUser();
      return { authenticated: true, user };
    } catch {
      return { authenticated: false, user: null };
    }
  },

  // Logout
  logout: async () => {
    console.log('🔍 authAPI: Logging out');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};

// Tournament API
export const tournamentAPI = {
  // Get all tournaments with filters
  getTournaments: async (filters = {}) => {
    console.log('🔍 tournamentAPI: Getting tournaments with filters', filters);
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
        params.append(key, filters[key]);
      }
    });
    const response = await api.get(`/tournaments?${params.toString()}`);
    return response.data;
  },

  // Get my tournaments (created by me)
  getMyTournaments: async () => {
    console.log('🔍 tournamentAPI: Getting my tournaments');
    const response = await api.get('/tournaments/my');
    return response.data;
  },

  // Get joined tournaments
  getJoinedTournaments: async () => {
    console.log('🔍 tournamentAPI: Getting joined tournaments');
    const response = await api.get('/tournaments/joined');
    return response.data;
  },

  // Get upcoming tournaments
  getUpcomingTournaments: async (limit = 10) => {
    console.log('🔍 tournamentAPI: Getting upcoming tournaments');
    const response = await api.get(`/tournaments/upcoming?limit=${limit}`);
    return response.data;
  },

  // Get tournament formats
  getTournamentFormats: async () => {
    console.log('🔍 tournamentAPI: Getting tournament formats');
    const response = await api.get('/tournaments/formats');
    return response.data;
  },

  // Get tournament statuses
  getTournamentStatuses: async () => {
    console.log('🔍 tournamentAPI: Getting tournament statuses');
    const response = await api.get('/tournaments/statuses');
    return response.data;
  },

  // Get tournament by ID
  getTournament: async (id) => {
    console.log('🔍 tournamentAPI: Getting tournament', id);
    const response = await api.get(`/tournaments/${id}`);
    return response.data;
  },

  // Create tournament
  createTournament: async (tournamentData) => {
    console.log('🔍 tournamentAPI: Creating tournament', tournamentData);
    const response = await api.post('/tournaments', tournamentData);
    return response.data;
  },

  // Update tournament
  updateTournament: async (id, tournamentData) => {
    console.log('🔍 tournamentAPI: Updating tournament', id);
    const response = await api.put(`/tournaments/${id}`, tournamentData);
    return response.data;
  },

  // Delete tournament
  deleteTournament: async (id) => {
    console.log('🔍 tournamentAPI: Deleting tournament', id);
    const response = await api.delete(`/tournaments/${id}`);
    return response.data;
  },

  // Join tournament
  joinTournament: async (id) => {
    console.log('🔍 tournamentAPI: Joining tournament', id);
    const response = await api.post(`/tournaments/${id}/join`);
    return response.data;
  },

  // Leave tournament
  leaveTournament: async (id) => {
    console.log('🔍 tournamentAPI: Leaving tournament', id);
    const response = await api.post(`/tournaments/${id}/leave`);
    return response.data;
  },

  // Check if can join tournament
  canJoinTournament: async (id) => {
    console.log('🔍 tournamentAPI: Checking can join tournament', id);
    const response = await api.get(`/tournaments/${id}/can-join`);
    return response.data;
  },

  // Get tournament players
  getTournamentPlayers: async (id) => {
    console.log('🔍 tournamentAPI: Getting tournament players', id);
    const response = await api.get(`/tournaments/${id}/players`);
    return response.data;
  },

  // Start tournament
  startTournament: async (id) => {
    console.log('🔍 tournamentAPI: Starting tournament', id);
    const response = await api.post(`/tournaments/${id}/start`);
    return response.data;
  },

  // Finish tournament
  finishTournament: async (id) => {
    console.log('🔍 tournamentAPI: Finishing tournament', id);
    const response = await api.post(`/tournaments/${id}/finish`);
    return response.data;
  },

  // Get current round matches
  getCurrentRoundMatches: async (id) => {
    console.log('🔍 tournamentAPI: Getting current round matches', id);
    const response = await api.get(`/tournaments/${id}/matches/current`);
    return response.data;
  },

  // Get all rounds
  getAllRounds: async (id) => {
    console.log('🔍 tournamentAPI: Getting all rounds', id);
    const response = await api.get(`/tournaments/${id}/rounds`);
    return response.data;
  },

  // Estimate duration
  estimateDuration: async (system, players, courts, pointsPerGame = 21, secondsPerPoint = 25, restSeconds = 60) => {
    console.log('🔍 tournamentAPI: Estimating duration', system, players, courts, pointsPerGame, secondsPerPoint, restSeconds);
    const params = new URLSearchParams({ 
      system, 
      players: players.toString(), 
      courts: courts.toString(),
      points_per_game: pointsPerGame.toString(),
      seconds_per_point: secondsPerPoint.toString(),
      rest_seconds: restSeconds.toString()
    });
    const response = await api.get(`/tournaments/estimate-duration?${params.toString()}`);
    return response.data;
  },

  // Calculate optimal points
  calculateOptimalPoints: async (system, players, courts, hours, secondsPerPoint = 25, restSeconds = 60) => {
    console.log('🔍 tournamentAPI: Calculating optimal points', system, players, courts, hours, secondsPerPoint, restSeconds);
    const params = new URLSearchParams({ 
      system, 
      players: players.toString(), 
      courts: courts.toString(),
      hours: hours.toString(),
      seconds_per_point: secondsPerPoint.toString(),
      rest_seconds: restSeconds.toString()
    });
    const response = await api.get(`/tournaments/calculate-optimal-points?${params.toString()}`);
    return response.data;
  },
  
  // Get comprehensive tournament planning advice
  getTournamentPlanningAdvice: async (params) => {
    console.log('🔍 tournamentAPI: Getting tournament planning advice', params);
    const queryParams = new URLSearchParams();
    
    // Add required parameters
    queryParams.append('players', params.players.toString());
    queryParams.append('courts', params.courts.toString());
    queryParams.append('hours', params.hours.toString());
    queryParams.append('seconds_per_point', (params.secondsPerPoint || 25).toString());
    queryParams.append('rest_seconds', (params.restSeconds || 60).toString());
    queryParams.append('system', params.system || 'AMERICANO');
    
    // Add optional points_per_match if provided
    if (params.pointsPerMatch) {
      queryParams.append('points_per_match', params.pointsPerMatch.toString());
    }
    
    const response = await api.get(`/tournaments/tournament-planning-advice?${queryParams.toString()}`);
    return response.data;
  },

  // Record match result
  recordMatchResult: async (matchId, team1Score, team2Score) => {
    console.log('🔍 tournamentAPI: Recording match result', matchId);
    const response = await api.put(`/tournaments/matches/${matchId}/result`, {
      team1_score: team1Score,
      team2_score: team2Score
    });
    return response.data;
  },

  // Get tournament leaderboard
  getTournamentLeaderboard: async (id) => {
    console.log('🔍 tournamentAPI: Getting tournament leaderboard', id);
    const response = await api.get(`/tournaments/${id}/leaderboard`);
    return response.data;
  },

  // Get tournament scores
  getTournamentScores: async (id) => {
    console.log('🔍 tournamentAPI: Getting tournament scores', id);
    const response = await api.get(`/tournaments/${id}/scores`);
    return response.data;
  },

  // Add player to tournament (organizer only)
  addPlayerToTournament: async (tournamentId, playerId) => {
    console.log('🔍 tournamentAPI: Adding player to tournament', tournamentId, playerId);
    const response = await api.post(`/tournaments/${tournamentId}/add-player`, {
      player_id: playerId
    });
    return response.data;
  },

  // Remove player from tournament (organizer only)
  removePlayerFromTournament: async (tournamentId, playerId) => {
    console.log('🔍 tournamentAPI: Removing player from tournament', tournamentId, playerId);
    const response = await api.post(`/tournaments/${tournamentId}/remove-player`, {
      player_id: playerId
    });
    return response.data;
  },

  // Add player to tournament by name (searches for user first, creates guest if not found)
  addPlayerByName: async (tournamentId, playerName) => {
    console.log('🔍 tournamentAPI: Adding player by name', tournamentId, playerName);
    
    // First search for the user by name
    const searchResponse = await userAPI.searchUsers(playerName, 10);
    const users = searchResponse.users;
    
    let selectedUser = null;
    
    // Look for exact match first
    for (const user of users) {
      if (user.full_name.toLowerCase() === playerName.toLowerCase()) {
        selectedUser = user;
        break;
      }
    }
    
    // If no exact match found, create a guest user
    if (!selectedUser) {
      console.log('🔍 tournamentAPI: No existing user found, creating guest user');
      selectedUser = await userAPI.createGuestUser(playerName);
    }
    
    // Add the user to the tournament using their ID
    const response = await api.post(`/tournaments/${tournamentId}/add-player`, {
      player_id: selectedUser.id
    });
    return response.data;
  },

};

// User API
export const userAPI = {
  // Search users
  searchUsers: async (searchQuery = '', limit = 10) => {
    console.log('🔍 userAPI: Searching users', searchQuery);
    const params = new URLSearchParams();
    if (searchQuery) params.append('search', searchQuery);
    params.append('limit', limit.toString());
    const response = await api.get(`/users?${params.toString()}`);
    return response.data;
  },

  // Create guest user
  createGuestUser: async (fullName) => {
    console.log('🔍 userAPI: Creating guest user', fullName);
    const response = await api.post('/users/guest', {
      full_name: fullName
    });
    return response.data;
  },

  // Get user profile with statistics
  getUserProfile: async (userId) => {
    console.log('🔍 userAPI: Getting user profile', userId);
    const response = await api.get(`/users/${userId}/profile`);
    return response.data;
  },
};

// Player API (ELO and statistics)
export const playerAPI = {
  // Get player profile with ELO
  getProfile: async (userId) => {
    console.log('🔍 playerAPI: Getting profile for', userId);
    const response = await api.get(`/players/profile/${userId}`);
    return response.data;
  },

  // Get my profile
  getMyProfile: async () => {
    console.log('🔍 playerAPI: Getting my profile');
    const response = await api.get('/players/profile');
    return response.data;
  },

  // Get leaderboard
  getLeaderboard: async (limit = 50) => {
    console.log('🔍 playerAPI: Getting leaderboard');
    const response = await api.get(`/players/leaderboard?limit=${limit}`);
    return response.data;
  },

  // Search players
  searchPlayers: async (query, limit = 20) => {
    console.log('🔍 playerAPI: Searching players', query);
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });
    const response = await api.get(`/players/search?${params.toString()}`);
    return response.data;
  }
};

export default api; 