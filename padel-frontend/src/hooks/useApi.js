import { useState, useCallback } from 'react';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCall, options = {}) => {
    const { 
      onSuccess, 
      onError, 
      showLoading = true,
      resetError = true 
    } = options;

    try {
      if (showLoading) setLoading(true);
      if (resetError) setError(null);
      
      const result = await apiCall();
      
      if (onSuccess) onSuccess(result);
      return result;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred';
      setError(errorMessage);
      
      if (onError) {
        onError(err);
      } else {
        console.error('API Error:', errorMessage);
      }
      
      throw err;
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
  }, []);

  return { loading, error, execute, reset };
};