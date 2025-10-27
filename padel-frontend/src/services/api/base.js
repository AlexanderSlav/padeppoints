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

export default api;