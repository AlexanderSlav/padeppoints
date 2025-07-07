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
  // Get Google OAuth authorization URL
  getGoogleLoginUrl: async () => {
    console.log('🔍 authAPI: Getting Google login URL');
    const response = await api.get('/auth/google/authorize');
    return response.data;
  },

  // Complete OAuth login
  completeGoogleLogin: async (code, state) => {
    console.log('🔍 authAPI: Completing Google login');
    const response = await api.get('/auth/google/callback', {
      params: { code, state },
    });
    return response.data;
  },

  // Login with email and password
  login: async (email, password) => {
    console.log('🔍 authAPI: Login with credentials for', email);
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    const response = await api.post('/auth/jwt/login', form);
    return response.data;
  },

  // Register a new account
  register: async (email, password, fullName) => {
    console.log('🔍 authAPI: Register new user', email);
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  // Get current user profile
  getCurrentUser: async () => {
    console.log('🔍 authAPI: Getting current user');
    const response = await api.get('/auth/users/me');
    return response.data;
  },

  // Logout
  logout: async () => {
    console.log('🔍 authAPI: Logging out');
    const response = await api.post('/auth/jwt/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    return response.data;
  },
};

// Tournament API
export const tournamentAPI = {
  // Get all tournaments
  getTournaments: async () => {
    console.log('🔍 tournamentAPI: Getting all tournaments');
    const response = await api.get('/tournaments');
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
};

export default api; 
