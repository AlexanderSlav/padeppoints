import api from './base';

export const userAPI = {
  // Get user profile by ID
  getUserProfile: async (userId) => {
    console.log('🔍 userAPI: Getting user profile', userId);
    const response = await api.get(`/users/${userId}/profile`);
    return response.data;
  },

  // Update current user
  updateCurrentUser: async (updateData) => {
    console.log('🔍 userAPI: Updating current user');
    const response = await api.patch('/users/me', updateData);
    return response.data;
  },

  // Delete current user account
  deleteAccount: async () => {
    console.log('🔍 userAPI: Deleting account');
    const response = await api.delete('/users/me');
    return response.data;
  },

  // Search users
  searchUsers: async (query, limit = 10) => {
    console.log('🔍 userAPI: Searching users', query);
    const params = new URLSearchParams();
    params.append('q', query);
    params.append('limit', limit);
    
    const response = await api.get(`/users/search?${params.toString()}`);
    return response.data;
  },

  // Get user statistics
  getUserStats: async (userId) => {
    console.log('🔍 userAPI: Getting user stats', userId);
    const response = await api.get(`/users/${userId}/stats`);
    return response.data;
  },

  // Get user tournaments
  getUserTournaments: async (userId) => {
    console.log('🔍 userAPI: Getting user tournaments', userId);
    const response = await api.get(`/users/${userId}/tournaments`);
    return response.data;
  }
};