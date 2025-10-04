import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './components/AuthContext';
import AppLayout from './components/AppLayout';
import CookieConsent from './components/CookieConsent';
import { initGA, trackPageView } from './utils/analytics';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import CallbackPage from './pages/CallbackPage';
import DashboardPage from './pages/DashboardPage';
import CreateTournamentPage from './pages/CreateTournamentPage';
import RegisterPage from './pages/RegisterPage';
import TournamentDiscoveryPage from './pages/TournamentDiscoveryPage';
import TournamentDetailPage from './pages/TournamentDetailPage';
import UserProfilePage from './pages/UserProfilePage';
import SettingsPage from './pages/SettingsPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AdminUsersPage from './pages/AdminUsersPage';
import AdminTournamentsPage from './pages/AdminTournamentsPage';
import AdminAuditPage from './pages/AdminAuditPage';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '32px', marginBottom: '16px' }}>🔄</div>
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route component (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '32px', marginBottom: '16px' }}>🔄</div>
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
};

// Admin Route component (requires superuser)
const AdminRoute = ({ children }) => {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '32px', marginBottom: '16px' }}>🔄</div>
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!user?.is_superuser) {
    return (
      <div className="container">
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚫</div>
            <h2>Access Denied</h2>
            <p style={{ color: '#718096' }}>You don't have permission to access this page.</p>
            <div style={{ marginTop: '24px' }}>
              <a href="/dashboard" className="btn">
                Go to Dashboard
              </a>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return children;
};

// Analytics page tracking component
const AnalyticsTracker = () => {
  const location = useLocation();

  useEffect(() => {
    // Track page view on route change
    trackPageView(location.pathname, document.title);
  }, [location]);

  return null;
};

const AppRoutes = () => {
  return (
    <>
      <AnalyticsTracker />
      <Routes>
      {/* Landing page - accessible to everyone */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Public routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />
      
      {/* OAuth callback route */}
      <Route path="/callback" element={<CallbackPage />} />
      
      {/* Protected routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/create-tournament" 
        element={
          <ProtectedRoute>
            <CreateTournamentPage />
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/tournaments" 
        element={
          <ProtectedRoute>
            <TournamentDiscoveryPage />
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/tournaments/:id" 
        element={
          <ProtectedRoute>
            <TournamentDetailPage />
          </ProtectedRoute>
        } 
      />

      <Route
        path="/users/:userId/profile"
        element={
          <ProtectedRoute>
            <UserProfilePage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />

      {/* Admin Routes (superuser only) */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminDashboardPage />
          </AdminRoute>
        }
      />

      <Route
        path="/admin/users"
        element={
          <AdminRoute>
            <AdminUsersPage />
          </AdminRoute>
        }
      />

      <Route
        path="/admin/tournaments"
        element={
          <AdminRoute>
            <AdminTournamentsPage />
          </AdminRoute>
        }
      />

      <Route
        path="/admin/audit"
        element={
          <AdminRoute>
            <AdminAuditPage />
          </AdminRoute>
        }
      />

      {/* 404 Not Found */}
      <Route 
        path="*" 
        element={
          <div className="container">
            <div className="card">
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>❌</div>
                <h2>Page Not Found</h2>
                <p style={{ color: '#718096' }}>The page you're looking for doesn't exist.</p>
                <div style={{ marginTop: '24px' }}>
                  <a href="/dashboard" className="btn">
                    Go to Dashboard
                  </a>
                </div>
              </div>
            </div>
          </div>
        } 
      />
    </Routes>
    </>
  );
};

const App = () => {
  useEffect(() => {
    // Initialize Google Analytics on app mount (if user has consented)
    initGA();
  }, []);

  return (
    <AuthProvider>
      <Router>
        <AppLayout>
          <div className="App">
            <AppRoutes />
            <CookieConsent />
          </div>
        </AppLayout>
      </Router>
    </AuthProvider>
  );
};

export default App; 