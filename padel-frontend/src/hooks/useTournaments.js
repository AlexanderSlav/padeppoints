import { useState, useCallback } from 'react';
import { tournamentAPI } from '../services/api';
import { useApi } from './useApi';

export const useTournaments = () => {
  const [tournaments, setTournaments] = useState([]);
  const [tournament, setTournament] = useState(null);
  const { loading, error, execute, reset } = useApi();

  const fetchTournaments = useCallback(async (filters = {}) => {
    return execute(
      () => tournamentAPI.getTournaments(filters),
      {
        onSuccess: (data) => {
          setTournaments(data.tournaments || []);
        }
      }
    );
  }, [execute]);

  const fetchTournament = useCallback(async (id) => {
    return execute(
      () => tournamentAPI.getTournament(id),
      {
        onSuccess: (data) => {
          setTournament(data);
        }
      }
    );
  }, [execute]);

  const createTournament = useCallback(async (tournamentData) => {
    return execute(() => tournamentAPI.createTournament(tournamentData));
  }, [execute]);

  const joinTournament = useCallback(async (tournamentId) => {
    return execute(() => tournamentAPI.joinTournament(tournamentId));
  }, [execute]);

  const leaveTournament = useCallback(async (tournamentId) => {
    return execute(() => tournamentAPI.leaveTournament(tournamentId));
  }, [execute]);

  const startTournament = useCallback(async (tournamentId) => {
    return execute(() => tournamentAPI.startTournament(tournamentId));
  }, [execute]);

  const finishTournament = useCallback(async (tournamentId) => {
    return execute(() => tournamentAPI.finishTournament(tournamentId));
  }, [execute]);

  const fetchTournamentPlayers = useCallback(async (tournamentId) => {
    return execute(() => tournamentAPI.getTournamentPlayers(tournamentId));
  }, [execute]);

  const fetchTournamentRounds = useCallback(async (tournamentId) => {
    return execute(() => tournamentAPI.getTournamentRounds(tournamentId));
  }, [execute]);

  return {
    tournaments,
    tournament,
    loading,
    error,
    fetchTournaments,
    fetchTournament,
    createTournament,
    joinTournament,
    leaveTournament,
    startTournament,
    finishTournament,
    fetchTournamentPlayers,
    fetchTournamentRounds,
    reset
  };
};