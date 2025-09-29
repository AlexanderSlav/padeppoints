import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './TopNav.css';

const TopNav = ({ title }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="top-nav">
      <div className="top-nav-container">
        <div className="top-nav-brand">
          <span className="brand-icon">🏆</span>
          <span className="brand-text gradient-text">Tornetic</span>
        </div>
        
        <div className="top-nav-title">
          {title && <h1 className="page-title">{title}</h1>}
        </div>
        
        <div className="top-nav-actions">
          <div className="user-menu">
            <button className="user-button">
              <span className="user-avatar">
                {user?.email?.charAt(0).toUpperCase() || '?'}
              </span>
              <span className="user-name hide-mobile">{user?.email?.split('@')[0]}</span>
            </button>
            <div className="user-dropdown">
              <button onClick={() => navigate(`/users/${user?.id}/profile`)} className="dropdown-item">
                <span>👤</span> Profile
              </button>
              <button onClick={() => navigate('/settings')} className="dropdown-item">
                <span>⚙️</span> Settings
              </button>
              <hr className="dropdown-divider" />
              <button onClick={handleLogout} className="dropdown-item">
                <span>🚪</span> Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopNav;