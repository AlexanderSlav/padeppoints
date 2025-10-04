import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import analytics from '../utils/analytics';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    console.log('🔄 AuthProvider: Running initial checkAuthStatus');
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    console.log('🔍 checkAuthStatus: Starting...');
    try {
      const token = localStorage.getItem('access_token');
      console.log('🔍 checkAuthStatus: Token from localStorage:', token ? 'EXISTS' : 'MISSING');
      
      if (!token) {
        console.log('❌ checkAuthStatus: No token found, setting loading to false');
        setLoading(false);
        return;
      }

      console.log('🔍 checkAuthStatus: Calling authAPI.getCurrentUser()...');
      const userData = await authAPI.getCurrentUser();
      console.log('✅ checkAuthStatus: Got user data:', userData);
      
      setUser(userData);
      setIsAuthenticated(true);
      console.log('✅ checkAuthStatus: Authentication successful');
    } catch (error) {
      console.error('❌ checkAuthStatus: Auth check failed:', error);
      console.log('❌ checkAuthStatus: Removing tokens and setting unauthenticated');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      console.log('🔍 checkAuthStatus: Setting loading to false');
      setLoading(false);
    }
  };

  const login = (userData, token, method = 'email') => {
    console.log('✅ login: Called with user:', userData);
    console.log('✅ login: Token:', token ? 'PROVIDED' : 'MISSING');

    try {
      localStorage.setItem('access_token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      console.log('✅ login: Token stored in localStorage');

      // Verify storage worked
      const storedToken = localStorage.getItem('access_token');
      console.log('✅ login: Verification - stored token exists:', storedToken ? 'YES' : 'NO');

      setUser(userData);
      setIsAuthenticated(true);

      // Track login event
      analytics.trackLogin(method);

      console.log('✅ login: All steps completed successfully');
    } catch (error) {
      console.error('❌ login: Error storing token:', error);
    }
  };

  const logout = async () => {
    console.log('🚪 logout: Starting logout process');
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('❌ logout: Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      setUser(null);
      setIsAuthenticated(false);

      // Track logout event
      analytics.trackLogout();

      console.log('✅ logout: Completed');
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    checkAuthStatus,
  };

  console.log('🔄 AuthProvider: Current state - isAuthenticated:', isAuthenticated, 'loading:', loading);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 