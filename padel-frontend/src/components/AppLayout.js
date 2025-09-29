import React from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import TopNav from './TopNav';
import BottomNav from './BottomNav';
import './AppLayout.css';

const AppLayout = ({ children, title }) => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  
  // Don't show layout on login/register/landing pages
  const noLayoutPaths = ['/', '/login', '/register', '/callback'];
  const shouldShowLayout = !noLayoutPaths.includes(location.pathname) && isAuthenticated;
  
  if (!shouldShowLayout) {
    return <>{children}</>;
  }
  
  return (
    <div className="app-layout">
      <TopNav title={title} />
      <div className="app-content">
        {children}
      </div>
      <BottomNav />
    </div>
  );
};

export default AppLayout;