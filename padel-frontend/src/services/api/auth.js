import api from './base';

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

  // OAuth callback
  handleOAuthCallback: async (code, state) => {
    console.log('🔍 authAPI: Handling OAuth callback with code:', code?.substring(0, 10) + '...');
    const response = await api.post('/auth/google/callback', { code, state });
    return response.data;
  },

  // Logout
  logout: async () => {
    console.log('🔍 authAPI: Logging out');
    try {
      await api.post('/auth/jwt/logout');
    } catch (error) {
      console.warn('Logout API call failed, but continuing with local cleanup');
    }
    // Clear local storage regardless of API response
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }
};