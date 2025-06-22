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
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
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

// Auth API
export const authAPI = {
  // Get Google login URL
  getGoogleLoginUrl: async () => {
    const response = await api.get('/auth/google/login');
    return response.data;
  },

  // Test login (for development)
  testLogin: async (email = 'test@example.com') => {
    const response = await api.post('/auth/test-login', { email });
    return response.data;
  },

  // Get current user profile
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Check auth status
  getAuthStatus: async () => {
    const response = await api.get('/auth/status');
    return response.data;
  },

  // Logout
  logout: async () => {
    const response = await api.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    return response.data;
  },
};

// Tournament API
export const tournamentAPI = {
  // Get all tournaments
  getTournaments: async () => {
    const response = await api.get('/tournaments');
    return response.data;
  },

  // Get tournament by ID
  getTournament: async (id) => {
    const response = await api.get(`/tournaments/${id}`);
    return response.data;
  },

  // Create tournament
  createTournament: async (tournamentData) => {
    const response = await api.post('/tournaments', tournamentData);
    return response.data;
  },

  // Update tournament
  updateTournament: async (id, tournamentData) => {
    const response = await api.put(`/tournaments/${id}`, tournamentData);
    return response.data;
  },

  // Delete tournament
  deleteTournament: async (id) => {
    const response = await api.delete(`/tournaments/${id}`);
    return response.data;
  },
};

export default api; 