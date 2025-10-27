import api from './base';

export const tournamentAPI = {
  // Create tournament
  createTournament: async (tournamentData) => {
    console.log('🔍 tournamentAPI: Creating tournament', tournamentData.name);
    const response = await api.post('/tournaments/', tournamentData);
    return response.data;
  },

  // Get all tournaments with filters
  getTournaments: async (filters = {}) => {
    console.log('🔍 tournamentAPI: Getting tournaments with filters', filters);
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value);
      }
    });

    const response = await api.get(`/tournaments/?${params.toString()}`);
    return response.data;
  },

  // Get tournament by ID
  getTournament: async (id) => {
    console.log('🔍 tournamentAPI: Getting tournament', id);
    const response = await api.get(`/tournaments/${id}`);
    return response.data;
  },

  // Get user's tournaments
  getMyTournaments: async () => {
    console.log('🔍 tournamentAPI: Getting my tournaments');
    const response = await api.get('/tournaments/my');
    return response.data;
  },

  // Join tournament
  joinTournament: async (tournamentId) => {
    console.log('🔍 tournamentAPI: Joining tournament', tournamentId);
    const response = await api.post(`/tournaments/${tournamentId}/join`);
    return response.data;
  },

  // Leave tournament
  leaveTournament: async (tournamentId) => {
    console.log('🔍 tournamentAPI: Leaving tournament', tournamentId);
    const response = await api.post(`/tournaments/${tournamentId}/leave`);
    return response.data;
  },

  // Start tournament
  startTournament: async (tournamentId) => {
    console.log('🔍 tournamentAPI: Starting tournament', tournamentId);
    const response = await api.post(`/tournaments/${tournamentId}/start`);
    return response.data;
  },

  // Finish tournament
  finishTournament: async (tournamentId) => {
    console.log('🔍 tournamentAPI: Finishing tournament', tournamentId);
    const response = await api.post(`/tournaments/${tournamentId}/finish`);
    return response.data;
  },

  // Get tournament players
  getTournamentPlayers: async (tournamentId) => {
    console.log('🔍 tournamentAPI: Getting tournament players', tournamentId);
    const response = await api.get(`/tournaments/${tournamentId}/players`);
    return response.data;
  },

  // Get tournament rounds
  getTournamentRounds: async (tournamentId) => {
    console.log('🔍 tournamentAPI: Getting tournament rounds', tournamentId);
    const response = await api.get(`/tournaments/${tournamentId}/rounds`);
    return response.data;
  },

  // Update tournament
  updateTournament: async (tournamentId, updateData) => {
    console.log('🔍 tournamentAPI: Updating tournament', tournamentId);
    const response = await api.patch(`/tournaments/${tournamentId}`, updateData);
    return response.data;
  },

  // Delete tournament
  deleteTournament: async (tournamentId) => {
    console.log('🔍 tournamentAPI: Deleting tournament', tournamentId);
    const response = await api.delete(`/tournaments/${tournamentId}`);
    return response.data;
  },

  // Get tournament planning advice
  getTournamentPlanningAdvice: async (params) => {
    console.log('🔍 tournamentAPI: Getting tournament planning advice', params);
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });

    const response = await api.get(`/tournaments/planning-advice?${queryParams.toString()}`);
    return response.data;
  }
};