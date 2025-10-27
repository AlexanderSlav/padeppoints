import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ui/ProtectedRoute';
import PublicRoute from './ui/PublicRoute';
import NotFoundPage from './ui/NotFoundPage';
import { routes } from '../config/routes';

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      {routes.public.map(({ path, component: Component }) => (
        <Route
          key={path}
          path={path}
          element={
            <PublicRoute>
              <Component />
            </PublicRoute>
          }
        />
      ))}

      {/* OAuth callback routes */}
      {routes.callback.map(({ path, component: Component }) => (
        <Route key={path} path={path} element={<Component />} />
      ))}
      
      {/* Protected routes */}
      {routes.protected.map(({ path, component: Component }) => (
        <Route
          key={path}
          path={path}
          element={
            <ProtectedRoute>
              <Component />
            </ProtectedRoute>
          }
        />
      ))}
      
      {/* Default redirects */}
      {routes.redirects.map(({ from, to }) => (
        <Route key={from} path={from} element={<Navigate to={to} replace />} />
      ))}
      
      {/* 404 Not Found */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRoutes;